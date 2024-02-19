import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import psycopg2
from io import BytesIO
import base64

def spotifyholidaycorr():
    conn = psycopg2.connect(
        database="scrappeddata",
        user="postgres",
        
    )
    img=BytesIO()
    c = conn.cursor()

    # Fetch relevant data for the year 2023
    c.execute('''
        SELECT sa.artist_name, sa.artist_popularity, aa.album_release_date
        FROM spotify_artists sa
        LEFT JOIN artist_albums aa ON sa.artist_id = aa.artist_id
        WHERE aa.album_release_date BETWEEN '2023-01-01' AND '2023-12-31'
    ''')
    data = c.fetchall()

    # Create a DataFrame
    df = pd.DataFrame(data, columns=['artist_name', 'artist_popularity', 'album_release_date'])

    # Convert 'album_release_date' to datetime
    df['album_release_date'] = pd.to_datetime(df['album_release_date'], errors='coerce')

    # Define the holidays for 2023
    holidays_2023 = [
    '2023-01-01', '2023-01-16', '2023-02-20', '2023-05-29', '2023-07-04', '2023-09-04', '2023-10-09', '2023-11-11', '2023-11-23', '2023-12-25']


    # Include dates one day before and after the holidays
    extended_holidays = pd.to_datetime(holidays_2023).to_series()
    extended_holidays = extended_holidays - pd.to_timedelta(1, unit='d') 
    extended_holidays = pd.concat([extended_holidays, extended_holidays + pd.to_timedelta(1, unit='d')])


    # Create a new column 'is_holiday' based on album release date
    df['is_holiday'] = df['album_release_date'].dt.floor('d').isin(extended_holidays)

    # Group by release date and calculate average artist popularity
    time_series_data = df.groupby(['album_release_date', 'is_holiday'])['artist_popularity'].mean().reset_index()

    # Plotting
    plt.figure(figsize=(15, 8))

    # Time series plot for artist popularity on holidays vs. non-holidays
    sns.lineplot(x='album_release_date', y='artist_popularity', hue='is_holiday', data=time_series_data)
    plt.title('Time Series of Artist Popularity on Holidays vs. Non-Holidays in 2023')
    plt.xlabel('Album Release Date')
    plt.ylabel('Average Artist Popularity')

    # Save the figure before showing it
    plt.savefig('spotify_data_holiday_corelation.png')
    plt.show()

    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    spotify_url = base64.b64encode(img.getvalue()).decode('utf8')

    # Show the plot
    # Close the database connection
    conn.close()
    return spotify_url
