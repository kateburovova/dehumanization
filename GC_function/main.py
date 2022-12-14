import telethon
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
    me = await client.get_me()

    print(me.stringify())

    username = me.username
    print(username)
    print(me.phone)

    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)
        break

def msg_handler(msg):

    msg_attributes = {
        'message': msg.message,
        'type': 'text',
        'duration': '',
        'to_id': '',
        'fwd': msg.fwd_from,
    }

    if hasattr(msg.to_id, 'user_id'):
        msg_attributes['to_id'] = msg.to_id.user_id
    else:
        msg_attributes['to_id'] = msg.to_id

    if msg.sticker:
        for attribute in msg.sticker.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeSticker):
                msg_attributes['message'] = attribute.alt
                msg_attributes['type'] = 'sticker'

    elif msg.video:
        for attribute in msg.video.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeVideo):
                msg_attributes['duration'] = attribute.duration
                msg_attributes['type'] = 'video'

    elif msg.voice:
        for attribute in msg.voice.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeAudio):
                msg_attributes['duration'] = attribute.duration
                msg_attributes['type'] = 'voice'

    elif msg.photo:
        msg_attributes['type'] = 'photo'

    return msg_attributes


async def load_channel(client, name, MSG_LIMIT=10):

    try:
        tg_entity = await client.get_entity(name)
        print(MSG_LIMIT)
        messages = await client.get_messages(tg_entity, limit=MSG_LIMIT)

    except ValueError:
        errmsg = f'No NAME found: {name}'
        print(errmsg)

    channel = []

    for m in messages:

        msg_attrs = msg_handler(m)
        print(m.message, m.date)

        if isinstance(m.fwd_from, MessageFwdHeader):
            try:
                entity = await client.get_input_entity(PeerChannel(extract_id(m.fwd_from)))
                await asyncio.sleep(1)
                fwd_result = await client(GetFullChannelRequest(entity))
                fwd_title = fwd_result.chats[0].title
                channel.append(
                    {
                        'id': m.id,
                        'date': m.date,
                        'views': m.views,
                        'reactions': m.reactions,
                        'to_id': msg_attrs['to_id'],
                        'fwd_from': m.fwd_from,
                        'message': msg_attrs['message'],
                        'type': msg_attrs['type'],
                        'duration': msg_attrs['duration'],
                        'frw_from_title': fwd_title,
                        'frw_from_name': fwd_result.chats[0].username,
                        'msg_entity': m.entities
                    }
                )
            except telethon.errors.rpcerrorlist.ChannelPrivateError:
                pass
            except TypeError:
                pass

        else:

            channel.append(
                {
                    'id': m.id,
                    'date': m.date,
                    'views': m.views,
                    'reactions': m.reactions,
                    'to_id': msg_attrs['to_id'],
                    'fwd_from': m.fwd_from,
                    'message': msg_attrs['message'],
                    'type': msg_attrs['type'],
                    'duration': msg_attrs['duration']
                }
            )

        try:
            async for reply in client.iter_messages(tg_entity, reply_to=m.id, limit=10, reverse=True):
                reply_attrs = msg_handler(reply)

                channel.append(
                    {
                        'id': reply.id,
                        'date': reply.date,
                        'views': reply.views,
                        'reactions': reply.reactions,
                        'to_id': reply_attrs['to_id'],
                        'fwd_from': reply.fwd_from,
                        'message': reply_attrs['message'],
                        'type': reply_attrs['type'],
                        'duration': reply_attrs['duration'],
                    }
                )

        # deleted messages cause this error, it's safe to ignore them
        except telethon.errors.rpcerrorlist.MsgIdInvalidError:
            pass

        except ValueError:
            errmsg = f'No message id found: {m.id}'
            print(errmsg)

        except TypeError:
            err = f'TypeError raised on message {m.id}'
            print(err)


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
