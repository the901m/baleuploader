import telebot
from telebot import apihelper
import os, subprocess
import time
import psutil, shutil
import sys
import argparse
import glob

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

def compress_and_upload_files(file_list, process_status_msg, active_password):
    # Use the first file in the list to generate a unique timestamp/name
    time_in_nanosec = str(int(time.time_ns()))
    output_dir = os.path.join(folder_path, "temp_" + time_in_nanosec)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

        # Build the 7z command
        # file_list contains all the paths we want to include
        command = [
            "7z",
            "a",
            "-mx=0",
            "-mhe=on",
            f"-p{active_password}", 
            "-v50m",
            f"{output_dir}/{time_in_nanosec}.7z",
        ] + file_list # Append all files to the command
        
        subprocess.run(command)

    last_sent_file_path = os.path.join(output_dir, "last_sent_file.txt")
    last_sent_file_index = 0
    if os.path.exists(last_sent_file_path):
        with open(last_sent_file_path, "r") as f:
            last_sent_file = f.read().strip()
            try:
                # Extracts index from filename.7z.001 etc.
                last_sent_file_index = int(last_sent_file.split('.')[-1])
            except:
                last_sent_file_index = 0

    files_to_send = sorted(f for f in os.listdir(output_dir) if f != "last_sent_file.txt")

    bot.edit_message_text(f"sending archive {time_in_nanosec}", chat_id, process_status_msg.id)

    for file_to_send in files_to_send[last_sent_file_index:]:
        print(f"Uploading: {file_to_send}")
        file_full_path = os.path.join(output_dir, file_to_send)
        with open(file_full_path, "rb") as f_opened:
            bot.send_document(chat_id, f_opened)
        
        with open(last_sent_file_path, "w") as f:
            f.write(file_to_send)

    shutil.rmtree(output_dir)

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="Upload multiple files into one chunked zip.")
# nargs='+' allows one or more files/wildcards
parser.add_argument("files", nargs='+', help="Filenames or wildcards (e.g. file1.txt *.jpg)")
parser.add_argument("-p", "--password", help="Password for the zip file", default=DEFAULT_PASSWORD)

args = parser.parse_args()

# Expand wildcards and collect all valid files
all_matched_files = []
for pattern in args.files:
    # This handles both direct filenames and patterns like *.mp4
    full_pattern = os.path.join(folder_path, pattern)
    matches = glob.glob(full_pattern)
    all_matched_files.extend(matches)

# Remove duplicates (in case of overlapping wildcards)
all_matched_files = list(set(all_matched_files))

if all_matched_files:
    print(f"Found {len(all_matched_files)} files to compress.")
    main_message = bot.send_message(chat_id, f"I Started the process.")
    compress_and_upload_files(all_matched_files, main_message, args.password)
else:
    print("Error: No matching files found.")
    sys.exit(1)