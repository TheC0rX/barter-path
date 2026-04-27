from pathlib import Path
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore


def get_i18n_middleware() -> I18nMiddleware:
    locales_path = Path(__file__).parent.parent.parent / "locales"

    core = FluentRuntimeCore(path=str(locales_path / "{locale}"))
    middleware = I18nMiddleware(core=core, default_locale="en")

    return middleware
