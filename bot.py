import asyncio
import json
import logging
import os
import urllib.parse

import hmac
import hashlib

from aiogram import Bot, Dispatcher, types
from aiogram.methods import Request
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_response import json_response
from beanie.odm.actions import wrap_with_actions

from config import config

logging.basicConfig(level=logging.INFO)

bot = Bot(config.bot_token)
dp = Dispatcher()

@dp.message()
async def start(message: types.Message):
    data = {'d': json.dumps({'user_id': message.from_user.id})}
    data['k'] = hmac.new('SECRET'.encode(), data['d'].encode(), 'sha256').hexdigest()

    aa=urllib.parse.urlencode(data)

    print(f"https://04e9-94-29-26-16.ngrok-free.app/?{aa}")
    webAppInfo = types.WebAppInfo(url=f"https://04e9-94-29-26-16.ngrok-free.app/?{aa}")
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='zz', webAppInfo=webAppInfo))

    await message.reply('yo', reply_markup=builder.as_markup())


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())
