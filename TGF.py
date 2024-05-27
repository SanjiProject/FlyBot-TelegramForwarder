import os
import sys
import time
import asyncio
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, SessionPasswordNeededError, ForbiddenError
from telethon import types

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def forward_messages_to_channels(self, source_chat_id, destination_channel_ids, keywords):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                code = input('Enter the code: ')
                await self.client.sign_in(self.phone_number, code)
            except SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Please enter your password: ')
                await self.client.sign_in(password=password)

        last_message_id = (await self.client.get_messages(source_chat_id, limit=1))[0].id

        while True:
            print("Checking Message to Make it Flying...")
            messages = await self.client.get_messages(source_chat_id, min_id=last_message_id, limit=None)

            for message in reversed(messages):
                if message.media:
                    if isinstance(message.media, types.MessageMediaDocument) and message.media.document.mime_type == 'video/mp4':
                        await self.forward_message(destination_channel_ids, message)
                    elif isinstance(message.media, types.MessageMediaPhoto):
                        await self.forward_message(destination_channel_ids, message)
                elif keywords:
                    if message.text and any(keyword in message.text.lower() for keyword in keywords):
                        print(f"Message contains a keyword: {message.text}")
                        await self.forward_message(destination_channel_ids, message)
                else:
                    await self.forward_message(destination_channel_ids, message)

                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(2)

    async def forward_message(self, destination_channel_ids, message):
        for destination_channel_id in destination_channel_ids:
            try:
                if message.media:
                    if message.text:
                        caption = f"{message.text}\n{message.media.caption}" if hasattr(message.media, 'caption') else message.text
                        await self.client.send_file(destination_channel_id, message.media, caption=caption)
                    else:
                        caption = message.media.caption if hasattr(message.media, 'caption') else None
                        await self.client.send_file(destination_channel_id, message.media, caption=caption)
                elif message.text:
                    await self.client.send_message(destination_channel_id, message.text)
                print("Message forwarded")
            except Exception as e:
                print(f"Error forwarding message to channel ID {destination_channel_id}: {e}. Skipping.")
                continue  # Continue to the next channel ID


    async def insert_incoming(self):
        while True:
            chat_id = input("Enter the Chat ID to insert (leave blank to exit): ")
            if not chat_id:
                break
            with open("1.Your TG Source.txt", "a") as file:
                file.write(chat_id + "\n")
            print("New value inserted into 1.Your TG Source.txt.")

    async def insert_outgoing(self):
        while True:
            channel_id = input("Enter the Channel ID to insert (leave blank to exit): ")
            if not channel_id:
                break
            with open("2.Target Outgoing.txt", "a") as file:
                file.write(channel_id + "\n")
            print("New value inserted into 2.Target Outgoing.txt.")

    async def list_chats(self):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input('Enter the code: '))
            except SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Please enter your password: ')
                await self.client.sign_in(password=password)

        dialogs = await self.client.get_dialogs()
        
        with open(f"3.ChatIDList.txt", "w", encoding="utf-8") as chats_file:
            for dialog in dialogs:
                chat_info = f"Chat ID: {dialog.id}, Title: {dialog.title}\n"
                print(chat_info)
                chats_file.write(chat_info)

        print("File Saved on 3.ChatIDList Please Kindly Check!")

def read_credentials():
    try:
        with open("ID.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("No ID Detected Please Fill the Information")
        return None, None, None

def write_credentials(api_id, api_hash, phone_number):
    with open("ID.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    api_id, api_hash, phone_number = read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print("""
$$$$$$$$\ $$\   $$\     $$\ $$$$$$$\   $$$$$$\ $$$$$$$$\ 
$$  _____|$$ |  \$$\   $$  |$$  __$$\ $$  __$$\\__$$  __|
$$ |      $$ |   \$$\ $$  / $$ |  $$ |$$ /  $$ |  $$ |   
$$$$$\    $$ |    \$$$$  /  $$$$$$$\ |$$ |  $$ |  $$ |   
$$  __|   $$ |     \$$  /   $$  __$$\ $$ |  $$ |  $$ |   
$$ |      $$ |      $$ |    $$ |  $$ |$$ |  $$ |  $$ |   
$$ |      $$$$$$$$\ $$ |    $$$$$$$  | $$$$$$  |  $$ |   
\__|      \________|\__|    \_______/  \______/   \__|                                                    
""")
    print("FLYBOT - Telegram Fowarding by Sanji")
    print("Visit me on github https://github.com/sanjiproject")
    print("")
    print("Choose an option:")
    print("1. List All Chat on your Telegram")
    print("2. Start Forwarding Messages")
    print("3. Insert Incoming")
    print("4. Insert Outgoing")
    print("5. Reset Bot")
    
    choice = input("Please Choose Bro.. : ")
    
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
            with open("1.Your TG Source.txt", "r") as file:
                source_chat_id = int(file.readline().strip())
            print("Source Chat ID:", source_chat_id)
            
            destination_channel_ids = []
            with open("2.Target Outgoing.txt", "r") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        try:
                            channel_id = int(line)
                            destination_channel_ids.append(channel_id)
                        except ValueError:
                            print(f"Invalid line in '2.Target Outgoing.txt': {line}. Skipping.")
            print("Destination Channel IDs:", destination_channel_ids)
            
            print("Enter keywords if you want to forward messages with specific keywords, or leave blank to forward every message!")
            keywords = input("Put keywords (comma separated if multiple, or leave blank): ").split(",")
            
            await forwarder.forward_messages_to_channels(source_chat_id, destination_channel_ids, keywords)

    elif choice == "3":
        await forwarder.insert_incoming()
    elif choice == "4":
        await forwarder.insert_outgoing()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
