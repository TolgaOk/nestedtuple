# Nested Named Tuple

Create a nested and typed `NamedTuple` using class definitions. Useful for defining configurations.

## Example

The decorator `nestedtuple` recursively converts class definitions into a Python `NamedTuple`.

```Python
from nestedtuple import nestedtuple

@nestedtuple
class Config:

    seed: int

    class logging:
        verbose: bool
        level: str = "error"

        class logger:
            port: int = 9076
            hostname: str = "localhost"

    flag: bool = False
```

Once the definition is created, you can instantiate the object and use it as a proper `NamedTuple`:

```IPython
In  [1]: config = Config(42, Config.logging(verbose=True))
In  [2]: config.logging
Out [3]: (verbose=True, level='error', logger=logger(port=9076, hostname='localhost'))
```

Notice, `Config.logging` is the class, hence, we instantiate it by providing its arguments, while `config.logging` is the `NamedTuple` instance.

```IPython
In  [4]: config._asdict()
Out [5]: {'seed': 42,
 'logging': {'verbose': True,
  'level': 'error',
  'logger': {'port': 9076, 'hostname': 'localhost'}},
 'flag': False}
```

The above example is equivalent to separately defining the inner classes with a `NamedTuple` base class and assigning them to their parent classes.

## Installation

> [!WARNING]
> Required: Python 3.11+

Install the package in development mode via:

```bash
pip install -e .
```

> Note: There are no additional requirements!
