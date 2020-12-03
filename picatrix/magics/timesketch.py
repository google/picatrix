"""Timesketch magic module.

This module conatins an implementation for the Picatrix Timesketch integration.
It enables colab/jupyter to send and receive data from a Timesketch sketch.
"""
import datetime
import logging
import os

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Text
from typing import Union

import dateutil.parser

from dfdatetime import time_elements

import pandas as pd

from timesketch_api_client import aggregation as api_aggregation
from timesketch_api_client import config
from timesketch_api_client import view as api_view
from timesketch_api_client import search as api_search
from timesketch_api_client import sketch as api_sketch
from timesketch_api_client import story as api_story
from timesketch_api_client import timeline as api_timeline
from timesketch_import_client import helper
from timesketch_import_client import importer

from picatrix.lib import framework
from picatrix.lib import state
from picatrix.lib import utils


logger = logging.getLogger('picatrix.magics.timesketch')


def _fix_return_fields(
    return_fields: Union[Text, List[Text], None]) -> Optional[Text]:
  """Returns a fixed string of return fields.

  The Timesketch API expects the return fields to be a comma separated
  string with no spaces in it and it cannot start with a quotation mark.

  Args:
    return_fields (str|list): a list of strings or a string with the
        return fields.

  Returns:
    A string that can be passed to the Timesketch API.
  """
  if isinstance(return_fields, str):
    return_fields = return_fields.split(',')

  if return_fields is None:
    return None

  return_field_list = []
  for field in return_fields:
    field = field.replace('\'', '')
    field = field.replace('"', '')
    field = field.strip()

    return_field_list.append(field)

  return ','.join(return_field_list)


def _label_search(
    label: Text,
    return_fields: Optional[Text] = '',
    max_entries: Optional[int] = None) -> pd.DataFrame:
  """Returns a DataFrame with all events that have a certain label.

  Args:
    label (str): a string representing the label to search for.
    return_fields (str): a comma separated string with all the fields that
        should be returned. If not provided all fields will be returned.
    max_entries (int): an integer with the maximum number of entries to return.

  Returns:
      A pandas DataFrame with the search results.
  """
  connect()
  state_obj = state.state()

  sketch = state_obj.get_from_cache('timesketch_sketch')
  if not sketch:
    print('No data, not connected to a sketch.')
    return pd.DataFrame()

  if not return_fields:
    return_fields = '*'

  return sketch.search_by_label(
      label,
      return_fields=_fix_return_fields(return_fields),
      max_entries=max_entries,
      as_pandas=True)


def connect(
    ignore_sketch: Optional[bool] = False,
    force_switch: Optional[bool] = False,
    config_section: Optional[Text] = 'timesketch',
    confirm_choices: Optional[bool] = False,
    token_password: Optional[Text] = ''):
  """Check if Timesketch has been set up and connect if it hasn't.

  Args:
    ignore_sketch (optional): if set to True sketch check is ignored.
    force_switch (optional): if set to True then a new client will be created,
        irrelevant if another client was stored.
    confirm_choices (bool): an optional bool. if set to the user is given
        a choice to change the value for all already configured parameters.
        This defaults to False.
    token_password (str): Optional password for the token file, if
        not provided the value inside the RC file is used.

  Raises:
    ValueError: if Timesketch is not properly configured.
  """
  state_obj = state.state()

  client = state_obj.get_from_cache('timesketch_client')
  sketch = state_obj.get_from_cache('timesketch_sketch')

  if client and force_switch:
    state_obj.remove_from_cache('timesketch_client')
    client = None

  if client:
    if ignore_sketch:
      return

    if sketch:
      return

    raise ValueError(
        'No sketch configured, either create a new one using '
        '%timesketch_create_sketch or assign an already existing '
        'one using %timesketch_set_active_sketch <sketch_id>')

  client = config.get_client(
      config_section=config_section, token_password=token_password,
      confirm_choices=confirm_choices)
  if not client:
    raise ValueError('Unable to connect to Timesketch')

  state_obj.add_to_cache('timesketch_client', client)


