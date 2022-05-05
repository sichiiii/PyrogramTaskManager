import os
import uuid
import uvicorn
import aiofiles
import app_logger

from time import sleep
from typing import Optional
from pyrogram import Client
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI, File, UploadFile, Form


logger = app_logger.get_logger(__name__)
tgSendApp = FastAPI()
app = Client(
        "cyberjabka",
        api_id=2823137,
        api_hash='df822805777e34b345af4e53bd07c246'
    )


@tgSendApp.on_event("startup")
async def startup_event() -> None:
    await app.start()


@tgSendApp.on_event("startup")
@repeat_every(seconds=2)
async def check_emotions_task() -> None:
    await check_emotions()


async def forward_message(message_id: int,  chat_id: int, hours: float):
    parent_mes = await app.get_messages(chat_id, message_id)
    if isinstance(hours, float):
        sleep(hours*3600)
    else:
        sleep(14400)
    await parent_mes.forward(chat_id)
    await parent_mes.delete()


async def check_emotions():
    try:
        chat_id = -716352016
        async for message in app.get_chat_history(chat_id=chat_id):
            if message.reply_to_message_id:
                try:
                    message_id = message.reply_to_message_id
                    await forward_message(message_id, chat_id, float(message.text))
                except:
                    pass
            if message.from_user.id == 1003945710:
                if message.reactions:
                    emoji_arr = []
                    for i in message.reactions:
                        emoji_arr.append(i.emoji)
                    if '🔥' in emoji_arr:
                        await message.delete()
                        return
                    elif '👍' in emoji_arr:
                        if not message.text:
                            if message.caption:
                                message_end = message.caption[-11:]
                                if message_end != "В обработке":
                                    await app.edit_message_caption(chat_id, message.id, message.caption + " - В обработке")
                            else:
                                await app.edit_message_caption(chat_id, message.id, "В обработке")
                        else:
                            message_end = message.text[-11:]
                            if message_end != "В обработке":
                                await message.edit_text(message.text + " - В обработке")
        return
    except Exception as ex:
        if str(ex) != 'Telegram says: [400 MESSAGE_ID_INVALID] - The message id is invalid (caused by "messages.EditMessage")':
            logger.error(str(ex))


@tgSendApp.post('/')
async def chat(chat_id: int = Form(...), text: Optional[str] = Form(None), file: Optional[UploadFile] = File(None),
               file_path: Optional[str] = Form(None)):
    try:
        chat_id = -716352016
        if file:
            file.filename = f"{uuid.uuid4()}.jpg"
            picture_path = f'{os.getcwd()}/storage/{file.filename}'
            async with aiofiles.open(picture_path, 'wb') as out_file:
                contents = await file.read()
                await out_file.write(contents)
            await app.send_photo(chat_id, photo=open(picture_path, 'rb'))
            os.remove(picture_path)
            return {"status": "ok", "filename": file.filename}
        if file_path:
            await app.send_photo(chat_id, photo=open(file_path, 'rb'))
            os.remove(file_path)
            return {"status": "ok", "filename": file_path}
        if text:
            await app.send_message(chat_id, str(text))
            return {"status": "ok", "text": text}
        raise Exception('Wrong data (specify picture or text)')
    except Exception as ex:
        logger.error(str(ex))

if __name__ == '__main__':
    uvicorn.run(app="app:tgSendApp", host="0.0.0.0", port=5000, reload=False, debug=True)
