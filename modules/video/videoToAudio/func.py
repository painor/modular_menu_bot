import os.path
from gettext import gettext as _

import moviepy.editor as mp
from telethon.events import CallbackQuery
from telethon.tl.custom import Message

from utils import set_state, load_state


async def callback_func(event: CallbackQuery.Event, *args):
    await event.respond(_("Please send a video to extract audio from"))
    set_state("audio_extract", "waiting")


async def message_func(event: Message, *args):
    if load_state("audio_extract") == "waiting":
        if event.video:
            # we're not removing these files as they will be overwritten later
            video_path = os.path.join(os.path.dirname(__file__), "video.mp4")
            audio_path = os.path.join(os.path.dirname(__file__), "audio.mp3")

            await event.respond(_("Please wait..."))
            await event.client.download_media(event.media, video_path)

            my_clip = mp.VideoFileClip(video_path)
            my_clip.audio.write_audiofile(audio_path)

            await event.respond(_("Uploading audio..."))
            await event.respond(file=audio_path)
        else:
            await event.respond(_("Please send a video instead"))
