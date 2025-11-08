# typer-invoke

[![pypi](https://img.shields.io/pypi/v/typer-invoke.svg)](https://pypi.python.org/pypi/typer-invoke)
[![Project License - MIT](https://img.shields.io/pypi/l/typer-invoke.svg)](https://github.com/joaonc/show_dialog/blob/main/LICENSE.txt)

Simplified invocation of typer apps from any directory.

The idea is that you place typer apps in a directory in your project and then you can invoke them
from anywhere inside that project.

## Example
1. Place scripts anywhere in the project (ex `admin` directory).
2. Make sure they're `typer` apps.
3. Register them in `pyproject.toml`.
4. Invoke them from anywhere in the project.

Ex:
```
inv --help
inv help-full
inv build deploy
inv test unit --pri1
```

In this project there's the `admin` directory with scripts actually used for managing the project
and the `sample` directory with more samples on how to use this package.

## Why?
The main use case is for project management that require custom scripts for various tasks.  
Wrapping those scripts as typer apps makes them easier to use.  
Making typer easier to use makes those scripts even easier to use.

An alternative to:

* [Make](https://www.gnu.org/software/make/manual/make.html)
* [Invoke](https://www.pyinvoke.org/)

### Versus Invoke
The main driver for this project is as a replacement for Invoke, which I've been using for
a while and found the following limitations:

* `--help` and `--list` options are clunky, in that they need to be placed right after the `inv`
  command, ex:
  ```
  inv --help some.task
  ```
  Here a more common pattern is used and `--help` acts as both help and list:
  ```
  inv some task --help
  ```
  There's also `help-full`, which lists all tasks recursively:
* ```
  inv help-full
  ```
* Output can be subdued.  
  If you use tools that have colors in their output, often that output is stripped of colors and
  other formatting. There are settings you can play with, but often it doesn't work.
* Lack of support.  
  Some issues and features have been piling up for a while, and I'm not sure if they will ever
  be addressed. Seems like [the project](https://github.com/pyinvoke/invoke) has had new development
  recently, though.  
  [Typer](https://typer.tiangolo.com/) is widely used and has a lot of support.

Other advantages (in my opinion):
* Prettier.  
  Developer experience counts. Other than more common usage patterns, Typer supports
  [rich](https://github.com/Textualize/rich) and Markdown formatting.  
  Including using `rich` for logging, which is done in this project.
* No dot `.` namespace.  
  Invoke uses a dot `.` namespace for tasks, which is not very common when running scripts.  
  Typer follows a normal CLI pattern. Namespaces are Typer apps and are separated by a space.

Invoke is the inspiration for this project, hence the name `typer-invoke` and keeping the `inv`
command name.

#### Cool things about Invoke
Invoke concepts and features I was using that are not native to this project, but the workarounds
work well:

* **Task dependencies.**  
  In Invoke, it's easy to declare a task dependent on others and they will be executed in the
  correct order.  
  While we don't have this feature, it's very easy to simply call other functions and end up with
  the same functionality.
* **Namespaces (task groups)**  
  You can declare namespaces and whatever tasks you want in them.  
  The same is done in Typer by with apps. Each app added is the equivalent of a namespace.  
  Usually, one app is in one file, but it's not a requirement.
* **Dry runs**  
  The `--dry` option in Invoke is very useful and available to all tasks.  
  Typer doesn't have this feature, but it's easy to add. See the examples in this project, under
  the `admin` directory.
