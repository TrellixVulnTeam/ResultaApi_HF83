from flask import Flask
import datetime
import requests
from flask_cors import CORS, cross_origin
import json
from flask import jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello World!"


@app.route('/<start_date>/<end_date>', methods=['GET'])
@cross_origin(supports_credentials=True)
def testApi(start_date, end_date):
    # run sql for getting all the sites
    response_list = []
    try:
        start_date_ = datetime.datetime.strptime(
            start_date, "%Y-%m-%d").date()

        end_date_ = datetime.datetime.strptime(
            end_date, "%Y-%m-%d").date()
    except:
        response_list = {
            "error": "Please use format like : /dev/{start-date}/{end-date}   (Start and end date should be in format YYYY-MM-DD)"}
    try:

        scoreboard_url = "https://delivery.chalk247.com/scoreboard/NFL/" + str(start_date_) + \
            "/" + str(end_date_) + \
            ".json?api_key=74db8efa2a6db279393b433d97c2bc843f8e32b0"

        teamranks_url = "https://delivery.chalk247.com/team_rankings/NFL.json?api_key=74db8efa2a6db279393b433d97c2bc843f8e32b0"

        scoreboard = requests.get(scoreboard_url)
        teamranks = requests.get(teamranks_url)

        # convert to pyton dict
        scoreboard_obj = json.loads(scoreboard.content)
        teamranks_obj = json.loads(teamranks.content)

        # assuming the keys from API will never change
        teams = teamranks_obj["results"]["data"]

        # get in demand values from scoreboard

        scoreboard_results = scoreboard_obj["results"]

        for date in scoreboard_results:
            if not scoreboard_results[date]:
                print("No events on date " + date)
            else:
                tempobj = scoreboard_results[date]
                events = tempobj["data"]

                for key in events:
                    event = events[key]
                    tmp_response_obj = {
                        "event_id": event["event_id"],
                        "away_team_id": event["away_team_id"],
                        "away_nick_name": event["away_nick_name"],
                        "away_city": event["away_city"],
                        "home_team_id": event["home_team_id"],
                        "home_nick_name": event["home_nick_name"],
                        "home_city": event["home_city"],
                    }

                    # convert date time to date and time

                    tmp_response_obj["event_date"] = str(datetime.datetime.strptime(
                        event["event_date"], "%Y-%m-%d %H:%M").date())

                    timeOnly = datetime.datetime.strptime(
                        event["event_date"], "%Y-%m-%d %H:%M").time()

                    tmp_response_obj["event_time"] = str(timeOnly.hour) + \
                        ":" + str(timeOnly.minute)

                    # team ranking aggregation

                    tmp_response_obj["home_rank"], tmp_response_obj["home_rank_points"] = getRankAndAdjustedPoints(
                        teams, event["away_team_id"])

                    tmp_response_obj["home_rank"], tmp_response_obj["home_rank_points"] = getRankAndAdjustedPoints(
                        teams, event["home_team_id"])

                    response_list.append(tmp_response_obj)
    except:
        response_list = {
            "error": "Start and end date difference should not more than 7 days"}

    return jsonify(response_list)


def getRankAndAdjustedPoints(teams, team_id):
    teamObj = list(filter(lambda team: team['team_id'] == team_id, teams))[0]

    return teamObj["rank"], "{:.2f}".format(float(teamObj["adjusted_points"]))


if __name__ == '__main__':
    app.run()
