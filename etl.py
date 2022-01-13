import os
import glob
import psycopg2
import pandas as pd 
from sql_queries import *

def process_song_file(cur, filepath):
    """
    This function processes a song file given by `filepath`.
    It extracts the song data and stores it in the `songs` table,
    then extracts the artist data and stores it in the `artists` table.

    INPUTS:
        - cur: the psycopg2 database cursor variable
        - filepath: the file path to the song file
    OUTPUTS:
        - None
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
    This function processes a log file given by `filepath`.
    It filters and cleans the log data, then:
        - inserts records into the `time` table
        - inserts users into the `users` table
        - queries the `songs` and `artists` table for song and artist ids, if they exist,
            then inserts the songplay record into the `songplays` table


    INPUTS:
        - cur: the psycopg2 database cursor variable
        - filepath: the file path to the song file
    OUTPUTS:
        - None
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
    This function lists all files in the directory given by `filepath`,
    then processes them with the function `func`. The database cursor 
    `cur` must be passed to `func` as well.

    INPUTS:
        - cur: the psycopg2 database cursor
        - conn: the psycopg2 database connection
        - filepath: the file path to the song file
        - func: the process function, currently either `process_song_file`
            or `process_log_file`
    OUTPUTS:
        - None
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
    This script connects to the existing database `sparkifydb` (created by
    `create_tables.py`) and processes the song data in `data/song_data` and then
    the log data in `data/log_data`.
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()