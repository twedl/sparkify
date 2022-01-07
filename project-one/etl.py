import os
import glob
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import pandas as pd 
import numpy as np
# import json
from sql_queries import *

psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)

#                                    0
# num_songs                          1
# artist_id         ARGCY1Y1187B9A4FA5
# artist_latitude             36.16778
# artist_longitude           -86.77836
# artist_location       Nashville, TN.
# artist_name                 Gloriana
# song_id           SOQOTLQ12AB01868D0
# title             Clementina Santafè
# duration                   153.33832
# year                               0


# num_songs             int64
# artist_id            object str
# artist_latitude     float64
# artist_longitude    float64 
# artist_location      object str 
# artist_name          object str
# song_id              object str
# title                object str
# duration            float64
# year                  int64
# dtype: object
# 69/71 files processed.
def process_song_file(cur, filepath):
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = list(list(df[["song_id", "title", "artist_id", "year", "duration"]].iloc(0))[0])
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_data = list(list(df[["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]].iloc(0))[0])
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df.page == "NextSong"]
    # print(df.loc[0].transpose())
    # print(df.dtypes)

    # convert timestamp column to datetime
    t = pd.to_datetime(df["ts"], unit="ms")

    # insert time data records
    time_data = [t, t.dt.hour, t.dt.day, t.dt.isocalendar().week, t.dt.month, t.dt.year, t.dt.weekday]
    column_labels = ["start_time", "hour", "day", "week", "month", "year", "weekday"] # should these have song_ prefixes or what
    time_df = pd.DataFrame(dict(zip(column_labels, time_data)))

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[["userId", "firstName", "lastName", "gender", "level"]].drop_duplicates()

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        print(results)
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None
        

        # insert songplay record
        songplay_data = None # idk what
        print(songplay_data)
        # cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json.gz'))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print(f'{num_files} files found in {filepath}')

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        if i>1:
            break
        func(cur, datafile)
        conn.commit()
        print(f'{i}/{num_files} files processed.')

def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    # no tables yet huh; create them here or somewhere else

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()