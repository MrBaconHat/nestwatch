from copy import deepcopy

class Event:
    def __init__(self, added, removed, changed):
        self.added = added
        self.removed = removed
        self.changed = changed

        #self.old_state = old_state
        #self.new_state = new_state
        # NOTE: Originally I had the old and new state, which contained the entire state of the file. This is not ideal for large files.
        # as a improvement, i will add a property that will convert self.add, self.removed and self.changed to a dict, ensuring that the dict only contains the new state of the KEY rather than the entire state of the file.
        # new properties will be called self.raw_old and self.raw_new.

        self.__raw_old = None
        self.__raw_new = None

    def _set_nested(self, data, path, value):
        keys = path.split(".")

        current = data

        for key in keys[:-1]:
            current = current.setdefault(key, {})

        current[keys[-1]] = value

    @property
    def has_changed(self):
        return bool(self.added or self.removed or self.changed)

    @property
    def old(self):
        if self.__raw_old is not None:
            return self.__raw_old
            
        old_data = {}

        for key, value in self.changed.items():
            self._set_nested(
                old_data,
                key,
                value["old"]
            )

        self.__raw_old = old_data
        return old_data

    @property
    def new(self):
        if self.__raw_new is not None:
            return self.__raw_new

        new_data = deepcopy(self.old)

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