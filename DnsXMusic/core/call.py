#
# Copyright (C) 2024 by MISH0009@Github, < https://github.com/MISH0009 >.
#
# This file is part of < https://github.com/MISH0009/DNS > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/MISH0009/DNS/blob/master/LICENSE >
#
# All rights reserved.
#
import asyncio
from datetime import datetime, timedelta
from typing import Union

from ntgcalls import TelegramServerError
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, filters
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall
from pytgcalls.types import (
    ChatUpdate,
    GroupCallParticipant,
    MediaStream,
    StreamAudioEnded,
    StreamVideoEnded,
    Update,
)

import config
from strings import get_string
from DnsXMusic import LOGGER, YouTube, app
from DnsXMusic.misc import db
from DnsXMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_audio_bitrate,
    get_lang,
    get_loop,
    get_video_bitrate,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from DnsXMusic.utils.exceptions import AssistantErr
from DnsXMusic.utils.inline.play import stream_markup, telegram_markup
from DnsXMusic.utils.stream.autoclear import auto_clean
from DnsXMusic.utils.thumbnails import gen_thumb

autoend = {}
counter = {}
AUTO_END_TIME = 1


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="DnsString1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )
        self.userbot2 = Client(
            name="DnsString2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )
        self.userbot3 = Client(
            name="DnsString3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )
        self.userbot4 = Client(
            name="DnsString4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )
        self.userbot5 = Client(
            name="DnsString5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def mute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.mute_stream(chat_id)

    async def unmute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.unmute_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except:
            pass

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id)
        except:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality,
            )
        else:
            if image and config.PRIVATE_BOT_MODE == str(True):
                stream = MediaStream(
                    link,
                    image,
                    audio_parameters=audio_stream_quality,
                    video_parameters=video_stream_quality,
                )
            else:
                stream = MediaStream(link, audio_parameters=audio_stream_quality)
        await assistant.play(
            chat_id,
            stream,
        )

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        stream = (
            MediaStream(
                file_path,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else MediaStream(
                file_path,
                audio_parameters=audio_stream_quality,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
                video_flags=MediaStream.Flags.IGNORE,
            )
        )
        await assistant.play(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOG_GROUP_ID)
        await assistant.play(
            config.LOG_GROUP_ID,
            MediaStream(link),
        )
        await asyncio.sleep(0.5)
        await assistant.leave_call(config.LOG_GROUP_ID)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality,
            )
        else:
            if image and config.PRIVATE_BOT_MODE == str(True):
                stream = MediaStream(
                    link,
                    image,
                    audio_parameters=audio_stream_quality,
                    video_parameters=video_stream_quality,
                )
            else:
                stream = (
                    MediaStream(
                        link,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality,
                    )
                    if video
                    else MediaStream(link, audio_parameters=audio_stream_quality)
                )
        try:
            await assistant.play(
                chat_id,
                stream,
            )
        except NoActiveGroupCall:
            try:
                await assistant.play(
                    chat_id,
                    stream,
                )
            except Exception:
                raise AssistantErr(
                    "**É´á´ á´€á´„á´›Éªá´ á´‡ á´ Éªá´…á´‡á´ á´„Êœá´€á´› Ò“á´á´œÉ´á´…**\n\ná´©ÊŸá´‡á´€sá´‡ á´á´€á´‹á´‡ sá´œÊ€á´‡ Êá´á´œ sá´›á´€Ê€á´›á´‡á´… á´›Êœá´‡ á´ Éªá´…á´‡á´á´„Êœá´€á´›."
                )
        except Exception as e:
            if "phone.CreateGroupCall" in str(e):
                try:
                    await assistant.play(
                        chat_id,
                        stream,
                    )
                except Exception:
                    raise AssistantErr(
                        f"**Â» É´á´ á´€á´„á´›Éªá´ á´‡ á´ Éªá´…á´‡á´á´„Êœá´€á´› Ò“á´á´œÉ´á´….**\n\ná´©ÊŸá´‡á´€sá´‡ á´á´€á´‹á´‡ sá´œÊ€á´‡ Êá´á´œ sá´›á´€Ê€á´›á´‡á´… á´›Êœá´‡ á´ Éªá´…á´‡á´á´„Êœá´€á´›."
                    )

        except AlreadyJoinedError:
            raise AssistantErr(
                "**á´€ssÉªsá´›á´€É´á´› á´€ÊŸÊ€á´‡á´€á´…Ê ÉªÉ´ á´ Éªá´…á´‡á´á´„Êœá´€á´›**\n\ná´á´œsÉªá´„ Ê™á´á´› sÊsá´›á´‡á´s á´…á´‡á´›á´‡á´„á´›á´‡á´… á´›Êœá´€á´› á´€ssÉªá´›á´€É´á´› Éªs á´€ÊŸÊ€á´‡á´€á´…Ê ÉªÉ´ á´›Êœá´‡ á´ Éªá´…á´‡á´á´„Êœá´€á´›, ÉªÒ“ á´›ÊœÉªs á´©Ê€á´Ê™ÊŸá´‡á´ á´„á´É´á´›ÉªÉ´á´œá´‡s Ê€á´‡sá´›á´€Ê€á´› á´›Êœá´‡ á´ Éªá´…á´‡á´á´„Êœá´€á´› á´€É´á´… á´›Ê€Ê á´€É¢á´€ÉªÉ´."
            )
        except TelegramServerError:
            raise AssistantErr(
                "**á´›á´‡ÊŸá´‡É¢Ê€á´€á´ sá´‡Ê€á´ á´‡Ê€ á´‡Ê€Ê€á´Ê€**\n\ná´©ÊŸá´‡á´€sá´‡ á´›á´œÊ€É´ á´Ò“Ò“ á´€É´á´… Ê€á´‡sá´›á´€Ê€á´› á´›Êœá´‡ á´ Éªá´…á´‡á´á´„Êœá´€á´› á´€É¢á´€ÉªÉ´."
            )
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            if popped:
                await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
        except:
            try:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
            except:
                return
        else:
            queued = check[0]["file"]
            language = await get_lang(chat_id)
            _ = get_string(language)
            title = (check[0]["title"]).title()
            user = check[0]["by"]
            original_chat_id = check[0]["chat_id"]
            streamtype = check[0]["streamtype"]
            audio_stream_quality = await get_audio_bitrate(chat_id)
            video_stream_quality = await get_video_bitrate(chat_id)
            videoid = check[0]["vidid"]
            userid = check[0].get("user_id")
            check[0]["played"] = 0
            video = True if str(streamtype) == "video" else False
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_7"],
                    )
                if video:
                    stream = MediaStream(
                        link,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality,
                    )
                else:
                    try:
                        image = await YouTube.thumbnail(videoid, True)
                    except:
                        image = None
                    if image and config.PRIVATE_BOT_MODE == str(True):
                        stream = MediaStream(
                            link,
                            image,
                            audio_parameters=audio_stream_quality,
                            video_parameters=video_stream_quality,
                        )
                    else:
                        stream = MediaStream(
                            link,
                            audio_parameters=audio_stream_quality,
                        )
                try:
                    await client.play(chat_id, stream)
                except Exception:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_7"],
                    )
                img = await gen_thumb(videoid)
                button = telegram_markup(_, chat_id)
                run = await app.send_photo(
                    original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        title[:27],
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_8"])
                try:
                    file_path, direct = await YouTube.download(
                        videoid,
                        mystic,
                        videoid=True,
                        video=True if str(streamtype) == "video" else False,
                    )
                except:
                    return await mystic.edit_text(
                        _["call_7"], disable_web_page_preview=True
                    )
                if video:
                    stream = MediaStream(
                        file_path,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality,
                    )
                else:
                    try:
                        image = await YouTube.thumbnail(videoid, True)
                    except:
                        image = None
                    if image and config.PRIVATE_BOT_MODE == str(True):
                        stream = MediaStream(
                            file_path,
                            image,
                            audio_parameters=audio_stream_quality,
                            video_parameters=video_stream_quality,
                        )
                    else:
                        stream = MediaStream(
                            file_path,
                            audio_parameters=audio_stream_quality,
                        )
                try:
                    await client.play(chat_id, stream)
                except Exception:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_7"],
                    )
                img = await gen_thumb(videoid)
                button = stream_markup(_, videoid, chat_id)
                await mystic.delete()
                run = await app.send_photo(
                    original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        title[:27],
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            elif "index_" in queued:
                stream = (
                    MediaStream(
                        videoid,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality,
                    )
                    if str(streamtype) == "video"
                    else MediaStream(videoid, audio_parameters=audio_stream_quality)
                )
                try:
                    await client.play(chat_id, stream)
                except Exception:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_7"],
                    )
                button = telegram_markup(_, chat_id)
                run = await app.send_photo(
                    original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                if videoid == "telegram":
                    image = None
                elif videoid == "soundcloud":
                    image = None
                else:
                    try:
                        image = await YouTube.thumbnail(videoid, True)
                    except:
                        image = None
                if video:
                    stream = MediaStream(
                        queued,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality,
                    )
                else:
                    if image and config.PRIVATE_BOT_MODE == str(True):
                        stream = MediaStream(
                            queued,
                            image,
                            audio_parameters=audio_stream_quality,
                            video_parameters=video_stream_quality,
                        )
                    else:
                        stream = MediaStream(
                            queued,
                            audio_parameters=audio_stream_quality,
                        )
                try:
                    await client.play(chat_id, stream)
                except Exception:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_7"],
                    )
                if videoid == "telegram":
                    button = telegram_markup(_, chat_id)
                    run = await app.send_photo(
                        original_chat_id,
                        photo=(
                            config.TELEGRAM_AUDIO_URL
                            if str(streamtype) == "audio"
                            else config.TELEGRAM_VIDEO_URL
                        ),
                        caption=_["stream_1"].format(
                            title, config.SUPPORT_GROUP, check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    button = telegram_markup(_, chat_id)
                    run = await app.send_photo(
                        original_chat_id,
                        photo=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(
                            title, config.SUPPORT_GROUP, check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                
