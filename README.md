# Picatrix

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google/picatrix/blob/main/notebooks/Quick_Primer_on_Colab_Jupyter.ipynb)

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

Want to discuss the project, have issues, want new features, join the slack
workspace [here](http://join-open-source-dfir-slack.herokuapp.com/), the
channel for picatrix is #picatrix.
