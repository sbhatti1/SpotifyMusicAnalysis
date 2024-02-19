import requests
import random
import string
import psycopg2
import json
import time
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt


sid = SentimentIntensityAnalyzer()
nltk.download('vader_lexicon')



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

merged_df_title = pd.merge(posts, tracks, left_on='title', right_on='track_name', how='inner')

# Merge based on track_name in selftext
merged_df_selftext = pd.merge(posts, tracks, left_on='selftext', right_on='track_name', how='inner')

# Concatenate the two merged DataFrames
merged_df = pd.concat([merged_df_title, merged_df_selftext])

# Drop duplicate rows based on post_id
merged_df = merged_df.drop_duplicates(subset='post_id')

# Display the resulting DataFrame
print(merged_df)

sentiment_scores=[]
for index, row in merged_df.iterrows():
    text = row['track_name'] + " " + row['title'] + " " + row['selftext']
    ss = sid.polarity_scores(text)
    sentiment_scores.append(row['track_name'])
    sentiment_scores.append(ss)

text_entries = []
compound_scores = []

for i in range(0, len(sentiment_scores), 2):  # Assuming the data structure alternates between text and sentiment scores
    text_entries.append(sentiment_scores[i])
    compound_scores.append(sentiment_scores[i+1]['compound'])

# Create a bar plot
plt.figure(figsize=(10, 6))
plt.bar(range(len(text_entries)), compound_scores, color='skyblue')
plt.xlabel('Text Entry Index')
plt.ylabel('Compound Sentiment Score')
plt.title('Sentiment Analysis Results')
plt.xticks(range(len(text_entries)), text_entries, rotation=90)
plt.tight_layout()
plt.savefig("sentiment_analysis_track")
plt.show()

