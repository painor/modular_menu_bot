import asyncio
import os
from gettext import gettext as _
from telethon import TelegramClient
from telethon.events import NewMessage, CallbackQuery, StopPropagation
from telethon.tl.custom import Message

from config import API_ID, API_HASH, BOT_TOKEN
from utils import load_buttons, load_more_buttons, dynamic_import, handle_back, get_current_func, import_file, \
    reset_current_func

asyncio.set_event_loop(asyncio.new_event_loop())
client = TelegramClient("bot", API_ID, API_HASH).start(
    bot_token=BOT_TOKEN
)


@client.on(NewMessage(incoming=True, pattern='^/start$'))
async def start(event: NewMessage.Event):
    """
    This function is called when the user sends /start
    We want to show the user a list of buttons of the main modules
    :return:
    """
    modules, description = dynamic_import(os.path.join(os.path.dirname(__file__), 'modules'))

    await event.reply(description, buttons=load_buttons(modules, add_back=False))

    raise StopPropagation


@client.on(CallbackQuery)
async def handle_callback(event: CallbackQuery.Event):
    """
    This function is called when the user clicks on a button
    :return:
    """
    original_data = event.data.decode('utf-8')
    # we want to know if the clicked button is nested or not
    data = original_data.split('_')
    # the name of the module is the last element
    func_name = data[-1]
    # everything else is the location of the module
    path = data[:-1]
    # if the model is "back" then we're going up one level
    if func_name == "back":
        await event.answer("going back!")
        await handle_back(event, original_data)
        return
    # we want to get the full location of the module so we can load it.
    path_location = os.path.join(os.path.dirname(__file__), 'modules', *path)
    # we dynamically load all the modules
    modules, description = dynamic_import(path_location)
    # we get the specific module that the user clicked on
    module = modules[func_name]
    # since the user clicked on this we will call the callback_func of said module.
    # If the module has no callback_func that means it has nesetd modules and we want to load more buttons
    function = module.get("callback_func", load_more_buttons)
    await event.answer(_("Working on your request.."))
    try:
        # you can never be sure with theses
        await function(event, original_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        await event.answer(_("An error has happened while processing your request"))


@client.on(NewMessage(incoming=True))
async def handle_messages(event: Message):
    """
    This function is called when the user sends a message.
    It's purpose is to figure out what module function to call
    :param event:
    :return:
    """
    # if the user sends cancel at any point we just resets to the start
    if event.text == "/cancel":
        await event.reply(_("Canceled"))
        reset_current_func()
        return
    # this will return the stored function of the module that the user clicked on previously
    func = get_current_func()
    # if the user has clicked on nothing then we just tell them to do so
    if func is not None:
        # we load the module's message function to call
        func = import_file("func", func).message_func
        try:
            await func(event)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await event.reply(_("An error has happened while processing your request"))
        # This might get spammy because we're telling the user that they can cancel after each message.
        await event.respond(_("Use /cancel to cancel the current request"))
    else:
        await event.respond(_("Please click on /start to get a menu"))


print("Running!")
client.run_until_disconnected()
