import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    database="scrappeddata",
    user="postgres",
    
)
c = conn.cursor()

# Create a table to store combined information
combined_table_query = '''
    CREATE TABLE IF NOT EXISTS combined_data (
        artist_name TEXT PRIMARY KEY,
        avg_track_popularity REAL,
        avg_artist_popularity REAL,
        composite_score REAL,
        avg_post_score REAL,
        avg_comment_score REAL
    );
'''
c.execute(combined_table_query)

# Summary query with composite score calculation for Spotify data
summary_query = '''
    SELECT
        sa.artist_id,
        sa.artist_name,
        COALESCE(AVG(CAST(att.track_popularity AS INTEGER)), 0) AS avg_track_popularity,
        COALESCE(AVG(sa.artist_popularity), 0) AS avg_artist_popularity,
        (COALESCE(AVG(CAST(att.track_popularity AS INTEGER)), 0) + COALESCE(AVG(sa.artist_popularity), 0)) AS composite_score
    FROM
        spotify_artists sa
    LEFT JOIN
        artist_top_tracks att ON sa.artist_id = att.artist_id
    GROUP BY
        sa.artist_id, sa.artist_name
    ORDER BY
        composite_score DESC
    LIMIT 10
'''

# Execute the query and fetch data
c.execute(summary_query)
top_artists_data = c.fetchall()

# Create a DataFrame for the top artists from Spotify data
top_artists_df = pd.DataFrame(top_artists_data, columns=[
    'Artist ID', 'Artist Name', 'Average Track Popularity',
    'Average Artist Popularity', 'Composite Score'
])

# Create a dictionary to store the average scores for each artist from Reddit data
average_scores = {}

# Iterate over each artist from Spotify data
for index, row in top_artists_df.iterrows():
    artist = row['Artist Name']
    # Construct a query to find posts mentioning the artist
    post_query = f'''
        SELECT AVG(score) as avg_post_score
        FROM reddit_posts
        WHERE (LOWER(title) LIKE '%{artist.lower()}%' OR LOWER(selftext) LIKE '%{artist.lower()}%')
         AND subreddit IN ('music', 'LetsTalkMusic', 'MusicRecommendations', 'Spotify');
    '''
    
    # Execute the post query
    c.execute(post_query)
    avg_post_score = c.fetchone()[0] or 0  # If no matching posts, set the average score to 0
    
    # Construct a query to find comments mentioning the artist
    comment_query = f'''
        SELECT AVG(score) as avg_comment_score
        FROM reddit_comments
        WHERE (LOWER(body) LIKE '%{artist.lower()}%')
        AND subreddit IN ('music', 'LetsTalkMusic', 'MusicRecommendations', 'Spotify');
    '''
    
    # Execute the comment query
    c.execute(comment_query)
    avg_comment_score = c.fetchone()[0] or 0  # If no matching comments, set the average score to 0
    
    # Store the average scores in the dictionary
    average_scores[artist] = {'avg_post_score': avg_post_score, 'avg_comment_score': avg_comment_score}
    
    # Insert the combined data into the table
    combined_insert_query = '''
        INSERT INTO combined_data (artist_name, avg_track_popularity, avg_artist_popularity, composite_score, avg_post_score, avg_comment_score)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (artist_name) DO UPDATE 
        SET avg_track_popularity = EXCLUDED.avg_track_popularity,
            avg_artist_popularity = EXCLUDED.avg_artist_popularity,
            composite_score = EXCLUDED.composite_score,
            avg_post_score = EXCLUDED.avg_post_score,
            avg_comment_score = EXCLUDED.avg_comment_score;
    '''
    c.execute(combined_insert_query, (artist, row['Average Track Popularity'], row['Average Artist Popularity'], row['Composite Score'], avg_post_score, avg_comment_score))

# Commit the changes to the database
conn.commit()

combined_table_query = 'SELECT * FROM combined_data;'
combined_df = pd.read_sql(combined_table_query, conn)

# Set display options for better printing
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.width', None)  # Auto-expand width to display data

# Print the pretty table
# print("Combined Table:")
# print(combined_df.to_string(index=False))

# Save the combined table as an image
plt.figure(figsize=(15, 10))
plt.table(cellText=combined_df.values, colLabels=combined_df.columns, cellLoc='center', loc='center', colColours=['#f2f2f2']*combined_df.shape[1])
plt.axis('off')  # Turn off axis
#plt.title('Combined Data Table')
plt.savefig('top10ArtistsTable.png')

# Close the database connection
conn.close()
