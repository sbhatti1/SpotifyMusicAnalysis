import base64
from io import BytesIO
import re
from flask import Flask, render_template, request
from matplotlib import pyplot as plt
import psycopg2
import pandas as pd

'''app = Flask(__name__)'''

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    database="scrappeddata",
    user="postgres",
    
)
c = conn.cursor()

#@app.route('/')
#def index():
    #return render_template('index.html')

'''@app.route('/index1')
def index1():
    return render_template('index1.html')

@app.route('/result', methods=['POST'])'''
def result():
    user_input_year = request.form['year']
    #app.logger.debug(f"User Input Year: {user_input_year}")
    
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
        WHERE
            SUBSTRING(att.track_release_date FROM 1 FOR 4) = %s
        GROUP BY
            sa.artist_id, sa.artist_name
        ORDER BY
            composite_score DESC
        LIMIT 10
    '''

    c.execute(summary_query, (user_input_year,))
    top_artists_data = c.fetchall()
    if not top_artists_data:
        # Set a variable to indicate no data
        no_data_message = "No data available for the year {user_input_year}"
        #return no_data_message
    
    # Convert the result to a list of dictionaries for rendering in HTML
    top_artists = [{'artist_name': row[1], 'composite_score': row[4]} for row in top_artists_data]
    
    top_artists_df = pd.DataFrame(top_artists_data, columns=[
    'Artist ID', 'Artist Name', 'Average Track Popularity',
    'Average Artist Popularity', 'Composite Score'
    ])
    
    c.execute("SELECT * FROM reddit_posts WHERE subreddit IN ('music', 'LetsTalkMusic', 'MusicRecommendations', 'Spotify');")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    posts = pd.DataFrame(rows, columns=colnames)
    c.execute("SELECT * FROM reddit_comments WHERE subreddit IN ('music', 'LetsTalkMusic', 'MusicRecommendations', 'Spotify');")
    rows = c.fetchall()
    colnames = [column[0] for column in c.description]
    comments = pd.DataFrame(rows, columns=colnames)
    
    artist_counts = {}
    
    for artist in top_artists_df.values:
        posts_count, comments_count = post_comments(posts,comments,artist[1])
        artist_counts[artist[1]] = {'posts_count': posts_count, 'comments_count': comments_count}
        
    #print(artist_counts)
    artist_counts_df = pd.DataFrame.from_dict(artist_counts, orient='index')
    
    conn.commit()

    # Plot a horizontal bar graph
    fig, ax = plt.subplots(figsize=(10, 6))

    if not artist_counts_df.empty:
        # Sort DataFrame by the sum of posts and comments counts
        artist_counts_df['total_mentions'] = artist_counts_df['posts_count'] + artist_counts_df['comments_count']
        sorted_df = artist_counts_df.sort_values(by='total_mentions', ascending=False)

        # Plot the horizontal bar chart
        artist_counts_df.plot(kind='barh', y=['posts_count', 'comments_count'], stacked=True, ax=ax)
        ax.set_xlabel('Number of Mentions')
        ax.set_ylabel('Artist')
        ax.set_title('Mentions of Artists in Posts and Comments')
        plt.savefig("Artist mentions in reddit.png")
        
        img = BytesIO()
        ax.figure.savefig(img, format='png', bbox_inches='tight')
        plt.close()
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    else:
        # Handle the case when there is no data
        plot_url = None
    #return render_template('result.html', year=user_input_year, plot_url=plot_url)
    return plot_url
def post_comments(posts,comments,artist_name):
    artist_name_escaped = re.escape(artist_name)

    # Check mentions in titles and self-text for posts
    posts_mentions = posts[posts['title'].str.contains(artist_name_escaped, case=False, na=False) |
                          posts['selftext'].str.contains(artist_name_escaped, case=False, na=False)]

    # Check mentions in comments
    comments_mentions = comments[comments['body'].str.contains(artist_name_escaped, case=False, na=False)]

    return len(posts_mentions), len(comments_mentions)
    
'''if __name__ == '__main__':
    app.run(debug=True)'''
