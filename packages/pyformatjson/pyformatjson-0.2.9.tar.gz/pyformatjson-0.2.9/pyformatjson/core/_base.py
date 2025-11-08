import os
import re


def split_text_by_length(text, max_length=120) -> list[str]:
    """Split text into lines of specified maximum length.

    This function breaks long text into multiple lines, ensuring each line
    does not exceed the specified maximum length. It attempts to break at
    word boundaries when possible.

    Args:
        text (str): The input text to be split into lines.
        max_length (int, optional): Maximum length for each line. Defaults to 120.

    Returns:
        list[str]: A list of text lines, each not exceeding max_length characters.

    Example:
        >>> split_text_by_length("This is a very long text that needs to be split", 20)
        ['This is a very long', 'text that needs to be', 'split']
    """
    lines = []
    while text:
        if len(text) <= max_length:
            lines.append(text)
            break

        split_pos = text.rfind(" ", 0, max_length + 1)
        if split_pos == -1:
            split_pos = max_length

        line = text[:split_pos]
        lines.append(line)

        text = text[split_pos:]

    new_lines = []
    for line in lines:
        new_lines.append(line)
    return new_lines


def split_data_list(split_pattern: str, data_list: list[str], last_next: str = "next") -> list[str]:
    r"""Split data list according to the split pattern.

    This function splits each string in the data list using the provided regex pattern
    and reconstructs the data based on the last_next parameter. The pattern must use
    capturing parentheses to define split points.

    Args:
        split_pattern (str): Regular expression pattern for splitting. Must use capturing
            parentheses, e.g., r"(\n)" for newline splits.
        data_list (list[str]): List of strings to be split and processed.
        last_next (str, optional): Determines how to handle split parts. "next" places
            the split character at the beginning of the next part, "last" places it at
            the end of the current part. Defaults to "next".

    Returns:
        list[str]: New list of processed strings with empty strings filtered out.

    Raises:
        re.error: If the split_pattern is not a valid regular expression.

    Example:
        >>> split_data_list(r"(\n)", ["line1\nline2", "line3\nline4"], "next")
        ['line1', 'line2', 'line3', 'line4']
    """
    new_data_list = []
    for line in data_list:
        split_list = re.split(split_pattern, line)
        list_one = split_list[0: len(split_list): 2]
        list_two = split_list[1: len(split_list): 2]

        temp = []
        if last_next == "next":
            list_two.insert(0, "")
            temp = [list_two[i] + list_one[i] for i in range(len(list_one))]
        if last_next == "last":
            list_two.append("")
            temp = [list_one[i] + list_two[i] for i in range(len(list_one))]
        new_data_list.extend(temp)
    new_data_list = [line for line in new_data_list if line.strip()]
    return new_data_list


def standardize_path(path_input: str) -> str:
    """Standardize and ensure a directory path exists.

    This function expands environment variables and user home directory references
    in the path, then creates the directory if it doesn't exist.

    Args:
        path_input (str): The input path to be standardized and created.

    Returns:
        str: The standardized absolute path.

    Example:
        >>> standardize_path("~/Documents/data")
        '/Users/username/Documents/data'
    """
    path_input = os.path.expandvars(os.path.expanduser(path_input))
    if not os.path.exists(path_input):
        os.makedirs(path_input)
    return path_input


def sort_strings_with_embedded_numbers(s: str) -> list[str]:
    """Split string into pieces for natural sorting with embedded numbers.

    This function splits a string into pieces where numbers are converted to integers
    for proper natural sorting (e.g., "item2" comes before "item10").

    Args:
        s (str): The string to be split into sortable pieces.

    Returns:
        list[str]: List of string pieces with numbers converted to integers.

    Example:
        >>> sort_strings_with_embedded_numbers("item10")
        ['item', 10]
    """
    re_digits = re.compile(r"(\d+)")
    pieces = re_digits.split(s)
    pieces[1::2] = map(int, pieces[1::2])
    return pieces


def sort_int_str(str_int: list[str], reverse: bool = False) -> list[str]:
    """Sort list of strings with embedded numbers naturally.

    This function sorts a list of strings using natural sorting that handles
    embedded numbers correctly (e.g., "item2" comes before "item10").

    Args:
        str_int (list[str]): List of strings to be sorted.
        reverse (bool, optional): If True, sorts in descending order. Defaults to False.

    Returns:
        list[str]: Sorted list of strings.

    Example:
        >>> sort_int_str(["item10", "item2", "item1"])
        ['item1', 'item2', 'item10']
    """
    return sorted(str_int, key=sort_strings_with_embedded_numbers, reverse=reverse)


class IterateSortDict:
    """A class for recursively sorting dictionary keys with natural sorting.

    This class provides methods to sort dictionary keys recursively, handling
    nested dictionaries and using natural sorting for strings with embedded numbers.

    Attributes:
        reverse (bool): If True, sorts keys in descending order. Defaults to False.

    Example:
        >>> sorter = IterateSortDict(reverse=False)
        >>> data = {"item10": {"sub2": 1, "sub1": 2}, "item2": 3}
        >>> sorted_data = sorter.dict_update(data)
    """

    def __init__(self, reverse: bool = False) -> None:
        """Initialize the IterateSortDict instance.

        Args:
            reverse (bool, optional): If True, sorts keys in descending order.
                Defaults to False.
        """
        self.reverse = reverse

    def dict_update(self, old: dict) -> dict:
        """Update and sort a dictionary recursively.

        This method sorts the dictionary keys and recursively processes
        any nested dictionaries.

        Args:
            old (dict): The dictionary to be sorted and updated.

        Returns:
            dict: The updated dictionary with sorted keys at all levels.
        """
        old = self.dict_sort_iteration(old)
        old = self.dict_sort(old)
        return old

    def dict_sort_iteration(self, old: dict) -> dict:
        """Recursively sort nested dictionaries.

        This method iterates through the dictionary and recursively sorts
        any nested dictionary values.

        Args:
            old (dict): The dictionary to be processed recursively.

        Returns:
            dict: The dictionary with nested dictionaries sorted.
        """
        for key in old:
            if isinstance(old[key], dict):
                old[key] = self.dict_update(old[key])
        return old

    def dict_sort(self, old: dict) -> dict:
        """Sort dictionary keys using natural sorting.

        This method sorts the top-level keys of the dictionary using
        natural sorting that handles embedded numbers.

        Args:
            old (dict): The dictionary whose keys are to be sorted.

        Returns:
            dict: A new dictionary with sorted keys.
        """
        return {k: old[k] for k in sort_int_str(list(old.keys()), self.reverse)}
