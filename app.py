import os
import uuid
import uvicorn
import aiofiles

from typing import Optional
from config import Configuration
from app_logger import get_logger
from telegram_api import Telegram
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI, File, UploadFile, Form

config_path = './config.ini'

tgSendApp = FastAPI()
telegram_api = Telegram()
logger = get_logger(__name__)


@tgSendApp.on_event("startup")
async def startup_event() -> None:
    await telegram_api.app.start()


@tgSendApp.on_event("startup")
@repeat_every(seconds=2)
async def check_emotions_task() -> None:
    await telegram_api.parse_chats()


@tgSendApp.post('/')
async def chat(chat_id: int = Form(...), text: Optional[str] = Form(None), file: Optional[UploadFile] = File(None),
               file_path: Optional[str] = Form(None)):
    try:
        chat_id = int(chat_id)
        if file:
            file.filename = f"{uuid.uuid4()}.jpg"
            picture_path = f'{os.getcwd()}/storage/{file.filename}'
            async with aiofiles.open(picture_path, 'wb') as out_file:
                contents = await file.read()
                await out_file.write(contents)
            await telegram_api.app.send_photo(chat_id, photo=open(picture_path, 'rb'))
            os.remove(picture_path)
            return {"status": "ok", "filename": file.filename}
        if file_path:
            await telegram_api.app.send_photo(chat_id, photo=open(file_path, 'rb'))
            os.remove(file_path)
            return {"status": "ok", "filename": file_path}
        if text:
            await telegram_api.app.send_message(chat_id, str(text))
            return {"status": "ok", "text": text}
        raise Exception('Wrong data (specify picture or text)')
    except Exception as ex:
        logger.error(str(ex))

if __name__ == '__main__':
    config = Configuration()
    config.load(config_path)
    uvicorn.run(app="app:tgSendApp",
                host=config.get('fastapi', 'host'),
                port=int(config.get('fastapi', 'port')),
                reload=False,
                debug=True)
