import re
import asyncio
from triggers import *
from typing import Any
from contextlib import suppress
from datetime import datetime, timedelta
from aiogram import Router,Bot,Dispatcher, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from pymorphy2 import MorphAnalyzer
def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        return None 
    match_ = re.match(r"(\d+)([a-z])", time_string.lower().strip())
    current_datetime = datetime.utcnow()
    if match_:
        value = int(match_.group(1))
        unit = match_.group(2)

        match unit:
            case "h": time_delta = timedelta(hours=value)
            case "d": time_delta = timedelta(days=value)
            case "w": time_delta = timedelta(weeks=value)
            case _: return None
    else:
        return None
    new_datetime = current_datetime + time_delta
    return new_datetime
router = Router()
router.message.filter(F.chat.type == "supergroup", F.from_user.id==5817631829)

morph = MorphAnalyzer(lang="ru")


@router.message(Command("ban"))
async def ban(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    reply = message.reply_to_message
    if not reply:
        return await message.answer("👀 Пользователь не найден!")
    
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(
            chat_id=message.chat.id, user_id=reply.from_user.id, until_date = until_date 
        )
        await message.answer(f"😮 Пользователя <b>{mention}</b> забанили!")
@router.message(Command("mute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    reply = message.reply_to_message
    if not reply:
        return await message.answer("👀 Пользователь не найден!")
    
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=until_date,
            permissions=ChatPermissions(can_send_message=False)
        )
        await message.answer(f"😮 Пользователя <b>{mention}</b> заткнули!")


@router.message(F.text)
async def profinty_filter(message: Message) -> Any:
    for word in message.text.lower().strip().split():
        parsed_word = morph.parse(word)[0]
        normal_form = parsed_word.normal_form

        for trigger in triggers:
            if trigger in normal_form:
                return await message.answer("Не ругайся")
@router.message(Command("unmute"))
async def unmute(message: Message, bot: Bot) -> Any:
    reply = message.reply_to_message
    if not reply:
        return await message.answer("👀 Пользователь не найден!")
    
    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=None,
            permissions=ChatPermissions()
        )
        await message.answer(f"😃 Пользователю {reply.from_user.mention_html(reply.from_user.first_name)} сняли затычку!")

async def main() -> None:
    bot = Bot('6594162607:AAH4IRhOCvC0uWJZSBWThyL9S6fkBw44ylE')
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())