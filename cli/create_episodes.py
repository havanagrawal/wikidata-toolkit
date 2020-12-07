import click
import commands
from pywikibot import Site

from .click_utils import validate_item_id


@click.command()
@click.argument("series_id", callback=validate_item_id)
@click.argument("season_id", callback=validate_item_id)
@click.argument("titles_file", type=click.Path(exists=True))
@click.option("--quickstatements", help="Print out QuickStatements for creating the items, instead of creating the items directly on Wikidata.", is_flag=True, default=False)
@click.option("--dry", help="Enable dry run mode. Does not create any items on Wikidata.", is_flag=True, default=False)
def create_episodes(series_id, season_id, titles_file, quickstatements=False, dry=False):
    Site().login()
    try:
        commands.create_episodes(series_id, season_id, titles_file, quickstatements, dry)
    except commands.errors.SuspiciousTitlesError as e:
        click.confirm(f"An error occurred when reading the CSV file:\n{e.message}\nDo you want to continue?", abort=True)
        commands.create_episodes(series_id, season_id, titles_file, quickstatements, dry, confirm_titles=True)

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    create_episodes()
