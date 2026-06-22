from copy import deepcopy

class Event:
    def __init__(self, added, removed, changed):
        """
        Represents a change event in a nested dictionary.
        """
        self.added = added
        self.removed = removed
        self.changed = changed

        self.__raw_old = None
        self.__raw_new = None

    def _set_nested(self, data, path, value):
        """
        Internal helper to set a value inside a nested dictionary
        using a dot-path string (e.g. "a.b.c").
        """
        keys = path.split(".")

        current = data

        for key in keys[:-1]:
            current = current.setdefault(key, {})

        current[keys[-1]] = value

    def _deep_merge(self, old, new):
        """
        Deeply merges two dictionaries.

        - Nested dictionaries are merged recursively
        - Other values in `new` overwrite `old`

        Returns a new merged dictionary.
        """
        result = deepcopy(old)

        for key, value in new.items():

            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(
                    result[key],
                    value
                )

            else:
                result[key] = value

        return result

    @property
    def has_changed(self) -> bool:
        """
        Returns True if the event has any changes.
        """
        return bool(self.added or self.removed or self.changed)

    @property
    def old(self):
        """
        Returns a partial reconstruction of the previous state.

        Includes:
        - Values from removed keys
        - Old values from changed keys

        Note:
        This does NOT return the full previous file,
        only the parts affected by the event.
        """
        if self.__raw_old is not None:
            return self.__raw_old
            
        old_data = {}

        for key, value in self.changed.items():
            self._set_nested(
                old_data,
                key,
                value["old"]
            )

        for key, value in self.removed.items():
            self._set_nested(
                old_data,
                key,
                value
            )

        self.__raw_old = old_data
        return old_data

    @property
    def new(self):
        """
        Returns a partial reconstruction of the new state.

        Includes:
        - Values from added keys
        - New values from changed keys

        Note:
        This does NOT return the full new file,
        only the parts affected by the event.
        """
        if self.__raw_new is not None:
            return self.__raw_new

        new_data = {}

        for key, value in self.added.items():
            self._set_nested(
                new_data,
                key,
                value
            )

        for key, value in self.changed.items():
            self._set_nested(
                new_data,
                key,
                value["new"]
            )

        self.__raw_new = new_data
        return new_data

    @property
    def updated(self):
        """
        Returns a reconstructed state after applying the event.

        This is created by deep-merging:
        - old (base structure)
        - new (changes applied)

        Useful for getting a snapshot of the affected final state.
        """
        return self._deep_merge(
            self.old,
            self.new
        )