from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel, MessageFwdHeader
import asyncio
import pandas as pd
import os
import json


def extract_id(text):
    text = str(text)
    if text is None:
        return 50039420
    else:
        try:
            pos = text.find('channel_id=') + len('channel_id=')
            if pos > 1:
                result = text[pos:(pos + 25)].split('),')[0]
                return int(result)
            else:
                pass
        except ValueError:
            return ''
        except TypeError:
            return ''


async def main(client):
    # Getting information about yourself
    me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    username = me.username
    print(username)
    print(me.phone)

    # You can print all the dialogs/conversations that you are part of:
    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)
        break

def get_my_data(request):
    api_id = 000000
    api_hash = '000000000000000000000000'
    session = '000000000000000000000000000000000000000000'

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client = TelegramClient(StringSession(session), api_id, api_hash, loop=loop)

    with client:
        client.loop.run_until_complete(main(client))

    return "OK"
