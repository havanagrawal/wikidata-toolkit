import click
import commands

@click.command()
@click.argument("url")
@click.option("--episode-counts", help="A comma-separated list of values representing the number of episodes in each season", default="")
@click.option("--title", help="A title to use as a prefix for the CSV files", default=None)
@click.option("--outdir", help="Directory in which episode list files are output", default=".")
@click.option("--skip-titles", help="A list of titles to skip (not counted in episode numbers)", default=None)
@click.option("--skip-first-n", help="Skip the first n rows found", default=0)
def list_episodes(url, episode_counts, title, outdir, skip_titles, skip_first_n):
    commands.list_episodes(url, episode_counts, title, outdir, skip_titles, skip_first_n)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    list_episodes()
