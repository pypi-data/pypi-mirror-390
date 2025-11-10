def get_leading_zeroes(month: int) -> str:
    """
    Function to add leading zeroes to a month (1 (January) -> 01).

    Args:
        month (int): The month integer (created from `datetime.now().month`)

    Returns:
        The same month integer with a leading 0 if it is less than 10 (Nov/Dec aka 11/12 unaffected).
    """
    if len(str(month)) > 1:
        return str(month)
    else:
        return f"0{month}"
