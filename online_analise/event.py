'''
В этом блоке в таблицу csv сохраняется дата и id нового участника группы. Две колонки
Этот блок временно не задействован, но сохранён для дальнейшего использования.
'''


from telethon.sync import TelegramClient, events
import csv
from datetime import datetime

# Set up your API ID, hash, and session name
api_id   = 'enter_api_id'
api_hash = 'enter_api_id'
session_name = 'enter_session_name'

# Set up your client object
client = TelegramClient(session_name, api_id, api_hash)

# Create a function to handle user join events
async def handle_join_event(event):
    print('задействовали')
    if event.user_joined:
        print('если')
        # If the event is a user join event, extract the user and the event date
        user = await event.get_user()
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{user.username} joined on {date}')

        # Write the user and event date to a CSV file
        with open('files/user_joins.csv', 'a', newline='') as file:
            print('идёт запись')
            writer = csv.writer(file)
            writer.writerow([user.id, user.username, date])

# Set up your event loop
with client:
    # Register your event handler for new messages
    client.add_event_handler(handle_join_event, events.ChatAction)

    # Get the chat ID of the group you want to monitor
    chat_id = 1647080650

    # Get the input entity for the group
    entity = client.get_input_entity(chat_id)

    # Get the chat history of the group
    messages = client.get_messages(entity)

    # Iterate through each message and process it
    for message in messages:
        print(message)

    # Start the event loop to handle any new events
    client.run_until_disconnected()