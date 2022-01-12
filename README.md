# Schema for Song Play Analysis 

<!--
Notes:

0. The readme file includes a summary of the project, how to run the python scripts, and an explanation of the files in the repository. Comments are used effectively and each function has a docstring.
1. Discuss the purpose of this database in the context of the startup, Sparkify, and their analytical goals.
2. State and justify your database schema design and ETL pipeline.
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

Put schema in here.

## Pipeline


## Example queries

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


