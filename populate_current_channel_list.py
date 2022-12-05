import json
import os
import pandas as pd
import glob

if __name__ == "__main__":
    with open('/Users/katerynaburovova/PycharmProjects/dehumanization/data/channels_list.json', 'r') as openfile:
        data = json.load(openfile)

    loaded_channels_path = "/Users/katerynaburovova/PycharmProjects/dehumanization/data/channels"
    channel_data_files = glob.glob(f"{loaded_channels_path}/*.csv")

    already_loaded_list = []
    for channel in channel_data_files:
        local_df = pd.read_csv(channel)
        already_loaded_list.append(os.path.basename(channel).split(".")[0])

    current_list = set(data['names']) - set(already_loaded_list)
    current_list = list(current_list)

    dict2 = {"names": current_list}
    json_object = json.dumps(dict2, indent=4)

    with open("/Users/katerynaburovova/PycharmProjects/dehumanization/data/current_channel_list", "w") as outfile:
        outfile.write(json_object)
    print(f'Total channels to load: {len(current_list)}, excluded: {already_loaded_list}')