def get_context_date(
    date_string: Text, minutes: Optional[int] = 0, seconds: Optional[int] = 90,
    return_fields: Text = '') -> pd.DataFrame:
  """Return time context surrounding a single data frame row.

  Args:
    date_string (str): a date string to gather context around, in the form
        of %Y-%m-%dT%H:%M:%S%z.
    minutes (int): if provided used as number of minutes before
        and after the provided date string to provide context for. If minutes
        are provided seconds argument is ignored.
    seconds (int): if minutes is not provided seconds is used to determine
        the number of seconds before and after the date string to provide
        context for. Default value is 90 seconds.
    return_fields (str): string with comma separated names of fields to
        return back.

  Returns:
    pd.DataFrame: returns a data frame with all events in Timesketch
        that occurred within the timeframe supplied to the function.
  """
  chip = api_search.DateIntervalChip()
  date_object = dateutil.parser.parse(date_string)
  chip.date = date_object.strftime('%Y-%m-%dT%H:%M:%S%')

  if minutes:
    chip.unit = 'm'
    chip.before = minutes
    chip.after = minutes
  else:
    chip.unit = 's'
    chip.before = seconds
    chip.after = seconds

  return_fields = _fix_return_fields(return_fields)

  search_obj = query_timesketch(
      '*',
      return_fields=return_fields)
  search_obj.add_chip(chip)
  return search_obj


def get_context_row(
    row: pd.Series, minutes: Optional[int] = 0,
    seconds: Optional[int] = 90,
    return_fields: str = '') -> pd.DataFrame:
  """Return time context surrounding a single data frame row.

  Args:
    row (pandas.core.series.Series): a single row to use to extract the
        date from.
    minutes (int): if provided used as number of minutes before
        and after the provided date string to provide context for. If minutes
        are provided seconds argument is ignored.
    seconds (int): if minutes is not provided seconds is used to determine
        the number of seconds before and after the date string to provide
        context for. Default value is 90 seconds.
    return_fields (string): string with comma separated names of fields to
        return back.

  Returns:
    pandas.DataFrame: returns a data frame with all events in Timesketch
        that occurred within the timeframe supplied to the function.
  """
  if not isinstance(row, pd.Series):
    return pd.DataFrame()

  if 'datetime' not in row:
    return pd.DataFrame()

  date_string = row.datetime

  if hasattr(date_string, 'year') and hasattr(date_string, 'strftime'):
    # We have a pandas date object.
    date_string = date_string.strftime('%Y-%m-%dT%H:%M:%S%z')

  return get_context_date(
      date_string, minutes=minutes, seconds=seconds,
      return_fields=return_fields)


def is_view_object(input_object: Any) -> bool:
  """Returns a boolean whether an object is a view object or not.

  Args:
    input_object (object): an object that is to be tested whether or
        not it is a View object.

  Returns:
    True if it is a View object, False otherwise.
  """
  if not hasattr(input_object, 'lazyload_data'):
    return False

  if not hasattr(input_object, 'query_dsl'):
    return False

  if not hasattr(input_object, 'name'):
    return False

  if not hasattr(input_object, 'query_filter'):
    return False

  return True


def format_data_frame_row(
    row: pd.Series, format_message_string: Text) -> pd.DataFrame:
  """Return a formatted data frame using a format string."""
  return format_message_string.format(**row)


def get_sketch_details(sketch_id: Optional[int] = 0) -> Text:
  """Return back details about an existing sketch.

  Args:
    sketch_id (int): the sketch ID to check.

  Returns:
    string containing information about the sketch.
  """
  sketch = None
  state_obj = state.state()

  if not sketch_id:
    sketch = state_obj.get_from_cache('timesketch_sketch')
    if not sketch:
      return 'Need to provide a sketch id, no sketch provided.'

  connect(ignore_sketch=True)
  client = state_obj.get_from_cache('timesketch_client')
  if not sketch:
    sketch = client.get_sketch(sketch_id)

  try:
    _ = sketch.name
  except KeyError:
    return 'TS server returned no information back about the sketch'

  return_string_list = []
  return_string_list.append(f'Name: {sketch.name}')
  return_string_list.append(f'Description: {sketch.description}')
  return_string_list.append(f'ID: {sketch.id}')
  return_string_list.append('')
  return_string_list.append('Active Timelines:')

  for timeline in sketch.list_timelines():
    objects = timeline.data.get('objects', [])
    if not objects:
      continue

    data = objects[0]
    description = data.get('description', 'No description')
    created_at = data.get('created_at', 'N/A')
    return_string_list.append(
        f'{timeline.name} [{description}] -> {created_at}')

  return '\n'.join(return_string_list)


