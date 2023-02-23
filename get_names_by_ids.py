import os
import argparse
import time
from datetime import datetime

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
# courtesy of https://github.com/SanGreel/telegram-dialogs-analysis-v2


def init_args():
    parser = argparse.ArgumentParser(
        description="Loads channels data"
    )

    # parser.add_argument(
    #     "--channel_msg_limit",
    #     type=int,
    #     help="constraint on the amount of messages per channel",
    #     default=-1,
    # )
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
        "--ids_list_path",
        type=str,
        help="path to list of channels being loaded",
        default="/Users/katerynaburovova/PycharmProjects/dehumanization/data/ids_channels_list.json"
    )

    return parser.parse_args()

def load_channel_ids(ids_list_path="/Users/katerynaburovova/PycharmProjects/dehumanization/data/ids_channels_list.json"):

    with open(ids_list_path, 'r') as openfile:
        ids_list = json.load(openfile)
    return [channel_id for channel_id in ids_list['ids']]


async def get_names(client, id):
    names = []

    tg_entity = await client.getHistory('margaritasimonyan')

    try:
        print(f"Getting id {id}")
        entity = await client.get_entity(PeerChat(id))
        print(entity.stringify())
        print("I got entity")
        await asyncio.sleep(1)
        fwd_result = await client(GetFullChannelRequest(entity))
        fwd_title = fwd_result.chats[0].title
        names.append(fwd_title)
        print(fwd_title)

    except ValueError:
        errmsg = f"No NAME found for id: {id}"
        print(errmsg)

    dict = {"titles": names}
    json_object = json.dumps(dict, indent=4)

    with open("/Users/katerynaburovova/PycharmProjects/dehumanization/data/names_from_ids_list.json", "a") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":

    args = init_args()

    SESSION_NAME = args.session_name

    ids_list_path = args.ids_list_path
    CHANNELS_IDS = load_channel_ids(ids_list_path)

    CONFIG_PATH = args.config_path
    config = init_config(CONFIG_PATH)

    client = telethon.TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

    if not os.path.exists(config["id_data_folder"]):
        os.mkdir(config["id_data_folder"])

    for id in CHANNELS_IDS:
        print(f"Loading channel {id}")

        with client:
            client.loop.run_until_complete(get_names(client, id))


