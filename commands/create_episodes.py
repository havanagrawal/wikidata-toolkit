import csv

from pywikibot import ItemPage, Site

import properties.wikidata_properties as wp
from utils import RepoUtils
from .errors import SuspiciousTitlesError


def read_titles(filepath):
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        return list(reader)


def create_episode_quickstatements(series_id, season_id, title, series_ordinal, season_ordinal):
    """Prints out QuickStatements that can be used to create an episode item on WikiData"""
    print("CREATE")
    print(f'LAST|Len|"{title}"')
    print(f"LAST|{wp.INSTANCE_OF.pid}|{wp.TELEVISION_SERIES_EPISODE}")
    print(f'LAST|{wp.PART_OF_THE_SERIES.pid}|{series_id}|{wp.SERIES_ORDINAL.pid}|"{series_ordinal}"')
    print(f'LAST|{wp.SEASON.pid}|{season_id}|{wp.SERIES_ORDINAL.pid}|"{season_ordinal}"')


def create_episode(series_id, season_id, title, series_ordinal, season_ordinal, dry):
    """Creates a season item on WikiData

    Arguments
    ---------
    series_id: str
        The Wiki ID of the series ItemPage
    season_id: str
        The Wiki ID of the season ItemPage
    title: str
        The title of this episode. This is used to set the label.
    series_ordinal: int
        The ordinal of this episode, within the series
    season_ordinal: int
        The ordinal of this episode, within the season
    dry: bool
        Whether or not this function should run in dry-run mode.
        In dry-run mode, no real changes are made to WikiData, they are only
        logged to stdout.

    Returns
    -------
    episode_id: str
        The Wiki ID of the episode item
    """
    dry_str = "[DRY-RUN] " if dry else ""
    print(f"{dry_str}Creating episode with label='{title}'")

    episode = None
    if not dry:
        repoutil = RepoUtils(Site().data_repository())

        season = ItemPage(repoutil.repo, season_id)
        season.get()

        # Check if season has part_of_the_series set to series_id
        if wp.PART_OF_THE_SERIES.pid not in season.claims:
            raise ValueError(f"The season {season_id} does not have a PART_OF_THE_SERIES ({wp.PART_OF_THE_SERIES.pid} property). Check the input series and season IDs for correctness.")
        actual_series_id = str(season.claims[wp.PART_OF_THE_SERIES.pid][0].getTarget().getID())
        if actual_series_id != series_id:
            raise ValueError(f"The season {season_id} has PART_OF_THE_SERIES={actual_series_id} but expected={series_id}. Check the input series and season IDs for correctness.")

        episode = ItemPage(repoutil.repo)

        episode.editLabels({"en": title}, summary="Setting label")
        print(f"Created a new Item: {episode.getID()}")

    print(f"{dry_str}Setting {wp.INSTANCE_OF}={wp.TELEVISION_SERIES_EPISODE}")
    if not dry:
        instance_claim = repoutil.new_claim(wp.INSTANCE_OF.pid)
        instance_claim.setTarget(ItemPage(repoutil.repo, wp.TELEVISION_SERIES_EPISODE))
        episode.addClaim(instance_claim, summary=f"Setting {wp.INSTANCE_OF.pid}")

    print(f"{dry_str}Setting {wp.PART_OF_THE_SERIES}={series_id}, with {wp.SERIES_ORDINAL}={series_ordinal}")
    if not dry:
        series_claim = repoutil.new_claim(wp.PART_OF_THE_SERIES.pid)
        series_claim.setTarget(ItemPage(repoutil.repo, series_id))

        series_ordinal_claim = repoutil.new_claim(wp.SERIES_ORDINAL.pid)
        series_ordinal_claim.setTarget(series_ordinal)
        series_claim.addQualifier(series_ordinal_claim)

        episode.addClaim(series_claim, summary=f"Setting {wp.PART_OF_THE_SERIES.pid}")

    print(f"{dry_str}Setting {wp.SEASON}={season_id}, with {wp.SERIES_ORDINAL}={season_ordinal}")
    if not dry:
        season_claim = repoutil.new_claim(wp.SEASON.pid)
        season_claim.setTarget(ItemPage(repoutil.repo, season_id))

        season_ordinal_claim = repoutil.new_claim(wp.SERIES_ORDINAL.pid)
        season_ordinal_claim.setTarget(season_ordinal)
        season_claim.addQualifier(season_ordinal_claim)

        episode.addClaim(season_claim, summary=f"Setting {wp.SEASON.pid}")

    return episode.getID() if episode is not None else "Q-1"


def create_episodes(series_id, season_id, titles_file, quickstatements=False, dry=False, confirm_titles=False):
    titles = read_titles(titles_file)

    maybe_erroneous_titles = check_erroneous_titles(titles)
    if maybe_erroneous_titles and not confirm_titles:
        raise SuspiciousTitlesError(
            "The following titles have an uncommon character in them: \n"
            + "\n".join([" * {t}" for t in maybe_erroneous_titles])
        )

    episode_ids = []
    for series_ordinal, season_ordinal, title in titles:
        if quickstatements:
            create_episode_quickstatements(series_id, season_id, title, series_ordinal, season_ordinal)
        else:
            episode_id = create_episode(series_id, season_id, title, series_ordinal, season_ordinal, dry)
            episode_ids.append(episode_id)

    return episode_ids

def check_erroneous_titles(titles):
    uncommon_chars = set("[", "]")
    maybe_erroneous_titles = [
        title
        for title in titles
        if any(c in title for c in uncommon_chars)
    ]
    return maybe_erroneous_titles
