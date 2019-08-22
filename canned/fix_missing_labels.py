"""Add an English label to TV episodes which have an English title but a missing label"""
import click
from pywikibot import Site, ItemPage

from sparql.queries import items_with_missing_labels_with_title


@click.command()
@click.option(
    "--dry",
    is_flag=True,
    default=False,
    help="Only print out the changes, don't run any commands",
)
def main(dry=False):
    dry_str = ""
    if dry:
        print("Running in dry-run mode, will not implement any changes")
        dry_str = "[DRY-RUN MODE] "
    repo = Site().data_repository()
    for item_link, item_id, title in items_with_missing_labels_with_title():
        print(
            f"{dry_str} ( {str(item_link).ljust(40, ' ')} ) Fixing {str(item_id).ljust(9, ' ')}: {title}"
        )
        if not dry:
            item = ItemPage(repo, item_id)
            item.get()
            if len(title) < 250:
                item.editLabels({"en": title})


if __name__ == "__main__":
    main()
