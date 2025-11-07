from os import makedirs
import os
import re
import tempfile
from typing import Union, Optional, List, Dict, Callable
import time
import optuna
from optuna_dashboard import save_note
from .http_client import ConnectRPCClient
from .serializer import serialize, build_requirements, object_to_json
from ._config import AIAUTO_API_TARGET


def _validate_study_name(name: str) -> None:
    """Validate study name follows Kubernetes DNS-1123 subdomain rules.

    Rules:
    - Must contain only lowercase letters, numbers, and hyphens (-)
    - Must start and end with a letter or number
    - Maximum 63 characters

    Raises:
        ValueError: If study name is invalid
    """
    if not name:
        raise ValueError("Study name cannot be empty")

    if len(name) > 63:
        raise ValueError(
            f"Study name too long ({len(name)} characters). "
            f"Maximum 63 characters allowed for Kubernetes resource names."
        )

    # Kubernetes DNS-1123 subdomain: lowercase alphanumeric and hyphen only
    # Must start and end with alphanumeric
    if not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$', name):
        raise ValueError(
            f"Invalid study name '{name}'. "
            f"Study name must contain only lowercase letters, numbers, and hyphens (-). "
            f"Must start and end with a letter or number."
        )


class AIAutoController:
    _instances = {}

    def __new__(cls, token: str):
        if token not in cls._instances:
            cls._instances[token] = super().__new__(cls)
        return cls._instances[token]

    def __init__(self, token: str):
        if hasattr(self, 'token') and self.token == token:
            return

        self.token = token
        self.client = ConnectRPCClient(token)

        # EnsureWorkspace 호출해서 journal_grpc_storage_proxy_host_external 받아와서 storage 초기화
        try:
            response = self.client.call_rpc("EnsureWorkspace", {})

            # 받아온 journal_grpc_storage_proxy_host_external로 storage 초기화
            host_external = response.get('journalGrpcStorageProxyHostExternal', '')
            if not host_external:
                raise RuntimeError("No storage host returned from EnsureWorkspace")

            host, port = host_external.split(':')
            self.storage = optuna.storages.GrpcStorageProxy(host=host, port=int(port))

            # Store the internal host for CRD usage (if needed later)
            self.storage_host_internal = response.get('journalGrpcStorageProxyHostInternal', '')
            self.dashboard_url = response.get('dashboardUrl', '')

        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize workspace: {e}\n"
                "Please delete and reissue your token from the web dashboard at https://dashboard.common.aiauto.pangyo.ainode.ai"
            ) from e

        # artifact store: lazily resolved at call time based on runtime environment
        self._artifact_store = None
        self.tmp_dir = tempfile.mkdtemp(prefix=f'ai_auto_tmp_')

    def get_storage(self):
        return self.storage

    def get_artifact_store(self) -> Union[
        optuna.artifacts.FileSystemArtifactStore,
        optuna.artifacts.Boto3ArtifactStore,
        optuna.artifacts.GCSArtifactStore,
    ]:
        # Lazy init: prefer container-mounted PVC at /artifacts (runner env),
        # fallback to local ./artifacts for client/local usage.
        if self._artifact_store is None:
            if os.path.isdir('/artifacts'):
                path = '/artifacts'
            else:
                path = './artifacts'
                if not os.path.isdir(path):
                    makedirs(path, exist_ok=True)
            self._artifact_store = optuna.artifacts.FileSystemArtifactStore(path)

        return self._artifact_store

    def get_artifact_tmp_dir(self):
        return self.tmp_dir

    def create_study(
        self,
        study_name: str,
        direction: Optional[str] = 'minimize',
        directions: Optional[List[str]] = None,
        sampler: Union[object, dict, None] = None,
        pruner: Union[object, dict, None] = None
    ) -> 'StudyWrapper':
        """Create a new study using the controller's token."""
        # Validate study name follows Kubernetes DNS rules
        _validate_study_name(study_name)

        if not direction and not directions:
            raise ValueError("Either 'direction' or 'directions' must be specified")

        if direction and directions:
            raise ValueError("Cannot specify both 'direction' and 'directions'")

        try:
            # Prepare request data for CreateStudy
            request_data = {
                "spec": {
                    "studyName": study_name,
                    "direction": direction or "",
                    "directions": directions or [],
                    "samplerJson": object_to_json(sampler),
                    "prunerJson": object_to_json(pruner)
                }
            }

            # Call CreateStudy RPC
            response = self.client.call_rpc("CreateStudy", request_data)

            # Return StudyWrapper
            return StudyWrapper(
                study_name=response.get("studyName", study_name),
                storage=self.storage,
                controller=self
            )

        except Exception as e:
            raise RuntimeError(f"Failed to create study: {e}") from e


