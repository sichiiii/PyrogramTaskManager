import os
import uuid
import requests
import subprocess
import app_logger


logger = app_logger.get_logger(__name__)


def getClipboardData():
    try:
        filename = f"{uuid.uuid4()}.jpg"
        picture_path = f'{os.getcwd()}/storage/{filename}'
        os.system(f"xclip -selection clipboard -target image/png -out > {picture_path}")
        data = {"file_path": picture_path, "chat_id": "1003945710"}
        if os.path.getsize(picture_path) < 3:
            p = subprocess.Popen(['xclip', '-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
            p.wait()
            data = p.stdout.read()
            data = {"text": data.decode(), "chat_id": "1003945710"}
        response = requests.post('http://0.0.0.0:5001', data=data)
        return
    except Exception as ex:
        logger.error(str(ex))


if __name__ == '__main__':
    getClipboardData()
