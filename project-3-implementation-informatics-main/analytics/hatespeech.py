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
    c = conn.cursor()
    c.execute("SELECT * FROM reddit_posts where subreddit = 'politics';")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    c.execute("SELECT * FROM reddit_posts where subreddit = 'politics';")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    non_poltics_posts = pd.DataFrame(rows, columns=colnames)
    flagged_posts_df = non_poltics_posts[(non_poltics_posts['title_class'] == 'flag') | (non_poltics_posts['selftext_class'] == 'flag')]
    c.execute("SELECT * FROM reddit_comments where subreddit = 'politics';")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    non_poltics_comments = pd.DataFrame(rows, columns=colnames)
    flagged_comments_df = non_poltics_comments[(non_poltics_comments['body_class'] == 'flag')]
    flagged_post_counts = posts[(posts['title_class'] == 'flag') | (posts['selftext_class'] == 'flag')].count()['post_id']
    non_flagged_post_counts = posts.count()['post_id'] - flagged_post_counts

    flagged_comment_counts = comments[(comments['body_class'] == 'flag')].count()['comment_id']
    non_flagged_comment_counts = comments.count()['comment_id'] - flagged_comment_counts
    
    # Calculate the ratios
    post_ratio = flagged_post_counts / non_flagged_post_counts
    comment_ratio = flagged_comment_counts / non_flagged_comment_counts

    # Create a bar plot
    # ax = plt.bar(x=['Posts', 'Comments'], height=[post_ratio, comment_ratio])
    # plt.title('Ratio of Flagged to Non-Flagged posts and comments')
    # plt.ylabel('Flagged/Non-Flagged')
    # plt.ylim(0, 0.025)  # Set the y-axis scale to be from 0 to 1
    x = ['Posts', 'Comments']
    height = [post_ratio, comment_ratio]

    fig, ax = plt.subplots()
    ax.bar(x, height)
    ax.set_title('Ratio of Flagged to Non-Flagged posts and comments')
    ax.set_ylabel('Flagged/Non-Flagged')
    ax.set_ylim(0, 0.025)
    plt.savefig("hatespeech.png")
    plt.show()
    img=BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    hate_speech = base64.b64encode(img.getvalue()).decode('utf8')

    conn.close()
    return hate_speech

# print(fetchdata())
