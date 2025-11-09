# PySingletonMeta

A lightweight singleton metaclass for clean and comfy imports.

---
## Installation

```bash
pip install PySingletonMeta
```

---
## Example

```python
from pysingletonmeta import SingletonMeta

class StreamingService(metaclass=SingletonMeta):
    pass

a = StreamingService()
b = StreamingService()

assert a is b  # True
```

---

That’s all you need.
