import importlib
from typing import Type, TypeVar, Dict

from .protocol import MessagesProtocol

T = TypeVar("T", bound=MessagesProtocol)


class LocaleManager:
    def __init__(self, default_locale: str):
        self.default_locale = default_locale
        self.locales: Dict[str, Type[MessagesProtocol]] = {}

    def load_locale(self, locale: str) -> Type[MessagesProtocol]:
        if locale == "zhs":
            locale = "zh-cn"
        elif locale == "zht":
            locale = "zh-TW"
        if locale in self.locales:
            return self.locales[locale]
        try:
            locale_module = importlib.import_module("locales.locales." + locale)
            self.locales[locale] = locale_module.Messages
            return locale_module.Messages
        except (ModuleNotFoundError, AttributeError):
            return self.load_locale(self.default_locale)

    def get_messages(self, locale: str) -> Type[MessagesProtocol]:
        messages_class = self.load_locale(locale)
        return messages_class


Locale = LocaleManager(default_locale="en")
