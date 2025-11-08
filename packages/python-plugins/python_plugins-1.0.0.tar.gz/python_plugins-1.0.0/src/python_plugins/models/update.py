def update_obj(db, old_obj, new_data: dict, NewClass, force=None):
    """insert or update object

    :param db: sqlalchemy db
    :param old_obj: old object
    :param new_data: new dict
    :param NewClass: object class
    :param force: update= update old object with new attribute
    """
    # 1. old is not exist
    if old_obj is None:
        new_obj = NewClass()
        for k in new_data:
            if hasattr(new_obj, k):
                setattr(new_obj, k, new_data.get(k))
        db.session.add(new_obj)
        db.session.commit()
        print(f"{new_obj} inserted")
        return

    # 2. old is exist
    match force:
        case None:
            print(f"{old_obj} exists")
        case "update":
            # update old
            for k in new_data:
                if hasattr(old_obj, k):
                    setattr(old_obj, k, new_data.get(k))
            db.session.commit()
            print(f"{old_obj} updated")
        case _:
            raise Exception
