import asyncio
from telethon.tl.types import PeerUser, PeerChannel
from telethon import TelegramClient, events
from decouple import config
import logging
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import PeerFloodError
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print("Detected change in Python file, restarting bot...")
            os.system("python bot.py")

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    print("Bot is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

print("Starting...")

# Basics
APP_ID = config("APP_ID", default=None)
if APP_ID is not None:
    APP_ID = int(APP_ID)
    
API_HASH = config("API_HASH", default=None)
SESSION = config("SESSION")
FROM_ = config("FROM_CHANNELS")
TO_ = config("TO_CHANNELS")


FROM = [int(i) for i in FROM_.split(',')]
TO = [int(i) for i in TO_.split()]

entity_cache = {}

async def check_connectivity():
    while True:
        print('Checking connectivity...')
        await asyncio.sleep(600)
        await asyncio.sleep(600)

try:
    BotzHubUser = TelegramClient(StringSession(SESSION), APP_ID, API_HASH)
    BotzHubUser.start()
except Exception as ap:
    print(f"ERROR - {ap}")
    exit(1)

async def get_input_entity(client, entity):
    if isinstance(entity, str):
        entity = await client.get_input_entity(entity)
    elif isinstance(entity, int):
         if entity in entity_cache:
            return entity_cache[entity]
         entity = PeerChannel(entity)
    entity_cache[entity.channel_id] = entity
    print("Entity cache:", entity_cache)       
    return entity
    

@BotzHubUser.on(events.NewMessage(incoming=True, chats=FROM))
async def sender_bH(event):
      for i in TO:
        print(f"FROM: {event.chat_id}, TO: {i}")
        try:
            i = await get_input_entity(BotzHubUser, i)
            await BotzHubUser.send_message(
                i,
                event.message
            )
        except PeerFloodError:
            print(f"O envio de mensagens para {i} foi limitado. O bot irá pausar temporariamente o envio de mensagens.")
            await asyncio.sleep(120) # Aguarda 120 segundos antes de continuar a enviar mensagens
        except Exception as e:
            print(f"Erro ao enviar a mensagem para {i}: {e}")
print("Bot has started.")
BotzHubUser.loop.create_task(check_connectivity())
BotzHubUser.run_until_disconnected()
