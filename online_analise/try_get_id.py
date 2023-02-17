from telethon import TelegramClient, events, sync

# Your API ID and hash
api_id = 'enter value'
api_hash = 'enter value'
name_group = '@enter value'
# Your phone number, including the country code
phone = '+7enter value'

# узнать id чата
def get_id_chat(api_id, api_hash, phone, name_group):
    # Create a new TelegramClient instance
    client = TelegramClient('session_name', api_id, api_hash)

    # Start the client
    client.start(phone)

    # Get the input entity for the group you want to monitor
    entity = client.get_input_entity(name_group)

    # Print the chat ID
    id_chat = entity.channel_id
    print(id_chat, '--id_chat')
    return id_chat


get_id_chat(api_id, api_hash, phone, name_group)