def set_active_sketch(
    sketch_id: int,
    section: Optional[Text] = 'timesketch',
    token_password: Optional[Text] = '',
    confirm_choices: Optional[bool] = False,
    reconnect: Optional[bool] = False):
  """Set the active sketch.

  Args:
      sketch_id (int): The sketch ID.
      section (str): Optional name of a configuration section inside
          the timesketchrc file for server information. Defaults to
          timesketch.
      token_password (str): Optional password for the token file, if
          not provided the value inside the RC file is used.
      confirm_choices (bool): an optional bool. if set to the user is given
          a choice to change the value for all already configured parameters.
          This defaults to False.
      reconnect (bool): Optional value if set refreshes the Timesketch
          client object.
  """
  connect(
      ignore_sketch=True, config_section=section,
      token_password=token_password,
      confirm_choices=confirm_choices,
      force_switch=reconnect)

  state_obj = state.state()
  client = state_obj.get_from_cache('timesketch_client')

  sketch = client.get_sketch(sketch_id)
  state_obj.add_to_cache('timesketch_sketch', sketch)


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_get_sketch(data='') -> api_sketch.Sketch:
  """Returns the Timesketch sketch object.

  Args:
    data (str): Not used, should be empty but is ignored.

  Returns:
    The selected sketch object (instance of api_sketch.Sketch).
  """
  connect()
  state_obj = state.state()
  return state_obj.get_from_cache('timesketch_sketch')


@framework.picatrix_magic
def timesketch_add_manual_event(
    data: Text, timestamp: Optional[int] = 0,
    date_string: Optional[Text] = '',
    timestamp_desc: Optional[Text] = '',
    attributes: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None) -> Dict[str, str]:
  """Add a manually generated event to the sketch.

  Args:
    data (str): The message string for for the event to be generated.
    timestamp (int): Optional timestamp in either seconds since Epoch or
        microseconds since Epoch.
    date_string (str): An optional date time as a human readable string. If
        neither date_string nor timestamp is provided then the current timestamp
        will be used as the time of the event.
    timestamp_desc (str): Optional timestamp description field.
    attributes (dict): Optional dict which contains extra attributes to add
        to the manual event.
    tags (list): Optional list of tags to add to the manual event.

  Returns:
    Dictionary with query results.
  """
  connect()
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')
  if not sketch:
    print('Not able to connect to a sketch.')
    return {}

  # Default timestamp.
  date_obj = datetime.datetime.now(datetime.timezone.utc)
  date = date_obj.isoformat()
  if timestamp:
    try:
      date_obj = datetime.datetime.fromtimestamp(
          timestamp, datetime.timezone.utc)
    except ValueError:
      date_obj = datetime.datetime.fromtimestamp(
          timestamp / 1e6, datetime.timezone.utc)
    date = date_obj.isoformat()
  elif date_string:
    elements = time_elements.TimeElements()
    if 'T' in date_string:
      try:
        elements.CopyFromStringISO8601(date_string)
      except ValueError:
        logger.error(
            'Unable to convert date string, is it really in ISO 8601 format?')
        return {}
    try:
      elements.CopyFromString(date_string)
    except ValueError:
      try:
        elements.CopyFromStringRFC1123(date_string)
      except ValueError:
        logger.error(
            'Unable to convert date string, needs to be in ISO 8601, 1123 or '
            'in the format YYYY-MM-DD hh:mm:ss.######[+-]##:##')
        return {}
    date = elements.CopyToDateTimeStringISO8601()

  if not timestamp_desc:
    timestamp_desc = 'Event Logged'

  if not isinstance(tags, (tuple, list)):
    tags = []

  if not isinstance(attributes, dict):
    attributes = {}

  if not date:
    logger.error('Unable to convert date string, please check it.')
    return {}

  return sketch.add_event(
      data, date, timestamp_desc, attributes=attributes, tags=tags)


@framework.picatrix_magic
def timesketch_upload_file(data: Text, name: Optional[Text] = ''):
  """Upload a file to Timesketch.

  Args:
    data (str): Path to the file that's about to be uploaded.
    name (str): Name of the timeline.
  """
  if not os.path.isfile(data):
    print('File [{0:s}] does not exist.'.format(data))
    return

  connect()
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')
  result = None

  if not name:
    name = data.split(os.sep)[-1]
    first, _, last = name.rpartition('.')
    name = first or last
    name = name.replace(' ', '_').replace('-', '_')

  with importer.ImportStreamer() as streamer:
    streamer.set_sketch(sketch)
    streamer.set_timeline_name(name)

    # Set the file size to 20Mb before the file is split.
    streamer.set_filesize_threshold(20971520)
    streamer.add_file(data)
    result = streamer.response

  if not result:
    print('Unable to upload data.')
    return

  for timesketch_object in result.get('objects', []):
    if not timesketch_object:
      continue
    print('Timeline: {0:s}\nStatus: {1:s}'.format(
        timesketch_object.get('description'),
        ','.join([x.get('status') for x in timesketch_object.get('status')])))


