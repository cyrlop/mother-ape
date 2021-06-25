import requests
import time


def get_latest_posts_by_flair(sub, flair, limit=20):
    url = f'https://www.reddit.com/r/{sub}/search.json?limit={limit}&sort=new&q=flair_name:"{flair}"'

    nb_try = 0
    while nb_try <= 6:
        nb_try += 1
        res = requests.get(url)

        if res.status_code == 200:
            return res.json()["data"]["children"]
        elif res.status_code == 429:
            time.sleep(1)
            continue

    raise Exception("Issue with request: `{res}`")
