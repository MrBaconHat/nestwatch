# NestWatch

![Python](https://img.shields.io/badge/python-3.10%2B-blue)

![License](https://img.shields.io/badge/license-MIT-green)

![PyPI](https://img.shields.io/pypi/v/nestwatch)

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

        # Affected changes only
        print(event.added)
        print(event.removed)
        print(event.changed)

        # Reconstructed views)
        print(event.old)
        print(event.new)
        print(event.updated)

    async def startup(self):

        await self.watcher.start()
```
---

# Event Object

NestWatch emits an `Event` object containing:

| Property | Description |
|----------|-------------|
| `event.added` | Keys that were added (dot-path → value) |
| `event.removed` | Keys that were removed (dot-path → old value) |
| `event.changed` | Keys that were modified (old + new) |
| `event.old` | Partial reconstruction of only affected old values |
| `event.new` | Partial reconstruction of only affected new values |
| `event.updated_state` | Final state after applying the event to the old data |

## Event Examples

Suppose this file:

```json
{
    "BOT_STATUS": {
        "presence": "online",
        "activity": {
            "type": "playing",
            "name": "Roblox"
        }
    }
}
```

becomes:

```json
{
    "BOT_STATUS": {
        "presence": "idle",
        "custom": "Watching NestWatch 👀"
    },
    "API": {
        "enabled": true
    }
}
```

Then:

### `event.added`

```python
{
    "BOT_STATUS.custom": "Watching NestWatch 👀",
    "API.enabled": True
}
```

### `event.removed`

```python
{
    "BOT_STATUS.activity.type": "playing",
    "BOT_STATUS.activity.name": "Roblox"
}
```

### `event.changed`

```python
{
    "BOT_STATUS.presence": {
        "old": "online",
        "new": "idle"
    }
}
```

### `event.old`

```python
{
    "BOT_STATUS": {
        "presence": "online",
        "activity": {
            "type": "playing",
            "name": "Roblox"
        }
    }
}
```

### `event.new`

```python
{
    "BOT_STATUS": {
        "presence": "idle",
        "custom": "Watching NestWatch 👀"
    },
    
    "API": {
        "enabled": True
    }
}
```

### `event.updated_state`

```python
{
    "BOT_STATUS": {
        "presence": "idle",
        "custom": "Watching NestWatch 👀"
    },
    "API": {
        "enabled": True
    }
}
```

**IMPORTANT NOTE:** “These are partial reconstructions of only affected regions, not full file snapshots.”

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

The **Watcher** class supports asynchronous serializers as well.

This allows you to perform asynchronous file reads before NestWatch processes the data.

```python
import aiofiles
from nestwatch.watchers import Watcher

class MyCustomWatcher(Watcher):

    async def _serialize(self):
        async with aiofiles.open(self.file_path) as f:
            content = await f.read()
            return my_language.load(content)
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

> "Did the file change?"

NestWatch answers:

> "What changed inside the file?"

---

# NestWatch's Dependency

| Package | Version | Usage |
|---------|---------|-------|
| `watchdog` | `>=6.0.0` | Listens for file changes |
| `aiofiles` | `>=25.1.0` | For reading files in async for internal asynchronous serializers.