import click
import csv

from pywikibot import Claim, ItemPage, Site
from pywikibot.data.api import Request

import properties.wikidata_properties as wp
from utils import RepoUtils

from click_utils import validate_item_id

def read_titles(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        return [s for s in reader]


def create_episode_quickstatements(series_id, season_id, title, ordinal):
    print("CREATE")
    print(f'LAST|Len|"{title}"')
    print(f"LAST|{wp.INSTANCE_OF.pid}|{wp.TELEVISION_SERIES_EPISODE}")
    print(f"LAST|{wp.PART_OF_THE_SERIES.pid}|{series_id}")
    print(f'LAST|{wp.SEASON.pid}|{season_id}|{wp.SERIES_ORDINAL.pid}|"{ordinal}"')


def create_episode(series_id, season_id, title, ordinal):
    repoutil = RepoUtils(Site().data_repository())
    episode = ItemPage(repoutil.repo)
    print(f"Created a new Item: {episode.getID()}")
    episode.editLabels({"en": title})

    print(f'Setting {wp.INSTANCE_OF.pid}')
    instance_claim = repoutil.new_claim(wp.INSTANCE_OF.pid)
    instance_claim.setTarget(wp.TELEVISION_SERIES_EPISODE)
    episode.addClaim(instance_claim, summary=f'Setting {wp.INSTANCE_OF.pid}')

    print(f'Setting {wp.PART_OF_THE_SERIES.pid}')
    series_claim = repoutil.new_claim(wp.PART_OF_THE_SERIES.pid)
    series_claim.setTarget(series_id)
    episode.addClaim(series_claim, summary=f'Setting {wp.PART_OF_THE_SERIES.pid}')

    print(f'Setting {wp.SEASON.pid}')
    season_claim = repoutil.new_claim(wp.SEASON.pid)
    season_claim.setTarget(season_id)
    season_ordinal = repoutil.new_claim(wp.SERIES_ORDINAL.pid)
    season_ordinal.setTarget(ordinal)
    season_claim.addQualifier(season_ordinal)
    episode.addClaim(season_claim, summary=f'Setting {wp.SEASON.pid}')


@click.command()
@click.argument("series_id", callback=validate_item_id)
@click.argument("season_id", callback=validate_item_id)
@click.argument("titles_file", type=click.Path(exists=True))
@click.option("--quickstatements", is_flag=True, default=False)
def create_episodes(series_id, season_id, titles_file, quickstatements=False):
    titles = read_titles(titles_file)
    for ordinal, title in titles:
        if quickstatements:
            create_episode_quickstatements(series_id, season_id, title, ordinal)
        else:
            raise ValueError("Non-quickstatements creation not permitted. Please use the --quickstatements option")
            # create_episode(series_id, season_id, title, ordinal)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    create_episodes()

