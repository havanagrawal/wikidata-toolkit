from typing import Iterable

from pywikibot import Site, ItemPage, Claim
import properties.wikidata_properties as wp
from utils import RepoUtils

REPO = Site('wikidata', 'wikidata').data_repository()

def clone(src, dest, props: Iterable[wp.WikidataProperty]):
    """Copy all specified properties from the src ID to the dest ID"""
    repoutil = RepoUtils(REPO)
    if not src.startswith('Q'):
        raise ValueError(f"Expected item ID of the format 'Q####', found {src}")
    if not dest.startswith('Q'):
        raise ValueError(f"Expected item ID of the format 'Q####', found {dest}")

    src_item = ItemPage(self.repo, src)
    dest_item = ItemPage(self.repo, dest)

    repoutil.copy(src_item, dest_item, props)

def clone_episode(src, dest):
    props = [
        wp.INSTANCE_OF,
        wp.PART_OF_THE_SERIES,
        wp.ORIGINAL_NETWORK,
        wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
        wp.COUNTRY_OF_ORIGIN,
        wp.PRODUCTION_COMPANY,
        wp.PUBLICATION_DATE,
        wp.DIRECTOR,
        wp.SEASON
    ]

    clone(src, dest, props)

def main():
    clone_episode(src='Q65605482', dest='Q65640224')

if __name__ == '__main__':
    main()
