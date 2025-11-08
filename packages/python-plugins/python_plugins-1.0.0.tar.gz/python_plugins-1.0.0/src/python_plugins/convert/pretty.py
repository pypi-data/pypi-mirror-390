from re import sub


def prettify_class_name(name):
    """Split words in PascalCase string into separate words.

    :param name:
        String to split
    """
    return sub(r"(?<=.)([A-Z])", r" \1", name)

