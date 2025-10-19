from helpers.sonolus_typings import Text, ItemType, Icon
from helpers.models import (
    ServerItemSection,
    ServerItem,
    ServerForm,
    ServerOption,
    ServerCollectionItemOption,
    ServerFileOption,
    ServerMultiOption,
    ServerSelectOption,
    ServerSliderOption,
    ServerServerItemsOption,
    ServerServerItemOption,
    ServerTextAreaOption,
    ServerTextOption,
    ServerToggleOption,
    SIL,
)


def create_section(
    title: Text | str,
    item_type: ItemType,
    items: list[ServerItem],
    description: str | None = None,
    icon: Icon | str | None = None,
    search: ServerForm | None = None,
    search_values: str | None = None,
    help: str | None = None,
) -> ServerItemSection:
    section_dict = {
        "title": title,
        "itemType": item_type.removesuffix("s"),
        "items": items,
    }

    if description:
        section_dict["description"] = description

    if icon:
        section_dict["icon"] = icon

    if search:
        section_dict["search"] = search

    if search_values:
        section_dict["searchValues"] = search_values

    if help:
        section_dict["help"] = help

    return section_dict


def create_server_form(
    type: str,
    title: Text | str,
    require_confirmation: bool,
    options: list[ServerOption],
    description: str | None = None,
    icon: Icon | str | None = None,
    help: str | None = None,
) -> ServerForm:
    server_form_dict = {
        "type": type,
        "title": title,
        "requireConfirmation": require_confirmation,
        "options": options,
    }

    if description:
        server_form_dict["description"] = description
    if icon:
        server_form_dict["icon"] = icon
    if help:
        server_form_dict["help"] = help

    return server_form_dict


class ServerFormOptionsFactory:
    @staticmethod
    def server_text_option(
        query: str,
        name: Text | str,
        required: bool,
        default: str,
        placeholder: Text | str,
        limit: int,
        shortcuts: list[str],
        description: str | None = None,
    ) -> ServerTextOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "text",
            "def": default,
            "placeholder": placeholder,
            "limit": limit,
            "shortcuts": shortcuts,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_text_area_option(
        query: str,
        name: Text | str,
        required: bool,
        default: str,
        placeholder: Text | str,
        limit: int,
        shortcuts: list[str],
        description: str | None = None,
    ) -> ServerTextAreaOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "textArea",
            "def": default,
            "placeholder": placeholder,
            "limit": limit,
            "shortcuts": shortcuts,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_slider_option(
        query: str,
        name: Text | str,
        required: bool,
        default: float,
        min_value: float,
        max_value: float,
        step: float,
        unit: Text | str | None = None,
        description: str | None = None,
    ) -> ServerSliderOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "slider",
            "def": default,
            "min": min_value,
            "max": max_value,
            "step": step,
        }
        if unit:
            option["unit"] = unit
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_toggle_option(
        query: str,
        name: Text | str,
        required: bool,
        default: bool,
        description: str | None = None,
    ) -> ServerToggleOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "toggle",
            "def": default,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_select_option(
        query: str,
        name: Text | str,
        required: bool,
        default: str,
        values: list[dict],  # [{"name": str, "title": Text | str}]
        description: str | None = None,
    ) -> ServerSelectOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "select",
            "def": default,
            "values": values,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_multi_option(
        query: str,
        name: Text | str,
        required: bool,
        default: list[bool],
        values: list[dict],  # [{"name": str, "title": Text | str}]
        description: str | None = None,
    ) -> ServerMultiOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "multi",
            "def": default,
            "values": values,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_server_item_option(
        query: str,
        name: Text | str,
        required: bool,
        item_type: ItemType,
        allow_other_servers: bool,
        default: SIL | None = None,
        description: str | None = None,
    ) -> ServerServerItemOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "serverItem",
            "itemType": item_type,
            "allowOtherServers": allow_other_servers,
        }
        if default is not None:
            option["def"] = default
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_server_items_option(
        query: str,
        name: Text | str,
        required: bool,
        item_type: ItemType,
        allow_other_servers: bool,
        limit: int,
        default: list[SIL] = None,
        description: str | None = None,
    ) -> ServerServerItemsOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "serverItems",
            "itemType": item_type,
            "allowOtherServers": allow_other_servers,
            "limit": limit,
        }
        if default is not None:
            option["def"] = default
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_collection_item_option(
        query: str,
        name: Text | str,
        required: bool,
        item_type: ItemType,
        description: str | None = None,
    ) -> ServerCollectionItemOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "collectionItem",
            "itemType": item_type,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_file_option(
        query: str,
        name: Text | str,
        required: bool,
        default: str,
        description: str | None = None,
    ) -> ServerFileOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "file",
            "def": default,
        }
        if description:
            option["description"] = description
        return option
