import json
from typing import Dict


class Loc:
    def __init__(self, data: dict, default: dict):
        self._data = data
        self._default = default

    def _get(self, value: str) -> str:
        try:
            return self._data[value]
        except:
            return self._default[value]

    @property
    def server_description(self) -> str:
        return self._get("server_description")

    def item_not_found(self, item: str, name: str) -> str:
        return self._get("item_not_found").format(item=item, name=name)

    def item_type_not_found(self, item: str) -> str:
        return self._get("item_type_not_found").format(item=item)

    def items_not_found(self, item: str) -> str:
        return self._get("items_not_found").format(item=item)

    def items_not_found_search(self, item: str) -> str:
        return self._get("items_not_found_search").format(item=item)

    @property
    def not_logged_in(self) -> str:
        return self._get("not_logged_in")

    @property
    def not_found(self) -> str:
        return self._get("not_found")

    @property
    def unknown_error(self) -> str:
        return self._get("unknown_error")


class LocaleManager:
    def __init__(self, default_locale: str):
        self.default_locale = default_locale
        self.locales: Dict[str, Loc] = {}

        self._default_locale = None
        self._default_locale = self.load_locale("en", overwrite_default={})

    def load_locale(self, locale: str, overwrite_default: dict = None) -> Loc:
        if locale == "zhs":
            locale = "zh-cn"
        elif locale == "zht":
            locale = "zh-TW"
        if locale in self.locales:
            return self.locales[locale]
        try:
            with open(f"locales/locales/{locale}.json", "r", encoding="utf8") as f:
                d = json.load(f)
            locale_class = Loc(
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

    def get_messages(self, locale: str) -> Loc:
        locale_class = self.load_locale(locale)
        return locale_class


Locale = LocaleManager(default_locale="en")
