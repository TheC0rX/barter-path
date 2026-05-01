from aiogram import Router


def setup_routers() -> Router:
    from . import start, menu, add_task, settings

    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(add_task.router)
    router.include_router(settings.router)
    return router
