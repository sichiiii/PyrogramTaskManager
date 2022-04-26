

import os
import uuid
import telebot
import datetime
import aiofiles
import app_logger

from pyrogram import Client
from pyrogram.raw.functions.messages import GetMessageReactionsList

from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form



logger = app_logger.get_logger(__name__)
tgSendApp = FastAPI()
bot = telebot.TeleBot('5367760046:AAFhNxfSjYSaLccGBCbzAZ5q-JHFnaEIjsM')

#https://my.telegram.org/apps
app = Client(
    "cyberjabka",
    api_id=2823137,
    api_hash='df822805777e34b345af4e53bd07c246'
)

chat_id = -716352016

try:
    with app:
        peer = app.resolve_peer(chat_id)
        for message in app.get_chat_history(chat_id=chat_id):

            if message.from_user.id == 1003945710:
                if message.reactions:
                    emoji = message.reactions[0].emoji
                    print(emoji)
                    if emoji == '🔥':
                        message.delete()
                    elif emoji == '👍':
                        message.edit_text(message.text + " - В обработке")
except Exception as ex:
    print(str(ex))