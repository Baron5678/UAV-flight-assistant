def patch_update(columns, excluded, db_object, dom_object):
    values = {}
    for column in columns:
        field = column.name

        if field in excluded:
            continue
        db_value = getattr(db_object, field)
        new_value = getattr(dom_object, field)

        if db_value != new_value:
            values[field] = new_value

    if not values:
        return None

    return values
