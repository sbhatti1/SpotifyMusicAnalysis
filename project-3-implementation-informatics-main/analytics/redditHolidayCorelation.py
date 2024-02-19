import psycopg2
import matplotlib.pyplot as plt


def plot_reddit_holiday():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        database="scrappeddata",
        user="postgres",
        
    )
    c = conn.cursor()

    # Lists to store data for plotting
    dates = []
    average_scores = []
    holidays_2023 = [
    '2023-01-01', '2023-01-16', '2023-02-20', '2023-05-29', '2023-07-04', '2023-09-04', '2023-10-09', '2023-11-11', '2023-11-23', '2023-12-25']

    # Iterate through holidays
    for holiday in holidays_2023:
        # Retrieve Spotify data for the given release date
        spotify_query = """
            SELECT a.artist_name, aa.album_name, att.track_name
            FROM spotify_artists a
            JOIN artist_albums aa ON a.artist_id = aa.artist_id
            JOIN artist_top_tracks att ON a.artist_id = att.artist_id
            WHERE aa.album_release_date::text = %s OR att.track_release_date::text = %s
        """
        c.execute(spotify_query, (holiday, holiday))
        spotify_data = c.fetchall()

        # Adjust the Reddit query to search for keywords related to the artist, album, and track
        reddit_query = """
            SELECT *
            FROM reddit_posts p
            JOIN reddit_comments c ON p.post_id = c.post_id
            WHERE 
                (LOWER(p.title) LIKE %s OR LOWER(p.selftext) LIKE %s OR
                LOWER(c.body) LIKE %s OR
                LOWER(p.title) LIKE %s OR LOWER(p.selftext) LIKE %s OR
                LOWER(c.body) LIKE %s OR
                LOWER(p.title) LIKE %s OR LOWER(p.selftext) LIKE %s OR
                LOWER(c.body) LIKE %s)
                AND p.subreddit IN ('music', 'LetsTalkMusic', 'MusicRecommendations', 'Spotify','indieheads','popheads','Coldplay','hiphopheads','rap','Kanye','arcticmonkeys')
        """

        # Iterate Through Spotify Data to Extract Artist, Album, and Track:
        for entry in spotify_data:
            artist = entry[0] if entry[0] else 'N/A'
            album = entry[1] if entry[1] else 'N/A'
            track = entry[2] if entry[2] else 'N/A'

            # Print information for debugging
            print(f"\nHoliday: {holiday}")
            print(f"Spotify Data - Artist: {artist}, Album: {album}, Track: {track}")

            c.execute(reddit_query, (
                f'%{artist}%', f'%{artist}%', f'%{artist}%',
                f'%{album}%', f'%{album}%', f'%{album}%',
                f'%{track}%', f'%{track}%', f'%{track}%'
            ))
            reddit_data = c.fetchall()

            # Calculate average scores for posts and comments
            total_score = 0
            total_count = 0
            for post in reddit_data:
                total_score += post[2]  
                total_count += 1

            average_score = total_score / total_count if total_count > 0 else 0

            # Print information for debugging
            #print(f"\nHoliday: {holiday}")
            #print(f"Spotify Data: {entry}")
            #print("Reddit Data:", reddit_data)
            #print(f"Total Score: {total_score}, Total Count: {total_count}, Average Score: {average_score}")

            # Append data to lists for plotting
            dates.append(holiday)
            average_scores.append(average_score)

    # Plot time series graph
    plt.figure(figsize=(10, 6))
    plt.plot(dates, average_scores, marker='o', linestyle='-', color='b')
    plt.title('Average Scores Over Time')
    plt.xlabel('Release Dates')
    plt.ylabel('Average Scores')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph as a PNG file
    plt.savefig('reddit_data_holiday_corelation.png')

    # Show the graph
    plt.show()

    # Close the database connection
    conn.close()

plot_reddit_holiday()