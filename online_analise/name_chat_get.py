from telethon.sync import TelegramClient

api_id = 'enter value'
api_hash = 'enter value'
phone_number = '+7enter value'
url = '@enter value'

def get_name(api_id, api_hash, phone_number, url):
    # Create a new TelegramClient instance
    client = TelegramClient('session_name', api_id, api_hash)
    # Start the client
    client.start(phone_number)
    # Get the chat ID and name
    chat_id = url
    chat = client.get_entity(chat_id)
    print(chat.title)
    naming=chat.title
    return naming