from gettext import gettext as _

import mishkal.tashkeel
from codernitydb3.database import Database

from telethon.events import CallbackQuery
from telethon.tl.custom import Message

from utils import set_state, load_state
from googletrans import Translator


async def callback_func(event: CallbackQuery.Event, *args):
    await event.respond(_("Please send text to translate to arabic"))
    set_state("translate_arabic", "waiting")


async def message_func(event: Message, *args):
    if load_state("translate_arabic") == "waiting":
        translator = Translator()
        t_ar = translator.translate(event.text, dest='ar')
        await event.respond(t_ar.text)
