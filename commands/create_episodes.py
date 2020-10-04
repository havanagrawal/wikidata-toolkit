import csv

import properties.wikidata_properties as wp
from pywikibot import Claim, ItemPage, Site
from utils import RepoUtils


def read_titles(filepath):
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        return [s for s in reader]


def create_episode_quickstatements(series_id, season_id, title, ordinal):
    print("CREATE")
    print(f'LAST|Len|"{title}"')
    print(f"LAST|{wp.INSTANCE_OF.pid}|{wp.TELEVISION_SERIES_EPISODE}")
    print(f"LAST|{wp.PART_OF_THE_SERIES.pid}|{series_id}")
    print(f'LAST|{wp.SEASON.pid}|{season_id}|{wp.SERIES_ORDINAL.pid}|"{ordinal}"')


def create_episode(series_id, season_id, title, ordinal, dry):
    dry_str = "[DRY-RUN] " if dry else ""
    print(f"{dry_str}Creating episode with label='{title}'")
    if not dry:
        repoutil = RepoUtils(Site().data_repository())
        episode = ItemPage(repoutil.repo)

        episode.editLabels({"en": title}, summary="Setting label")
        print(f"Created a new Item: {episode.getID()}")

    print(f"{dry_str}Setting {wp.INSTANCE_OF}={wp.TELEVISION_SERIES_EPISODE}")
    if not dry:
        instance_claim = repoutil.new_claim(wp.INSTANCE_OF.pid)
        instance_claim.setTarget(ItemPage(repoutil.repo, wp.TELEVISION_SERIES_EPISODE))
        episode.addClaim(instance_claim, summary=f"Setting {wp.INSTANCE_OF.pid}")

    print(f"{dry_str}Setting {wp.PART_OF_THE_SERIES}={series_id}")
    if not dry:
        series_claim = repoutil.new_claim(wp.PART_OF_THE_SERIES.pid)
        series_claim.setTarget(ItemPage(repoutil.repo, series_id))
        episode.addClaim(series_claim, summary=f"Setting {wp.PART_OF_THE_SERIES.pid}")

    print(f"{dry_str}Setting {wp.SEASON}={season_id}, with {wp.SERIES_ORDINAL}={ordinal}")
    if not dry:
        season_claim = repoutil.new_claim(wp.SEASON.pid)
        season_claim.setTarget(ItemPage(repoutil.repo, season_id))
        season_ordinal = repoutil.new_claim(wp.SERIES_ORDINAL.pid)
        season_ordinal.setTarget(ordinal)
        season_claim.addQualifier(season_ordinal)
        episode.addClaim(season_claim, summary=f"Setting {wp.SEASON.pid}")


def create_episodes(series_id, season_id, titles_file, quickstatements=False, dry=False):
    titles = read_titles(titles_file)
    for ordinal, title in titles:
        if quickstatements:
            create_episode_quickstatements(series_id, season_id, title, ordinal)
        else:
            create_episode(series_id, season_id, title, ordinal, dry)
