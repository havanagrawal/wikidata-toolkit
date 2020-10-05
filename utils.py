from typing import Iterable, Optional
import click
import re
import requests
from bs4 import BeautifulSoup
from pywikibot import Claim, Site, ItemPage

import constraints.api as api
import properties.wikidata_properties as wp


def format(item: ItemPage):
    return f"{item.title()} ({item.labels.get('en', None)})"


def printable_target_value(value):
    try:
        return value.labels["en"]
    except (AttributeError, KeyError):
        try:
            return value.title()
        except AttributeError:
            try:
                return value.toTimestr()
            except:
                return str(value)


def copy_delayed(
    src_item: ItemPage, dest_item: ItemPage, props: Iterable[wp.WikidataProperty]
) -> Iterable[api.Fix]:
    repo = Site().data_repository()

    src_item.get()
    dest_item.get()

    claims = []

    for prop in props:
        src_claims = src_item.claims.get(prop.pid, [])

        if len(src_claims) > 1:
            print(
                f"Cannot copy {prop} from {format(src_item)} to {format(dest_item)}. Only scalar properties can be copied"
            )
            continue

        if prop.pid in dest_item.claims:
            print(f"{prop} already has a value in {format(dest_item)}")
            continue

        targets = [claim.getTarget() for claim in src_claims]

        for target in targets:
            target.get()

            target_str = printable_target_value(target)

            print(
                f"Creating claim to copy {prop}={target_str} from {format(src_item)} to {format(dest_item)}"
            )

            new_claim = Claim(repo, prop.pid)
            new_claim.setTarget(target)
            summary = f"Setting {prop.pid} ({prop.name})"
            claims.append(api.ClaimFix(new_claim, summary, dest_item))
    return claims


def imdb_title(imdb_id):
    if imdb_id is None:
        return None
    response = requests.get(f"https://www.imdb.com/title/{imdb_id}")
    soup = BeautifulSoup(response.content, features="lxml")
    heading = soup.select_one("div.title_wrapper > h1")
    if heading is not None:
        return heading.get_text().strip()
    return None


def tv_com_title(tv_com_id):
    if tv_com_id is None:
        return None
    response = requests.get(f"https://www.tv.com/{tv_com_id}")
    soup = BeautifulSoup(response.content, features="lxml")
    heading = soup.select_one(".ep_title")
    if heading is not None:
        return heading.get_text().strip()
    return None


def bgg_title(bgg_id) -> Optional[str]:
    if bgg_id is None:
        return None

    response = requests.get(f"https://www.boardgamegeek.com/boardgame/{bgg_id}")
    soup = BeautifulSoup(response.content, features="lxml")
    heading = soup.find("title")
    if heading is not None:
        # the title for BGG is in the format "<title | Board Game | BoardGameGeek"
        heading = heading.get_text().split("|")[0]
        return heading.strip()
    return None


def no_of_episodes(imdb_id):
    if imdb_id is None:
        return None

    response = requests.get(f"https://www.imdb.com/title/{imdb_id}")
    soup = BeautifulSoup(response.content, features="lxml")
    maybe_episode_counts = (
        x.get_text().strip() for x in soup.select("span.bp_sub_heading")
    )

    pattern = r"(\d+)\s+episodes"

    matches = (re.match(pattern, no_of_epis) for no_of_epis in maybe_episode_counts)
    matches = list(filter(None, matches))

    if not matches:
        return None

    return int(matches[0].group(1))


class RepoUtils:
    def __init__(self, repo=None):
        if repo is None:
            repo = Site().data_repository()
        self.repo = repo

    def copy(
        self,
        src_item: ItemPage,
        dest_item: ItemPage,
        props: Iterable[wp.WikidataProperty],
    ):
        """Copy properties from the source item to the destination item

            Returns a tuple of (successes, failures)
        """
        src_item.get()
        dest_item.get()

        failures = 0
        successes = 0

        for prop in props:
            if prop.pid not in src_item.claims:
                print(f"{prop} not found in {src_item.title()}")
                failures += 1
                continue

            src_claims = src_item.claims[prop.pid]
            if len(src_claims) > 1:
                copy_multiple = click.confirm(
                    f"There are {len(src_claims)} values for {prop}. Are you sure you want to copy all of them?"
                )
                # copy_multiple = False
                if not copy_multiple:
                    print(
                        f"Cannot copy {prop} from {format(src_item)} to {format(dest_item)}. Only scalar properties can be copied"
                    )
                    failures += 1
                    continue

            if prop.pid in dest_item.claims:
                print(f"{prop} already has a value in {format(dest_item)}")
                failures += 1
                continue

            targets = [claim.getTarget() for claim in src_claims]

            for target in targets:
                if hasattr(target, "get"):
                    target.get()

                target_str = printable_target_value(target)

                print(
                    f"Copying {prop}={target_str} from {format(src_item)} to {format(dest_item)}"
                )

                new_claim = Claim(self.repo, prop.pid)
                new_claim.setTarget(target)
                dest_item.addClaim(
                    new_claim, summary=f"Setting {prop.pid} ({prop.name})"
                )
                successes += 1
        return (successes, failures)

    def new_claim(self, prop):
        return Claim(self.repo, prop)