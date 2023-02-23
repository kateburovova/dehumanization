import telethon
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel, MessageFwdHeader
import asyncio
# import functions_framework
import pandas as pd
from datetime import datetime
from google.cloud import storage
import csv
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


async def load_channel(client, name, MSG_LIMIT=None):

    try:
        tg_entity = await client.get_entity(name)
        messages = await client.get_messages(tg_entity, limit=MSG_LIMIT)

    except ValueError:
        errmsg = f'No NAME found: {name}'
        print(errmsg)

    channel = []

    for m in messages:

        msg_attrs = msg_handler(m)
        print(m.message, m.date)

        # if isinstance(m.fwd_from, MessageFwdHeader):
        #     try:
        #         entity = await client.get_input_entity(PeerChannel(extract_id(m.fwd_from)))
        #         await asyncio.sleep(0.001)
        #         fwd_result = await client(GetFullChannelRequest(entity))
        #         fwd_title = fwd_result.chats[0].title
        #         channel.append(
        #             {
        #                 'id': m.id,
        #                 'date': m.date,
        #                 'views': m.views,
        #                 'reactions': m.reactions,
        #                 'to_id': msg_attrs['to_id'],
        #                 'fwd_from': m.fwd_from,
        #                 'message': msg_attrs['message'],
        #                 'type': msg_attrs['type'],
        #                 'duration': msg_attrs['duration'],
        #                 'frw_from_title': fwd_title,
        #                 'frw_from_name': fwd_result.chats[0].username,
        #                 'msg_entity': m.entities
        #             }
        #         )
        #     except telethon.errors.rpcerrorlist.ChannelPrivateError:
        #         pass
        #     except TypeError:
        #         pass
        #
        # else:

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

        # try:
        #     async for reply in client.iter_messages(tg_entity, reply_to=m.id, limit=3, reverse=True):
        #         reply_attrs = msg_handler(reply)
        #
        #         channel.append(
        #             {
        #                 'id': reply.id,
        #                 'date': reply.date,
        #                 'views': reply.views,
        #                 'reactions': reply.reactions,
        #                 'to_id': reply_attrs['to_id'],
        #                 'fwd_from': reply.fwd_from,
        #                 'message': reply_attrs['message'],
        #                 'type': reply_attrs['type'],
        #                 'duration': reply_attrs['duration'],
        #             }
        #         )
        #
        # # deleted messages cause this error, it's safe to ignore them
        # except telethon.errors.rpcerrorlist.MsgIdInvalidError:
        #     pass
        #
        # except ValueError:
        #     errmsg = f'No message id found: {m.id}'
        #     print(errmsg)
        #
        # except TypeError:
        #     err = f'TypeError raised on message {m.id}'
        #     print(err)

    df = pd.DataFrame(channel)
    csv_str = df.to_csv()

    def upload_blob(bucket_name, data, destination_blob_name):

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        # Note the use of upload_from_string here. Please, provide
        # the appropriate content type if you wish
        blob.upload_from_string(data, content_type='text/csv')

    now = datetime.now()
    dt_string = now.strftime('%d_%m_%Y_%H_%M_%S')

    upload_blob('tg_scr_bucket', csv_str, 'data-' + name + '_' + dt_string + '.csv')

# @functions_framework.http
def get_channel_data(request):

    request_json = request.get_json()

    if request.args and 'name' in request.args:
        channel_name = request.args.get('name')
    elif request_json and 'name' in request_json:
        channel_name = request_json['name']
    else:
        channel_name = 'margaritasimonyan'

    api_id = 27051890
    api_hash = '3a0e430c3d84e890ee7077fc51b96c48'
    session = '1ApWapzMBu3OrUpeBVN_yEKOXxuLq8O-l3odTXsyl0Hm2_jUTzIWBjT5WSWlFAU7tHBVi5w5qHuRF3fBv3-riXKnxjiI5jKMU9czfx0HhzcDVDkR68uOEXLXuVgB46rpAbau_OmaZ2cwNcjoF8KJkMm_o8Sqz5bTNffgK0dcvalaxBw6rgi_KQrPfahJK1fNcr_u0x9kcQ5nliT89zaQ3XwTZWF-_03zJrmRavfZ-e7DJc6mRtHNUbYu17R3-GrHwkr5HmTgjua_856nvwSH7pc67Ikkye1j_6V0iwOfklhi7k4utVYR-r75kLkVwtmdc8cmbzVQSFN-4UmUrPgauXY0Mv0YFJ8A='

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client = TelegramClient(StringSession(session), api_id, api_hash, loop=loop)

    # channel_name = 'readovkanews'

    with client:
        client.loop.run_until_complete(load_channel(client, channel_name))

    return 'OK'
