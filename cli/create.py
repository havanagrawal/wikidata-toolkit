import glob
import time

import click
import commands
from pywikibot import Site

from .click_utils import validate_item_id


@click.command()
@click.argument("series_id", callback=validate_item_id)
@click.argument("titles_dir", type=click.Path(exists=True))
@click.option("--dry", help="Enable dry run mode. Does not create any items on Wikidata.", is_flag=True, default=False)
def create(series_id, titles_dir, dry=False):
    Site().login()

    files = sorted(glob.glob(f"{titles_dir}/*.csv"))
    season_count = len(files)

    season_ids = commands.create_seasons(series_id, season_count, dry=dry)
    episode_ids = []

    for season_file, season_id in zip(files, season_ids):
        try:
            e_ids = commands.create_episodes(series_id, season_id, season_file, dry=dry)
        except commands.errors.SuspiciousTitlesError as e:
            click.confirm(f"An error occurred when reading the CSV file:\n{e.message}\nDo you want to continue?", abort=True)
            e_ids = commands.create_episodes(series_id, season_id, season_file, dry=dry, confirm_titles=True)
        episode_ids.extend(e_ids)

    # Sleep for a few seconds to let the data be persisted in WikiData
    # This isn't necessary, but it results in fewer warnings in the next step
    time.sleep(10)

    commands.check_tv_show(series_id, child_type="all", autofix=True, accumulate=False, interactive=False)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    create()

