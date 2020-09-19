import click
import requests
from bs4 import BeautifulSoup

def get_episode_list(url):
    page = requests.get(url)
    html_page = page.content
    soup = BeautifulSoup(html_page, 'html.parser')
    episode_names = [t.text for t in soup.find_all('td', attrs={'class': 'summary'}, text=True)]
    return episode_names


def print_episode_list(episodes, episode_counts):
    if not episode_counts:
        episode_counts = [len(episodes)]
    else:
        episode_counts = [int(k) for k in episode_counts.split(",")]
    j = 0
    for ep_count in episode_counts:
        for i, e in enumerate(episodes[j:j+ep_count]):
            print(f"{i + 1},{e}")
        j += ep_count

@click.command()
@click.argument("url")
@click.option("--episode-counts", help="A comma-separated list of values representing the number of episodes in each season", default="")
def episode_list(url, episode_counts):
    title = slugify(url.replace("https://en.wikipedia.org/wiki/", ""))
    print(title)
    print_episode_list(get_episode_list(url), episode_counts)


def slugify(s):
    return s.replace("(", "").replace(")", "").lower().replace("_", "-")


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    episode_list()