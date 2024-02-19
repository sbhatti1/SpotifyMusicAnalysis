import psycopg2
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO


# Database connection parameters
db_params = {
    "database": "scrappeddata",
    "user": "postgres",
}


# Function to fetch data for a specific subreddit on a given date
def fetch_subreddit_data(subreddit, start_date, end_date):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query = """
        SELECT
            DATE_TRUNC('day', job_start) AS post_date,
            SUM(posts_added) AS total_posts_added
        FROM
            reddit_job_stats
        WHERE
            subreddit = %s
            AND job_start >= %s::timestamp
            AND job_start < %s::timestamp
        GROUP BY
            post_date
        ORDER BY
            post_date;
    """

    cursor.execute(query, (subreddit, start_date, end_date))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def plotpolitics():
    # Specify the date range (from November 1st to November 16th)
    start_date = datetime(2023, 11, 1).date()
    end_date = datetime(2023, 11, 16).date()
    politics_data_specific_date = fetch_subreddit_data("politics", start_date, end_date)

    # Extract data for plotting
    dates = [row[0] for row in politics_data_specific_date]
    total_posts = [row[1] for row in politics_data_specific_date]

    # Plotting
    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Dates")
    ax1.set_ylabel("No of Posts", color="tab:blue")
    ax1.plot(dates, total_posts, color="tab:blue", label="Total Posts")
    ax1.tick_params(axis="y", labelcolor="tab:blue")


    fig.autofmt_xdate()
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    plt.title("Total Posts per Date")
    img=BytesIO()
    ax1.figure.savefig(img, format='png', bbox_inches='tight')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url