class TrialController:
    def __init__(self, trial: Union[optuna.trial.Trial, optuna.trial.FrozenTrial]):
        self.trial = trial
        self.logger = optuna.logging.get_logger("optuna")
        self.logs = []
        self.last_save_time = time.time()
        self.log_count = 0

    def get_trial(self) -> Union[optuna.trial.Trial, optuna.trial.FrozenTrial]:
        return self.trial

    def log(self, value: str):
        # 로그를 배열에 추가
        self.logs.append(value)
        self.log_count += 1

        # 5개 로그마다 + 1분마다 save_note 호출
        current_time = time.time()
        if self.log_count % 5 == 0 or current_time - self.last_save_time >= 60:
            self._save_note()

        # 콘솔에도 출력 (Pod 실행 중 실시간 확인용)
        self.logger.info(f'\ntrial_number: {self.trial.number}, {value}')

    def _save_note(self):
        """optuna_dashboard의 save_note로 로그 저장"""
        try:
            # 각 로그에 인덱스 번호 추가 및 구분선으로 구분
            separator = '\n' + '-' * 10 + '\n'
            formatted_logs = [f"[{i+1:05d}] {log}" for i, log in enumerate(self.logs)]
            note_content = separator.join(formatted_logs)
            save_note(self.trial, note_content)
            self.last_save_time = time.time()
        except Exception as e:
            # save_note 실패해도 계속 진행 (fallback: console log)
            self.logger.warning(f"Failed to save note: {e}")

    def flush(self):
        """Trial 종료 시 남은 로그 강제 저장 (조건 3)"""
        if self.logs:
            self._save_note()


# 용량 제한으로 상위 N개의 trial artifact 만 유지
class CallbackTopNArtifact:
    def __init__(
        self,
        artifact_store: Union[
            optuna.artifacts.FileSystemArtifactStore,
            optuna.artifacts.Boto3ArtifactStore,
            optuna.artifacts.GCSArtifactStore,
        ],
        artifact_attr_name: str = 'artifact_id',
        n_keep: int = 5,
    ):
        self.artifact_store = artifact_store
        self.check_attr_name = artifact_attr_name
        self.n_keep = n_keep

    def __call__(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial):
        # COMPLETE 상태이고 artifact를 가진 trial들만 정렬
        finished_with_artifacts = [
            t for t in study.trials
            if t.state == optuna.trial.TrialState.COMPLETE and self.check_attr_name in t.user_attrs
        ]

        # 방향에 따라 정렬 (maximize면 내림차순, minimize면 오름차순)
        reverse_sort = study.direction == optuna.study.StudyDirection.MAXIMIZE
        finished_with_artifacts.sort(key=lambda t: t.value, reverse=reverse_sort)

        # 상위 n_keep개 초과하는 trial들의 artifact 삭제
        for old_trial in finished_with_artifacts[self.n_keep:]:
            artifact_id = old_trial.user_attrs.get(self.check_attr_name)
            if artifact_id:
                # 삭제 대상 trial의 로그를 기록하기 위한 TrialController 생성
                tc = TrialController(old_trial)

                try:
                    self.artifact_store.remove(artifact_id)
                    tc.log(f"Artifact {artifact_id} removed (ranked below top {self.n_keep})")
                except Exception as e:
                    tc.log(f"Warning: Failed to remove artifact {artifact_id}: {e}")
                finally:
                    try:
                        # Journal Storage는 append-only WAL 방식이므로 기존 attr 수정 불가
                        # 대신 새로운 artifact_removed 플래그를 추가
                        # UI에서 이 플래그를 체크하여 Download 버튼을 숨김 (CRD Status는 user_attrs를 그대로 노출)
                        # Note: old_trial은 FrozenTrial이므로 study._storage 사용
                        study._storage.set_trial_user_attr(old_trial._trial_id, 'artifact_removed', True)
                    except Exception as e2:
                        tc.log(f"Warning: Failed to set artifact_removed flag for trial {old_trial.number}: {e2}")

                    # 로그 즉시 저장
                    tc.flush()


