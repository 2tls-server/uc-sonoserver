from typing import Protocol, Callable


class MessagesProtocol(Protocol):
    server_description: str
    item_not_found: Callable
    item_type_not_found: Callable
    items_not_found: Callable
    items_not_found_search: Callable
