import requests
import datetime
import time


def get_reddit_user_agent():
    """Needed according to: https://github.com/reddit-archive/reddit/wiki/API#rules"""
    return {"User-Agent": "Discord bot - Ape mother (by /u/cyrlop)"}


def get_latest_posts_by_flair(sub, flair, limit=20):
    url = f'https://www.reddit.com/r/{sub}/search.json?limit={limit}&sort=new&q=flair_name:"{flair}"'

    nb_try = 0
    while nb_try <= 6:
        nb_try += 1
        res = requests.get(url, headers=get_reddit_user_agent())

        if res.status_code == 200:
            return res.json()["data"]["children"]
        elif res.status_code == 429:
            time.sleep(1)
            continue

    raise Exception("Issue with request: `{res}`")


def get_post_embed_field_data(post_data):
    """Returns an embed dict with "name", "value" and "inline" as keys."""
    name = f"🖍 {post_data['title']}"
    if len(name) >= 210:
        name = name[:210] + " [...]"

    date = datetime.datetime.fromtimestamp(post_data["created_utc"])

    value = (
        f"[Link to post]({post_data['url']})"
        f" {post_data['score']} ({post_data['upvote_ratio']*100}% upvoted)"
        f" by u/{post_data['author']}"
        f" on {date}"
    )

    return {"name": name, "value": value, "inline": False}
