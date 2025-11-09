import importlib
from typing import Literal, Optional
from instaui import ui
from instaui_tdesign.types import TLocale


class LazyLocaleDict:
    def __init__(self):
        self._locale_map = {}

    def get(self, key: str):
        key = key.lower()

        if key not in self._locale_map:
            self._locale_map[key] = self._load_locale(key)
        return self._locale_map[key]

    def _load_locale(self, key: str):
        module_name = key
        try:
            module = importlib.import_module(f"instaui_tdesign.locales.{module_name}")
            return module.locale

        except ImportError:
            raise ImportError(f"Cannot import module {module_name}")


_locale_dict = LazyLocaleDict()


def get_locale(locale: TLocale) -> dict:
    """
    Get locale dict by locale name.
    Args:
        locale (TLocale): locale name, e.g. "zh-CN", "en-US"
    """
    return _locale_dict.get(locale)


def get_locales(locales: list[TLocale]) -> dict:
    """
    Get locale dicts by locale names.
    Args:
        locales (list[TLocale]): locale names, e.g. ["zh-CN", "en-US"]
    """
    return {locale: get_locale(locale) for locale in locales}


def use_locale_dict(
    *,
    pre_load_locales: Optional[list[TLocale]] = None,
    type: Literal["server", "client"] = "server",
) -> tuple[dict, str]:
    """
    Get locale dict and language by locale names.

    Args:
        pre_load_locales (Optional[list[TLocale]]): locale names to pre-load, e.g. ["zh-CN", "en-US"]. Defaults to ["en-US", "zh-CN"].
        type (Literal[&quot;server&quot;, &quot;client&quot;], optional): The type of locale dict, "server" or "client". Defaults to "server".

    Examples:
    .. code-block:: python
        locale_dict, lang = use_locale_dict(pre_load_locales=["en-US", "zh-CN"])

        td.select(["en_US", "zh_CN"], lang)

        with td.config_provider(global_config=locale_dict):
            td.input()
    """

    pre_load_locales = pre_load_locales or ["en_US", "zh_CN"]

    lang = ui.use_language()

    if type == "server":

        @ui.computed(inputs=[get_locales(pre_load_locales), lang])
        def locale_dict(locales: dict, lang: str) -> dict:
            return locales[lang]

        return locale_dict, lang

    locale_dict = ui.js_computed(
        inputs=[get_locales(pre_load_locales), lang],
        code=r"(locales,lang) =>  locales[lang]",
    )

    return locale_dict, lang
