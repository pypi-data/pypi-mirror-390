def all_are_none(*args) -> bool:
    """Returns False if any argument is not None."""
    return all(arg is None for arg in args)


def all_are_not_none(*args) -> bool:
    """Returns False if any element is None."""
    return all(arg is not None for arg in args)


def count_none(*args) -> int:
    """Count number of None elements"""
    return sum(1 for arg in args if arg is None)


def count_not_none(*args) -> int:
    """Count number of not None elements"""
    return sum(1 for arg in args if arg is not None)
