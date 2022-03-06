import io
import os.path
from gettext import gettext as _
from telethon.events import CallbackQuery
from telethon.tl.custom import Message
import ocrspace
from utils import set_state, load_state


async def callback_func(event: CallbackQuery.Event, *args):
    await event.respond(_("Please send an image to read text from"))
    set_state("image_ocr", "waiting")


API_KEY = ""


async def message_func(event: Message, *args):
    if load_state("image_ocr") == "waiting":
        if event.photo:
            # we're not removing the image as it will be overwritten later
            file_path = os.path.join(os.path.dirname(__file__), "photo.jpg")
            await event.respond(_("Please wait..."))
            await event.client.download_media(event.media, file_path)
            api = ocrspace.API(api_key=API_KEY)
            result = api.ocr_file(file_path)
            await event.respond(_("Parsed text is :") + "\n" + result)
        else:
            await event.respond(_("Please send an image instead (compressed)"))
