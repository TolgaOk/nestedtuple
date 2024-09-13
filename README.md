# Nested Named Tuple

Create a nested and typed namedtuple using class definitions. Useful for defining configs.

## Example

The decorator ```nestedtuple``` recursively converts class definition into a Python ```NamedTuple```.

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

Once the definition is created, you can initiate the object and use it as a proper ```NamedTuple```:

```IPython
In  [1]: config = Config(42, Config.logging(verbose=True))
In  [2]: config.logging
Out [3]: (verbose=True, level='error', logger=logger(port=9076, hostname='localhost'))
```

Notice, ```Config.logging``` is the class, hence, we initiate it by providing its arguments, while ```config.logging``` is the namedtuple instance.

```IPython
In  [4]: config._asdict()
Out [5]: {'seed': 42,
 'logging': {'verbose': True,
  'level': 'error',
  'logger': {'port': 9076, 'hostname': 'localhost'}},
 'flag': False}
```

The above example is equivalent to separately defining the inner classes with a ```NamedTuple``` base class and assigning them to their parent classes.

## Install

> [!Warning]
> Required: Python 3.9+

Install the package in development mode via:

```bash
pip install -e .
```

> Note: There is no requirements!
