# User guide

`clig` is a single module, written in pure python, that wraps around the
_stdlib_ module [`argparse`](https://docs.python.org/3/library/argparse.html) to
generate command line interfaces through simple functions.

## Basic usage

Create or import some function and call `clig.run()` with it:



```python
# example01.py
import clig

def printperson(name, title="Mister"):
    print(f"{title} {name}")

clig.run(printperson)
```

In general, the function arguments that have a "default" value are turned into
optional _flagged_ (`--`) command line arguments, while the "non default" will
be positional arguments.



```
> python example01.py -h

    usage: printperson [-h] [--title TITLE] name
    
    positional arguments:
      name
    
    options:
      -h, --help     show this help message and exit
      --title TITLE
    
```
The script can then be used in the same way as used with `argparse`:



```
> python example01.py John 

    Mister John
    
```

```
> python example01.py Maria --title Miss

    Miss Maria
    
```
You can also pass arguments in code (like with the original
[`parse_args()`](https://docs.python.org/3/library/argparse.html#the-parse-args-method)
method)



```python
>>> import clig
... 
>>> def printperson(name, title="Mister"):
...     print(f"{title} {name}")
... 
>>> clig.run(printperson, ["Isaac", "--title", "Sir"])
Sir Isaac

```
The `run()` function accepts other arguments to customize the interface


## Helps

Arguments and command Helps are taken from the docstring when possible:



```python
# example02.py
import clig

def greetings(name, greet="Hello"):
    """Description of the command: A greeting prompt!

    Args:
        name: The name to greet
        greet: The greeting used. Defaults to "Hello".
    """
    print(f"Greetings: {greet} {name}!")

clig.run(greetings)
```


```
> python example02.py --help

    usage: greetings [-h] [--greet GREET] name
    
    Description of the command: A greeting prompt!
    
    positional arguments:
      name           The name to greet
    
    options:
      -h, --help     show this help message and exit
      --greet GREET  The greeting used. Defaults to "Hello".
    
```
There is an internal list of docstring templates from which you can choose if
the inferred docstring is not correct. It is also possible to specify your own
custom docstring template.


## Argument inference

Based on [type annotations](https://docs.python.org/3/library/typing.html), some
arguments can be inferred from the function signature to pass to the original
[`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method)
method:



```python
# example03.py
import clig

def recordperson(name: str, age: int, height: float):
    print(locals())

clig.run(recordperson)
```

The types in the annotation may be passed to
[`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method)
method as [`type`](https://docs.python.org/3/library/argparse.html#type) keyword
argument, when possible:



```
> python example03.py John 37 1.73

    {'name': 'John', 'age': 37, 'height': 1.73}
    
```
And the type conversions are performed as usual



```
> python example03.py Mr John Doe

    usage: recordperson [-h] name age height
    recordperson: error: argument age: invalid int value: 'John'
    
```
### Booleans

Booleans are transformed in arguments with
[`action`](https://docs.python.org/3/library/argparse.html#action) of kind
`"store_true"` or `"store_false"` (depending on the default value).



```python
# example04.py
import clig

def recordperson(name: str, graduate: bool = False):
    print(locals())

clig.run(recordperson)
```


```
> python example04.py -h

    usage: recordperson [-h] [--graduate] name
    
    positional arguments:
      name
    
    options:
      -h, --help  show this help message and exit
      --graduate
    
```

```
> python example04.py Leo --graduate

    {'name': 'Leo', 'graduate': True}
    
```
#### Required booleans

If no default is given to the boolean, a
[`required`](https://docs.python.org/3/library/argparse.html#required)`=True`
keyword argument is passed to `add_argument()` method in the flag boolean option
and a
[`BooleanOptionalAction`](https://docs.python.org/3/library/argparse.html#argparse.BooleanOptionalAction)
(available in `argparse`) is passed as
[`action`](https://docs.python.org/3/library/argparse.html#action) keyword
argument, adding support for a boolean complement action in the form
`--no-option`:



```python
# example05.py
import clig

def recordperson(name: str, graduate: bool):
    print(locals())

clig.run(recordperson)
```


```
> python example05.py -h

    usage: recordperson [-h] --graduate | --no-graduate name
    
    positional arguments:
      name
    
    options:
      -h, --help            show this help message and exit
      --graduate, --no-graduate
    
```

```
> python example05.py Ana

    usage: recordperson [-h] --graduate | --no-graduate name
    recordperson: error: the following arguments are required: --graduate/--no-graduate
    
```
### Tuples, Lists and Sequences: [`nargs`](https://docs.python.org/3/library/argparse.html#nargs)

The original [`nargs`](https://docs.python.org/3/library/argparse.html#nargs)
keyword argument associates a different number of command-line arguments with a
single action. This is inferrend in types using `tuple`, `lists` and `Sequence`.

#### Tuples

If the type is a `tuple` of specified length `N`, the argument automatically
uses `nargs=N`.



```python
# example06.py
import clig

def main(name: tuple[str, str]):
    print(locals())

clig.run(main)
```


```
> python example06.py -h

    usage: main [-h] name name
    
    positional arguments:
      name
    
    options:
      -h, --help  show this help message and exit
    
```

```
> python example06.py rocky yoco

    {'name': ('rocky', 'yoco')}
    
```

```
> python example06.py rocky

    usage: main [-h] name name
    main: error: the following arguments are required: name
    
```
The argument can be positional (required, as above) or optional (with a
default).



```python
# example07.py
import clig

def main(name: tuple[str, str, str] = ("john", "mary", "jean")):
    print(locals())

clig.run(main)
```


```
> python example07.py --name yoco

    usage: main [-h] [--name NAME NAME NAME]
    main: error: argument --name: expected 3 arguments
    
```

```
> python example07.py --name yoco rocky sand

    {'name': ('yoco', 'rocky', 'sand')}
    
```
#### List, Sequences and Tuples of any length

If the type is a generic `Sequence`, a `list` or a `tuple` of _any_ length
(i.e., `tuple[<type>, ...]`), it uses `nargs="+"` if it is required (non default
value) or `nargs="*"` if it has a default value.



```python
# example08.py
import clig

def main(names: list[str]):
    print(locals())

clig.run(main)
```

In this example, we have `names` with `nargs="+"`



```
> python example08.py -h

    usage: main [-h] names [names ...]
    
    positional arguments:
      names
    
    options:
      -h, --help  show this help message and exit
    
```

```
> python example08.py chester philip

    {'names': ['chester', 'philip']}
    
```

```
> python example08.py

    usage: main [-h] names [names ...]
    main: error: the following arguments are required: names
    
```
In the next example, we have `names` as optional argument, with `nargs="*"`



```python
# example09.py
import clig

def main(names: list[str] | None = None):
    print(locals())

clig.run(main)
```


```
> python example09.py -h

    usage: main [-h] [--names [NAMES ...]]
    
    options:
      -h, --help           show this help message and exit
      --names [NAMES ...]
    
```

```
> python example09.py --names katy buba

    {'names': ['katy', 'buba']}
    
```

```
> python example09.py

    {'names': None}
    
```
### Literals and Enums: [`choices`](https://docs.python.org/3/library/argparse.html#choices)

If the type is a `Literal` or a `Enum` the argument automatically uses
[`choices`](https://docs.python.org/3/library/argparse.html#choices).



```python
# example10.py
from typing import Literal
import clig

def main(name: str, move: Literal["rock", "paper", "scissors"]):
    print(locals())

clig.run(main)
```


```
> python example10.py -h

    usage: main [-h] name {rock,paper,scissors}
    
    positional arguments:
      name
      {rock,paper,scissors}
    
    options:
      -h, --help            show this help message and exit
    
```
As is expected in `argparse`, an error message will be displayed if the argument
was not one of the acceptable values:



```
> python example10.py John knife

    usage: main [-h] name {rock,paper,scissors}
    main: error: argument move: invalid choice: 'knife' (choose from rock, paper, scissors)
    
```

```
> python example10.py Mary paper

    {'name': 'Mary', 'move': 'paper'}
    
```
#### Passing Enums

In the command line, `Enum` should be passed by name, regardless of if it is a
number Enum or ar string Enum



```python
# example11.py
from enum import Enum, StrEnum
import clig

class Color(Enum):
    red = 1
    blue = 2
    yellow = 3

class Statistic(StrEnum):
    minimun = "minimun"
    mean = "mean"
    maximum = "maximum"

def main(color: Color, statistic: Statistic):
    print(locals())

clig.run(main)
```


```
> python example11.py -h

    usage: main [-h] {red,blue,yellow} {minimun,mean,maximum}
    
    positional arguments:
      {red,blue,yellow}
      {minimun,mean,maximum}
    
    options:
      -h, --help            show this help message and exit
    
```
It is correctly passed to the function



```
> python example11.py red mean

    {'color': <Color.red: 1>, 'statistic': <Statistic.mean: 'mean'>}
    
```

```
> python example11.py green

    usage: main [-h] {red,blue,yellow} {minimun,mean,maximum}
    main: error: argument color: invalid choice: 'green' (choose from red, blue, yellow)
    
```
#### Literal with Enum

You can even mix `Enum` and `Literal`, following the
[`Literal` specification](https://typing.python.org/en/latest/spec/literal.html#legal-parameters-for-literal-at-type-check-time)



```python
# example12.py
from typing import Literal
from enum import Enum
import clig

class Color(Enum):
    red = 1
    blue = 2
    yellow = 3

def main(color: Literal[Color.red, "green", "black"]):
    print(locals())

clig.run(main)
```


```
> python example12.py red

    {'color': <Color.red: 1>}
    
```

```
> python example12.py green

    {'color': 'green'}
    
```
## Argument specification

In some complex cases supported by
[`argparse`](https://docs.python.org/3/library/argparse.html), the arguments may
not be completely inferred by `clig.run()` function.

In theses cases, you can directly specificy the arguments parameters using the
[`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated)
typing (or its `clig`'s alias `Arg`) with its "metadata" created by the `data()`
function.

The `data()` function accepts all possible arguments of the original
[`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method)
method:


### name or flags

The
[`name_or_flags`](https://docs.python.org/3/library/argparse.html#name-or-flags)
argument can be used to define additional flags for the arguments, like `-f` or
`--foo`:



```python
# example13.py
from clig import Arg, data, run

def main(foobar: Arg[str, data("-f", "--foo")] = "baz"):
    print(locals())

run(main)
```


```
> python example13.py -h

    usage: main [-h] [-f FOOBAR]
    
    options:
      -h, --help            show this help message and exit
      -f FOOBAR, --foo FOOBAR
    
```
[`name or flags`](https://docs.python.org/3/library/argparse.html#name-or-flags)
can also be used to turn a positional argument (without default) into an
[`required`](https://docs.python.org/3/library/argparse.html#required) flagged
argument (_required option_):



```python
# example14.py
from clig import Arg, data, run

def main(foo: Arg[str, data("-f")]):
    print(locals())

run(main)
```


```
> python example14.py -h

    usage: main [-h] -f FOO
    
    options:
      -h, --help         show this help message and exit
      -f FOO, --foo FOO
    
```

```
> python example14.py

    usage: main [-h] -f FOO
    main: error: the following arguments are required: -f/--foo
    
```
Some options for the
[`name or flags`](https://docs.python.org/3/library/argparse.html#name-or-flags)
arguments can also be set in the `run()` function


### nargs

Other cases of [`nargs`](https://docs.python.org/3/library/argparse.html#nargs)
can be specified in the `data()` function.

This next example uses a optional argument with
[`nargs="?"`](https://docs.python.org/3/library/argparse.html#nargs) and
[`const`](https://docs.python.org/3/library/argparse.html#const), which brings 3
different behavior for the optional argument:

- value passed
- value not passed (sets default value)
- option passed without value (sets const value):



```python
>>> from clig import Arg, data, run
... 
>>> def main(foo: Arg[str, data(nargs="?", const="c")] = "d"):
...     print(locals())
... 
>>> run(main, ["--foo", "YY"])
>>> run(main, [])
>>> run(main, ["--foo"])
{'foo': 'YY'}
{'foo': 'd'}
{'foo': 'c'}

```
This next example makes optional a positional argument (not flagged), by using
`nargs="?"` and
[`default`](https://docs.python.org/3/library/argparse.html#default) (which
would defaults to `None`):



```python
>>> from clig import Arg, data, run
... 
>>> def main(foo: Arg[str, data(nargs="?", default="d")]):
...     print(locals())
... 
>>> run(main, ["YY"])
>>> run(main, [])
{'foo': 'YY'}
{'foo': 'd'}

```
### action

Other options from the
[`action`](https://docs.python.org/3/library/argparse.html#action) parameter can
also be used in the `data()` function:



```python
>>> from clig import Arg, data, run
... 
>>> def append(foo: Arg[list[str], data(action="append")] = ["0"]):
...     print(locals())
... 
>>> def append_const(bar: Arg[list[int], data(action="append_const", const=42)] = [42]):
...     print(locals())
... 
>>> def extend(baz: Arg[list[float], data(action="extend")] = [0]):
...     print(locals())
... 
>>> def count(ham: Arg[int, data(action="count")] = 0):
...     print(locals())
... 
>>> run(append, "--foo 1 --foo 2".split())
>>> run(append_const, "--bar --bar --bar --bar".split())
>>> run(extend, "--baz 25 --baz 50 65 75".split())
>>> run(count, "--ham --ham --ham".split())
{'foo': ['0', '1', '2']}
{'bar': [42, 42, 42, 42, 42]}
{'baz': [0, 25.0, 50.0, 65.0, 75.0]}
{'ham': 3}

```
### metavar

The parameter
[`metavar`](https://docs.python.org/3/library/argparse.html#metavar) is used to
set alternative names in help messages to refer to optional arguments (which, by
default, would be referend as the argument name uppercased)



```python
# example15.py
from clig import Arg, data, run

def main(foo: Arg[str, data("-f", metavar="<foobar>")]):
    print(locals())

run(main)
```


```
> python example15.py -h

    usage: main [-h] -f <foobar>
    
    options:
      -h, --help            show this help message and exit
      -f <foobar>, --foo <foobar>
    
```
Some options for the
[`metavar`](https://docs.python.org/3/library/argparse.html#metavar) argument
can also be set in the `run()` function


## Groups

The `argparse` module has the feature of
[Argument groups](https://docs.python.org/3/library/argparse.html#argument-groups)
and
[Mutually exclusive argument groups](https://docs.python.org/3/library/argparse.html#mutual-exclusion).
These features can be used in `clig` with 2 additional classes: `ArgumentGroup`
and `MutuallyExclusiveGroup`.

Each class accepts all the parameters of the original methods
[`add_argument_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group)
and
[`add_mutually_exclusive_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_mutually_exclusive_group).



```python
# example16.py
from clig import Arg, data, run, ArgumentGroup

g = ArgumentGroup(title="Group of arguments", description="This is my group of arguments")

def main(foo: Arg[str, data(group=g)], bar: Arg[int, data(group=g)] = 42):
    print(locals())

run(main)
```


```
> python example16.py -h

    usage: main [-h] [--bar BAR] foo
    
    options:
      -h, --help  show this help message and exit
    
    Group of arguments:
      This is my group of arguments
    
      foo
      --bar BAR
    
```
Remember that mutually exclusive argument groups
[must be optional](https://github.com/python/cpython/blob/7168553c00767689376c8dbf5933a01af87da3a4/Lib/argparse.py#L1805)
(either by using a flag in the `data` function, or by setting a deafult value):



```python
# example17.py
from clig import Arg, data, run, MutuallyExclusiveGroup

g = MutuallyExclusiveGroup()

def main(foo: Arg[str, data("-f", group=g)], bar: Arg[int, data(group=g)] = 42):
    print(locals())

run(main)
```


```
> python example17.py --foo rocky --bar 23

    usage: main [-h] [-f FOO | --bar BAR]
    main: error: argument --bar: not allowed with argument -f/--foo
    
```
### Required mutually exclusive group

A `required` argument is accepted by the `MutuallyExclusiveGroup` in the same
way it is done with the original method
[`add_mutually_exclusive_group()`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_mutually_exclusive_group)
(to indicate that at least one of the mutually exclusive arguments is required):



```python
# example18.py
from clig import Arg, data, run, MutuallyExclusiveGroup

g = MutuallyExclusiveGroup(required=True)

def main(foo: Arg[str, data(group=g)] = "baz", bar: Arg[int, data(group=g)] = 42):
    print(locals())

run(main)
```


```
> python example18.py -h

    usage: main [-h] (--foo FOO | --bar BAR)
    
    options:
      -h, --help  show this help message and exit
      --foo FOO
      --bar BAR
    
```

```
> python example18.py

    usage: main [-h] (--foo FOO | --bar BAR)
    main: error: one of the arguments --foo --bar is required
    
```
### Mutually exclusive group added to an argument group

The `MutuallyExclusiveGroup` class also accepts an additional `argument_group`
parameter, because a mutually exclusive group can be added to an argument group.



```python
# example19.py
from clig import Arg, data, run, ArgumentGroup, MutuallyExclusiveGroup

ag = ArgumentGroup(title="Group of arguments", description="This is my group of arguments")
meg = MutuallyExclusiveGroup(argument_group=ag)

def main(foo: Arg[str, data(group=meg)] = "baz", bar: Arg[int, data(group=meg)] = 42):
    print(locals())

run(main)
```


```
> python example19.py -h

    usage: main [-h] [--foo FOO | --bar BAR]
    
    options:
      -h, --help  show this help message and exit
    
    Group of arguments:
      This is my group of arguments
    
      --foo FOO
      --bar BAR
    
```
### The walrus operator (`:=`)

You can do argument group definition all in one single line (in the function
declaration) by using the
[walrus operator](https://docs.python.org/3/reference/expressions.html#assignment-expressions)
(`:=`):



```python
# example20.py
from clig import Arg, data, run, ArgumentGroup, MutuallyExclusiveGroup

def main(
    foo: Arg[str,data(group=(g:=MutuallyExclusiveGroup(argument_group=ArgumentGroup("G"))))]="baz",
    bar: Arg[int,data(group=g)]=42,
):
    print(locals())

run(main)
```


```
> python example20.py -h

    usage: main [-h] [--foo FOO | --bar BAR]
    
    options:
      -h, --help  show this help message and exit
    
    G:
      --foo FOO
      --bar BAR
    
```
## Subcommands

Instead of using the function `clig.run()`, you can create an object instance of
the type `Command`, passing your function to its constructor, and call the
`Command.run()` method.



```python
# example21.py
from clig import Command

def main(name:str, age: int, height: float):
    print(locals())

cmd = Command(main)
cmd.run()
```


```
> python example21.py "Carmem Miranda" 42 1.85

    {'name': 'Carmem Miranda', 'age': 42, 'height': 1.85}
    
```
This makes possible to use some methods to add subcommands. All subcommands will
also be instances of the same class `Command`. There are 4 methods available:

- `subcommand`: Creates the subcommand and returns the input function unchanged.
  This is a proper method to be used as a
  [function decorator](https://docs.python.org/3/glossary.html#term-decorator).
- `new_subcommand`: Creates a subcommand and returns the new created `Command`
  instance.
- `add_subcommand`: Creates the subcommand and returns the caller object. This
  is useful to add multiple subcommands in one single line.
- `end_subcommand`: Creates the subcommand and returns the parent of the caller
  object. If the caller doesn't have a parent, an error will be raised. This is
  useful when finishing to add subcommands in the object on a single line.

The command functions execute sequentially, from a `Command` to its subcommands.

The `Command()` constructor also accepts other arguments to customize the
interface.

### Using `@subcommand` decorator

Create a `Command` and use the method `.subcommand()` as a decorator. The
decorator only registries the functions as commands (it doesn't change their
definitions).



```python
# example22.py
from inspect import getframeinfo, currentframe
from clig import Command

def main(verbose: bool = False):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

cmd = Command(main) 

@cmd.subcommand
def foo(a, b):
    """Help for foo sub command"""
    print(f"{getframeinfo(currentframe()).function} {locals()}")

@cmd.subcommand
def bar(c, d):
    """Help for bar sub command"""
    print(f"{getframeinfo(currentframe()).function} {locals()}")

cmd.run()
```


```
> python example22.py -h

    usage: main [-h] [--verbose] {foo,bar} ...
    
    options:
      -h, --help  show this help message and exit
      --verbose
    
    subcommands:
      {foo,bar}
        foo       Help for foo sub command
        bar       Help for bar sub command
    
```
Subcommands are correctly handled as
[subparsers](https://docs.python.org/3/library/argparse.html#sub-commands)



```
> python example22.py foo -h

    usage: main foo [-h] a b
    
    Help for foo sub command
    
    positional arguments:
      a
      b
    
    options:
      -h, --help  show this help message and exit
    
```

```
> python example22.py bar -h

    usage: main bar [-h] c d
    
    Help for bar sub command
    
    positional arguments:
      c
      d
    
    options:
      -h, --help  show this help message and exit
    
```
Remember: the command functions execute sequentially, from a `Command` to its
subcommands.



```
> python example22.py bar baz ham

    main {'verbose': False}
    bar {'c': 'baz', 'd': 'ham'}
    
```
**Note**  
The `cmd` object in the example above could also be created without a function
(i.e., `cmd = Command()`)


**Note**  
You could also use de `Command()` constructor as a
[decorator](https://docs.python.org/3/glossary.html#term-decorator), above the
function `main()`. However, that would redefine the name `main` (as a `Command`
instance).


### Using `new_subcommand`, `add_subcommand` and `end_subcommand`

To give a clear example, the next code tries to reproduce some of the
[Git](https://git-scm.com/) cli interface, using methods after the function
definitions. These methods could be placed in a separated file.



```python
# example23.py
from inspect import getframeinfo, currentframe 
from pathlib import Path
from clig import Command

def git(exec_path: Path = Path("git"), work_tree: Path = Path("C:/Users")):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def status(branch: str):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def commit(message: str):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def remote(verbose: bool = False):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def add(name: str, url: str):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def rename(old: str, new: str):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def remove(name: str):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def submodule(quiet: bool):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def init(path: Path = Path(".").resolve()):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

def update(init: bool, path: Path = Path(".").resolve()):
    print(f"{getframeinfo(currentframe()).function} {locals()}")

######################################################################################
# The interface is all built in the code below, which could also be in another file
 
(
    Command(git)
    .add_subcommand(status)
    .add_subcommand(commit)
    .new_subcommand(remote)
        .add_subcommand(add)
        .add_subcommand(rename)
        .end_subcommand(remove)
    .new_subcommand(submodule)
        .add_subcommand(init)
        .end_subcommand(update)
    .run()
)
```


```
> python example23.py -h

    usage: git [-h] [--exec-path EXEC_PATH] [--work-tree WORK_TREE]
               {status,commit,remote,submodule} ...
    
    options:
      -h, --help            show this help message and exit
      --exec-path EXEC_PATH
      --work-tree WORK_TREE
    
    subcommands:
      {status,commit,remote,submodule}
        status
        commit
        remote
        submodule
    
```

```
> python example23.py remote -h

    usage: git remote [-h] [--verbose] {add,rename,remove} ...
    
    options:
      -h, --help           show this help message and exit
      --verbose
    
    subcommands:
      {add,rename,remove}
        add
        rename
        remove
    
```

```
> python example23.py remote rename oldName newName

    git {'exec_path': WindowsPath('git'), 'work_tree': WindowsPath('C:/Users')}
    remote {'verbose': False}
    rename {'old': 'oldName', 'new': 'newName'}
    
```