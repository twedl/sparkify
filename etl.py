import os
import glob
import psycopg2
import pandas as pd 
from sql_queries import *

def process_song_file(cur, filepath):
    """
    - insert records into songs table
    - insert records into artists table
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    song_data = list(df[["song_id", "title", "artist_id", "year", "duration"]].values[0])
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_data = list(df[["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]].values[0])
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    - filter and clean log data
    - insert records into time table
    - insert records into users table
    - query songs and artists table for ids, then
    - insert records into songplays table
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df.page == "NextSong"]

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

    # convert timestamp in df from milliseconds to timestamp for insertion into songplays database
    df["ts"] = t

    # insert songplay records
    for index, row in df.iterrows():
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length)) 
        results = cur.fetchone()

        if results:
            song_id, artist_id = results
        else:
            song_id, artist_id = None, None
        

        # insert songplay record
        songplay_data = tuple(row[["ts", "userId", "level"]]) + \
            (song_id, artist_id) + \
            tuple(row[["sessionId", "location", "userAgent"]])
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    - process files in directory `filepath` with function `func`
    """
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
        func(cur, datafile)
        conn.commit()
        print(f'{i}/{num_files} files processed.')

def main():
    """
    - connect to sparkifydb
    - process song and log data
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()