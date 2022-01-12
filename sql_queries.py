# DROP TABLES

songplay_table_drop = "DROP DATABASE IF EXISTS songplays;"
user_table_drop = "DROP DATABASE IF EXISTS users;"
song_table_drop = "DROP DATABASE IF EXISTS songs;"
artist_table_drop = "DROP DATABASE IF EXISTS artists;"
time_table_drop = "DROP DATABASE IF EXISTS time;"

# CREATE TABLES

songplay_table_create = ("""CREATE TABLE IF NOT EXISTS songplays(
    songplay_id SERIAL PRIMARY KEY NOT NULL,
    start_time TIMESTAMP,
    user_id INT,
    level TEXT,
    song_id TEXT,
    artist_id TEXT,
    session_id INT,
    location TEXT,
    user_agent TEXT);
""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS users(
    user_id INT PRIMARY KEY NOT NULL,
    first_name TEXT,
    last_name TEXT,
    gender TEXT,
    level TEXT);
""")

song_table_create = ("""CREATE TABLE IF NOT EXISTS songs(
    song_id TEXT PRIMARY KEY NOT NULL,
    title TEXT,
    artist_id TEXT,
    year INT,
    duration FLOAT);
""")

artist_table_create = ("""CREATE TABLE IF NOT EXISTS artists(
    artist_id TEXT PRIMARY KEY NOT NULL,
    name TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL);
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS time(
    start_time TIMESTAMP PRIMARY KEY NOT NULL,
    hour INT,
    day INT,
    week INT,
    month INT,
    year INT,
    weekday INT);
""")

# INSERT RECORDS

songplay_table_insert = (""" INSERT INTO songplays (
    start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
""")

user_table_insert = ("""INSERT INTO users(
    user_id, first_name, last_name, gender, level)
    VALUES(%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
""")

song_table_insert = ("""INSERT INTO songs(
    song_id, title, artist_id, year, duration)
    VALUES(%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING; 
""")

artist_table_insert = ("""INSERT INTO artists(
    artist_id, name, location, latitude, longitude)
    VALUES(%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING; 
""")


time_table_insert = ("""INSERT INTO time(
    start_time, hour, day, week, month, year, weekday)
    VALUES(%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
""")

# FIND SONGS

# get songid and artistid from song and artist tables
song_select = ("""
    SELECT songs.song_id, artists.artist_id
    FROM songs 
    INNER JOIN artists on songs.artist_id = artists.artist_id
    WHERE songs.title = %s AND artists.name = %s AND songs.duration = %s;
""")

# QUERY LISTS

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]