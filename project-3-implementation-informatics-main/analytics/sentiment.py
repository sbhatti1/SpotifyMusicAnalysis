import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import sys
import base64
from io import BytesIO

db_settings = {
    "dbname": "scrappeddata",
    "user": "postgres",
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

c.execute("SELECT * FROM sentiment_posts;")
rows = c.fetchall()
colnames = [column[0] for column in c.description]
sentiment_posts = pd.DataFrame(rows, columns=colnames)

c.execute("SELECT * FROM sentiment_comments;")
rows = c.fetchall()
colnames = [column[0] for column in c.description]
sentiment_comments = pd.DataFrame(rows, columns=colnames)

merged_posts = pd.merge(posts, sentiment_posts, on="post_id", how="inner")
merged_comments = pd.merge(comments, sentiment_comments, on="comment_id", how="inner")


def calculate_sentiment(input_type, track_name):
    posts_mentions = merged_posts[
        merged_posts["title"].str.contains(track_name, case=False, na=False)
        | merged_posts["selftext"].str.contains(track_name, case=False, na=False)
    ]

    # Check mentions in comments
    comments_mentions = merged_comments[
        merged_comments["body"].str.contains(track_name, case=False, na=False)
    ]

    # Classify posts as negative, positive, or neutral based on compound score
    posts_mentions["title_sentiment"] = posts_mentions["title_compound"].apply(
        lambda x: "negative" if x < 0 else ("positive" if x > 0 else "neutral")
    )

    posts_mentions["selftext_sentiment"] = posts_mentions["selftext_compound"].apply(
        lambda x: "negative" if x < 0 else ("positive" if x > 0 else "neutral")
    )

    comments_mentions["body_sentiment"] = comments_mentions["body_compound"].apply(
        lambda x: "negative" if x < 0 else ("positive" if x > 0 else "neutral")
    )
    # Count the number of negative, positive, and neutral posts
    sentiment_counts = (
        posts_mentions["selftext_sentiment"].value_counts()
        + posts_mentions["title_sentiment"].value_counts()
        + comments_mentions["body_sentiment"].value_counts()
    )

    # Display the results
    print("Average Title Sentiment:", posts_mentions["title_compound"].mean())
    print("Average Selftext Sentiment:", posts_mentions["selftext_compound"].mean())
    print("Average Comment Sentiment:", comments_mentions["body_compound"].mean())
    print(
        "Average Overall Sentiment:",
        (
            comments_mentions["body_compound"].mean()
            + posts_mentions["title_compound"].mean()
            + posts_mentions["selftext_compound"].mean()
        )
        / 3,
    )
    print("\nSentiment Counts:")
    print(sentiment_counts)

    # Assuming artist_popularity is the popularity from Spotify

    if input_type == "artist":
        filtered_track = artists[artists["artist_name"] == track_name]
        artist_popularity = filtered_track["artist_popularity"]
    else:
        filtered_track = tracks[tracks["track_name"] == track_name]
        artist_popularity = filtered_track["track_popularity"]

    # Sample data
    fig1 = plt.figure(figsize=(10, 6))
    x_labels = [
        "Average Post Title Sentiment",
        "Average Post Description Sentiment",
        "Average Comment Sentiment",
        "Average Overall Sentiment",
    ]
    x_values = [
        posts_mentions["title_compound"].mean(),
        posts_mentions["selftext_compound"].mean(),
        comments_mentions["body_compound"].mean(),
        (
            comments_mentions["body_compound"].mean()
            + posts_mentions["title_compound"].mean()
            + posts_mentions["selftext_compound"].mean()
        )
        / 3,
    ]

    y_labels = ["artist_popularity"]
    y_value = int(artist_popularity.values[0])
    y_values = [
        y_value,
        y_value,
        y_value,
        y_value,
    ]  # Adjust this value based on your actual data

    # Colors for each label
    colors = ["blue", "green", "orange", "red"]

    # Marker style for "Average Overall Sentiment"
    markers = ["o", "o", "o", "o"]

    # Marker size
    marker_sizes = [50, 50, 50, 100]  # Adjust the size for each marker as needed

    # Quadrant lines
    quadrant_lines = {"x": [0, 0], "y": [50, 50]}

    # Create a scatter plot
    for i in range(len(x_labels)):
        plt.scatter(
            x_values[i],
            y_values[0],
            label=x_labels[i],
            color=colors[i],
            marker=markers[i],
            s=marker_sizes[i],
        )

    # Draw lines from axes to "Average Overall Sentiment" point
    plt.plot(
        [x_values[3], x_values[3]], [y_values[3], 50], color="red", linestyle="--"
    )  # Line from x-axis
    plt.plot(
        [0, x_values[3]], [y_values[3], y_values[3]], color="red", linestyle="--"
    )  # Line from y-axis

    # Add quadrant lines
    plt.axvline(x=quadrant_lines["x"][0], color="black", linestyle="--")
    plt.axhline(y=quadrant_lines["y"][0], color="black", linestyle="--")

    # Set labels and title
    plt.xlabel("Sentiment Scores")
    plt.ylabel("Artist Popularity")
    plt.title("4-Quadrant Chart")

    # Set axis limits
    plt.ylim(0, 102)
    plt.xlim(-1, 1)

    # Shade the area in each quadrant
    plt.fill_between([-1, 0], 50, 102, color="lightgrey", alpha=0.5, label="Quadrant 4")
    plt.fill_between([0, 1], 0, 50, color="lightgrey", alpha=0.5, label="Quadrant 2")
    plt.fill_between([-1, 0], 0, 50, color="lightblue", alpha=0.5, label="Quadrant 1")
    plt.fill_between([0, 1], 50, 102, color="lightblue", alpha=0.5, label="Quadrant 3")

    # Create a legend with colored boxes
    # Add text to each quadrant
    plt.text(
        -0.5,
        75,
        "Not Justified",
        ha="center",
        va="center",
        fontsize=10,
        color="black",
    )
    plt.text(
        0.5, 25, "Not Justified", ha="center", va="center", fontsize=10, color="black"
    )
    plt.text(
        -0.5,
        25,
        "Justified",
        ha="center",
        va="center",
        fontsize=10,
        color="black",
    )
    plt.text(0.5, 75, "Justified", ha="center", va="center", fontsize=10, color="black")

    plt.text(
        1.1,
        50,
        f"Popularity: {y_value}\nPost Title Sentiment: {x_values[0]} \nPost Description Sentiment: {x_values[1]}\nComment Sentiment: {x_values[2]}\nOverall Sentiment: {x_values[3]}",
        ha="left",
        va="center",
        fontsize=12,
        color="black",
        bbox=dict(facecolor="white", alpha=0.5, edgecolor="black"),
    )

    plt.text(
        1.1,
        20,
        "Justified: \n  popularity>=50 and Sentiment Score>=0 \n  popularity<50 and Sentiment Score<0 \nNot Justified: \n  popularity>=50 and Sentiment Score<0 \n  popularity<50 and Sentiment Score>=0",
        ha="left",
        va="center",
        fontsize=12,
        color="black",
        bbox=dict(facecolor="white", alpha=0.5, edgecolor="black"),
    )

    # Create a legend with colored boxes
    legend_labels = [f"{label}" for label, color in zip(x_labels, colors)]
    plt.legend(legend_labels, loc="upper right", bbox_to_anchor=(1.5, 1))

    # Show the plot
    plt.grid(True)
    plt.show()

    img = BytesIO()
    # ax.figure.savefig(img, format='png', bbox_inches='tight')
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode("utf8")

    plt.close(fig1)

    # print to justify popularity
    result_string = ""
    if (y_value >= 50 and x_values[3] >= 0) or (y_value < 50 and x_values[3] < 0):
        result_string = "Popularity is justified"
    else:
        result_string = "Popularity is not justified"

    # Plotting the bar graph
    fig2 = plt.figure(figsize=(10, 6))
    sentiment_counts.plot(kind="bar", color=["red", "gray", "green"])

    # Adding labels and title
    plt.xlabel("Sentiment")
    plt.ylabel("Count")
    plt.title("Sentiment Counts")
    for i, count in enumerate(sentiment_counts):
        plt.text(i, count + 5, str(count), ha="center", va="bottom")

    # Display the plot
    plt.show()

    img_2 = BytesIO()
    plt.savefig(img_2, format="png", bbox_inches="tight")
    img_2.seek(0)
    plot_url_2 = base64.b64encode(img_2.getvalue()).decode("utf8")

    plt.close(fig2)

    return plot_url, plot_url_2, result_string


if __name__ == "__main__":
    num_args = len(sys.argv) - 1
    # Access individual command-line arguments
    if num_args >= 2:
        input_type = sys.argv[1]  # The first argument
        input_name = sys.argv[2]
        print(input_name)
        print(input_type)
        calculate_sentiment(input_type, input_name)
