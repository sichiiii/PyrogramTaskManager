from typing import Optional

import os
import uuid
import telebot
import aiofiles

from fastapi import FastAPI, File, UploadFile, Form

import app_logger

logger = app_logger.get_logger(__name__)
tgSendApp = FastAPI()
bot = telebot.TeleBot('5367760046:AAFhNxfSjYSaLccGBCbzAZ5q-JHFnaEIjsM');


@tgSendApp.post('/')
async def chat(chat_id: int = Form(...), text: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    try:
        if file:
            file.filename = f"{uuid.uuid4()}.jpg"
            picture_path = f'{os.getcwd()}/storage/{file.filename}'
            async with aiofiles.open(picture_path, 'wb') as out_file:
                contents = await file.read()
                await out_file.write(contents)
            bot.send_photo(chat_id, photo=open(picture_path, 'rb'))
            os.remove(picture_path)
            return {"status": "ok", "filename": file.filename}
        if text:
            bot.send_message(chat_id, str(text))
            return {"status": "ok", "text": text}
        raise Exception('Wrong data (specify picture or text' )
    except Exception as ex:
        logger.error(str(ex))