class StudyWrapper:
    def __init__(self, study_name: str, storage, controller: AIAutoController):
        self.study_name = study_name
        self._storage = storage
        self._controller = controller
        self._study = None

    def get_study(self) -> optuna.Study:
        if self._study is None:
            try:
                self._study = optuna.create_study(
                    study_name=self.study_name,
                    storage=self._storage,
                    load_if_exists=True,
                )

                # Wrap the original ask() method to add trialbatch_name
                original_ask = self._study.ask

                def wrapped_ask(fixed_distributions=None):
                    print("⚠️  WARNING: ask/tell trial runs locally (not in Kubernetes)")
                    print("    - No Pod created")
                    print("    - Not counted in TrialBatch statistics")
                    print("    - Visible in Optuna Dashboard with 'ask_tell_local' tag")

                    trial = original_ask(fixed_distributions=fixed_distributions)

                    try:
                        trial.set_user_attr('trialbatch_name', 'ask_tell_local')
                    except Exception as e:
                        print(f"Warning: Failed to set trialbatch_name: {e}")

                    return trial

                self._study.ask = wrapped_ask

            except Exception as e:
                raise RuntimeError(
                    "Failed to get study. If this persists, please delete and reissue your token "
                    "from the web dashboard at https://dashboard.common.aiauto.pangyo.ainode.ai"
                ) from e
        return self._study

    def optimize(
        self,
        objective: Callable,
        n_trials: int = 10,
        parallelism: int = 2,
        requirements_file: Optional[str] = None,
        requirements_list: Optional[List[str]] = None,
        resources_requests: Optional[Dict[str, str]] = None,
        resources_limits: Optional[Dict[str, str]] = None,
        runtime_image: Optional[str] = None,
        use_gpu: bool = False
    ) -> None:
        # 리소스 기본값 설정
        if resources_requests is None:
            if use_gpu:
                resources_requests = {"cpu": "2", "memory": "4Gi"}
            else:
                resources_requests = {"cpu": "1", "memory": "1Gi"}

        if resources_limits is None:
            resources_limits = {}  # 빈 dict로 전달, operator가 requests 기반으로 처리

        if runtime_image is None or runtime_image == "":
            if use_gpu:
                runtime_image = "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime"
            else:
                runtime_image = "ghcr.io/astral-sh/uv:python3.8-bookworm-slim"
        try:
            request_data = {
                "objective": {
                    "sourceCode": serialize(objective),
                    "requirementsTxt": build_requirements(requirements_file, requirements_list),
                    "objectiveName": objective.__name__  # 함수명 추출하여 전달
                },
                "batch": {
                    "studyName": self.study_name,
                    "nTrials": n_trials,
                    "parallelism": parallelism,
                    "runtimeImage": runtime_image or "",
                    "resourcesRequests": resources_requests or {},
                    "resourcesLimits": resources_limits or {},
                    "useGpu": use_gpu
                }
            }

            self._controller.client.call_rpc("Optimize", request_data)

        except Exception as e:
            raise RuntimeError(f"Failed to start optimization: {e}") from e

    def get_status(self) -> dict:
        try:
            response = self._controller.client.call_rpc(
                "GetStatus",
                {"studyName": self.study_name}
            )

            # Convert camelCase to snake_case for backward compatibility
            return {
                "study_name": response.get("studyName", ""),
                "count_active": response.get("countActive", 0),
                "count_succeeded": response.get("countSucceeded", 0),
                "count_pruned": response.get("countPruned", 0),
                "count_failed": response.get("countFailed", 0),
                "count_total": response.get("countTotal", 0),
                "count_completed": response.get("countCompleted", 0),
                "dashboard_url": response.get("dashboardUrl", ""),
                "last_error": response.get("lastError", ""),
                "updated_at": response.get("updatedAt", "")
            }

        except Exception as e:
            raise RuntimeError(f"Failed to get status: {e}") from e

    def __repr__(self) -> str:
        return f"StudyWrapper(study_name='{self.study_name}', storage={self._storage})"
