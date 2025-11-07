import os
from dataclasses import dataclass
from typing import Any, Dict

from ...core.utils.common_utils import HashableDataclass
from ...core.contracts.exceptions import MissingRunningContextException
from ..contracts.telemetry import StoreToolEventCustomDimensions

SUBSCRIPTION_ENV_NAME = "AZUREML_ARM_SUBSCRIPTION"
RESOURCEGROUP_ENV_NAME = "AZUREML_ARM_RESOURCEGROUP"
WORKSPACE_ENV_NAME = "AZUREML_ARM_WORKSPACE_NAME"


class MissingAMLRunningContextException(MissingRunningContextException):
    pass


@dataclass
class PFRuntimeInfo(HashableDataclass):
    edition: str = None
    compute_type: str = None
    runtime_mode: str = None
    runtime_version: str = None


class PromptflowRuntimeUtils:
    @staticmethod
    def is_running_in_aml() -> bool:
        return SUBSCRIPTION_ENV_NAME in os.environ

    @staticmethod
    def get_current_workspace_info():
        if not PromptflowRuntimeUtils.is_running_in_aml():
            raise MissingAMLRunningContextException(
                "No Azure ML running context provided from Promptflow."
            )
        from ...core.utils.aml_helpers import WorkspaceInfo

        return WorkspaceInfo(
            subscription_id=os.environ[SUBSCRIPTION_ENV_NAME],
            resource_group=os.environ[RESOURCEGROUP_ENV_NAME],
            workspace_name=os.environ[WORKSPACE_ENV_NAME],
        )

    @staticmethod
    def get_pf_context_info() -> Dict[str, Any]:
        from promptflow._internal import OperationContext

        pf_operation_context = OperationContext.get_instance()
        context = {}
        if pf_operation_context:
            context.update(pf_operation_context.get_context_dict())
            context[StoreToolEventCustomDimensions.REQUEST_ID] = pf_operation_context.request_id
        return context

    @staticmethod
    def get_pf_context_info_for_telemetry() -> Dict[str, Any]:

        telemetry_dimensions = [dimension.value for dimension in StoreToolEventCustomDimensions]

        pf_context_info = PromptflowRuntimeUtils.get_pf_context_info()
        candidates_for_telemetry = {k.replace("-", "_"): v for k, v in pf_context_info.items()}

        return {k: v for k, v in candidates_for_telemetry.items() if k in telemetry_dimensions}

    @staticmethod
    def get_app_insight_conn_str() -> str:
        from promptflow.runtime.utils.internal_logger_utils import TelemetryLogHandler

        return TelemetryLogHandler.CONNECTION_STRING

    @staticmethod
    def get_url_for_relative_path_on_workspace_blob_store(relative_path: str) -> str:
        if PromptflowRuntimeUtils.is_running_in_aml():
            from ...core.utils.aml_helpers import AmlAgent

            workspace_info = PromptflowRuntimeUtils.get_current_workspace_info()
            return AmlAgent(workspace_info).get_url_for_relative_path_on_workspace_blob_store(relative_path)
        return None

    @staticmethod
    def get_credential_if_blob_is_on_workspace_default_storage(blob_url: str) -> str:
        if PromptflowRuntimeUtils.is_running_in_aml():
            from ...core.utils.aml_helpers import AmlAgent

            workspace_info = PromptflowRuntimeUtils.get_current_workspace_info()
            aml_agent = AmlAgent(workspace_info)
            if aml_agent.is_blob_on_workspace_default_storage(blob_url):
                return aml_agent.get_default_storage_credential()
        return None
