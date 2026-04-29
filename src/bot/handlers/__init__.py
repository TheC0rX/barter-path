from aiogram import Router


def setup_routers() -> Router:
    from . import start, menu, settings

    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(settings.router)
    return router
