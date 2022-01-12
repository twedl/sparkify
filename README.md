# Schema for Song Play Analysis 

<!--
Notes:

0. The readme file includes a summary of the project, how to run the python scripts, and an explanation of the files in the repository. Comments are used effectively and each function has a docstring.
1. Discuss the purpose of this database in the context of the startup, Sparkify, and their analytical goals.
3. Provide example queries and results for song play analysis.
-->

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

## ETL Pipeline

The pipeline: 

1. Delete existing `sparkifydb`, if any
2. Create `sparkifydb` with schema described above
3. For each file in `data/song_data`:
  1. Read file into pandas dataframe
  2. Select song information and insert record into `songs` table
  3. Select artist information and insert record into `artists` table
4. For each file in `data/log_data`:
  1. Read file into pandas dataframe
  2. Process: filter dataframe by page equal to "NextSong", convert time from milliseconds to timestamp
  3. Create dataframe of timestamps with specific time units and insert into `time` table
  4. For each songplay record in the dataframe:
    - use artist, song title and song length to query `songs` table to get `song_id`, and `artists` table to get `artist_id`
    - add `song_id` and `artist_id` to the record
    - insert record into `songplays` table

## Example queries

Top 5 songs by number of plays:
```
SELECT COUNT(*) AS total_plays, songs.title, artists.name
FROM songplays
INNER JOIN songs ON songplays.song_id = songs.song_id
INNER JOIN artists ON songplays.artist_id = artists.artist_id
GROUP BY song_id
ORDER BY total_plays DESC
LIMIT 5
```

<!--
## 1.

* business: music streaming. likely goals: time on app, mau, dau, market share, etc.
* analytical goals: report to user; report to management; report to artists;
    - e.g., sparkify wrapped; suggested next songs, artists, playlists, search
    - to management: no. of users using, artists, songs played, popular things
    - to artists: /// idk. which songs are beign played, etc.
## 2.

* Relational database, not document or nosql; for olap.
* purpose: stats, analytical reports, top songs, artists; user behaviour;
* prepare metrics to feed into models and back into app
* considerations: query time, update time, storage, memory, integration
* schema design: star; why? 
    - bad: queries require more joins, possibly hard to incorporate more complex data (e.g., keep track of band members over time? idk. need a better example of this)
    - good: for simple data structures, less repitition means less likely to screw up updates -- only need to update, e.g., user name in one place, not on users table *and also* songplays table
    - example: level is on songplays table and also users table; level can change over time, so maybe historical songplays table records user on free level then switching to paid later; vs. users table that only has one unique level value at the current time

## 3.

Example queries for song play analysis. Simple: total estimated streaming time per user, sorted for top users; same for artists, or songs, etc.

Top 50 songs by number of plays:
```
SELECT COUNT(*) AS total_plays, songs.title, artists.name
FROM songplays
INNER JOIN songs ON songplays.song_id = songs.song_id
INNER JOIN artists ON songplays.artist_id = artists.artist_id
GROUP BY song_id
ORDER BY total_plays DESC
LIMIT 50
```
********************* Not sure total_plays is available as a variable down here, use subquery
maybe, or refer to COUNT(*) ****************
Select top songs for a single user, or find latest song played:

``` 
SELECT start_time, user_id, songs.title, artists.name
FROM songplays
INNER JOIN songs ON songplays.song_id = songs.song_id
INNER JOIN artsts ON songplays.artist_id = artists.artist_id
WHERE user_id = 'XYZ'
ORDER BY start_time DESC
LIMIT 1
```
-->


