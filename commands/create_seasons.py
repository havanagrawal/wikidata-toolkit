from pywikibot import Claim, ItemPage, Site
from pywikibot.data.api import Request

import properties.wikidata_properties as wp
from utils import RepoUtils


def create_season_quickstatements(series_id, label, descr, ordinal):
    print("CREATE")
    print(f'LAST|Len|"{label}"')
    print(f'LAST|Den|"{descr}"')
    print(f"LAST|{wp.INSTANCE_OF.pid}|{wp.TELEVISION_SERIES_SEASON}")
    print(f'LAST|{wp.PART_OF_THE_SERIES.pid}|{series_id}|{wp.SERIES_ORDINAL.pid}|"{ordinal}"')


def create_season(series_id: str, label: str, descr: str, ordinal: int, dry: bool):
    """Creates a season item on WikiData

    Arguments
    ---------
    series_id: str
        The Wiki ID of the series ItemPage
    label: str
        The label to use for this season.
        Typically "<Series Name>, season x", where x is the ordinal
    descr: str
        The description to use for this season.
        Typically "season x of <Series Name>" where x is the ordinal
    ordinal: int
        The ordinal of this season, within the series
    dry: bool
        Whether or not this function should run in dry-run mode.
        In dry-run mode, no real changes are made to WikiData, they are only
        logged to stdout.
    """
    dry_str = "[DRY-RUN] " if dry else ""
    repoutil = RepoUtils(Site().data_repository())
    season_ids = []
    print(f"{dry_str}Creating season with\n\tlabel='{label}'\n\tdescription='{descr}'")
    if not dry:
        season = repoutil.new_item(labels={"en": label}, descriptions={"en": descr})
        print(f"Created a new Item: {season.getID()}")
        season_ids.append(str(season.getID()))

    print(f"{dry_str}Setting {wp.INSTANCE_OF}={wp.TELEVISION_SERIES_SEASON}")
    if not dry:
        instance_claim = repoutil.new_claim(wp.INSTANCE_OF.pid)
        instance_claim.setTarget(ItemPage(repoutil.repo, wp.TELEVISION_SERIES_SEASON))
        season.addClaim(instance_claim, summary=f"Setting {wp.INSTANCE_OF.pid}")


    print(f"{dry_str}Setting {wp.PART_OF_THE_SERIES}={series_id}, with {wp.SERIES_ORDINAL.pid}={ordinal}")
    if not dry:
        series_claim = repoutil.new_claim(wp.PART_OF_THE_SERIES.pid)
        series_claim.setTarget(ItemPage(repoutil.repo, series_id))
        season_ordinal = repoutil.new_claim(wp.SERIES_ORDINAL.pid)
        season_ordinal.setTarget(str(ordinal))
        series_claim.addQualifier(season_ordinal)
        season.addClaim(series_claim, summary=f"Setting {wp.PART_OF_THE_SERIES.pid}")

    # Easier to pipe through to other scripts
    print("\n".join(season_ids))

    return season_ids


def create_seasons(series_id, number_of_seasons, quickstatements=False, dry=False):
    series_title = ItemPage(Site().data_repository(), series_id)
    series_title.get(force=True)
    series_label = series_title.labels['en']
    for i in range(1, number_of_seasons + 1):
        label = f"{series_label}, season {i}"
        descr = f"season {i} of {series_label}"
        if quickstatements:
            create_season_quickstatements(series_id, label, descr, i)
        else:
            return create_season(series_id, label, descr, i, dry)

