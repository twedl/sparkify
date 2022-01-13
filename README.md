# Schema for Song Play Analysis 

This repo has python code and sql queries for a data pipeline that creates analytical database for song play analysis at Sparkify. Given data on songs and data on song plays logged from the service, this constructs a postgresql database with schema optimized for song play analysis. Analysis could include summary statistics for song plays by user type, time, artist, and location, among many other possibilities.

## Setup

### Prerequisites

PostgreSQL (tested on version 14.1 on MacOS 12.1), with default database studentdb, with user student / password student. To create this default, run this in your terminal:

```
createdb --host=127.0.0.1 --username=student --password studentdb
```
then type in the `student` in the password prompt. Test the connection by running
```
psql --host=127.0.0.1 --dbname=student --username=student --password
```
and type `student` in the password prompt again. You should see a message like `You are now connected to database "studentdb" as user "student" on host "127.0.0.1" at post "5432"`.

### Install

To set up the scripts, first clone the git repo:
```
git clone git@github.com:twedl/sparkify.git
cd sparkify
```
Then create and activate a python virtual environment (for bash/zsh):
```
python3 -m venv env 
source env /bin/activate
```
Then install all python packages listed in `requirements.txt`:
```
pip install -r requirements.txt
```

### Files

* `data`: folder that contains song data (`song_data`) and log data (`log_data`) for ingestion into the database
* `sql_queries.py`: SQL queries stored as Python strings for execution with `psycopg2` in the scripts `create_tables.py` and `etl.py`
* `create_tables.py`: script to delete (if exists) and re-create `sparkifydb` database in PostgreSQL
* `etl.py`: script to ingest all the data in `data` and insert into correct tables in `sparkifydb`

### Run

To create the database and insert the data into tables, run:
```
python create_tables.py && python etl.py
```

Important:
- the default database `studentdb` must exist with user/password `student/student`
- `create_tables.py` drops any existing `sparkifydb` database and recreates it

After running this, the `sparkifydb` database should exist with tables `songplays`, `users`, `songs`, `artists`, and `time`. To see and test the database in PostgreSQL, connect to it by running:
```
psql --host=127.0.0.1 --dbname=sparkifydb --username=student --password
```

## Input Data

Song data:
```
> gunzip -c data/song_data/A/A/A/TRAAAAW128F429D538.json.gz | jq .
{
  "num_songs": 1,
  "artist_id": "ARD7TVE1187B99BFB1",
  "artist_latitude": null,
  "artist_longitude": null,
  "artist_location": "California - LA",
  "artist_name": "Casual",
  "song_id": "SOMZWCG12A8C13C480",
  "title": "I Didn't Mean To",
  "duration": 218.93179,
  "year": 0
}
```

Log data:
```
> gunzip -c data/log_data/2018/11/2018-11-01-events.json.gz | jq --slurp '.[1]'
{
  "artist": null,
  "auth": "Logged In",
  "firstName": "Kaylee",
  "gender": "F",
  "itemInSession": 0,
  "lastName": "Summers",
  "length": null,
  "level": "free",
  "location": "Phoenix-Mesa-Scottsdale, AZ",
  "method": "GET",
  "page": "Home",
  "registration": 1540344794796,
  "sessionId": 139,
  "song": null,
  "status": 200,
  "ts": 1541106106796,
  "userAgent": "\"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36\"",
  "userId": "8"
}
```

## Schema

`sparkifydb` uses a star schema optimized for song play analytical queries. It includes the following tables (fact table populated from files located in `data/log_data`, dimension tables populated with information in `data/song_data`):

The fact table is `songplays` (populated from files located in `data/log_data`, with columns `song_id` from `songs` table and `artist_id` from `artist` table)
- `songplays` (fact table); columns: 
  - `songplay_id`,`start_time`,`user_id`,`level`,`song_id`,`artist_id`,`session_id`,`location`,`user_agent`

The dimensions tables are populated with data from the song information in `data/song_data`. They include the following tables:

