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


def create_season(series_id, label, descr, ordinal, dry):
    dry_str = "[DRY-RUN] " if dry else ""
    repoutil = RepoUtils(Site().data_repository())
    print(f"{dry_str}Creating season with\n\tlabel='{label}'\n\tdescription='{descr}'")
    if not dry:
        season = ItemPage(repoutil.repo)
        season.editLabels({"en": label}, summary="Setting label")
        season.editDescriptions({"en": descr}, summary="Setting description")
        print(f"Created a new Item: {season.getID()}")

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
            create_season(series_id, label, descr, i, dry)

