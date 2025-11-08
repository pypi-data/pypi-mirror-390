import copy
from typing import Any

from pyadvtools.core.sort import sort_int_str


class IterateSortDict:
    """Recursively sort dictionary keys using natural string ordering.

    This class provides functionality to recursively sort dictionary keys
    at all levels of nesting using natural string ordering that handles
    embedded numbers properly.

    Attributes:
        reverse: If True, sorts keys in descending order.
    """

    def __init__(self, reverse: bool = False) -> None:
        """Initialize the dictionary sorter.

        Args:
            reverse: If True, sorts keys in descending order.
        """
        self.reverse = reverse

    def dict_update(self, old: dict) -> dict:
        """Update and sort a dictionary recursively.

        Sorts the dictionary keys at all levels using natural string ordering.

        Args:
            old: Dictionary to sort.

        Returns:
            dict: Dictionary with all keys sorted recursively.
        """
        old = self.dict_sort_iteration(old)
        old = self.dict_sort(old)
        return old

    def dict_sort_iteration(self, old: dict) -> dict:
        """Recursively sort nested dictionary keys.

        Args:
            old: Dictionary to sort recursively.

        Returns:
            dict: Dictionary with nested keys sorted.
        """
        for key in old:
            if isinstance(old[key], dict):
                old[key] = self.dict_update(old[key])
        return old

    def dict_sort(self, old: dict) -> dict:
        """Sort dictionary keys using natural string ordering.

        Args:
            old: Dictionary to sort.

        Returns:
            dict: Dictionary with keys sorted.
        """
        return {k: old[k] for k in sort_int_str(list(old.keys()), self.reverse)}


class IterateUpdateDict:
    """Recursively update nested dictionaries.

    This class provides functionality to recursively update nested dictionaries,
    merging new values into existing structures while preserving nested
    dictionary hierarchies.
    """

    def __init__(self) -> None:
        """Initialize the dictionary updater."""
        pass

    def dict_update(self, old: dict, new: dict) -> dict:
        """Update a dictionary with new values recursively.

        Merges new dictionary values into the old dictionary, handling
        nested dictionaries by recursively updating them.

        Args:
            old: Original dictionary to update.
            new: Dictionary containing new values to merge.

        Returns:
            dict: Updated dictionary with merged values.
        """
        old = self.dict_update_iteration(old, new)
        old = self.dict_add(old, new)
        return old

    def dict_update_iteration(self, old: dict, new: dict) -> dict:
        """Recursively update nested dictionary values.

        Args:
            old: Original dictionary to update.
            new: Dictionary with new values.

        Returns:
            dict: Dictionary with recursively updated values.
        """
        for key in old:
            if key not in new:
                continue

            if isinstance(old[key], dict) and isinstance(new[key], dict):
                old[key] = self.dict_update(old[key], new[key])
            else:
                old[key] = new[key]  # update

        return old

    @staticmethod
    def dict_add(old: dict, new: dict) -> dict:
        """Add new keys to dictionary.

        Adds keys from new dictionary that don't exist in old dictionary.

        Args:
            old: Dictionary to add keys to.
            new: Dictionary containing keys to add.

        Returns:
            dict: Dictionary with added keys.
        """
        for key in new:
            if key not in old:
                old[key] = new[key]
        return old


class IterateCombineExtendDict:
    """Combine and extend nested dictionaries with list values.

    This class processes nested dictionaries where the deepest level contains
    lists, and combines all lists into a single flat list.
    """

    def __init__(self) -> None:
        """Initialize the dictionary combiner."""
        pass

    def dict_update(self, data_dict: dict[str, Any]) -> list[Any]:
        """Update and combine nested dictionary lists.

        Processes a nested dictionary structure and combines all list values
        from the deepest level into a single flat list.

        Args:
            data_dict: Nested dictionary with list values at deepest level.

        Returns:
            List[Any]: Combined list of all values from nested structure.
        """
        data_dict = self.dict_update_iteration(copy.deepcopy(data_dict))
        data_list = self.data_combine(data_dict)
        return data_list

    def dict_update_iteration(self, old: dict[str, Any]) -> dict[str, Any]:
        """Recursively process nested dictionary structure.

        Args:
            old: Dictionary to process recursively.

        Returns:
            Dict[str, Any]: Processed dictionary structure.
        """
        for key in old:
            if isinstance(old[key], dict):
                old[key] = self.dict_update(old[key])
        return old

    @staticmethod
    def data_combine(old: dict[str, Any]) -> list[Any]:
        """Combine all list values from dictionary.

        Args:
            old: Dictionary with list values to combine.

        Returns:
            List[Any]: Combined list of all values.
        """
        data_list = []
        for key in old:
            data_list.extend(old[key])
        return data_list


if __name__ == "__main__":
    a = {"a": {"e": {"d": ["dd"]}, "c": ["cc"]}, "b": ["bb"]}
    aa = IterateCombineExtendDict().dict_update(a)
    print(aa)  # ['dd', 'cc', 'bb']

    b = IterateSortDict().dict_update(a)
    print(b)  # {'a': {'c': ['cc'], 'e': {'d': ['dd']}}, 'b': ['bb']}

    c = {"aa": ["111"], "b": ["222"]}
    cc = IterateUpdateDict().dict_update(a, c)
    print(cc)  # {'a': {'c': ['cc'], 'e': {'d': ['dd']}}, 'b': ['222'], 'aa': ['111']}

    d = IterateSortDict().dict_update(cc)
    print(d)  # {'a': {'c': ['cc'], 'e': {'d': ['dd']}}, 'aa': ['111'], 'b': ['222']}
