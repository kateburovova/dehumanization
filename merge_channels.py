import pandas as pd
import glob
import os


if __name__ == "__main__":
    merged_dataset_path = "/data/Telegram_initial_data/merged_dataset/df_channels.csv"
    loaded_channels_path = "/Users/katerynaburovova/PycharmProjects/dehumanization/data/channels"
    channel_data_files = glob.glob(f"{loaded_channels_path}/*.csv")
    # print(channel_data_files)
    df = []
    for channel in channel_data_files:
        local_df = pd.read_csv(channel)
        local_df["channel_name"] = os.path.basename(channel).split(".")[0]
        df.append(local_df)
    df_channels_merged = pd.concat(df, ignore_index=True)
    df_channels_merged.to_csv(merged_dataset_path, index=False)
