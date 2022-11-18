import os
import argparse
import pandas as pd
import json
import telethon
from utils.utils import init_config


def init_args():
    parser = argparse.ArgumentParser(
        description="Loads channels data"
    )

    parser.add_argument(
        "--channel_msg_limit",
        type=int,
        help="constraint on the amount of messages per channel",
        default=1000,
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

    return parser.parse_args()


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

        channel.append(
            {
                "id": m.id,
                "date": m.date,
                "from_id": m.from_id,
                "to_id": msg_attrs["to_id"],
                "fwd_from": m.fwd_from,
                "message": msg_attrs["message"],
                "type": msg_attrs["type"],
                "duration": msg_attrs["duration"],
            }
        )

    channel_file_path = os.path.join(config["channel_data_folder"], f"{str(name)}.csv")

    print(channel_file_path)

    df = pd.DataFrame(channel)
    df.to_csv(channel_file_path)

if __name__ == "__main__":

    args = init_args()

    CONFIG_PATH = args.config_path
    MSG_LIMIT = msg_limit_input_handler(args.channel_msg_limit)
    SESSION_NAME = args.session_name

    config = init_config(CONFIG_PATH)

    channels_list_path = "/Users/katerynaburovova/PycharmProjects/dehumanization/data/channels_list.json"

    client = telethon.TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

    CHANNELS_NAMES = load_channel_names(channels_list_path)

    if not os.path.exists(config["channel_data_folder"]):
        os.mkdir(config["channel_data_folder"])

    for name in CHANNELS_NAMES:
        print(f"Loading channel {name}")

        with client:
            client.loop.run_until_complete(load_channel(client, name, MSG_LIMIT, config))
