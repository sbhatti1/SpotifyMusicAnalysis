import requests
import random
import string
import psycopg2
import json
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def fetchdata():
    db_settings = {
        "dbname": 'scrappeddata',
        "user": 'postgres',
    }

    conn = psycopg2.connect(**db_settings)
    c = conn.cursor()
    c.execute("SELECT * FROM reddit_posts;")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    posts = pd.DataFrame(rows, columns=colnames)
    c.execute("SELECT * FROM reddit_comments;")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    comments = pd.DataFrame(rows, columns=colnames)
    c.execute("SELECT * FROM spotify_artists;")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    artists = pd.DataFrame(rows, columns=colnames)
    c.execute("SELECT * FROM artist_albums;")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    albums = pd.DataFrame(rows, columns=colnames)
    c.execute("SELECT * FROM artist_top_tracks;")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    tracks = pd.DataFrame(rows, columns=colnames)
    c.execute("SELECT * FROM track_audio_features;")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    audio_features = pd.DataFrame(rows, columns=colnames)
    return tracks,posts,comments,audio_features,albums,artists,conn
 


def spotifydata():
    img=BytesIO()
    tracks, posts, comments, audio_features, albums, artists,conn = fetchdata()
    tracks_count =len(tracks)
    artists_count = len(artists)
    albums_count = len(albums)
    audio_features_count = len(audio_features)

    # Create a bar plot
    df_names = ['Tracks', 'Artists', 'Albums', 'Audio Features']
    counts = [tracks_count, artists_count, albums_count, audio_features_count]
    x_values = range(len(df_names))

    # Create a figure and axis object using Matplotlib's object-oriented approach
    fig, ax = plt.subplots()

    # Create a bar plot using the axis object
    ax.bar(x=x_values, height=counts, color=['blue', 'orange', 'green', 'red'])

    # Set the x-axis labels and tick positions
    ax.set_xticks(x_values)
    ax.set_xticklabels(df_names)
    plt.title('Data Collected for Spotify')
    plt.ylabel('Count')
    plt.savefig("spotify_data_collection.png")
    plt.show()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    spotify_data = base64.b64encode(img.getvalue()).decode('utf8')

    # Show the plot
    # Close the database connection
    conn.close()
    return spotify_data

def redditdata():
    img=BytesIO()
    tracks, posts, comments, audio_features, albums, artists,conn = fetchdata()
    subreddits_of_interest = ['music', 'LetsTalkMusic', 'MusicRecommendations', 'indieheads', 'popheads', 'Spotify',
                           'MusicRecommendations', 'kpop', 'TaylorSwift', 'Coldplay', 'hiphopheads', 'rap', 'Kanye',
                           'arcticmonkeys', 'Eminem', 'politics']

    # Filter posts DataFrame for specified subreddits
    posts_subreddit_counts = posts[posts['subreddit'].isin(subreddits_of_interest)]['subreddit'].value_counts()

    # Filter comments DataFrame for specified subreddits
    comments_subreddit_counts = comments[comments['subreddit'].isin(subreddits_of_interest)]['subreddit'].value_counts()
    combined_counts = pd.concat([posts_subreddit_counts, comments_subreddit_counts], axis=1, keys=['Posts', 'Comments'])

    # Convert index to string
    combined_counts.index = combined_counts.index.astype(str)

    # Create a bar plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # Bar plot for posts
    axes[0].bar(posts_subreddit_counts.index, posts_subreddit_counts, color='skyblue')
    axes[0].set_title('Posts Collected for each subreddit')
    axes[0].set_xlabel('Subreddits')
    axes[0].set_ylabel('Count')
    axes[0].set_xticklabels(posts_subreddit_counts.index, rotation=45, ha='right')  # Set rotation here

    # Bar plot for comments
    axes[1].bar(comments_subreddit_counts.index, comments_subreddit_counts, color='lightcoral')
    axes[1].set_title('Comments Collected for each subreddit')
    axes[1].set_xlabel('Subreddits')
    axes[1].set_ylabel('Count')
    axes[1].set_xticklabels(comments_subreddit_counts.index, rotation=45, ha='right')  # Set rotation here

    plt.tight_layout()
    plt.savefig("reddit_data_collection.png")
    plt.show()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    reddit_data = base64.b64encode(img.getvalue()).decode('utf8')

    # Show the plot
    # Close the database connection
    conn.close()
    return reddit_data
