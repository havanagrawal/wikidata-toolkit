def generate_sparql_query(key_val_pairs):
    where_clause = ""
    for key, val in key_val_pairs.items():
        where_clause = where_clause + f"\t?item wdt:{key} wd:{val}.\n"
    return "SELECT ?item WHERE {\n" + where_clause + "}"
