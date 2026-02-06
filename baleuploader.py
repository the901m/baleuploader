import telebot
from telebot import apihelper
import os, subprocess
import time
import psutil, shutil
import sys
import argparse  # Added for flag handling

apihelper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"
apihelper.CONNECT_TIMEOUT = 600
apihelper.RETRY_ON_ERROR = True
apihelper.MAX_RETRIES = 50
apihelper.RETRY_TIMEOUT = 3
# apihelper.READ_TIMEOUT = 90
API_KEY = ""

bot = telebot.TeleBot(API_KEY)

# --- CONFIGURATION ---
folder_path = "path/of/your/folder/"
DEFAULT_PASSWORD = "your_default_password" 
chat_id = 123456789

def compress_and_upload_files(file_path_in_system, process_status_msg, active_password):
    time_in_nanosec = str(os.stat(file_path_in_system).st_ctime_ns)
    output_dir = os.path.join(folder_path, "temp_" + time_in_nanosec)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

        command = [
            "7z",
            "a",
            "-mx=0",
            "-mhe=on",
            f"-p{active_password}", 
            "-v50m",
            f"{output_dir}/{time_in_nanosec}.7z",
            file_path_in_system,
        ]
        subprocess.run(command)

    last_sent_file_path = os.path.join(output_dir, "last_sent_file.txt")
    last_sent_file_index = 0
    if os.path.exists(last_sent_file_path):
        with open(last_sent_file_path, "r") as f:
            last_sent_file = f.read().strip()
            try:
                last_sent_file_index = int(last_sent_file[-3:])
            except:
                last_sent_file_index = 0

    files_to_send = sorted(f for f in os.listdir(output_dir) if f != "last_sent_file.txt")

    bot.edit_message_text(f"sending the {time_in_nanosec}", chat_id, process_status_msg.id)

    for file_to_send in files_to_send[last_sent_file_index:]:
        print(f"Uploading: {file_to_send}")
        file_full_path = os.path.join(output_dir, file_to_send)
        with open(file_full_path, "rb") as f_opened:
            bot.send_document(chat_id, f_opened)
        
        with open(last_sent_file_path, "w") as f:
            f.write(file_to_send)

    shutil.rmtree(output_dir)

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="Upload files with optional password flag.")
# The filename is a positional argument (mandatory)
parser.add_argument("filename", help="Name of the file in the folder_path")
# The password is an optional flag (-p)
parser.add_argument("-p", "--password", help="Password for the zip file", default=DEFAULT_PASSWORD)

args = parser.parse_args()

# Construct final path
file_path_in_system = os.path.join(folder_path, args.filename)

if os.path.exists(file_path_in_system):
    print(f"Using password: {args.password}")
    main_message = bot.send_message(chat_id, "I started the process.")
    compress_and_upload_files(file_path_in_system, main_message, args.password)
else:
    print(f"Error: File {file_path_in_system} does not exist.")
    sys.exit(1)