from gettext import gettext as _

from telethon.events import CallbackQuery
from telethon.tl.custom import Message

from utils import set_state, load_state
import pyshorteners


async def callback_func(event: CallbackQuery.Event, *args):
    await event.respond(_("Please send link to shorten"))
    set_state("short_link", "waiting")


async def message_func(event: Message, *args):
    if load_state("short_link") == "waiting":
        s = pyshorteners.Shortener()
        result = s.chilpit.short(event.text)
        await event.respond(result)
