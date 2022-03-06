from gettext import gettext as _
from telethon.events import CallbackQuery
from telethon.tl.custom import Message

from utils import set_state, load_state
import pyshorteners


async def callback_func(event: CallbackQuery.Event, *args):
    await event.respond(_("Please send link to unshorten"))
    set_state("unshort_link", "waiting")


async def message_func(event: Message, *args):
    if load_state("unshort_link") == "waiting":
        s = pyshorteners.Shortener()
        result = s.chilpit.expand(event.text)
        await event.respond(result)
