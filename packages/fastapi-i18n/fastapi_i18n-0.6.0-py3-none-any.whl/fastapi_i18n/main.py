# TODO: Read config from pyproject.toml and fail if config is not found
import gettext
import logging
import os
from contextvars import ContextVar

from fastapi import Request

logger = logging.getLogger("fastapi_i18n")


class Translator:
    def __init__(self, locale: str):
        locale_dir = os.getenv("FASTAPI_I18N_LOCALE_DIR")
        self.translations = gettext.translation(
            domain="messages",
            localedir=locale_dir,
            languages=[locale],
            fallback=True,
        )

    def translate(self, message: str):
        return self.translations.gettext(message)


locale: ContextVar[str] = ContextVar("locale")
translator: ContextVar[Translator] = ContextVar("translator")


async def i18n(request: Request):
    locale_default = os.getenv("FASTAPI_I18N_LOCALE_DEFAULT", "en")
    locale_value = request.headers.get("Accept-Language", locale_default)
    token_locale = locale.set(locale_value)
    token_translator = translator.set(Translator(locale=locale_value))
    try:
        yield
    finally:
        locale.reset(token_locale)
        translator.reset(token_translator)


def _(message: str) -> str:
    try:
        return translator.get().translate(message)
    except LookupError:
        logger.debug(
            "FastAPI I18N translator is not set. Returning message untranslated."
        )
        return message


def get_locale() -> str:
    """Get the current setting for locale."""
    try:
        return locale.get()
    except LookupError:
        return os.getenv("FASTAPI_I18N_LOCALE_DEFAULT", "en")
