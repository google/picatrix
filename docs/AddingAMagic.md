[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google/picatrix/blob/main/notebooks/adding_magic.ipynb)

# Adding a Magic

There are two ways of adding a new magic or a helper function into
the picatrix library.

1. Temporary registration in a notebook.
2. Permanent one by checking files into the codebase.

Let's explore both.

There is also a second way to explore this document or these instructions,
through this document or through the [interactive notebook](https://colab.research.google.com/github/google/picatrix/blob/main/notebooks/adding_magic.ipynb)

## Temporary Registration in a Notebook

Wheter there is a need to register a helper function that will be
very specific to a single notebook and not helpful for the greater
community or in order to test a function while developin it, having
the ability to temporarily register a helper function inside a notebook
can be very handy. In order to do that you'll need two things:

1. Import the framework library
2. Add a decorator to a function.

The framework library needs to be loaded in order to register a magic,
that can be simply done:

```
from picatrix.lib import framework
```

Then a magic can be registered. A magic or a helper function is a regular
Python function that accepts at least one parameter, `data`. Other parameters
are optional and will be translated into regular parameters to the magic
and/or function. The function needs to have a proper docstring and typing
in order to correctly register. Then all that is needed in order to pass
it in is to put the decorator `@framework.picatrix_magic` on the function.

An example would be:

```
@framework.picatrix_magic
def my_silly_magic(data: Text, magnitude: Optional[int] = 100) -> Text:
  """Returns a string to demonstrate how to construct a magic.

  Args:
    data (str): This is a string that will be printed back.
    magnitude (int): A number that will be displayed in the string.

  Returns:
    A string that basically combines the two options.
  """
  return f'This magical magic produced {magnitude} magics of {data.strip()}'
```

As you can see in the above description there is a function declaration (def my...)
that defines the name of the magic. The magic will now be registered as
`%my_silly_magic`, %%my_silly_magic` and `my_silly_magic_func()`. In both cell
and line mode the text that is added will be passed in as the data attribute.
That is defined as a `str` (both by typing and in args section). That means the
input value will be interpreted as a string. You can pass in the optional
parameter `magnitude`, but by default it will be set to 100. So this could
be run as:

```
%my_silly_magic what today is magical
```

And that would return back:
```
This magical magic produced 100 magics of what today is magical
```

You can also run the function as:

```
%%my_silly_magic foobar
magics of what today is magical
this is surely a sorrow of a magic
```

And that would store the results of the magic into the variable `foobar`, so that
it would be:

```
foobar = 'This magical magic produced 100 magics of magics of what today is magical\nthis is surely a sorrow of a magic'
```

To pass in the parameters you can do:

```
my_silly_magic('foo', magnitude=1)
```

That would produce:

```
This magical magic produced 1 magics of foo
```

Or you can do it this way:

```
%my_silly_magic --bindto bar --magnitude 203 foobar
```

That would store the results into a variable called `bar`, so that: 

```
bar = 'This magical magic produced 203 magics of foobar
```

This is all that is required to register the magic temporarily.

## Checking the Magic Into the Library

If you want the magic to be more permanent the magic definition needs
to be checked into the library.

1. Create an appropriately named file inside `picatrix/magics/FILE.py`
2. Add an import statement for the file into `picatrix/magics/__init__.py`
3. Add unit tests for the magics into `picatrix/magics/FILE_test.py`
4. If needed, add e2e tests to the magic.
5. If needed, add new dependencies into `picatrix/dependencies.py`.
