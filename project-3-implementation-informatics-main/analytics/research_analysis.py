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
 


def heat_map():
    img=BytesIO()
    tracks, posts, comments, audio_features, albums, artists,conn = fetchdata()
    
    merged_df = pd.merge(tracks, audio_features, on='track_id')

    merged_df['track_popularity'] = pd.to_numeric(merged_df['track_popularity'], errors='coerce')
        # Select relevant columns for correlation analysis
    selected_columns = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'track_popularity']

    # Create a correlation matrix
    correlation_matrix = merged_df[selected_columns].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix')
    plt.savefig("heatmap.png")
    plt.show()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    heatmap_data = base64.b64encode(img.getvalue()).decode('utf8')

    # Close the database connection
    conn.close()
    return heatmap_data


def corr_track_popularity():
    img=BytesIO()
    tracks, posts, comments, audio_features, albums, artists,conn = fetchdata()
    merged_df = pd.merge(tracks, audio_features, on='track_id')

    merged_df['track_popularity'] = pd.to_numeric(merged_df['track_popularity'], errors='coerce')
    # Select relevant columns for correlation analysis
    selected_columns = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'track_popularity']

    # Create a correlation matrix
    correlation_matrix = merged_df[selected_columns].corr()

    plt.figure(figsize=(10, 6))
    correlation_with_popularity = correlation_matrix['track_popularity'].drop('track_popularity')  # Exclude popularity itself
    correlation_with_popularity.sort_values().plot(kind='bar', color='skyblue')
    plt.title('Correlation with Track Popularity')
    plt.xlabel('Audio Features')
    plt.ylabel('Correlation Coefficient')
    plt.savefig("Correlation_with_Track_popularity.png")
    plt.show()
    
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    corr_track = base64.b64encode(img.getvalue()).decode('utf8')

    # Show the plot
    # Close the database connection
    conn.close()
    return corr_track

# print(corr_track_popularity())
