### BEGIN Dependencies ###
import datetime
from pytz import timezone
### END Dependencies ###

TIMEZONE = timezone('America/Los_Angeles')

def time_stamp():
    """
    Generates a timestamp in the format 'YYYY-MM-DD_HH-MM-SSS', where the last digit represents 1/10th of a second based on the current date and time.

    returns:
        str: A string representing the current date and time in the format 'YYYY-MM-DD_HH-MM-SSS'.

    Example:
        >>> time_stamp()
        '2025-01-28_17-27-210'
    """
    now = datetime.datetime.now(TIMEZONE)
    formatted_datetime = now.strftime(f"%Y-%m-%d_%H-%M-%S") + str(int( now.microsecond / 100000 ))
    return formatted_datetime


def date():
    """
    Generates the current date in the format 'YYYY-MM-DD'.

    Returns:
        str: A string representing the current date in the format 'YYYY-MM-DD'.

    Example:
        >>> date()
        '2025-01-28'
    """
    now = datetime.datetime.now(TIMEZONE)
    formatted_datetime = now.strftime(f"%Y-%m-%d")
    return formatted_datetime
