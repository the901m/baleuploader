# BaleUploader

This bot splits each file into 50MB .7z chunks and sends them to you, which you can extract using 7-Zip or WinRAR.

## Usage

1. Create a virtual environment and run `pip install pyTelegramBotAPI`.
2. Clone this repository and edit the *API_KEY*, *folder_path*, *password*, and your *chat_id* in `baleuploader.py`.
3. Start the bot with `python3 file.py <file to send>`.

- Obtain the *API_KEY* from Bale's BotFather.
- The *folder_path* is your main download folder; only files from this folder can be uploaded.
- The *password* is the password for the compressed files.
- The *chat_id* is your account's numerical ID (in theory, you can use your account ID like @sampleid too, but I have never tested it). You can obtain it using the method described [here](https://stackoverflow.com/a/62429465) (the UPD part is not needed).
