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

    @property
    def has_changed(self):
        return bool(self.added or self.removed or self.changed)

    @property
    def old(self):
        if self.__raw_old is not None:
            return self.__raw_old
            
        old_data = {}
        changed = self.changed
        for key, value in changed.items():
            if "." in key:
                keys = key.split(".")
                keys_count = len(keys)
                last_key = keys[-1]
                
                # exclude the last key from keys before running it through the loop
                keys = keys[:-1]
                
                for k in keys:
                    if k not in old_data:
                        old_data[k] = {}

                    if len(keys) == keys_count:
                        old_data[k][last_key] = value["old"]

            else:
                old_data[key] = value["old"]

        self.__raw_old = old_data
        return old_data

    @property
    def new(self):
        if self.__raw_new is not None:
            return self.__raw_new

        new_data = {}
        added = self.added
        
        for key, value in added.items():
            if "." in key:
                keys = key.split(".")
                keys_count = len(keys)
                last_key = keys[-1]
                # exclude the last key from keys before running it through the loop
                keys = keys[:-1]

                for k in keys:
                    if k not in new_data:
                        new_data[k] = {}

                    if len(keys) == keys_count:
                        new_data[k][last_key] = value

            else:
                new_data[key] = value

        self.__raw_new = new_data
        return new_data