def query_timesketch(
    query: Optional[Text] = None,
    query_dsl: Optional[Text] = None,
    query_filter: Optional[Dict[Text, Any]] = None,
    view: Optional[api_view.View] = None,
    return_fields: Optional[Text] = None,
    start_date: Optional[Text] = '',
    end_date: Optional[Text] = '',
    max_entries: Optional[int] = None,
    indices: Optional[List[Text]] = None) -> pd.DataFrame:
  """Return back a data frame from a Timesketch query.

  Args:
    query (str): the query string to send to Timesketch.
    query_dsl (str): the query DSL to send to Timesketch.
    view (api_view.View): View object.
    return_fields (str): string with comma separated names of fields to
        return back.
    start_date (str): a timestamp in the form of
        'YYYY-MM-DDTHH:MM:SS+00:00' of when to start the search query.
    end_date (str): a timestamp in the form of
        'YYYY-MM-DDTHH:MM:SS+00:00' of when to end the search query.
    max_entries (int): Optional integer denoting a best effort to limit
        the output size to the number of events. Events are read in,
        10k at a time so there may be more events in the answer back
        than this number denotes, this is a best effort. This value defaults
        to 40k events. Setting max_entries to zero will return all entries
        back (as in no limit).
    indices (list): a list of indices to query, if not provided _all
        will be used.

  Returns:
    A data frame with the results gathered from the query.

  Raises:
    KeyError: if the query is sent in without a query, query_dsl or a view.
  """
  connect()
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')

  if all([x is None for x in [query, query_dsl, view]]):
    raise KeyError('Need to provide a query, query_dsl or a view')

  chip = None
  if start_date or end_date:
    if start_date and end_date:
      chip = api_search.DateRangeChip()
      chip.start_time = start_date
      chip.end_time = end_date
    else:
      chip = api_search.DateIntervalChip()
      if end_date:
        chip.date = end_date
      else:
        chip.date = start_date

  search_obj = api_search.Search(sketch)

  if view is not None:
    logger.warning(
        'Views will soon be deprecated, please transition to use search '
        'objects.')
    search_obj.from_saved(view.id)
  else:
    search_obj.from_manual(
        query_string=query,
        query_dsl=query_dsl,
        query_filter=query_filter,
        max_entries=max_entries)

  return_fields = _fix_return_fields(return_fields)
  if return_fields:
    search_obj.return_fields = return_fields

  if chip:
    search_obj.add_chip(chip)

  return search_obj


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_list_views(
    data: Optional[Text] = '') -> Dict[str, api_search.Search]:
  """List up all available views.

  Args:
    data (str): Not used.

  Returns:
    A dict with a list of available saved searches.
  """
  logger.warning(
      'This will soon be deprecated, use %timesketch_list_saved_searches')
  connect()
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')

  return_dict = {}
  for search_obj in sketch.list_saved_searches():
    key = f'{search_obj.id}:{search_obj.name}'
    return_dict[key] = search_obj
  return return_dict


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_list_saved_searches(
    data: Optional[Text] = '') -> Dict[str, api_search.Search]:
  """List up all available views.

  Args:
    data (str): Not used.

  Returns:
    A dict with a list of available saved searches.
  """
  connect()
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')

  return_dict = {}
  for search_obj in sketch.list_saved_searches():
    key = f'{search_obj.id}:{search_obj.name}'
    return_dict[key] = search_obj
  return return_dict


@framework.picatrix_magic
def timesketch_query(
    data: Text,
    fields: Optional[Text] = None,
    timelines: Optional[Text] = None,
    view: Optional[api_view.View] = None,
    start_date: Optional[Text] = '',
    end_date: Optional[Text] = '',
    query_filter: Optional[Dict[Text, Any]] = None,
    max_entries: Optional[int] = 40000) -> pd.DataFrame:
  """Run a Timesketch query using a magic.

  Args:
    data (str): the Timesketch query.
    fields (str): comma separated list of fields to include in the returned
        data frame.
    timelines (str): comma separated list of the names of the timelines.
    view (View): the View object.
    start_date (str): start date of the result set in the form of
        YYYY-MM-DDTHH:MM:SS+00:00.
    end_date (str): end date of the result set in the form of
        YYYY-MM-DDTHH:MM:SS+00:00.
    query_filter (dict): The query filter dict to use.
    max_entries (int): maximum entries of returned object, defaults to 40k.

  Raises:
    ValueError: If a view object is passed in and it's not a proper view
        object.

  Returns:
    DataFrame containing the results of the query.
  """
  connect()
  state_obj = state.state()

  if timelines:
    sketch = state_obj.get_from_cache('timesketch_sketch')
    timeline_list = sketch.list_timelines()
    names = timelines.split(',')
    indices = [
        x.index for x in timeline_list if x.name in names]
  else:
    indices = None

  if view and not is_view_object(view):
    raise ValueError('View is not a view instance, but rather [{0:s}]'.format(
        type(view)))

  return query_timesketch(
      query=data, view=view, return_fields=fields, query_filter=query_filter,
      indices=indices, start_date=start_date, end_date=end_date,
      max_entries=max_entries)


