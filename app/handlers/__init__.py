from aiogram import Router

from app.handlers import menu, recipes, settings, start


def get_root_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(recipes.router)
    router.include_router(menu.router)
    router.include_router(settings.router)
    return router
