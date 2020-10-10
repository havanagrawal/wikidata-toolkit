import click
import commands

@click.command()
@click.argument("url")
@click.option("--episode-counts", help="A comma-separated list of values representing the number of episodes in each season", default="")
@click.option("--title", help="A title to use as a prefix for the CSV files", default=None)
@click.option("--skip-titles", help="A list of titles to skip (not counted in episode numbers", default=None)
def list_episodes(url, episode_counts, title, skip_titles):
    commands.list_episodes(url, episode_counts, title, skip_titles)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    list_episodes()