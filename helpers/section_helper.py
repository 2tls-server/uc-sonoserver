from typing import Union, List, Optional

from helpers.sonolus_typings import Text, ItemType, Icon
from helpers.datastructs import ServerItemSection, ServerItem, ServerForm


def create_section(
    title: Union[Text, str],
    item_type: ItemType,
    items: List[ServerItem],
    description: Optional[str] = None,
    icon: Optional[Union[Icon, str]] = None,
    search: Optional[ServerForm] = None,
    search_values: Optional[str] = None,
    help: Optional[str] = None,
) -> ServerItemSection:
    section_dict = {
        "title": title,
        "itemType": item_type.removesuffix("s"),
        "items": items,
    }

    if description is not None:
        section_dict["description"] = description

    if icon is not None:
        section_dict["icon"] = icon

    if search is not None:
        section_dict["search"] = search

    if search_values is not None:
        section_dict["searchValues"] = search_values

    if help is not None:
        section_dict["help"] = help

    return section_dict
