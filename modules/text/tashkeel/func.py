from gettext import gettext as _

import mishkal.tashkeel
from codernitydb3.database import Database

from telethon.events import CallbackQuery
from telethon.tl.custom import Message

from utils import set_state, load_state


async def callback_func(event: CallbackQuery.Event, *args):
    await event.respond(_("Please send text to format/tashkeel"))
    set_state("tashkeel", "waiting")


async def message_func(event: Message, *args):
    if load_state("tashkeel") == "waiting":
        if event.text:
            vocalizer = mishkal.tashkeel.TashkeelClass()
            await event.respond(vocalizer.tashkeel(event.text))
