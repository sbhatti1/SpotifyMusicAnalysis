from flask import Flask, render_template, request

from analytics.dailypoliticsstats import fetch_subreddit_data, plotpolitics
from analytics.spotifyHolidayCorelation import spotifyholidaycorr
from analytics.otherplots import spotifydata, redditdata
from analytics.hatespeech import fetchdata
from analytics.research_analysis import heat_map, corr_track_popularity
from app import result, post_comments
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from flask import Flask, render_template
from io import BytesIO
import base64
from datetime import datetime, timedelta
import analytics.sentiment
from analytics.sentiment import calculate_sentiment


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("homepage.html")


@app.route("/result", methods=["GET", "POST"])
def result_route():
    user_input_year = request.form["year"]
    plot_url = result()
    return render_template("result.html", year=user_input_year, plot_url=plot_url)


# For sentiment anaylsis
@app.route("/sentimentAnalysis", methods=["GET", "POST"])
def sentimentAnalysis():
    user_input_trackOrArtist = request.form["trackOrArtist"]
    user_input_popularTrackOrArtist = request.form["popularTracksOrArtists"]
    # print(user_input_trackOrArtist)
    # print(user_input_popularTrackOrArtist)
    plot_url, plot_url2, result_string = calculate_sentiment(
        user_input_trackOrArtist, user_input_popularTrackOrArtist
    )
    return render_template(
        "sentimentAnalysis.html",
        trackOrArtist=user_input_trackOrArtist,
        popularTracksOrArtists=user_input_popularTrackOrArtist,
        plot_url=plot_url,
        plot_url2=plot_url2,
        result_string=result_string,
    )


# For otherplots
@app.route("/otherplot", methods=["GET"])
def otherplots():
    plot_politics = plotpolitics()
    spotify_corr = spotifyholidaycorr()
    spotify_data = spotifydata()
    reddit_data = redditdata()
    hate_speech = fetchdata()
    # plot_politics=plot_politics,spotify_corr=spotify_corr, reddit_data=reddit_data, spotify_data=spotify_data,
    return render_template(
        "otherplotspage.html",
        plot_politics=plot_politics,
        spotify_corr=spotify_corr,
        reddit_data=reddit_data,
        spotify_data=spotify_data,
        hate_speech=hate_speech,
    )


@app.route("/researchanalysis", methods=["POST"])
def researchanalysis():
    heatmap_data = heat_map()
    corr_track = corr_track_popularity()

    return render_template(
        "researchanalysis.html", heatmap_data=heatmap_data, corr_track=corr_track
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