@framework.picatrix_magic
def timesketch_context_date(
    data: Text, minutes: int, seconds: Optional[int] = 90,
    fields: Optional[Text] = '') -> pd.DataFrame:
  """Run a Timesketch context query using a magic.

  This is a magic to run a context query in Timesketch around a
  single date and save them to a dataframe.

  If minutes are provided the seconds will be ignored.

  Args:
    data (str): the date string, in the form of %Y-%m-%dT%H:%M:%S%z.
    minutes (int): number of minutes to include in context.
    seconds (int): number of seconds to include in context, defaults
        to 90 seconds.
    fields (str): optional list of fields to include in the returned data.

  Returns:
    DataFrame containing the all surrounding events.
  """
  connect()
  date = data.strip()

  if minutes:
    seconds = minutes * 60

  return get_context_date(
      date, minutes=minutes, seconds=seconds, return_fields=fields)


@framework.picatrix_magic
def timesketch_context_row(
    data: pd.Series, minutes: int, seconds: Optional[int] = 90) -> pd.DataFrame:
  """Run a Timesketch context query using a magic.

  This is a magic to run a context query in Timesketch around a
  single date and save them to a dataframe.

  If minutes are provided the seconds will be ignored.

  Args:
    data (pandas.core.series.Series): pandas Series that contain the date
        string, in the form of %Y-%m-%dT%H:%M:%S%z.
    minutes (int): number of minutes to include in context.
    seconds (int): number of seconds to include in context, defaults
        to 90 seconds.

  Raises:
    ValueError: if the data field is not of the correct type.

  Returns:
    DataFrame containing the all surrounding events.
  """
  connect()

  if not isinstance(data, pd.Series):
    raise ValueError((
        'This magic expects a pandas Series object, use curly braces '
        '{{var_name}} to expand variable names.'))

  if minutes:
    seconds = minutes * 60

  return get_context_row(data, minutes=minutes, seconds=seconds)


@framework.picatrix_magic
def timesketch_get_timelines(data: Text) -> Dict[str, api_timeline.Timeline]:
  """Magic to get all available timelines for the sketch.

  Args:
    data (str): sketch ID to check for timelines, otherwise the active sketch
        is used.

  Returns:
    A dict with all timelines attached to the sketch, with keys as timeline name
    and value the timeline object (instance of Timeline).
  """
  connect()
  state_obj = state.state()

  if data:
    sketch_id = data.strip()
    client = state_obj.get_from_cache('timesketch_client')
    sketch = client.get_sketch(sketch_id)
  else:
    sketch = state_obj.get_from_cache('timesketch_sketch')

  if not sketch:
    return []

  return {x.name: x for x in sketch.list_timelines()}


@framework.picatrix_magic
def timesketch_create_sketch(
    data: Text, description: Text, set_active: Optional[bool] = False) -> Text:
  """Magic to create a new sketch in Timesketch.

  Args:
    data (str): name of the new sketch.
    description (str): sketch description.
    set_active (bool): whether to set the newly created sketch as the active
        one. Defaults to False.

  Returns:
    str: response string with sketch IDs.
  """
  connect(ignore_sketch=True)
  state_obj = state.state()
  client = state_obj.get_from_cache('timesketch_client')

  name = data.strip()
  sketch = client.create_sketch(name, description)

  if not sketch:
    return 'No response, sketch not created.'

  try:
    _ = sketch.name
  except KeyError:
    return 'It seems like the sketch was not created, verify on TS server.'

  if set_active:
    set_active_sketch(sketch.id)

  return_string_list = []
  return_string_list.append(f'Sketch: {sketch.id}')
  return_string_list.append(f'Name: {sketch.name}')

  data_objects = sketch.data.get('objects')
  if data_objects:
    data = data_objects[0]
    status_dict = data.get('status', [{}])[0]
    creation_time = status_dict.get('created_at', 'N/A')
    return_string_list.append('Creation Time: {0:s}'.format(creation_time))
    status = status_dict.get('status', 'N/A')
    return_string_list.append('Status: {0:s}'.format(status))

  return '\n'.join(return_string_list)


