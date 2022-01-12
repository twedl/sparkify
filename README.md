# Schema for Song Play Analysis 

Notes:

0. The readme file includes a summary of the project, how to run the python scripts, and an explanation of the files in the repository. Comments are used effectively and each function has a docstring.
1. Discuss the purpose of this database in the context of the startup, Sparkify, and their analytical goals.
2. State and justify your database schema design and ETL pipeline.
3. Provide example queries and results for song play analysis.

This repo has python code and sql queries for a data pipeline that creates analytical database for song play analysis at Sparkify. Given data on songs and data on song plays logged from the service, this constructs a postgresql database with schema optimized for song play analysis. Analysis could include summary statistics for song plays by user type, time, artist, and location, among many other possibilities.

## Setup

### Prerequisites

PostgreSQL (tested on version 14.1 on MacOS 12.1), with default database studentdb, with user student / password student. To create this default, run:

```
createdb --host=127.0.0.1 --username=student --password studentdb
```
then type in the `student` in the password prompt. Test the connection by running
```
psql --host=127.0.0.1 --dbname=student --username=student --password
```
and type `student` in the password prompt again. You should see a message like `You are now connected to database "studentdb" as user "student" on host "127.0.0.1" at post "5432"`.

### Install

git clone, environment, pip install from requirements.txt.

To set up the scripts, first clone the git repo:
```
git clone git@github.com:twedl/sparkify.git
cd sparkify
```
Then activate a python virtual environment:
```
python3 -m venv env 
```
Then install all python packages listed in `requirements.txt`:
```
pip install -r requirements.txt
```

### Run
then create_tables.py, then etl.py.

## Data

song data in. structure is...etc.

log data in: etc.

## Schema

Put schema in here.

## Pipeline

gz.

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



