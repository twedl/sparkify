# DROP TABLES

songplay_table_drop = "DROP DATABASE IF EXISTS songplays;"
user_table_drop = "DROP DATABASE IF EXISTS users;"
song_table_drop = "DROP DATABASE IF EXISTS songs;"
artist_table_drop = "DROP DATABASE IF EXISTS artists;"
time_table_drop = "DROP DATABASE IF EXISTS time;"

# CREATE TABLES

songplay_table_create = ("""CREATE TABLE IF NOT EXISTS songplays(
    songplay_id BIGSERIAL,
    start_time TIMESTAMP,
    user_id INT,
    level VARCHAR(4),
    song_id VARCHAR(20),
    artist_id VARCHAR(20),
    session_id INT,
    location VARCHAR(100),
    user_agent VARCHAR(100));
""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS users(
    user_id INT,
    first_name VARCHAR(25),
    last_name VARCHAR(25),
    gender VARCHAR(15),
    level VARCHAR(4));
""")

song_table_create = ("""CREATE TABLE IF NOT EXISTS songs(
    song_id VARCHAR(20),
    title VARCHAR(100),
    artist_id VARCHAR(20),
    year INT,
    duration REAL);
""")

artist_table_create = ("""CREATE TABLE IF NOT EXISTS artists(
    artist_id VARCHAR(20),
    artist_name VARCHAR(100),
    artist_location VARCHAR(100),
    artist_latitude REAL,
    artist_longitude REAL);
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS time(
    start_time TIMESTAMP,
    hour INT,
    day INT,
    week INT,
    month INT,
    year INT,
    weekday INT);
""")

# INSERT RECORDS

songplay_table_insert = (""" INSERT INTO songplays (all colnames) VALUES (%s, %s, %s * num of cols...)
""")

user_table_insert = ("""INSERT INTO users(user_id, first_name, last_name, gender, level)
    VALUES(%s, %s, %s, %s, %s); 
""")

song_table_insert = ("""INSERT INTO songs(song_id, title, artist_id, year, duration)
    VALUES(%s, %s, %s, %s, %s); 
""")

artist_table_insert = ("""INSERT INTO artists(
    artist_id, artist_name, artist_location, artist_latitude, artist_longitude)
    VALUES(%s, %s, %s, %s, %s); 
""")


# time here, might need to add the timestamp to the thing
time_table_insert = ("""INSERT INTO time(
    start_time, hour, day, week, month, year, weekday)
    VALUES(%s, %s, %s, %s, %s, %s, %s);
""")

# FIND SONGS

song_select = (""" aahahh i see , i need to select from artist and song tables, not songplay
""")

# QUERY LISTS

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]