from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    await msg.answer("Hi! I'm starting...")
