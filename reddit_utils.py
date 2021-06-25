import requests


def get_latest_posts_by_flair(sub, flair, limit=20):
    url = f'https://www.reddit.com/r/{sub}/search.json?limit={limit}&sort=new&q=flair_name:"{flair}"'
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()["data"]["children"]
    elif res.status_code == 429:
        raise Exception("Too many requests, don't spam!")
