import json
from typing import Dict


class Locale:
    def __init__(self, data: dict, default: dict):
        self._data = data
        self._default = default

    @property
    def server_description(self) -> str:
        return self._data["server_description"]

    def item_not_found(self, item: str, name: str) -> str:
        return self._data["item_not_found"].format(item=item, name=name)

    def item_type_not_found(self, item: str) -> str:
        return self._data["item_type_not_found"].format(item=item)

    def items_not_found(self, item: str) -> str:
        return self._data["items_not_found"].format(item=item)

    def items_not_found_search(self, item: str) -> str:
        return self._data["items_not_found_search"].format(item=item)


class LocaleManager:
    def __init__(self, default_locale: str):
        self.default_locale = default_locale
        self.locales: Dict[str, Locale] = {}

        self._default_locale = None
        self._default_locale = self.load_locale("en", overwrite_default={})

    def load_locale(self, locale: str, overwrite_default: dict = None) -> Locale:
        if locale == "zhs":
            locale = "zh-cn"
        elif locale == "zht":
            locale = "zh-TW"
        if locale in self.locales:
            return self.locales[locale]
        try:
            with open(f"locales/locales/{locale}.json", "r", encoding="utf8") as f:
                d = json.load(f)
            locale_class = Locale(
                d,
                (
                    overwrite_default
                    if overwrite_default != None
                    else self._default_locale._data
                ),
            )
            self.locales[locale] = locale_class
            return locale_class
        except FileNotFoundError:
            return self._default_locale

    def get_messages(self, locale: str) -> Locale:
        locale_class = self.load_locale(locale)
        return locale_class


Locale = LocaleManager(default_locale="en")