@framework.picatrix_magic
def timesketch_get_saved_searches(
      data: Optional[Text] = '') -> Dict[str, api_search.Search]:
  """Get all saved searches from an active sketch.

  Args:
    data (str): the sketch ID used to fetch saved searches from. Defaults to the
        active sketch.

  Returns:
      Dict that contains Search objects (instance of Search) as value and the
      name of the Search as the key.

  Raises:
    ValueError: if Timesketch is not properly configured.
  """
  connect()
  state_obj = state.state()

  if data:
    sketch_id = data.strip()
    if not sketch_id.isdigit():
      raise ValueError('Sketch ID is not a digit.')
    sketch_id = int(sketch_id, 10)
    client = state_obj.get_from_cache('timesketch_client')
    sketch = client.get_sketch(sketch_id)
  else:
    sketch = state_obj.get_from_cache('timesketch_sketch')

  if not sketch:
    raise ValueError('No sketch ID provided.')

  return {x.name: x for x in sketch.list_saved_searches()}


@framework.picatrix_magic
def timesketch_set_active_sketch(
    data: Text, reconnect: Optional[bool] = False,
    token_password: Optional[Text] = '',
    confirm_choices: Optional[bool] = False,
    config_section: Optional[Text] = 'timesketch'):
  """Sets the active sketch.

  Args:
    data (str): the sketch ID to set configure Timesketch for.
    reconnect (bool): optional boolean that forces a new Timesketch
        client to be created. Defaults to False.
    token_password (str): optional manual password for the token file.
    confirm_choices (bool): an optional bool. if set to the user is given
        a choice to change the value for all already configured parameters.
        This defaults to False.
    config_section (str): optional section in the timesketchrc file to
        read the config from. This can be used when the RC file contains
        information about more than one Timesketch server to connect to.
  """
  sketch_id = int(data.strip(), 10)
  set_active_sketch(
      sketch_id, section=config_section, token_password=token_password,
      reconnect=reconnect, confirm_choices=confirm_choices)
  utils.clear_notebook_output()


@framework.picatrix_magic
def timesketch_upload_data(
    data: pd.DataFrame,
    name: Optional[Text] = '',
    format_message_string: Optional[Text] = ''):
  """Upload a data frame to TimeSketch.

  Args:
    data (pandas.core.frame.DataFrame): the DataFrame to upload.
    name (str): the name used for the timeline in Timesketch.
    format_message_string (str): formatting string for the message column of
        the data frame, eg: "{src_ip:s} to {dst_ip:s}, {bytes:d} bytes
        transferred"'

  Raises:
    ValueError: if the dataframe cannot be uploaded to Timesketch or the
        data is invalid.
  """
  if not isinstance(data, pd.DataFrame):
    raise ValueError((
        'The data attribute is not a pandas DataFrame, please use curly '
        'braces to expand variables.'))

  if not name:
    name = 'unknown_timeline'

  connect()
  state_obj = state.state()

  sketch = state_obj.get_from_cache('timesketch_sketch')
  if not sketch:
    raise ValueError('Unable to upload data frame, need to set sketch.')

  result = None

  import_helper = helper.ImportHelper()
  with importer.ImportStreamer() as streamer:
    streamer.set_sketch(sketch)

    if 'data_type' not in data:
      data_type = utils.ask_question(
          'What is the value of [data_type]?', input_type=str)
      if data_type:
        streamer.set_data_type(data_type)
    else:
      data_types = data.data_type.unique()
      data_type = data_types[0]

    columns = list(data.columns)
    streamer.set_config_helper(import_helper)
    import_helper.configure_streamer(
        streamer, data_type=data_type, columns=columns)

    if format_message_string:
      streamer.set_message_format_string(format_message_string)

    streamer.set_timeline_name(name)

    streamer.add_data_frame(data)
    result = streamer.response

  if not result:
    print('Unable to upload data.')
    return

  for timesketch_object in result.get('objects', []):
    if not timesketch_object:
      continue
    print('Timeline: {0:s}\nStatus: {1:s}'.format(
        timesketch_object.get('description'),
        ','.join([x.get('status') for x in timesketch_object.get('status')])))


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_list_timelines(data: Optional[Text] = '') -> Text:
  """Returns a string with information about timelines and analyzer results."""
  connect()
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')
  if not sketch:
    return 'No data, not connected to a sketch.'

  timelines = sketch.list_timelines()
  return_lines = []

  for timeline in timelines:
    return_lines.append('         --- Timeline: {0:^s} ---'.format(
        timeline.name))
    return_lines.append('-'*80)
    return_lines.append('')

    data = timeline.data
    for index, data_object in enumerate(data.get('objects', [])):
      return_lines.append('Object nr: {0:d}'.format(index + 1))

      description = data_object.get('description')
      if description:
        return_lines.append('Description: {0:s}'.format(description))
        return_lines.append('')

      status_list = data_object.get('status', [])
      status = 'unknown'
      if status_list:
        status_dict = status_list[0]
        status = status_dict.get('status', 'N/A')
        return_lines.append('Status: {0:s}'.format(status))
        return_lines.append('')

      analyzer_output = data_object.get('searchindex', {}).get('description')
      if status == 'ready':
        return_lines.append('Analyzer Reports:')
        analyzer_lines = []
        for x in analyzer_output.split('\n'):
          if x and x not in analyzer_lines:
            analyzer_lines.append(x)
        for line_number, line in enumerate(analyzer_lines):
          return_lines.append(
              '  [{0:d}] {1:s}'.format(line_number + 1, line.strip()))
      else:
        return_lines.append('Error Message:')
        return_lines.append(analyzer_output)

    return_lines.append('='*80)
    return_lines.append('')
  return '\n'.join(return_lines)


