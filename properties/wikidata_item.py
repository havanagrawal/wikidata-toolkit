class WikidataItemId():
    """Wrapper for an item ID on Wikidata, such as Q65604139"""
    def __init__(self, item_id):
        if len(item_id) == 0:
            raise ValueError(f"Expected non-empty item ID")

        fail_msg = f'Expected item ID of format Q#####, got {item_id}'
        if item_id[0].upper() != 'Q':
            raise ValueError(fail_msg)
        if len(item_id[1:]) == 0:
            raise ValueError(fail_msg)
        try:
            code = int(item_id[1:])
        except TypeError:
            raise ValueError(fail_msg)

        self.item_id = item_id

    def __str__(self):
        return self.item_id

    def __repr__(self):
        return self.item_id
