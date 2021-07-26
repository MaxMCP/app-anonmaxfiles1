import os
import sys
import time
import logging
import pyrogram
import aiohttp
import asyncio
import requests
import aiofiles
from random import randint
from progress import progress
from config import Config
from pyrogram.errors import UserNotParticipant, UserBannedInChannel
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery, InputTextMessageContent


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

DOWNLOAD = "./"

# vars
APP_ID = Config.APP_ID
API_HASH = Config.API_HASH
BOT_TOKEN = Config.BOT_TOKEN

   
bot = Client(
    "AnonMaxCloud",
    api_id=APP_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)


FIRST_MESSAGE = """Привет пользователь \nЯ могу загружать файлы с телеграмма на облако AnonFiles \nА создал это чудо: @prog2k21"""
SUPPORT_MESSAGE = """Помощь по боту \nПришлите мне любой медиа файл telegram, я его загружу, anonfiles.com и дам вам **прямую ссылку для скачивания**\n"""
CONTACTS_MESSAGE = """**Создатель :** [Твой господин](https://telegram.me/prog2k21)"""

FIRST_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Помощь', callback_data='help'),
        InlineKeyboardButton('О боте', callback_data='about'),
        InlineKeyboardButton('Закрыть', callback_data='close')
        ]]
    )
SUPPORT_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Помощь', callback_data='help'),
        InlineKeyboardButton('О боте', callback_data='about'),
        InlineKeyboardButton('Закрыть', callback_data='close')
        ]]
    )
CONTACTS_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Помощь', callback_data='help'),
        InlineKeyboardButton('О боте', callback_data='about'),
        InlineKeyboardButton('Закрыть', callback_data='close')
        ]]
    )


@bot.on_callback_query()
async def cb_data(bot, update):
    if update.data == "home":
        await update.message.edit_text(
            text=FIRST_MESSAGE,
            disable_web_page_preview=True,
            reply_markup=FIRST_BUTTONS
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=SUPPORT_MESSAGE,
            disable_web_page_preview=True,
            reply_markup=SUPPORT_BUTTONS
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=CONTACTS_MESSAGE,
            disable_web_page_preview=True,
            reply_markup=CONTACTS_BUTTONS
        )
    else:
        await update.message.delete()
        
        
@bot.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    text = FIRST_MESSAGE
    reply_markup = FIRST_BUTTONS
    await update.reply_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )

      
@bot.on_message(filters.media & filters.private)
async def upload(client, message):
    if Config.UPDATES_CHANNEL is not None:
        try:
            user = await client.get_chat_member(Config.UPDATES_CHANNEL, message.chat.id)
            if user.status == "kicked":
                await client.send_message(
                    chat_id=message.chat.id,
                    text="Прости, но ты не можешь пользоваться мной",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await client.send_message(
                chat_id=message.chat.id,
                text="Пожалуйста зайди на наш канал с обновлениями",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Зайти на наш канал с обновлениями:", url=f"https://t.me/{Config.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await client.send_message(
                chat_id=message.chat.id,
                text="Что-то пошло не так, попробуйте ещё раз!",
                parse_mode="markdown",
                disable_web_page_preview=True)
            return
    m = await message.reply("Загрузка файла на облако подождите...")
    now = time.time()
    sed = await bot.download_media(
                message, DOWNLOAD,
          progress=progress,
          progress_args=(
            "Процесс загрузки пошел, ожидайте\nВремя загрузки зависит от размера файла ", 
            m,
            now
            )
        )
    try:
        files = {'file': open(sed, 'rb')}
        await m.edit("Загрузка на облако AnonFiles пожалуйста подождите")
        callapi = requests.post("https://api.anonfiles.com/upload", files=files)
        text = callapi.json()
        output = f"""
<u>Ваш файл успешно загружен на облако</u>

Название файла: {text['data']['file']['metadata']['name']}
Размер файла: {text['data']['file']['metadata']['size']['readable']}
Ссылка на скачивание: `{text['data']['file']['url']['full']}`

Удачного дня!"""
        btn = InlineKeyboardMarkup(
                                [[InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ Fɪʟᴇ", url=f"{text['data']['file']['url']['full']}")]])
        await m.edit(output, reply_markup=btn)
        os.remove(sed)
    except Exception:
        await m.edit("Ошибка! Файл слишком большой! 20 GB на каждый файл!")
        return
      
@bot.on_message(filters.regex(pattern="https://cdn-") & filters.private & ~filters.edited)
async def url(client, message):
    msg = await message.reply("Проверка URL")
    lenk = message.text
    cap = "© @prog2k21"
    try:
         await msg.edit("Большие файлы займут больше времени на загрузку")
         filename = await download(lenk)
         await msg.edit("Загрузка файла в телеграм...")
         await message.reply_document(filename, caption=cap)
         await msg.delete()
         os.remove(filename)
    except Exception:
        await msg.edit("Сбой процесса! Возможно приостановлено из-за большого размера файла!")
        
async def download(url):
    ext = url.split(".")[-1]
    filename = str(randint(1000, 9999)) + "." + ext
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(filename, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return filename
        
        
bot.start()
print("AnonMaxCloud working...")
idle()
