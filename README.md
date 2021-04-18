# Picatrix

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google/picatrix/blob/main/notebooks/Quick_Primer_on_Colab_Jupyter.ipynb)
[![Open In Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/google/picatrix.git/main?filepath=notebooks%2F)
[![Version](https://img.shields.io/pypi/v/picatrix.svg)](https://pypi.python.org/pypi/picatrix)
![GitHub e2e Test Status](https://img.shields.io/github/workflow/status/google/picatrix/picatrix-end-to-end)

Picatrix is a framework that is meant to be used within a [Colab](https://colab.research.google.com) or
[Jupyter](https://jupyter.org/) notebooks. The framework is designed around
providing a security analyst with the libraries to develop helper functions
that will be exposed as magics and regular python functions in notebooks.

This makes it easier to share an environment with other analysts, exposing
common functions that are used in notebooks to everyone. In addition to that
the functions themselves are designed to make it easier to work with various
APIs and backends in a notebook environment. The functions mostly involve
returning data back as a pandas DataFrame for further processing or to work
with pandas (manipulate pandas, change values, enrich data, upload data frames
to other services, etC).

## Howto Get Started

Read the [installation instructions](docs/Installation.md) on the best ways
to install picatrix.

After installing, connect to the Jupyter notebook in your web browser (should open
up automatically). Inside the notebook you need to import the picatrix library
and initialize it:

```
from picatrix import notebook_init
notebook_init.init()
```

(if you are using the docker container you don't need to import these libraries,
that is done for you automatically).

And that's it, then all the magics/helper functions are now ready and accessible
to your notebook. To get a list of the available helpers, use:

```
%picatrixmagics
```

Or

```
picatrixmagics_func()
```

Each magic has a `--help` parameter or the functions with `_func?`. Eg.

```
timesketch_set_active_sketch_func?
```

## Examples

To get all sketches, you can use the following magic

```
%timesketch_get_sketches
```

For most of the magics you need to set an active sketch

```
%timesketch_set_active_sketch 1
```

To query the sketch, the following magic will execute a search and return the results as a search object,
that can be easily converted into a pandas dataframe:

```
search_obj = %timesketch_query 'message:Another'
search_obj.table
```

Further documentation on the search object can be [found
here](https://timesketch.org/developers/api-client/#search-query)


To add a manual event with a function use:

```
timesketch_add_manual_event_func('Eventdescriptiontext', attributes=attributesdict)
```

Which is the same as:
```
%timesketch_add_manual_event Eventdescriptiontext --attributes {{attributesdict}}
```

## Discussions

Want to discuss the project, have issues, want new features, join the slack
workspace [here](http://join-open-source-dfir-slack.herokuapp.com/), the
channel for picatrix is #picatrix.
