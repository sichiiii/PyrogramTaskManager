import os
import uuid
import asyncio
import aiofiles
import app_logger

from pyrogram import Client
from functools import wraps
from typing import Callable, Awaitable, Optional
from fastapi import FastAPI, File, UploadFile, Form
from starlette.concurrency import run_in_threadpool as run_in_threadpool

logger = app_logger.get_logger(__name__)
tgSendApp = FastAPI()


async def check_emotions():
    chat_id = -716352016
    app = Client(
        "cyberjabka",
        api_id=2823137,
        api_hash='df822805777e34b345af4e53bd07c246'
    )
    try:
        await app.start()
        async for message in app.get_chat_history(chat_id=chat_id):
            print(message.from_user.id)
            if message.from_user.id == 1003945710:
                if message.reactions:
                    emoji = message.reactions[0].emoji
                    if emoji == '🔥':
                        await message.delete()
                    elif emoji == '👍':
                        message_end = message.text[-14:]
                        if message_end != " - В обработке":
                            await message.edit_text(message.text + " - В обработке")
    except Exception as ex:
        print(str(ex))


def repeat_every():
    def decorator(func: Callable[[], Optional[Awaitable[None]]]):
        is_coroutine = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def wrapped():
            async def loop():
                while True:
                    try:
                        if is_coroutine:
                            await func()
                        else:
                            await run_in_threadpool(func)
                    except Exception as e:
                        logger.error(str(e))
                    await asyncio.sleep(5)
            asyncio.create_task(loop())
        return wrapped
    return decorator


@tgSendApp.on_event("startup")
@repeat_every()
async def remove_expired_tokens_task():
    _ = await check_emotions()


@tgSendApp.post('/')
async def chat(chat_id: int = Form(...), text: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    try:
        chat_id = -716352016
        app = Client(
            "cyberjabka",
            api_id=2823137,
            api_hash='df822805777e34b345af4e53bd07c246'
        )
        await app.start()
        if file:
            file.filename = f"{uuid.uuid4()}.jpg"
            picture_path = f'{os.getcwd()}/storage/{file.filename}'
            async with aiofiles.open(picture_path, 'wb') as out_file:
                contents = await file.read()
                await out_file.write(contents)
            await app.send_photo(chat_id, photo=open(picture_path, 'rb'))
            os.remove(picture_path)
            return {"status": "ok", "filename": file.filename}
        if text:
            await app.send_message(chat_id, str(text))
            return {"status": "ok", "text": text}
        raise Exception('Wrong data (specify picture or text)')
    except Exception as ex:
        logger.error(str(ex))
