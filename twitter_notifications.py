import tweepy
import telegram

from datetime import datetime, timedelta
from time import sleep
import random

import os
import requests
import json
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup():
    """Setup Twitter and Telegram"""

    # Twitter
    try:
        tc = os.environ["TWITTER_CREDENTIALS"]
        with open("./twitter_credentials.json", "w") as f:
            json.dump(json.loads(tc), f)
    except KeyError:
        logging.error("Twitter credentials not available in environment")
        pass

    # Using file to make life easy to run locally
    try:
        with open("twitter_credentials.json", "r") as f:
            tc = json.load(f)["TWITTER_CREDENTIALS"]
    except FileNotFoundError:
        logging.error("Twitter credentials not available")

    auth = tweepy.OAuthHandler(tc["consumer_key"], tc["consumer_secret"])
    auth.set_access_token(tc["access_token"], tc["access_token_secret"])

    api = tweepy.API(
        auth=auth, wait_on_rate_limit=True)

    # Telegram
    bot_token = os.environ["MONITOR_BOT_TOKEN"]
    bot = telegram.Bot(bot_token)

    chat_id_data_ops = os.environ["DATA_OPS_CHAT_ID"]
    chat_id_aux = os.environ["AUX_CHAT_ID"]

    return bot, api, chat_id_data_ops, chat_id_aux


def get_latest_search_space():
    """
    Get the serach filters from sheet
    Since we need to route the queries now,
    Capture the destination key too
    """

    try:
        result = requests.get(
            "https://api.covid19india.org/twitter_queries.json"
        ).json()["twitter_queries"]
        # queries = [x["searchcriteria"] for x in result]
        # destination = [x["destination"] for x in result]
    except Exception as e:
        logging.error("Error while fetching filters", e)

    # return queries, destination
    return result


def stream_tweets(api, results, bot, chat_id_data_ops, chat_id_aux, minutes=10):
    """Get the chats that match the `queries`
    in the past `minutes` and post to `chat_id`"""

    since = datetime.utcnow() - timedelta(minutes=minutes)
    logging.info(f"Fetching tweets since {since}")
    # Traverse the queries list forward or backward (probabilistically)
    # order = random.choice([-1, 1])
    # logging.info(f"Traverse order = {order}")
    for result in results:
        logging.info(f"Query : {result['searchcriteria']} to {result['destination']}")
        try:
            # print(result['searchcriteria'])
            # if 'from:jabalpurdm' not in result['searchcriteria']:
            #     continue
            for status in tweepy.Cursor(
                api.search,
                q=result["searchcriteria"],
                count=15,
                result="recent",
                include_entities=True,
            ).items():
                sleep(2)  # Avoid per minute rate limitation
                if status.created_at < since:
                    break
                try:
                    # Tweet url is combination of user screen name and the tweet ID
                    url = f"http://twitter.com/{status._json['user']['screen_name']}/status/{status._json['id_str']}"

                    # TODO : Use automation scripts here
                    # automate(url)

                    message = (
                        f"@{status._json['user']['screen_name']} tweeted :\n\n{url}"
                        f"\n\n#{result['statename'].replace(' ','')} "
                        f"{'#'+result['districtname'].replace(' ','') if result['districtname']!='' else ''}"
                    )
                    # Route the tweet according to destination
                    if "data_ops" in result["destination"]:
                        post_telegram_message(bot, chat_id_data_ops, message)
                    if "aux" in result["destination"]:
                        post_telegram_message(bot, chat_id_aux, message)

                    logging.info(f"Sent to {result['destination']} :\n {message}")
                except KeyError:
                    logging.error("Couldn't capture tweet url")
                    continue
        except tweepy.TweepError as e:
            logging.error("Error while fetching data from Twitter")
            continue


def post_telegram_message(bot, chat_id, message):
    """Send `message` to `chat_id`"""

    try:
        bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logging.error("Error while sending message to group")
        pass


def main():
    """Run all"""

    bot, api, chat_id_data_ops, chat_id_aux = setup()
    results = get_latest_search_space()
    stream_tweets(api, results, bot, chat_id_data_ops, chat_id_aux, minutes=16)


if __name__ == "__main__":
    main()
