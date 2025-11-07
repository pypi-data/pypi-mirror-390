from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import functools
from requests_cache import CachedSession
import threading


class CallbackContext(object):
    __instances = dict()
    __instances_lock = threading.Lock()

    __http_session = CachedSession(
        'http_session',
        expire_after=120,
        stale_if_error=False,
        backend='memory')

    def __init__(self, subscription_id, resource_group, workspace_name) -> None:
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.workspace_name = workspace_name
        self.credential = DefaultAzureCredential()

    @staticmethod
    def get(subscription_id, resource_group, workspace_name):
        if (subscription_id, resource_group, workspace_name) not in CallbackContext.__instances:
            with CallbackContext.__instances_lock:
                if (subscription_id, resource_group, workspace_name) not in CallbackContext.__instances:
                    CallbackContext.__instances[(subscription_id, resource_group, workspace_name)] =\
                        CallbackContext(subscription_id, resource_group, workspace_name)

        return CallbackContext.__instances[(subscription_id, resource_group, workspace_name)]

    @property
    def arm_id(self):
        return f'/subscriptions/{self.subscription_id}' +\
            f'/resourceGroups/{self.resource_group}' +\
            f'/providers/Microsoft.MachineLearningServices/workspaces/{self.workspace_name}'

    @property
    @functools.lru_cache(maxsize=32)
    def ml_client(self):
        return MLClient(
            credential=self.credential,
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name)

    @property
    def http(self):
        return CallbackContext.__http_session


def tool_ui_callback(func):
    def wrapper(subscription_id, resource_group_name, workspace_name, *args, **kwargs):
        context = CallbackContext.get(subscription_id, resource_group_name, workspace_name)
        return func(context, *args, **kwargs)

    return wrapper
