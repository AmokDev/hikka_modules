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
# scope: hikka_only

import os
import frida
from telethon import TelegramClient
from telethon.tl.custom import Message
from telethon.tl.functions.channels import JoinChannelRequest

from .. import loader, utils

@loader.tds
class FridaCompile(loader.Module):
    """Модуль для компилирования js-файлов с помощью скрипта frida-compile."""

    strings = {
        "name": "FridaCompile",
        "author": "@amokmodules",
        "wait": "<emoji document_id=5242318591939848121>⚙️</emoji><b>  Please wait...</b>",
        "nothing_found": "<emoji document_id=5242583239234692447>📱</emoji> <b>Where's the file?</b>",
        "sending": "<emoji document_id=5244914117986231107>➡️</emoji> <b>Sending...</b>",
        "done": "<emoji document_id=5244814479039931647>✅</emoji> <b>Done!</b>",
        "error": "<emoji document_id=5242583239234692447>📱</emoji> <b>Oops, there seems to be some kind of error:</b>",
    }

    strings_ru = {
        "wait": "<emoji document_id=5242318591939848121>⚙️</emoji> <b>Пожалуйста, подождите...</b>",
        "nothing_found": "<emoji document_id=5242583239234692447>📱</emoji><b>  А где файл?</b>",
        "sending": "<emoji document_id=5244914117986231107>➡️</emoji>  Отправляю...</b>",
        "done": "<emoji document_id=5244814479039931647>✅</emoji> <b>Готово!</b>",
        "error": "<emoji document_id=5242583239234692447>📱</emoji><b>  Упс, кажется произошла какая-то ошибка:</b>",
    }

    async def client_ready(self, client: TelegramClient, _):
        """client_ready hook"""
        await client(JoinChannelRequest(channel=self.strings("author")))

    async def fridacompilecmd(self, msg: Message):
        """<reply to file> - Скомпилировать js-файл с помощью скрипта frida-compile (QJS)"""
        await msg.edit(self.strings("wait"))
        try:
            msg_file = (
                await self._client.download_file(msg.media, bytes)
            ).decode("utf-8")
        except Exception:
            msg_file = None

        try:
            reply = await msg.get_reply_message()
            reply_file = (
                await self._client.download_file(reply.media, bytes)
            ).decode("utf-8")
        except Exception:
            reply_file = None

        if not msg_file and not reply_file:
            await msg.edit(self.strings("nothing_found"))
            return

        code = msg_file or reply_file
        compiler = await utils.run_sync(self.compile, code)
        if type(compiler) is str:
            await msg.edit(self.strings("error") + f" {compiler}")
            return
        await msg.edit(self.strings("sending"))
        await self._client.send_file(msg.peer_id, "/tmp/libfrida.script.so", caption=self.strings("done"))
        await msg.delete()
        os.remove("/tmp/libfrida.script.so")

    def compile(self, code: str):
        try:
            with open(f"/tmp/libfrida.script.so", "wb+") as f:
                session = frida.get_local_device().attach(0)
                script = session.compile_script(code, "agent.js", "qjs")
                f.write(script)
        except Exception as e:
            os.remove("/tmp/libfrida.script.so")
            return self.strings("error") + f" <code>{e}</code>"
        return True
