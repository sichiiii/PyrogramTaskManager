from time import sleep
from pyrogram import Client
from config import Configuration
from app_logger import get_logger


config_path = './config.ini'


class Telegram:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = Configuration()
        self.config.load(config_path)
        self.chat_id = int(self.config.get('telegram', 'chat_id'))
        self.app = Client(
            self.config.get('telegram', 'username'),
            api_id=int(self.config.get('telegram', 'api_id')),
            api_hash=self.config.get('telegram', 'api_hash')
        )

    async def forward_message(self, message_id: int, chat_id: int, hours: float):
        parent_mes = await self.app.get_messages(chat_id, message_id)
        if isinstance(hours, float):
            sleep(hours * 3600)
        else:
            sleep(14400)
        await parent_mes.forward(chat_id)
        await parent_mes.delete()

    async def check_emotions(self):
        try:
            async for message in self.app.get_chat_history(chat_id=self.chat_id):  # TODO: limit messages amount
                if message.reply_to_message_id:
                    message_id = message.reply_to_message_id
                    await self.forward_message(message_id, self.chat_id, float(message.text))
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
                                        await self.app.edit_message_caption(self.chat_id, message.id, message.caption
                                                                            + " - В обработке")
                                else:
                                    await self.app.edit_message_caption(self.chat_id, message.id, "В обработке")
                            else:
                                message_end = message.text[-11:]
                                if message_end != "В обработке":
                                    await message.edit_text(message.text + " - В обработке")
            return
        except Exception as ex:
            if str(ex) != 'Telegram says: [400 MESSAGE_ID_INVALID] - The message id is invalid (caused by "messages.EditMessage")':
                self.logger.error(str(ex))
