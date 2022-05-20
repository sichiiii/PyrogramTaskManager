import asyncio

from pyrogram import Client
from config import Configuration
from app_logger import get_logger

config_path = './config.ini'


class Telegram:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = Configuration()
        self.config.load(config_path)
        self.username = self.config.get('telegram', 'username')
        self.user_id = int(self.config.get('telegram', 'user_id'))
        self.app = Client(
            self.username,
            api_id=int(self.config.get('telegram', 'api_id')),
            api_hash=self.config.get('telegram', 'api_hash')
        )
        self.tasks_list = []

    @staticmethod
    def check_float_str(message_text: str):
        try:
            float(message_text)
            return True
        except ValueError:
            return False

    async def parse_chats(self):
        async for dialog in self.app.get_dialogs():
            await self.parse_messages(dialog.chat.id)

    async def parse_messages(self, chat_id: int):
        try:
            async for message in self.app.get_chat_history(chat_id=chat_id, limit=300):
                try:
                    if message.reply_to_message_id:
                        reply_message_id = message.reply_to_message_id
                        if reply_message_id not in self.tasks_list:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            if self.check_float_str(message.text):
                                asyncio.create_task(self.forward_message(reply_message_id, message.id,
                                                                         float(message.text), chat_id))
                            else:
                                asyncio.create_task(self.forward_message(reply_message_id, message.id, 4.0, chat_id))
                    else:
                        if message.from_user.id == self.user_id:
                            await self.parse_emotions(message, chat_id)
                        else:
                            await self.resend_message(message, chat_id)
                except Exception as ex:
                    self.logger.error(str(ex))
            return
        except Exception as ex:
            if str(ex) != 'Telegram says: [400 MESSAGE_ID_INVALID] - The message id is invalid (caused by "messages.EditMessage")':
                self.logger.error(str(ex))
            else:
                pass

    async def resend_message(self, message, chat_id):
        if message.text:
            await self.app.send_message(chat_id, message.text)
            await message.delete()
        elif message.photo:
            if message.caption:
                await self.app.send_photo(chat_id, message.photo.file_id, caption=message.caption)
            else:
                await self.app.send_photo(chat_id, message.photo.file_id)
            await message.delete()
        elif message.video:
            if message.caption:
                await self.app.send_video(chat_id, message.video.file_id, caption=message.caption)
            else:
                await self.app.send_video(chat_id, message.video.file_id)
            await message.delete()

    async def forward_message(self, parent_message_id: int, time_message_id: int, hours: float, chat_id: int):
        self.tasks_list.append(chat_id)
        await asyncio.sleep(hours * 3600)
        parent_mes = await self.app.get_messages(chat_id, parent_message_id)
        time_mes = await self.app.get_messages(chat_id, time_message_id)
        if not parent_mes.empty:
            await self.resend_message(parent_mes, chat_id)
            await parent_mes.delete()
            await time_mes.delete()
            self.tasks_list.remove(chat_id)

    async def parse_emotions(self, message, chat_id: int):
        if message.reactions:
            emoji_arr = []
            for i in message.reactions:
                emoji_arr.append(i.emoji)
            if '🔥' in emoji_arr:
                await message.delete()
                return
            if '👍' in emoji_arr:
                if not message.text:
                    if message.caption:
                        message_end = message.caption[-11:]
                        if message_end != "В обработке":
                            await self.app.edit_message_caption(chat_id, message.id, message.caption
                                                                + " - В обработке")
                    else:
                        await self.app.edit_message_caption(chat_id, message.id, "В обработке")
                else:
                    message_end = message.text[-11:]
                    if message_end != "В обработке":
                        await message.edit_text(message.text + " - В обработке")
