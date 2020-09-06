from typing import Iterable

import click

from pywikibot import Site, ItemPage
import properties.wikidata_properties as wp
from utils import RepoUtils


def _clone(src: str, dest: str, props: Iterable[wp.WikidataProperty]):
    """Copy all specified properties from the src ID to the dest ID"""
    repoutil = RepoUtils(Site().data_repository())
    if not src.startswith("Q"):
        raise ValueError(f"Expected item ID of the format 'Q####', found {src}")
    if not dest.startswith("Q"):
        raise ValueError(f"Expected item ID of the format 'Q####', found {dest}")

    src_item = ItemPage(repoutil.repo, src)
    dest_item = ItemPage(repoutil.repo, dest)

    success, failures = repoutil.copy(src_item, dest_item, props)
    print(f"Success: {success}, Failures: {failures}")


@click.group()
def clone():
    pass


@clone.command()
@click.argument("src")
@click.argument("dest")
def episode(src, dest):
    """Clone an episode's properties from SRC to DEST,
        assuming they both are from the same season
    """
    props = [
        wp.INSTANCE_OF,
        wp.PART_OF_THE_SERIES,
        wp.ORIGINAL_NETWORK,
        wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
        wp.COUNTRY_OF_ORIGIN,
        wp.PRODUCTION_COMPANY,
        wp.PUBLICATION_DATE,
        wp.DIRECTOR,
        wp.SEASON,
    ]

    _clone(src, dest, props)


@clone.command()
@click.argument("src")
@click.argument("dest")
def season(src, dest):
    """Clone an season's properties from SRC to DEST"""
    props = [
        wp.INSTANCE_OF,
        wp.PART_OF_THE_SERIES,
        wp.ORIGINAL_NETWORK,
        wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
        wp.COUNTRY_OF_ORIGIN,
    ]

    _clone(src, dest, props)


if __name__ == "__main__":
    clone()
