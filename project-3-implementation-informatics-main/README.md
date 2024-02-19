[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/4OC8STES)



## Analysis of Popularity of Artists on Spotify

## Description

The project collects real-time data from two data sources: Reddit, and Spotify. For Reddit, it collects data from various music subreddit threads using Reddit API. For Spotify, using Spotify API data is collected for artists, their albums, top tracks and their features. The Reddit job is scheduled for every 5 mins for a single subreddit whereas the Spotify one is scheduled ever 10 hours. The data is stored in PostgresSQL database.

Using the data collection, we have performed two analysis and tried to answer one research question:
* Analysis
    * Top 10 artists for a particular year
    * Sentiment Analysis to justify the popularity of artist/track
* Research Question
    * Correlation of song popularity with song features


## Tech-stack

* `python` - The project is developed and tested using python. 
* `Flask` - A micro web framework for Python.
* `matplotlib` - A plotting library for the Python programming language and its numerical mathematics extension NumPy.
* `nltk` - A natural language processing library that provides tools for working with human language data.
* `pandas` -A powerful data manipulation and analysis library for Python.
* `psycopg2-binary` - A PostgreSQL adapter for Python, providing a fast and efficient way to interact with PostgreSQL databases.
* `requests` - A simple HTTP library for making requests to web services.
* `seaborn` - A statistical data visualization library based on Matplotlib, providing a high-level interface for drawing attractive and informative statistical graphics.

## How to run the project?

1. Install requirements.txt to install all the dependencies added in the remote server: 
```
   pip install -r requirements.txt
```
2. To launch the Flask application, run
```
   python3 FlaskServer.py
```



