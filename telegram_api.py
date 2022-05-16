import asyncio

from database import SQL
from config import Configuration
from app_logger import get_logger
from pyrogram import Client, enums

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
        self.sql = SQL()

    @staticmethod
    def check_float_str(message_text):
        try:
            float(message_text)
            return True
        except ValueError:
            return False

    async def forward_message(self, message_id: int, hours: float, chat_id: int):
        await asyncio.sleep(hours * 3600)
        parent_mes = await self.app.get_messages(chat_id, message_id)
        if not parent_mes.empty:
            await parent_mes.forward(chat_id)
            await parent_mes.delete()

    async def parse_emotions(self, message, chat_id):
        emoji_arr = []
        if message.reactions:
            for i in message.reactions:
                emoji_arr.append(i.emoji)
            if '🔥' in emoji_arr:
                await message.delete()
                return
            elif '👍' in emoji_arr:  # TODO: simplify
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

    async def parse_chats(self):
        async for dialog in self.app.get_dialogs():
            await self.parse_messages(dialog.chat.id)

    async def parse_messages(self, chat_id: int):
        try:
            async for message in self.app.get_chat_history(chat_id=chat_id, limit=300):
                try:
                    if message.text == 'Получить отчет':
                        print(self.sql.get_tasks())
                    if message.reply_to_message_id:
                        message_id = message.reply_to_message_id
                        if self.check_float_str(message.text):
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            asyncio.create_task(self.forward_message(message_id, float(message.text), chat_id))
                        else:
                            asyncio.create_task(self.forward_message(message_id, 4.0, chat_id))
                    else:
                        if message.from_user.id == self.user_id:
                            await self.parse_emotions(message, chat_id)
                        else:
                            if message.text:
                                await self.app.send_message(chat_id, message.text)
                                await message.delete()
                except Exception as ex:
                    self.logger.error(str(ex))
            return
        except Exception as ex:
            if str(ex) != 'Telegram says: [400 MESSAGE_ID_INVALID] - The message id is invalid (caused by "messages.EditMessage")':
                self.logger.error(str(ex))
