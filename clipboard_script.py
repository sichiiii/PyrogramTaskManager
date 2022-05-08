import os
import uuid
import requests
import subprocess

from app_logger import get_logger
from config import Configuration

config_path = './config.ini'


class Clipboard:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = Configuration()
        self.config.load(config_path)
        self.chat_id = int(self.config.get('clipboard', 'chat_id'))
        self.address = 'http://' + self.config.get('fastapi', 'host') + ":" + self.config.get('fastapi', 'port')

    def getClipboardData(self):
        try:
            print(1)
            filename = f"{uuid.uuid4()}.jpg"
            picture_path = f'{os.getcwd()}/storage/{filename}'
            os.system(f"xclip -selection clipboard -target image/png -out > {picture_path}")
            data = {"file_path": picture_path, "chat_id": self.chat_id}
            if os.path.getsize(picture_path) < 3:
                p = subprocess.Popen(['xclip', '-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
                p.wait()
                data = p.stdout.read()
                data = {"text": data.decode(), "chat_id": self.chat_id}
            response = requests.post(self.address, data=data)
            return
        except Exception as ex:
            self.logger.error(str(ex))


if __name__ == '__main__':
    clipboard = Clipboard()
    clipboard.getClipboardData()
