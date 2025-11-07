import numpy as np

__all__ = [
]

def _is_number(s):
    """Checks if a string is a float number or has other characters."""
    try:
        float(s)
        return True
    except ValueError:
        return False


def _return_significant_value(b):
    """
    Return a number rounded to its significant value.

    Parameters
    ----------
    b : `~int` or `~float`
        Number to round to sognificant values.

    Returns
    -------
    number : `~float`
        Rounded number.
    number_str : `str`
        Rounded number as a string for significant last position decimal zeros.
    rounding_index : `int`
        Index of the last significant value.

    """

    # Convert the number into a string to avoid scientific notation
    c = str(np.format_float_positional(b)) + '00'

    first_index = 0
    stop = False
    for i in range(len(c)):
        if stop:
            continue
        if c[i] == '0' or c[i] == '.':
            continue
        else:
            stop = True
            first_index = i

    first_loop = False
    # Store index of the second significant number
    if c[first_index+1] != '.':
        second_index = first_index + 1
    else:
        second_index = first_index + 2

    if c[0] == '0' and c[1] == '.':
        first_loop = True

    # Main loop
    if first_loop:
        # First significant number is located after a decimal point
        if int(c[first_index]+c[second_index]) < 25:
            rounding_index = first_index
            number = np.format_float_positional(round(b, rounding_index))
            number_str = str(number)
            # Add the zero for .*10 and .*20 because it gets discarded in a
            # float number when rounding, and it is important to keep.
            if len(number_str) < second_index + 1:
                number_str = number_str + '0'
        else:
            rounding_index = first_index - 1
            # Ensure numbers ending with 5 get rounded up
            if int(c[second_index]) == 5:
                d = c[:second_index] + '6' + c[second_index:]
                c = d
                b = float(c)
            number = np.format_float_positional(round(b, rounding_index))
            number_str = str(number)
            # To add the needed zero when changing >=0.095 to 0.10
            if first_index > 2 and int(c[first_index]+c[second_index]) >= 95:
                number_str = number_str + '0'
    else:
        # For values >= 1.0
        if b > 2.5:
            rounding_index = None
            number = round(b)
            number_str = str(number)
        elif b == 2.5:
            rounding_index = None
            number = 3
            number_str = str(number)
        else:
            rounding_index = first_index + 1
            number = round(b,1)
            number_str = str(number)

    return number, number_str, rounding_index
