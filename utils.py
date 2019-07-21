from typing import Iterable

from pywikibot import Claim
import properties.wikidata_properties as wp

class RepoUtils():
    def __init__(self, repo):
        self.repo = repo

    def copy(self, src_item, dest_item, props: Iterable[wp.WikidataProperty]):
        src_item.get()
        dest_item.get()

        for prop in props:
            if prop.pid not in src_item.claims:
                print(f"{prop} not found in {src}")
                continue

            src_claims = src_item.claims[prop.pid]
            if len(src_claims) > 1:
                print("Only scalar properties can be copied")
                continue

            if prop.pid in dest_item.claims:
                print(f"{prop} already has a value in {dest_item}")
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
