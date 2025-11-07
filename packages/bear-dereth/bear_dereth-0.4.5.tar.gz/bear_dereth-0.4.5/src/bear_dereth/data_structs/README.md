# bear_dereth.data_structs

Reusable collections, queues, stacks, and immutability helpers used throughout
Bear Dereth. These utilities back the datastore caching layer, logging
infrastructure, dependency injection containers, and more.

## Core Exports
Available directly from `bear_dereth.data_structs`:

| Name | Purpose |
| --- | --- |
| `Counter` | Pydantic-backed counter with reset/tick helpers. |
| `LRUCache` | OrderedDict-based least-recently-used cache. |
| `FrozenDict` / `FrozenModel` / `freeze` / `thaw` | Immutable data for hashing & caching. |
| `PriorityQueue`, `SimpooQueue` | Thread-safe priority queue / simple queue. |
| `SimpleStack`, `SimpleStackCursor` | Stack implementations with cursor support. |

Other handy modules live in this package (`autosort_list`, `to_dot`, `wal`, etc.)
and are highlighted below.

---

## Immutability & Caching

```python
from bear_dereth.data_structs import FrozenDict, FrozenModel, freeze, thaw, LRUCache

cache = LRUCache(capacity=128)
cache["key"] = {"a": 1}

class QueryHash(FrozenModel):
    path: tuple[str, ...]
    value: object

record = QueryHash(path=("user", "id"), value=42)
cache_key = record.frozen  # FrozenDict suitable for hashing
```

- `freeze(obj)` converts dict/list/set into immutable equivalents (`FrozenDict`,
  tuple, frozenset).
- `FrozenModel` wraps Pydantic models with immutability + hashing.
- `LRUCache` provides `.get()`, `.set()`, eviction, and key ordering (uses
  `math.infinity.INFINITE` as default capacity).

---

## Stacks & Queues

```python
from bear_dereth.data_structs import SimpleStack, SimpleStackCursor, PriorityQueue, SimpooQueue

stack = SimpleStack()
stack.push("bear")
stack.push("dereth")
assert stack.pop() == "dereth"

cursor = SimpleStackCursor(stack)
cursor.move_bottom()

pq = PriorityQueue()
pq.put((1, "low"))
pq.put((0, "high"))
assert pq.get()[1] == "high"

queue = SimpooQueue()
queue.enqueue("first")
queue.enqueue("second")
assert queue.dequeue() == "first"
```

- `SimpleStack` / `FancyStack` / `BoundedStack`: variations on stack behaviour,
  all deriving from `BaseCollection`.
- `SimpleStackCursor`: adds cursor traversal (forward/back) on top of a stack.
- `PriorityQueue`: `heapq`-based with thread-safe locking and helper methods
  (`peek`, `remove_element`, `sorted_items`).
- `SimpooQueue`: deque-like FIFO structure built on `BaseCollection`.

---

## Sorted & Namespace Helpers

```python
from bear_dereth.data_structs.autosort_list import AutoSort
from bear_dereth.data_structs.to_dot import DotDict
from bear_dereth.data_structs.space import Names

numbers = AutoSort([5, 3, 9])
numbers.append(1)
assert list(numbers) == [1, 3, 5, 9]

data = DotDict({"user": {"name": "Bear"}})
assert data.user.name == "Bear"

services = Names()
services.add("logger", object())
assert services.logger is services["logger"]
```

- `AutoSort`: Maintains ordering on insert using `bisect` utilities, accepts a
  `key` function.
- `DotDict`: Attribute-style access for nested dicts, plus JSON/freeze helpers.
- `Names`: Lightweight namespace object for storing attributes dynamically with
  set/get and dictionary operations.

---

## Counters & Cursors

```python
from bear_dereth.data_structs import Counter

counter = Counter(start=10)
counter.tick()
assert counter.get() == 11
counter.reset(0)
```

- `Counter`: Pydantic-based, enforces non-negative values and supports cloning,
  `before`/`after` reads, arithmetic comparisons, and iteration.
- `cursor.py`: Cursor abstractions for iterating through collections with
  history tracking (used by stack cursors and other containers).

---

## Write-Ahead Log (WAL)

Need durable event streams?

```python
from bear_dereth.data_structs.wal import WriteAheadLog, Operation

with WriteAheadLog("wal.log") as wal:
    wal.add_op(txid=1, op=Operation.INSERT, data={"id": 5})
    wal.commit(txid=1)

records = wal.read_all()
for rec in records:
    ...
```

- `WriteAheadLog` stores `WALRecord`s (timestamped, JSON serialised) to disk,
  with background thread writing and recovery helpers.
- Supports `add_op`, `commit`, `start/stop`, and easy replay via `read_all`.

---

## Tips
- Most collections derive from `BaseCollection`: check its push/pop hooks if you
  plan to implement new variants.
- `to_dot.DotDict.freeze()` pairs nicely with `FrozenModel` when you need to
  hash nested structures.
- `PriorityQueue` and `SimpooQueue` are thread-safe (simple locking), making
  them suitable for basic producer/consumer patterns.
- `wal.WriteAheadLog` pairs naturally with `datastore` tables or queue handlers
  when you need durable operations in development.

May your collections stay tidy, Bear! 🐻📚✨
