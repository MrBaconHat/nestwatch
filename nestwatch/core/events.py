class Event:
    def __init__(self, added, removed, changed, old_state, new_state):
        self.added = added
        self.removed = removed
        self.changed = changed

        self.old_state = old_state
        self.new_state = new_state

    @property
    def has_changed(self):
        return bool(self.added or self.removed or self.changed)