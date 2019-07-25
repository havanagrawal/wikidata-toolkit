from typing import Iterable

from pywikibot import Claim, Site, ItemPage
import properties.wikidata_properties as wp

class RepoUtils():
    def __init__(self, repo=None):
        if repo is None:
            repo = Site().data_repository()
        self.repo = repo

    def copy(self, src_item: ItemPage, dest_item: ItemPage, props: Iterable[wp.WikidataProperty]):
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
                print(f"Cannot copy {prop} from {src_item} to {dest_item}. Only scalar properties can be copied")
                failures += 1
                continue

            if prop.pid in dest_item.claims:
                print(f"{prop} already has a value in {dest_item}")
                failures += 1
                continue

            value = src_claims[0].getTarget()

            try:
                value_str = value.labels['en']
            except (AttributeError, KeyError):
                try:
                    value_str = value.id
                except AttributeError:
                    try:
                        value_str = value.toTimestr()
                    except:
                        value_str = str(value)
            print(f"Copying {prop}={value_str} from {src_item} to {dest_item}")

            new_claim = Claim(self.repo, prop.pid)
            new_claim.setTarget(value)
            dest_item.addClaim(new_claim, summary=f'Setting {prop.pid} ({prop.name})')
            successes += 1
        return (successes, failures)
