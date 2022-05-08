import os
import uuid
import uvicorn
import aiofiles
import app_logger


from typing import Optional
from telegram_api import Telegram
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI, File, UploadFile, Form


tgSendApp = FastAPI()
telegram_api = Telegram()
logger = app_logger.get_logger(__name__)


@tgSendApp.on_event("startup")
async def startup_event() -> None:
    await telegram_api.app.start()


@tgSendApp.on_event("startup")
@repeat_every(seconds=2)
async def check_emotions_task() -> None:
    await telegram_api.check_emotions()


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
    uvicorn.run(app="app:tgSendApp", host="0.0.0.0", port=5000, reload=False, debug=True)
