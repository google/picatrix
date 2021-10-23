# Configuration file for jupyter-notebook.

## Use a regular expression for the Access-Control-Allow-Origin header
#
#  Requests from an origin matching the expression will get replies with:
#
#      Access-Control-Allow-Origin: origin
#
#  where `origin` is the origin of the request.
#
#  Ignored if allow_origin is set.
c.NotebookApp.allow_origin_pat = 'https://colab.[a-z]+.google.com'

## The IP address the notebook server will listen on.
c.NotebookApp.ip = '*'

## The directory to use for notebooks and kernels.
# Uncomment this if you want the notebook to start immediately in this folder.
#c.NotebookApp.notebook_dir = 'data/'

## Whether to open in a browser after starting. The specific browser used is
#  platform dependent and determined by the python standard library `webbrowser`
#  module, unless it is overridden using the --browser (NotebookApp.browser)
#  configuration option.
c.NotebookApp.open_browser = False

## Hashed password to use for web authentication.
#
#  To generate, type in a python/IPython shell:
#
#    from notebook.auth import passwd; passwd()
#
#  The string should be of the form type:salt:hashed-password.
# If this is enabled the password "picatrix" can be used.
#c.NotebookApp.password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$Q2sRv8dVZ8WBSmGNcTMuKg$VtFU0bwX81Ou+OaDWQgloA'
# Right now the token is set to picatrix, a plain text password.
c.NotebookApp.token = 'picatrix'

## The port the notebook server will listen on.
c.NotebookApp.port = 8899

## The number of additional ports to try if the specified port is not available.
c.NotebookApp.port_retries = 0

## The base name used when creating untitled notebooks.
c.ContentsManager.untitled_notebook = 'NewPicatrixNotebook'