- `users`: users in the app, with columns: 
  - `user_id`,`first_name`,`last_name`,`gender`,`level`
- `songs`: songs in the music database, with columns:
  - `song_id`,`title`,`artist_id`,`year`,`duration`
- `artists`: artists in the music database, with columns:
  - `artist_id`,`name`,`loction`,`latitude`,`longitude`
- `time`: timestamps of records in `songplays` broken down into specific units
  - `start_time`,`hour`,`day`,`week`,`month`,`year`,`weekday`

This star schema was chosen to reduce redundency in the database; this reduces storage required as well as reducing the chance that errors are introduced because song and artist information can be updated in one table only. The presence of `level` in both the `songplays` table and `users` table represents the fact that level can change over time; `level` in `users` is the current subscription level (paid or free) of the user, but that may not reflect the subscription level the user had when they played the song. The schema trades-off the confusing nature of a database that is not completely normalized for the accuracy of historical subscription levels. This is important for analytical queries of streaming behaviour and will inform the direction of the business. In the future, the schema should be changed to reflect highlight the difference in `levels`, by, e.g., renaming `level` to `level_historical` in the `songplays` table, or `level_current` in the `users` table.

Using the star schema may increase query time if every query requires joining the dimension tables to the fact tables to produce results. In this case, future schemas may include commonly required dimensions into the fact table itself. However, this increases the likelihood of errors introduced by updating dimensions in the dimension table but not the fact table, or vice versa.

## ETL Pipeline

The pipeline: 

1. Delete existing `sparkifydb` database, if any
2. Create `sparkifydb` database and tables `songplays`, `users`, `songs`, `artists`, and `time` with schema described above
3. For each file in `data/song_data`:
  1. Read file into pandas dataframe
  2. Select song information and insert record into `songs` table
  3. Select artist information and insert record into `artists` table
4. For each file in `data/log_data`:
  1. Read file into pandas dataframe
  2. Process: filter dataframe by page equal to "NextSong", convert time from milliseconds to timestamp
  3. Create dataframe of timestamps with specific time units and insert into `time` table
  4. Create dataframe of users from logs, deduplicate and insert into `users` table (updating `level` if there is a conflict with a previous record)
  5. For each songplay record in the dataframe:
    - use artist, song title and song length to query `songs` table to get `song_id`, and `artists` table to get `artist_id`
    - add `song_id` and `artist_id` to the record
    - insert record into `songplays` table

## Example queries

Top 5 songs by number of plays:
```
sparkifydb=> SELECT COUNT(*) AS total_plays, songplays.songplay_id, songs.title, artists.name
FROM songplays
LEFT JOIN songs ON songplays.song_id = songs.song_id
LEFT JOIN artists ON songplays.artist_id = artists.artist_id
GROUP BY songplays.songplay_id, songs.title, artists.name
ORDER BY total_plays DESC
LIMIT 5;
 total_plays | songplay_id | title | name
-------------+-------------+-------+------
           1 |        2734 |       |
           1 |        3066 |       |
           1 |         733 |       |
           1 |        6412 |       |
           1 |        1279 |       |
(5 rows)
```
Each song in the log was only played once during this time period.

Number of plays per hour of the day:
```
sparkifydb=> SELECT count(*) as count, time.hour
FROM songplays
INNER JOIN time ON songplays.start_time = time.start_time
GROUP BY time.hour
ORDER BY time.hour;
 count | hour
-------+------
   155 |    0
   154 |    1
   117 |    2
   109 |    3
   136 |    4
   162 |    5
   183 |    6
   179 |    7
   207 |    8
   270 |    9
   312 |   10
   336 |   11
   308 |   12
   324 |   13
   432 |   14
   477 |   15
   542 |   16
   494 |   17
   498 |   18
   367 |   19
   360 |   20
   280 |   21
   217 |   22
   201 |   23
(24 rows)
```
Song plays drop overnight and peak at hour 16 / 4:00pm.