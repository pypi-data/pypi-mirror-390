from _typeshed import Incomplete
from enum import Enum
from typing import Any, Coroutine, Protocol
from virtualitics_sdk.elements.button import ButtonType as ButtonType
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface

class CallbackType(Enum):
    STANDARD: Incomplete
    ASSET_DOWNLOAD: Incomplete
    DRILLDOWN: Incomplete
    PAGE_UPDATE: Incomplete

class CallbackReturnType(Enum):
    CARD: str
    PAGE: str
    TEXT: str

class AutoRefreshCallback(Protocol):
    """
    Protocol/Type Hint for the on_auto_refresh callback

    The callback must be an async function with the following signature:

    async def example_callback(store_interface: StoreInterface,
                               step_clients: dict[str, Any] | None = None,
                               default_refresh_rate: int = 500) -> None:
        pass

    :param store_interface: StoreInterface for modifying the page object and accessing stored data
    :param default_refresh_rate: The default refresh rate in seconds
    :param **step_clients: The pre-initialized clients (pyvip, etc) for the step
    """
    def __call__(self, store_interface: StoreInterface, default_refresh_rate: int = 500, **step_clients: dict[str, Any] | None) -> Coroutine[Any, Any, None]: ...

class PageUpdateCallback(Protocol):
    """
    Protocol/Type Hint for the ButtonType.PAGE_UPDATE.on_click callback

    The callback must be an async function with the following signature:

    async def example_callback(store_interface: StoreInterface,
                               step_clients: dict[str, Any] | None = None) -> None:

    :param store_interface: StoreInterface for modifying the page object and accessing stored data
    :param **step_clients: The pre-initialized clients (pyvip, etc) for the step
    """
    def __call__(self, store_interface: StoreInterface, **step_clients: dict[str, Any] | None) -> Coroutine[Any, Any, None]: ...

class StandardOnClickCallback(Protocol):
    '''
    Protocol/Type Hint for the ButtonType.STANDARD.on_click callback

    The callback must be an async function with the following signature:

    async def example_callback(store_interface: StoreInterface,
                               step_clients: dict[str, Any] | None = None) -> str:
        return "success message"

    :param store_interface: StoreInterface for modifying the page object and accessing stored data
    :param step_clients: The pre-initialized clients (pyvip, etc) for the step
    '''
    def __call__(self, store_interface: StoreInterface, **step_clients: dict[str, Any] | None) -> Coroutine[Any, Any, str]: ...