@framework.picatrix_magic
def timesketch_get_aggregations(
    data: Optional[Text] = '') -> Dict[Text, api_aggregation.Aggregation]:
  """Get all aggregations from an active sketch.

  Args:
    data (str): the sketch ID used to fetch aggregations from. Defaults to the
        active sketch.

  Returns:
      Dict that contains Aggregation objects (instance of Aggregation) as
      value and the name of the aggregation as the key.

  Raises:
    ValueError: if Timesketch is not properly configured.
  """
  connect()
  state_obj = state.state()

  if data:
    sketch_id = data.strip()
    if not sketch_id.isdigit():
      raise ValueError('Sketch ID is not a digit.')
    sketch_id = int(sketch_id, 10)
    client = state_obj.get_from_cache('timesketch_client')
    sketch = client.get_sketch(sketch_id)
  else:
    sketch = state_obj.get_from_cache('timesketch_sketch')

  if not sketch:
    raise ValueError('No sketch ID provided.')

  aggregations = sketch.list_aggregations()
  return {x.name: x for x in aggregations}


# pylint:disable=unused-argument
@framework.picatrix_magic
def timesketch_available_aggregators(
    data: Optional[Text] = '') -> pd.DataFrame:
  """Returns a data frame with information about available aggregators.

  Args:
    data (str): not used.

  Returns:
    A pandas DataFrame with information about available aggregators.
  """
  connect()
  state_obj = state.state()
  client = state_obj.get_from_cache('timesketch_client')
  if not client:
    return pd.DataFrame()

  lines = []
  for line in client.get_aggregator_info():
    fields = line.get('fields', [])
    if fields:
      del line['fields']
    for index, field in enumerate(fields):
      line['field_{0:d}'.format(index+1)] = '{0:s}: {1:s}'.format(
          field.get('description', 'N/A'), field.get('name'))
    lines.append(line)
  return pd.DataFrame(lines)


# pylint:disable=unused-argument
@framework.picatrix_magic
def timesketch_get_token_status(data: Optional[Text] = '') -> Text:
  """Returns a string with information about OAUTH token expiration.

  Args:
    data (str): not used.

  Returns:
    A string with indication about OAUTH token expiration.
  """
  connect()
  state_obj = state.state()
  client = state_obj.get_from_cache('timesketch_client')
  if not client:
    return 'Not connected to a Timesketch client.'

  status = client.get_oauth_token_status()
  if status.get('expired', True):
    return 'OAUTH token has expired.'

  return 'OAUTH token has not expired, expires at: {0:s}'.format(
      status.get('expiry_time', 'Unknown Time'))


# pylint:disable=unused-argument
@framework.picatrix_magic
def timesketch_refresh_token(data: Optional[Text] = '') -> Text:
  """Refreshes OAUTH token and returns a string with information the token.

  Args:
    data (str): not used.

  Returns:
    A string with indication about OAUTH token expiration.
  """
  connect()
  state_obj = state.state()
  client = state_obj.get_from_cache('timesketch_client')
  if not client:
    return 'Not connected to a Timesketch client.'
  client.refresh_oauth_token()
  return timesketch_get_token_status('')


