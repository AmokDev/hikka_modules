# ██████╗ ██╗   ██╗                                            
# ██╔══██╗╚██╗ ██╔╝                                            
# ██████╔╝ ╚████╔╝                                             
# ██╔══██╗  ╚██╔╝                                              
# ██████╔╝   ██║                                               
# ╚═════╝    ╚═╝                                               
#  █████╗ ███╗   ███╗ ██████╗ ██╗  ██╗██████╗ ███████╗██╗   ██╗
# ██╔══██╗████╗ ████║██╔═══██╗██║ ██╔╝██╔══██╗██╔════╝██║   ██║
# ███████║██╔████╔██║██║   ██║█████╔╝ ██║  ██║█████╗  ██║   ██║
# ██╔══██║██║╚██╔╝██║██║   ██║██╔═██╗ ██║  ██║██╔══╝  ╚██╗ ██╔╝
# ██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██╗██████╔╝███████╗ ╚████╔╝ 
# ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝  ╚═══╝  
# © Copyright 2024 | https://t.me/AmokModules
# Licensed under the MIT License
# meta developer: @AmokModules

import os
import requests
import subprocess
from pytube import YouTube
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1

from .. import loader, utils

@loader.tds
class YTMDownloaderMod(loader.Module):
    """Модуль для скачивания музыки с сервиса YouTube Music"""

    strings = {
        "name": "Youtube Music Downloader",
        "loading": "<emoji document_id=5332815674580416193>❤️‍🔥</emoji><b>  Loading...</b>",
        "link_arg": "<emoji document_id=5262969623627704708>💦</emoji><b>  You need to enter the track link to download it!</b>",
        "not_found": "<emoji document_id=5465665476971471368>❌</emoji><b>  Track not found!</b>",
        "sending": "<emoji document_id=5242658160644204099>📷</emoji> <b>Sending...</b>",
    }

    strings_ru = {
        "loading": "<emoji document_id=5332815674580416193>❤️‍🔥</emoji><b>  Загрузка...</b>",
        "link_arg": "<emoji document_id=5262969623627704708>💦</emoji><b>  Вам нужно ввести ссылку на трек, чтобы скачать его!</b>",
        "not_found": "<emoji document_id=5465665476971471368>❌</emoji><b>  Трек не найден!</b>",
        "sending": "<emoji document_id=5242658160644204099>📷</emoji><b>  Отправляю...</b>",
    }

    async def ytmcmd(self, msg):
        """<link> - Скачать музыку с YouTube Music"""
        args: str = utils.get_args_raw(msg)
        if len(args.split()) != 1:
            await msg.edit(self.strings("link_arg"))
            return

        await msg.edit(self.strings("loading"))
        try:
            track = await utils.run_sync(self.download_music, args.split()[0])
        except Exception:
            await msg.edit(self.strings("not_found"))
            return

        path = self.convert_to_mp3(track[0])
        await utils.run_sync(self.edit_voice_tags, path, track[1], track[2], track[3])
        await msg.edit(self.strings("sending"))
        await self._client.send_file(msg.peer_id, path)
        os.remove(path)
        await msg.delete()

    def edit_voice_tags(self, path, title, artist, image_url):
        audio = MP3(path, ID3=ID3)
        response = requests.get(image_url)
        image_data = response.content
        audio["TIT2"] = TIT2(encoding=3, text=title)
        audio["TPE1"] = TPE1(encoding=3, text=artist)
        artwork = APIC(encoding=3, mime='image/png', type=3, desc=u'Cover', data=image_data)
        try:
            audio.tags.add(artwork)
            audio.save()
        except error:
            pass

    def convert_to_mp3(self, file):
        file_name, ext = os.path.splitext(file)
        subprocess.call(
            ["ffmpeg", "-y", "-i", file, f"{file_name}.mp3"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        os.remove(file)
        return f"{file_name}.mp3"

    def download_music(self, url):
        music = YouTube(url)
        yt = (
            music.streams.filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
            .first()
        )
        return [
            yt.download("/tmp"),
            music.title,
            music.author,
            music.thumbnail_url,
        ]
