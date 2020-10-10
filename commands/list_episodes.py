import requests
from bs4 import BeautifulSoup

def get_episode_list(url):
    page = requests.get(url)
    html_page = page.content
    soup = BeautifulSoup(html_page, 'html.parser')
    episode_names = [t.text for t in soup.find_all('td', attrs={'class': 'summary'})]
    return episode_names


def print_episode_list(episodes, episode_counts, title, skip_titles):
    episodes = [e for e in episodes if e not in skip_titles]
    print(f"Skipped {len(skip_titles)} titles")
    if not episode_counts:
        episode_counts = [len(episodes)]
    else:
        episode_counts = [int(k) for k in episode_counts.split(",")]
    if sum(episode_counts) != len(episodes):
        print(f"[WARNING] Expected sum(episode_counts) = len(episodes) but {sum(episode_counts)} != {len(episodes)}")
    j = 0
    for season, ep_count in enumerate(episode_counts):
        season_str = f"{season + 1}".rjust(2, "0")
        with open(f"{title}_S{season_str}.csv", 'w') as f:
            for i, e in enumerate(episodes[j:j+ep_count]):
                print(f"{j + 1},{i + 1},{e}", file=f)
                j += 1


def list_episodes(url, episode_counts, title, skip_titles):
    if title is None:
        title = slugify(url.replace("https://en.wikipedia.org/wiki/", ""))
    skip_titles = set(skip_titles.split(",")) if skip_titles else set()
    print_episode_list(get_episode_list(url), episode_counts, title, skip_titles)


def slugify(s):
    return s.replace("(", "").replace(")", "").lower().replace("_", "-")