@framework.picatrix_magic
def timesketch_run_aggregation_dsl(
    data: Text, as_object: Optional[bool] = False) -> Union[
        pd.DataFrame, api_aggregation.Aggregation]:
  """Run an aggregation query against the datastore.

  Args:
    data (str): Elasticsearch aggregation query DSL string.
    as_object (bool): If set to True then the aggregation object
        will be returned, otherwise a pandas DataFrame (default).

  Returns:
    A pandas DataFrame with the results from the aggregation query.
  """
  connect()
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')
  if not sketch:
    return 'No data, not connected to a sketch.'

  agg_obj = sketch.aggregate(data.strip())

  if as_object:
    return agg_obj

  return agg_obj.table


@framework.picatrix_magic
def timesketch_run_aggregator(
    data: Text,
    parameters: Optional[Dict[str, Any]] = None) -> api_aggregation.Aggregation:
  """Run an aggregation query against the datastore.

  Args:
    data (str): the name of the aggregator class to run.
    parameters (dict): a dict with key/value pairs of parameters
        the aggregator needs to run.

  Returns:
    Dictionary with query results or a pandas DataFrame if as_pandas
    is set to True.
  """
  connect()
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')
  if not sketch:
    return 'No data, not connected to a sketch.'

  if parameters is None:
    parameters = {}

  return sketch.run_aggregator(
      data.strip(), aggregator_parameters=parameters)


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_get_sketches(
    data: Optional[Text] = '') -> Dict[Text, api_sketch.Sketch]:
  """Returns a dict with available sketches.

  Args:
    data (str): not used.

  Returns:
    A dict with the available sketches, with keys as sketch name and values
    as Sketch objects.
  """
  connect(ignore_sketch=True)
  state_obj = state.state()
  client = state_obj.get_from_cache('timesketch_client')

  return {x.name: x for x in client.list_sketches()}


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_get_searchindices(data: Optional[Text] = '') -> Dict[Text, Text]:
  """Returns a dict with available searchindices.

  Args:
    data (str): not used.

  Returns:
    A dict with the available search indices, with keys as names and values as
    search index names.
  """
  connect(ignore_sketch=True)
  state_obj = state.state()
  client = state_obj.get_from_cache('timesketch_client')

  return {x.name: x.index_name for x in client.list_searchindices()}


@framework.picatrix_magic
def timesketch_search_by_label(
    data: Text,
    return_fields: Optional[Text] = '',
    max_entries: Optional[int] = None) -> pd.DataFrame:
  """Returns a DataFrame with all events that have a certain label.

  Args:
    data (str): a string representing the label to search for.

  Returns:
      A pandas DataFrame with the search results.
  """
  return _label_search(
      data.strip(),
      return_fields=return_fields,
      max_entries=max_entries
  )


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_get_starred_events(
    data: Optional[Text] = '',
    return_fields: Optional[Text] = '',
    max_entries: Optional[int] = None) -> pd.DataFrame:
  """Returns a DataFrame with all starred events.

  Args:
    data (str): not used.

  Returns:
      A pandas DataFrame with starred events.
  """
  return _label_search(
      '__ts_star',
      return_fields=return_fields,
      max_entries=max_entries)


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_events_with_comments(
    data: Optional[Text] = '',
    return_fields: Optional[Text] = '',
    max_entries: Optional[int] = None) -> pd.DataFrame:
  """Returns a DataFrame with all events that have comments associated with it.

  Args:
    data (str): not used.

  Returns:
      A pandas DataFrame with all events that have comments associated with
      them.
  """
  return _label_search(
      '__ts_comment',
      return_fields=return_fields,
      max_entries=max_entries)


# pylint: disable=unused-argument
@framework.picatrix_magic
def timesketch_list_stories(
    data: Optional[Text] = '') -> Dict[Text, api_story.Story]:
  """Returns a dict with all the stories that are saved to the sketch.

  Args:
    data (str): not used.

  Returns:
    A dict with keys as story titles and values as Story objects.
  """
  connect(ignore_sketch=True)
  state_obj = state.state()
  sketch = state_obj.get_from_cache('timesketch_sketch')
  if not sketch:
    return 'No data, not connected to a sketch.'
  story_dict = {}
  for story in sketch.list_stories():
    story_dict[story.title] = story
  return story_dict
