# NestWatch

**NestWatch** is a Python package that allows applications to react to **meaningful file changes** instead of raw filesystem events.

Rather than repeatedly polling files and risking cache desynchronization, NestWatch instantly notifies your application whenever a file changes and provides both its previous and new state.

# Why NestWatch?

Many applications update caches using polling tasks.

```python
@tasks.loop(minutes=1)
async def update_cache():
    ...
```

While this works, it introduces a delay between when data changes and when applications become aware of those changes.

This becomes problematic when multiple applications depend on the same data source.

For example:

- Application A updates "config.json"
- Application B continues using outdated cached data
- Application B must wait for its polling task to run
- Both applications become temporarily out of sync

NestWatch solves this by allowing applications to react to changes instantly.

# Features

- ⚡ Instant file change detection
- 🧠 Returns both old and new state
- ➕ Detects added keys
- ➖ Detects removed keys
- 🔄 Detects changed values
- 📍 Dot-path support
- 🧩 Extensible architecture
- 📄 JSON support built in
- 🏗️ Create custom watchers for your own file formats

---

# Installation
```shell
pip install nestwatch
```
---

# Quick Start
```python
from nestwatch.watchers import JSONWatcher


class ConfigCache:

    def __init__(self):

        self.watcher = JSONWatcher("data/config.json")

        self.watcher.on_change(
            self.update_cache
        )

    async def update_cache(self, event):

        print(event.added)

        print(event.removed)

        print(event.changed)

        print(event.old_state)

        print(event.new_state)

    async def startup(self):

        await self.watcher.start()
```
---

# Event Object

NestWatch emits an "Event" object containing:

Property| Description
"event.added"| Newly added keys
"event.removed"| Removed keys
"event.changed"| Modified values
"event.old_state"| Previous file state
"event.new_state"| Updated file state

Example

Suppose:
```json
{
    "BOT_STATUS": {
        "presence": "online"
    }
}
```

becomes:
```json
{
    "BOT_STATUS": {
        "presence": "idle"
    }
}
```

Then:

event.changed

returns:
```json
{
    "BOT_STATUS.presence": {
        "old": "online",
        "new": "idle"
    }
}
```

---

# Creating Custom Watchers

NestWatch is designed to be extensible.

You can support any file format by subclassing "Watcher".

```python
from nestwatch.watchers import Watcher


class MyCustomWatcher(Watcher):

    def _serialize(self):

        return my_language.load(
            self.file_path
        )
```

That's it.

NestWatch will automatically handle:

- Watching the file
- Detecting changes
- Comparing states
- Generating events
- Calling your listeners

---

# Use Cases

NestWatch works especially well for:

- 🤖 Discord bots
- 🌐 FastAPI applications
- 📦 Shared caches
- ⚙️ Configuration files
- 🔄 Runtime reload systems
- 🧠 Multi-application projects

---

# Philosophy

Traditional file watchers answer:

«"Did the file change?"»

NestWatch answers:

«"What changed inside the file?"»