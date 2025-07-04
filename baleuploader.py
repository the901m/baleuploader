import telebot
from telebot import apihelper
import os, subprocess
import time
import psutil, shutil
import sys


apihelper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"
apihelper.CONNECT_TIMEOUT = 600
apihelper.RETRY_ON_ERROR = True
apihelper.MAX_RETRIES = 50
apihelper.RETRY_TIMEOUT = 3
# apihelper.READ_TIMEOUT = 90
API_KEY = ""

bot = telebot.TeleBot(API_KEY)

# choose a folder that your files are stored there
folder_path = "path/of/your/folder"
# choose a password for your compressed files
password = ""
# enter you chat_id
chat_id = 123456789


def compress_and_upload_files(file_path_in_system, process_status_msg):

    time_in_nanosec = str(os.stat(file_path_in_system).st_ctime_ns)

    output_dir = folder_path + "temp_" + time_in_nanosec

    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)

        command = [
            "7z",
            "a",
            "-mx=0",
            "-mhe=on",
            f"-p{password}",
            "-v50m",
            f"{output_dir}/{time_in_nanosec}.7z",
            file_path_in_system,
        ]
        subprocess.run(command)

    # File to store the last sent file name
    last_sent_file_path = os.path.join(output_dir, "last_sent_file.txt")

    # Read the last sent file name if it exists
    last_sent_file = None
    last_sent_file_index = 0
    if os.path.exists(last_sent_file_path):
        with open(last_sent_file_path, "r") as f:
            last_sent_file = f.read().strip()
            last_sent_file_index = int(last_sent_file[-3:])

    # Get the list of files to send, excluding the last_sent_file.txt
    files_to_send = sorted(
        f for f in os.listdir(output_dir) if f != "last_sent_file.txt"
    )

    bot.edit_message_text(
        f"sending the {time_in_nanosec}", chat_id, process_status_msg.id
    )

    for file_to_send in files_to_send[last_sent_file_index:]:
        print(file_to_send)
        with open(output_dir + "/" + file_to_send, "rb") as file_to_sent_opened:
            bot.send_document(chat_id, file_to_sent_opened)

        # Update the last sent file name
        with open(last_sent_file_path, "w") as f:
            f.write(file_to_send)

    shutil.rmtree(output_dir)


if len(sys.argv) != 2:
    print("Usage: python3 file.py <value>")
    sys.exit(1)

file_path_in_system = folder_path + sys.argv[1]

main_message = bot.send_message(chat_id, f"I started the process for {sys.argv[1]}.")

compress_and_upload_files(file_path_in_system, main_message)
