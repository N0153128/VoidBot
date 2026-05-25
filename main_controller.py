### Main goals of the Minimal branch is to cut out all unnecessary code and make the bot as lightweight as possible.
### TODO: Remove all example mods and integrate critical mods and tools into the base TelegramHandler class


from initial import Initial
from config import *  
from plugins.motd.motd_controller import motd_handler, motd_commands
import asyncio
from telegram_handler import Bot


base = Initial()
base.startup_time()

# this function is the message handler. every command is hardcoded for both private and group chats
async def webapi_handler(q, admin):
    async for item in base.feed(q):
        try:
            # callbacks
            if base.bot.is_callback(item):
                pass

            # messages
            if admin:
                if base.bot.get_chat_id(item) == ADMIN:
                    if base.get(item) in motd_commands:
                        await motd_handler(item)
                    else:
                        await command_cycle(item)
            elif not admin:
                  await command_cycle(item)

        except Exception as e:
            print(e)

async def command_cycle(data):
    if base.get(data) == '/debug':
        await base.send(data, 'Ping')
    elif base.get(data).startswith('/bal'):
        pass
        # await send(data, motd.balance)

async def supervised_loop():
    """Wraps loop_void so the event loop keeps running even if it crashes."""
    while True:
        try:
            await base.bot.loop_void(queue=base.queue, data_resolver=webapi_handler)
        except Exception as e:
            print(f'[supervisor] loop_void crashed: {e!r} — restarting in 10s')
            await asyncio.sleep(10)

asyncio.run(supervised_loop())
