import os
import argparse
import pandas as pd
import json
import telethon
import asyncio
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import PeerChannel, MessageFwdHeader, PeerUser, PeerChat, MessageEntityMentionName

from utils.utils import init_config

# https://tl.telethon.dev/constructors/message.html
# https://limits.tginfo.me/en +- 180 entities could be accessed


def init_args():
    parser = argparse.ArgumentParser(
        description="Loads channels data"
    )

    parser.add_argument(
        "--channel_msg_limit",
        type=int,
        help="constraint on the amount of messages per channel",
        default=10,
    )
    parser.add_argument(
        "--config_path",
        type=str,
        help="path to config file",
        default="config/config.json",
    )
    parser.add_argument(
        "--session_name",
        type=str,
        help="session name",
        default="tmp"
    )
    parser.add_argument(
        "--channel_list_path",
        type=str,
        help="path to list of channels being loaded",
        default="/Users/katerynaburovova/PycharmProjects/dehumanization/data/channels_list.json"
    )

    return parser.parse_args()


def extract_id(text):
    text = str(text)
    if text is None:
        return 50039420
    else:
        pos = text.find('channel_id=')+len('channel_id=')
        if pos>1:
            result = text[pos:(pos+25)].split('),')[0]
            return int(result)
        else:
            pass


def load_channel_names(channels_list_path="/Users/katerynaburovova/PycharmProjects/dehumanization/data/channels_list.json"):
    """
    :param channels_list_path: "/Users/katerynaburovova/PycharmProjects/dehumanization/data/channels_list.json"
    :return: list with channel names
    """

    with open(channels_list_path, 'r') as openfile:
        channels_list = json.load(openfile)
    return [channel_name for channel_name in channels_list['names']]


def msg_limit_input_handler(msg_limit):
    """
    Functions handles msg_limit depending on the input

    :param msg_limit: maximum amount of messages to be
                      downloaded for each dialog
    :return: msg_limit
    """
    msg_limit = 100000000 if msg_limit == -1 else msg_limit
    return msg_limit


def msg_handler(msg):
    """
    Handles attributes of a specific message, depending if
    it is text, photo, voice, video or sticker

    :param msg: message
    :return: dict of attributes
    """
    msg_attributes = {
        "message": msg.message,
        "type": "text",
        "duration": "",
        "to_id": "",
        "fwd": msg.fwd_from,
    }

    if hasattr(msg.to_id, "user_id"):
        msg_attributes["to_id"] = msg.to_id.user_id
    else:
        msg_attributes["to_id"] = msg.to_id


    if msg.sticker:
        for attribute in msg.sticker.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeSticker):
                msg_attributes["message"] = attribute.alt
                msg_attributes["type"] = "sticker"

    elif msg.video:
        for attribute in msg.video.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeVideo):
                msg_attributes["duration"] = attribute.duration
                msg_attributes["type"] = "video"

    elif msg.voice:
        for attribute in msg.voice.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeAudio):
                msg_attributes["duration"] = attribute.duration
                msg_attributes["type"] = "voice"

    elif msg.photo:
        msg_attributes["type"] = "photo"


    return msg_attributes



async def load_channel(client, name, MSG_LIMIT, config):
    """
    Download messages and their metadata for a specific channel name,
    and save them in *name*.csv

    :return: None
    """
    try:
        tg_entity = await client.get_entity(name)
        messages = await client.get_messages(tg_entity, limit=MSG_LIMIT)
    except ValueError:
        errmsg = f"No NAME found: {name}"
        print(errmsg)

    channel = []

    for m in messages:

        msg_attrs = msg_handler(m)

        if isinstance(m.fwd_from, MessageFwdHeader):
            try:
                entity = await client.get_input_entity(PeerChannel(extract_id(m.fwd_from)))
                await asyncio.sleep(1)
                fwd_result = await client(GetFullChannelRequest(entity))  #, flood_sleep_threshold=15)
                fwd_title = fwd_result.chats[0].title
                channel.append(
                    {
                        "id": m.id,
                        "date": m.date,
                        "views": m.views,
                        "reactions": m.reactions,
                        "to_id": msg_attrs["to_id"],
                        "fwd_from": m.fwd_from,
                        "message": msg_attrs["message"],
                        "type": msg_attrs["type"],
                        "duration": msg_attrs["duration"],
                        "frw_from_title": fwd_title,
                        "frw_from_name": fwd_result.chats[0].username,
                        "msg_entity": m.entities
                    }
                )
            except telethon.errors.rpcerrorlist.ChannelPrivateError:
                pass

        else:

            channel.append(
                {
                    "id": m.id,
                    "date": m.date,
                    "views": m.views,
                    "reactions": m.reactions,
                    "to_id": msg_attrs["to_id"],
                    "fwd_from": m.fwd_from,
                    "message": msg_attrs["message"],
                    "type": msg_attrs["type"],
                    "duration": msg_attrs["duration"]
                }
            )


        try:
            async for reply in client.iter_messages(tg_entity, reply_to=m.id, limit=10):

                reply_attrs = msg_handler(reply)

                channel.append(
                    {
                        "id": reply.id,
                        "date": reply.date,
                        "views": reply.views,
                        "reactions": reply.reactions,
                        "to_id": reply_attrs["to_id"],
                        "fwd_from": reply.fwd_from,
                        "message": reply_attrs["message"],
                        "type": reply_attrs["type"],
                        "duration": reply_attrs["duration"],
                    }
                )

        # deleted messages cause this error, it's safe to ignore them
        except telethon.errors.rpcerrorlist.MsgIdInvalidError:
            pass

        except ValueError:
            errmsg = f"No message id found: {m.id}"
            print(errmsg)

        except TypeError:
            err = f"TypeError raised on message {m.id}"
            print(err)


    channel_file_path = os.path.join(config["channel_data_folder"], f"{str(name)}.csv")

    df = pd.DataFrame(channel)
    df.to_csv(channel_file_path)

if __name__ == "__main__":

    args = init_args()

    MSG_LIMIT = msg_limit_input_handler(args.channel_msg_limit)
    SESSION_NAME = args.session_name

    channels_list_path = args.channel_list_path
    CHANNELS_NAMES = load_channel_names(channels_list_path)

    CONFIG_PATH = args.config_path
    config = init_config(CONFIG_PATH)

    client = telethon.TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

    if not os.path.exists(config["channel_data_folder"]):
        os.mkdir(config["channel_data_folder"])

    for name in CHANNELS_NAMES:
        print(f"Loading channel {name}")

        with client:
            client.loop.run_until_complete(load_channel(client, name, MSG_LIMIT, config))
