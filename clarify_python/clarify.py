"""
.. module:: clarify
   : synopsis: 'All of the functions covering the REST API calls. These calls (except for delete_* which are void) all return a python data structure equivalent to the JSON returned by the API.'
"""

import sys
import collections
import urllib3
import certifi
import urllib.parse
import json
from clarify_python import helper
from clarify_python.constants import __version__
from clarify_python.constants import __api_version__
from clarify_python.constants import __api_lib_name__
from clarify_python.constants import __host__

BUNDLES_PATH = 'bundles'
SEARCH_PATH = 'search'
PYTHON_VERSION = '.'.join(str(i) for i in sys.version_info[:3])

#
# Client.
#

class Client(object):
    """Holds the environment."""

    key = None # Our API key.
    conn = None # Or connection pool.

    def __init__(self, key):
        self.key = key
        self.conn = urllib3.HTTPSConnectionPool(__host__, maxsize=1,
                                                cert_reqs='CERT_REQUIRED',
                                                ca_certs=certifi.where())


    def get_bundle_list(self, href=None, limit=None, embed_items=None,
                        embed_tracks=None, embed_metadata=None):
        """Get a list of available bundles.

        'href' the relative href to the bundle list to retriev. If None,
        the first bundle list will be returned.
        'limit' the maximum number of bundles to include in the result.
        'embed_items' whether or not to expand the bundle data into the
        result.
        'embed_tracks' whether or not to expand the bundle track data
        into the result.
        'embed_metadata' whether or not to expand the bundle metadata
        into the result.

        NB: providing values for 'limit', 'embed_*' will override either
        the API default or the values in the provided href.

        Returns a data structure equivalent to the JSON returned by the API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert limit is None or limit > 0

        j = None
        if href is None:
            j = self._get_first_bundle_list(limit,
                                            embed_items,
                                            embed_tracks,
                                            embed_metadata)
        else:
            j = self._get_additional_bundle_list(href, limit,
                                                 embed_items,
                                                 embed_tracks,
                                                 embed_metadata)

        # Convert the JSON to a python data struct.

        return self._parse_json(j)


    def _get_first_bundle_list(self, limit=None,
                               embed_items=None,
                               embed_tracks=None,
                               embed_metadata=None):
        """Get a list of available bundles.

        'limit' may be None, which implies API default.  If not None,
        must be > 1.
        'embed_items' True will embed item data in the result.
        'embed_tracks' True will embed track data in the embeded items.
        'embed_metadata' True will embed metadata in the embeded items.

        Note that including tracks and metadata without including items
        is meaningless.

        Returns the raw JSON returned by the API.

        If the response status is not 2xx, throws an APIException."""

        # Prepare the data we're going to include in our query.
        path = '/' + __api_version__ + '/' + BUNDLES_PATH

        data = None
        fields = {}
        if limit is not None:
            fields['limit'] = limit
        embed = helper.process_embed(embed_items=embed_items,
                                     embed_tracks=embed_tracks,
                                     embed_metadata=embed_metadata)
        if embed is not None:
            fields['embed'] = embed

        if len(fields) > 0:
            data = fields

        raw_result = self.get(path, data)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)
        else:
            result = raw_result.json

        return result


    def _get_additional_bundle_list(self, href=None, limit=None,
                                    embed_items=None,
                                    embed_tracks=None,
                                    embed_metadata=None):
        """Get next, previous, first, last list (page) of available bundles.

        'href' the href to retrieve the bundles.

        All other arguments override arguments in the href.

        Returns the raw JSON returned by the API.

        If the response status is not 2xx, throws an APIException."""

        url_components = urllib.parse.urlparse(href)
        path = url_components.path
        data = urllib.parse.parse_qs(url_components.query)

        # Change all lists into discrete values.
        for key in data.keys():
            data[key] = data[key][0]

        # Deal with limit overriding.
        if limit is not None:
            data['limit'] = limit

        # Deal with embeds overriding.
        final_embed = helper.process_embed_override(data.get('embed'),
                                                    embed_items,
                                                    embed_tracks,
                                                    embed_metadata)
        if final_embed is not None:
            data['embed'] = final_embed

        raw_result = self.get(path, data)

        if raw_result.status < 200 or raw_result.status > 202:
            print('*****')
            print(raw_result.status)
            print(raw_result.json)
            print('*****')
            raise APIException(raw_result.status, raw_result.json)
        else:
            result = raw_result.json

        return result

        
    def create_bundle(self, name=None, media_url=None,
                      audio_channel=None, metadata=None, notify_url=None):
        """Create a new bundle.

        'metadata' may be None, or an object that can be converted to a JSON
        string.  See API documentation for restrictions.  The conversion
        will take place before the API call.
        
        All other parameters are also optional. For information about these
        see https://api.clarify.io/docs#!/audio/v1audio_post_1.
        
        Returns a data structure equivalent to the JSON returned by the API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Prepare the data we're going to include in our bundle creation.
        path = '/' + __api_version__ + '/' + BUNDLES_PATH

        data = None

        fields = {}
        if name is not None:
            fields['name'] = name
        if media_url is not None:
            fields['media_url'] = media_url
        if audio_channel is not None:
            fields['audio_channel'] = audio_channel
        if metadata is not None:
            fields['metadata'] = json.dumps(metadata)
        if notify_url is not None:
            fields['notify_url'] = notify_url

        if len(fields) > 0:
            data = fields

        raw_result = self.post(path, data)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)

        # Convert the JSON to a python data struct.

        return self._parse_json(raw_result.json)


    def delete_bundle(self, href=None):
        """
        Delete a bundle.

        :param href: the relative href to the bundle.
        :type href: string, may not be None
        :return: nothing
        :raises APIException: If the response code is not 204.
        """

        # Argument error checking.
        assert href is not None

        raw_result = self.delete(href)

        if raw_result.status != 204:
            raise APIException(raw_result.status, raw_result.json)


    def get_bundle(self, href=None, embed_tracks=False,
                   embed_metadata=False):
        """Get a bundle.

        'href' the relative href to the bundle. May not be None.
        'embed_tracks' determines whether or not to include track
        information in the response.
        'embed_metadata' determines whether or not to include metadata
        information in the response.

        Returns a data structure equivalent to the JSON returned by the API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert href is not None

        data = None
        fields = {}
        embed = helper.process_embed(embed_items=False,
                                     embed_tracks=embed_tracks,
                                     embed_metadata=embed_metadata)
        if embed is not None:
            fields['embed'] = embed

        if len(fields) > 0:
            data = fields

        raw_result = self.get(href, data)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)

        # Convert the JSON to a python data struct.

        return self._parse_json(raw_result.json)
        
    def update_bundle(self, href=None, name=None,
                      notify_url=None, version=None):
        """Update a bundle.  Note that only the 'name' and 'notify_url' can
        be update.

        'href' the relative href to the bundle. May not be None.
        'name' the name of the bundle.  May be None.
        'notify_url' the URL for notifications on this bundle.
        'version' the object version.  May be None; if not None, must be
        an integer, and the version must match the version of the
        bundle.  If not, a 409 conflict error will cause an APIException
        to be thrown.

        Returns a data structure equivalent to the JSON returned by the API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert href is not None
        assert version is None or isinstance(version, int)

        # Prepare the data we're going to include in our bundle update.
        data = None

        fields = {}
        if name is not None:
            fields['name'] = name
        if notify_url is not None:
            fields['notify_url'] = notify_url
        if version is not None:
            fields['version'] = version

        if len(fields) > 0:
            data = fields

        raw_result = self.put(href, data)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)

        # Convert the JSON to a python data struct.

        return self._parse_json(raw_result.json)


    def get_metadata(self, href=None):
        """Get metadata.

        'href' the relative href to the metadata. May not be None.

        Returns a data structure equivalent to the JSON returned by the
        API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert href is not None

        raw_result = self.get(href)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)

        # Convert the JSON to a python data struct.

        return self._parse_json(raw_result.json)


    def update_metadata(self, href=None, metadata=None, version=None):
        """Update the metadata in a bundle.

        'href' the relative href to the metadata. May not be None.
        'metadata' may be None, or an object that can be converted to a
        JSON string.  See API documentation for restrictions.  The
        conversion will take place before the API call.
        'version' the object version.  May be None; if not None, must be
        an integer, and the version must match the version of the
        bundle.  If not, a 409 conflict error will cause an APIException
        to be thrown.

        Returns a data structure equivalent to the JSON returned by the API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert href is not None
        assert metadata is not None
        assert version is None or isinstance(version, int)

        # Prepare the data we're going to include in our bundle update.
        data = None

        fields = {}
        if version is not None:
            fields['version'] = version
        fields['data'] = json.dumps(metadata)

        data = fields

        raw_result = self.put(href, data)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)

        # Convert the JSON to a python data struct.

        return self._parse_json(raw_result.json)


    def delete_metadata(self, href=None):
        """Delete metadata.

        'href' the relative href to the bundle. May not be None.

        Returns nothing.

        If the response status is not 204, throws an APIException."""

        # Argument error checking.
        assert href is not None

        raw_result = self.delete(href)

        if raw_result.status != 204:
            raise APIException(raw_result.status, raw_result.json)


    def create_track(self, href=None, media_url=None, label=None,
                     audio_channel=None):
        """Add a new track to a bundle.  Note that the total number of
        allowable tracks is limited. See the API documentation for
        details.

        'href' the relative href to the tracks list. May not be None.
        'media_url' public URL to media file. May not be None.
        'label' short name for the track. May be None.
        'audio_channel' the channel(s) to use in a stereo file. May be
        None. For details see the API documentation.

        Returns a data structure equivalent to the JSON returned by the
        API.

        If the response status is not 2xx, or if the maximum number of
        tracks is exceeded, throws an APIException.  If the JSON to
        python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert href is not None
        assert media_url is not None

        # Prepare the data we're going to write.
        data = None

        fields = {}
        fields['media_url'] = media_url
        if label is not None:
            fields['label'] = label
        if audio_channel is not None:
            fields['audio_channel'] = audio_channel

        if len(fields) > 0:
            data = fields

        raw_result = self.post(href, data)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)

        # Convert the JSON to a python data struct.

        return self._parse_json(raw_result.json)


    def get_track_list(self, href=None):
        """Get track list.

        'href' the relative href to the track list. May not be None.

        Returns a data structure equivalent to the JSON returned by the
        API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert href is not None

        raw_result = self.get(href)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)

        # Convert the JSON to a python data struct.

        return self._parse_json(raw_result.json)


    def get_track(self, href=None):
        """Get a track.

        'href' the relative href to the track. May not be None.

        Returns a data structure equivalent to the JSON returned by the
        API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert href is not None

        raw_result = self.get(href)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)

        # Convert the JSON to a python data struct.

        return self._parse_json(raw_result.json)


    def delete_track_at_index(self, href=None, index=None):
        """Delete a track, or all the tracks.

        'href' the relative href to the track list. May not be None.
        'index' the index of the track to delete. If none is given,
        all tracks are deleted.

        Returns nothing.

        If the response status is not 204, throws an APIException."""

        # Argument error checking.
        assert href is not None

        # Deal with any parameters that need to be passed in.
        data = None

        fields = {}
        if index is not None:
            fields['track'] = index

        if len(fields) > 0:
            data = fields

        raw_result = self.delete(href, data)

        if raw_result.status != 204:
            raise APIException(raw_result.status, raw_result.json)


    def delete_track(self, href=None):
        """Delete a track.

        'href' the relative index of the track. May not be none.

        Returns nothing.

        If the response status is not 204, throws and APIException."""

        # Argument error checking.
        assert href is not None

        raw_result = self.delete(href)

        if raw_result.status != 204:
            raise APIException(raw_result.status, raw_result.json)


    def search(self, href=None,
               query=None, query_fields=None, query_filter=None,
               limit=None, embed_items=None, embed_tracks=None,
               embed_metadata=None):

        """Search a media collection.

        'href' the relative href to the bundle list to retriev. If None,
        the first bundle list will be returned.
        'query' See API docs for full description. May not be None.
        'query_fields' See API docs for full description. May be None.
        'query_filter' See API docs for full description. May be None.
        'limit' the maximum number of bundles to include in the result.
        'embed_items' whether or not to expand the bundle data into the
        result.
        'embed_tracks' whether or not to expand the bundle track data
        into the result.
        'embed_metadata' whether or not to expand the bundle metadata
        into the result.

        NB: providing values for 'limit', 'embed_*' will override either
        the API default or the values in the provided href.

        Returns a data structure equivalent to the JSON returned by the
        API.

        If the response status is not 2xx, throws an APIException.
        If the JSON to python data struct conversion fails, throws an
        APIDataException."""

        # Argument error checking.
        assert query is not None
        assert limit is None or limit > 0

        if href is None:
            j = self._search_p1(query, query_fields, query_filter, limit,
                                embed_items, embed_tracks, embed_metadata)
                           
        else:
            j = self._search_pn(href, limit, embed_items, embed_tracks,
                                embed_metadata)

        # Convert the JSON to a python data struct.

        return self._parse_json(j)


    def _search_p1(self, query=None, query_fields=None, query_filter=None,
                   limit=None, embed_items=None, embed_tracks=None,
                   embed_metadata=None):
        """Function called to retrieve the first page."""

        # Prepare the data we're going to include in our query.
        path = '/' + __api_version__ + '/' + SEARCH_PATH

        data = None
        fields = {}
        fields['query'] = query
        if query_fields is not None:
            fields['query_fields'] = query_fields
        if query_filter is not None:
            fields['filter'] = query_filter
        if limit is not None:
            fields['limit'] = limit
        embed = helper.process_embed(embed_items=embed_items,
                                     embed_tracks=embed_tracks,
                                     embed_metadata=embed_metadata)
        if embed is not None:
            fields['embed'] = embed

        if len(fields) > 0:
            data = fields

        raw_result = self.get(path, data)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)
        else:
            result = raw_result.json

        return result


    def _search_pn(self, href=None, limit=None,
                   embed_items=None, embed_tracks=None, embed_metadata=None):
        """Function called to retrieve pages 2-n."""

        url_components = urllib.parse.urlparse(href)
        path = url_components.path
        data = urllib.parse.parse_qs(url_components.query)

        # Change all lists into discrete values.
        for key in data.keys():
            data[key] = data[key][0]

        # Deal with limit overriding.
        if limit is not None:
            data['limit'] = limit

        # Deal with embeds overriding.
        final_embed = helper.process_embed_override(data.get('embed'),
                                                    embed_items,
                                                    embed_tracks,
                                                    embed_metadata)
        if final_embed is not None:
            data['embed'] = final_embed

        raw_result = self.get(path, data)

        if raw_result.status < 200 or raw_result.status > 202:
            raise APIException(raw_result.status, raw_result.json)
        else:
            result = raw_result.json

        return result


    def _get_headers(self):
        """Get all the headers we're going to need:

        1. Authorization
        2. Content-Type
        3. User-agent

        Note that the User-agent string contains the library name, the
        libary version, and the python version. This will help us track
        what people are using, and where we should concentrate our
        development efforts."""

        user_agent = __api_lib_name__ + '/' + __version__ + '/' + \
                     PYTHON_VERSION 

        return {'Authorization': 'Bearer ' + self.key,
                'User-Agent': user_agent,
                'Content-Type': 'application/x-www-form-urlencoded'}


    def get(self, path, data=None):
        """Executes a GET.

        'path' may not be None. Should include the full path to the
        resource.
        'data' may be None or a dictionary. These values will be
        appended to the path as key/value pairs.

        Returns a named tuple that includes:

        status: the HTTP status code
        json: the returned JSON-HAL

        If the key was not set, throws an APIConfigurationException."""

        # Argument error checking.
        assert path is not None

        # Execute the request.
        response = self.conn.request('GET', path, data, self._get_headers())

        # Extract the result.
        response_status = response.status
        response_content = response.data.decode()

        return Result(status=response_status, json=response_content)


    def post(self, path, data):
        """Executes a POST.

        'path' may not be None, should not inlude a version number, and
        should not include a leading '/'
        'data' may be None or a dictionary.

        Returns a named tuple that includes:

        status: the HTTP status code
        json: the returned JSON-HAL

        If the key was not set, throws an APIConfigurationException."""

        # Argument error checking.
        assert path is not None
        assert data is None or isinstance(data, dict)

        # Execute the request.
        if data is None:
            data = {}
        response = self.conn.request_encode_body('POST', path, data,
                                                 self._get_headers(), False)

        # Extract the result.
        response_status = response.status
        response_content = response.data.decode()

        return Result(status=response_status, json=response_content)


    def delete(self, path, data=None):
        """Executes a DELETE.

        'path' may not be None. Should include the full path to the
        resoure.
        'data' may be None or a dictionary.

        Returns a named tuple that includes:

        status: the HTTP status code
        json: the returned JSON-HAL

        If the key was not set, throws an APIConfigurationException."""

        # Argument error checking.
        assert path is not None
        assert data is None or isinstance(data, dict)

        # Execute the request.
        response = self.conn.request('DELETE', path, data,
                                     self._get_headers())

        # Extract the result.
        response_status = response.status
        response_content = response.data.decode()

        # return (status, json)
        return Result(status=response_status, json=response_content)


    def put(self, path, data):
        """Executes a PUT.

        'path' may not be None. Should include the full path to the
        resoure.
        'data' may be None or a dictionary.
        
        Returns a named tuple that includes:

        status: the HTTP status code
        json: the returned JSON-HAL

        If the key was not set, throws an APIConfigurationException."""

        # Argument error checking.
        assert path is not None
        assert data is None or isinstance(data, dict)

        # Execute the request.
        if data is None:
            data = {}
        response = self.conn.request_encode_body('PUT', path, data,
                                                 self._get_headers(), False)

        # Extract the result.
        response_status = response.status
        response_content = response.data.decode()

        return Result(status=response_status, json=response_content)

    ### Utility functions.

    def _parse_json(self, jstring=None):
        """Parse jstring and return a Python data structure.

        'jstring' a string of JSON. May not be None.

        Returns a Python data structure.

        If jstring couldn't be parsed, raises an APIDataException."""

        # Argument error checking.
        assert jstring is not None

        result = None

        try:
            result = json.loads(jstring)
        except (ValueError) as exception:
            msg = 'Unable to convert JSON string to Python data structure.'
            raise APIDataException(exception, jstring, msg)

        return result


# This named tuple is returned by get(), put(), post(), delete()
# functions and consumed by the REST cover functions.

Result = collections.namedtuple('Result', ['status', 'json'])

#
# Exceptions.
#

KEY_STATUS = 'status'
KEY_MESSAGE = 'message'
KEY_CODE = 'code'


class APIException(Exception):
    """Thown when we don't receive the expected sucess response from an
    API call."""

    _data_struct = None
    http_response = None
    json_response = None

    def __init__(self, http_response, json_response):
        Exception.__init__(self)

        self.http_response = http_response
        self.json_response = json_response

        #  Try to turn the JSON and turn it into something we can use.
        #  Could be garbage, in which case we should just ignore it.
        try:
            self._data_struct = json.loads(json_response)
        except ValueError:
            pass

    def get_http_response(self):
        """Return the HTTP response that caused this exception to be
        thrown."""

        return self.http_response

    def get_status(self):
        """Return the status embedded in the JSON error response body,
        or an empty string if the JSON couldn't be parsed."""

        result = ''
        if self._data_struct is not None:
            result = self._data_struct[KEY_STATUS]
        return result

    def get_message(self):
        """Return the message embedded in the JSON error response body,
        or an empty string if the JSON couldn't be parsed."""

        result = ''
        if self._data_struct is not None:
            result = self._data_struct[KEY_MESSAGE]
        return result

    def get_code(self):
        """Return the code embedded in the JSON error response body,
        or an empty string if the JSON couldn't be parsed. This
        should always match the 'http_response'."""

        result = ''
        if self._data_struct is not None:
            result = self._data_struct[KEY_CODE]
        return result


class APIConfigurationException(Exception):
    """Thrown when the API isn't properly configured."""

    msg = None

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def get_message(self):
        """Returns the error message."""
        return self.msg


class APIDataException(Exception):
    """Thown when we can't parse the data returned by an API call."""

    base_exception = None
    offending_data = None
    msg = None

    def __init__(self, e=Exception, offending_data=None, msg=None):
        """Initializer.

        'msg' is additional information that might be valuable for
        determining the root cause of the exception."""

        Exception.__init__(self)

        self.base_exception = e
        self.offending_data = offending_data
        self.msg = msg

    def get_offending_data(self):
        """Returns the JSON data that caused the exception to be thrown
        in the first place."""

        return self.offending_data

    def get_base_exception(self):
        """Returns the exception that was oritinally thrown and caught
        which in turn generated this one. Unlikely to be useful."""

        return self.base_exception

    def get_msg(self):
        """Return whateve message the application programmer might have
        considered useful when throwing this exception."""

        return self.msg


######################################
##                                  ##
##  EVERYTHING BELOW IS DEPRECATED  ##
##                                  ##
######################################

KEY = None # Our key. Deprecated.
CONN = None # Our connection pool. Deprecated.

# The API functions.

def get_bundle_list(href=None, limit=None, embed_items=None,
                    embed_tracks=None, embed_metadata=None):
    print("This function is deprecated. Please use the Client class.")
    return _get_bundle_list(href, limit, embed_items, embed_tracks,
                            embed_metadata)


def _get_bundle_list(href=None, limit=None, embed_items=None,
                     embed_tracks=None, embed_metadata=None):
    """Get a list of available bundles.

    'href' the relative href to the bundle list to retriev. If None, the
    first bundle list will be returned.
    'limit' the maximum number of bundles to include in the result.
    'embed_items' whether or not to expand the bundle data into the result.
    'embed_tracks' whether or not to expand the bundle track data into
    the result.
    'embed_metadata' whether or not to expand the bundle metadata into
    the result.

    NB: providing values for 'limit', 'embed_*' will override either the
    API default or the values in the provided href.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Argument error checking.
    assert limit is None or limit > 0

    j = None
    if href is None:
        j = _get_first_bundle_list(limit, embed_items, embed_tracks,
                                   embed_metadata)
    else:
        j = _get_additional_bundle_list(href, limit, embed_items,
                                        embed_tracks, embed_metadata)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(j)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, j, msg)

    return result


def _get_first_bundle_list(limit=None, embed_items=None,
                           embed_tracks=None, embed_metadata=None):
    """Get a list of available bundles.

    'limit' may be None, which implies API default.  If not None, must be > 1.
    'embed_items' True will embed item data in the result.
    'embed_tracks' True will embed track data in the embeded items.
    'embed_metadata' True will embed metadata in the embeded items.

    Note that including tracks and metadata without including items is
    meaningless.

    Returns the raw JSON returned by the API.

    If the response status is not 2xx, throws an APIException."""

    # Prepare the data we're going to include in our query.
    path = '/' + __api_version__ + '/' + BUNDLES_PATH

    data = None
    fields = {}
    if limit is not None:
        fields['limit'] = limit
    embed = process_embed(embed_items=embed_items,
                          embed_tracks=embed_tracks,
                          embed_metadata=embed_metadata)
    if embed is not None:
        fields['embed'] = embed

    if len(fields) > 0:
        data = fields

    raw_result = get(path, data)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)
    else:
        result = raw_result.json

    return result


def _get_additional_bundle_list(href=None, limit=None, embed_items=None,
                                embed_tracks=None, embed_metadata=None):
    """Get next, previous, first, last list (page) of available bundles.

    'href' the href to retrieve the bundles.

    All other arguments override arguments in the href.

    Returns the raw JSON returned by the API.

    If the response status is not 2xx, throws an APIException."""

    url_components = urllib.parse.urlparse(href)
    path = url_components.path
    data = urllib.parse.parse_qs(url_components.query)

    # Change all lists into discrete values.
    for key in data.keys():
        data[key] = data[key][0]
        
    # Deal with limit overriding.
    if limit is not None:
        data['limit'] = limit

    # Deal with embeds overriding.
    final_embed = process_embed_override(data.get('embed'),
                                         embed_items,
                                         embed_tracks,
                                         embed_metadata)
    if final_embed is not None:
        data['embed'] = final_embed

    raw_result = get(path, data)

    if raw_result.status < 200 or raw_result.status > 202:
        print('*****')
        print(raw_result.status)
        print(raw_result.json)
        print('*****')
        raise APIException(raw_result.status, raw_result.json)
    else:
        result = raw_result.json

    return result


def create_bundle(name=None, media_url=None, audio_channel=None,
                  metadata=None, notify_url=None):
    print("This function is deprecated. Please use the Client class.")
    return _create_bundle(name, media_url, audio_channel, metadata,
                          notify_url)


def _create_bundle(name=None, media_url=None, audio_channel=None,
                  metadata=None, notify_url=None):
    """Create a new bundle.

    'metadata' may be None, or an object that can be converted to a JSON
    string.  See API documentation for restrictions.  The conversion
    will take place before the API call.

    All other parameters are also optional. For information about these
    see https://api.clarify.io/docs#!/audio/v1audio_post_1.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Prepare the data we're going to include in our bundle creation.
    path = '/' + __api_version__ + '/' + BUNDLES_PATH

    data = None

    fields = {}
    if name is not None:
        fields['name'] = name
    if media_url is not None:
        fields['media_url'] = media_url
    if audio_channel is not None:
        fields['audio_channel'] = audio_channel
    if metadata is not None:
        fields['metadata'] = json.dumps(metadata)
    if notify_url is not None:
        fields['notify_url'] = notify_url

    if len(fields) > 0:
        data = fields

    raw_result = post(path, data)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(raw_result.json)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, raw_result.json, msg)

    return result


def delete_bundle(href=None):
    print("This function is deprecated. Please use the Client class.")
    _delete_bundle(href)

        
def _delete_bundle(href=None):
    """
    Delete a bundle.

    :param href: the relative href to the bundle.
    :type href: string, may not be None
    :return: nothing
    :raises APIException: If the response code is not 204.
    """

    # Argument error checking.
    assert href is not None

    raw_result = delete(href)

    if raw_result.status != 204:
        raise APIException(raw_result.status, raw_result.json)


def get_bundle(href=None, embed_tracks=False, embed_metadata=False):
    print("This function is deprecated. Please use the Client class.")
    return _get_bundle(href, embed_tracks, embed_metadata)

    
def _get_bundle(href=None, embed_tracks=False, embed_metadata=False):
    """Get a bundle.

    'href' the relative href to the bundle. May not be None.
    'embed_tracks' determines whether or not to include track
    information in the response.
    'embed_metadata' determines whether or not to include metadata
    information in the response.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Argument error checking.
    assert href is not None

    data = None
    fields = {}
    embed = process_embed(embed_items=False,
                          embed_tracks=embed_tracks,
                          embed_metadata=embed_metadata)
    if embed is not None:
        fields['embed'] = embed

    if len(fields) > 0:
        data = fields

    raw_result = get(href, data)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)

    # Convert the JSON to a python data struct.
    try:
        result = json.loads(raw_result.json)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, raw_result.json, msg)

    return result


def update_bundle(href=None, name=None, notify_url=None, version=None):
    print("This function is deprecated. Please use the Client class.")
    return _update_bundle(href, name, notify_url, version)

    
def _update_bundle(href=None, name=None, notify_url=None, version=None):
    """Update a bundle.  Note that only the 'name' and 'notify_url' can
    be update.

    'href' the relative href to the bundle. May not be None.
    'name' the name of the bundle.  May be None.
    'notify_url' the URL for notifications on this bundle.
    'version' the object version.  May be None; if not None, must be
    an integer, and the version must match the version of the bundle.  If
    not, a 409 conflict error will cause an APIException to be thrown.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Argument error checking.
    assert href is not None
    assert version is None or isinstance(version, int)

    # Prepare the data we're going to include in our bundle update.
    data = None

    fields = {}
    if name is not None:
        fields['name'] = name
    if notify_url is not None:
        fields['notify_url'] = notify_url
    if version is not None:
        fields['version'] = version

    if len(fields) > 0:
        data = fields

    raw_result = put(href, data)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(raw_result.json)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, raw_result.json, msg)

    return result


def get_metadata(href=None):
    print("This function is deprecated. Please use the Client class.")
    return _get_metadata(href)

    
def _get_metadata(href=None):
    """Get metadata.

    'href' the relative href to the metadata. May not be None.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Argument error checking.
    assert href is not None

    raw_result = get(href)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(raw_result.json)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, raw_result.json, msg)

    return result


def update_metadata(href=None, metadata=None, version=None):
    print("This function is deprecated. Please use the Client class.")
    return _update_metadata(href, metadata, version)


def _update_metadata(href=None, metadata=None, version=None):
    """Update the metadata in a bundle.
    be update.

    'href' the relative href to the metadata. May not be None.
    'metadata' may be None, or an object that can be converted to a JSON
    string.  See API documentation for restrictions.  The conversion
    will take place before the API call.
    'version' the object version.  May be None; if not None, must be
    an integer, and the version must match the version of the bundle.  If
    not, a 409 conflict error will cause an APIException to be thrown.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Argument error checking.
    assert href is not None
    assert metadata is not None
    assert version is None or isinstance(version, int)

    # Prepare the data we're going to include in our bundle update.
    data = None

    fields = {}
    if version is not None:
        fields['version'] = version
    fields['data'] = json.dumps(metadata)

    data = fields

    raw_result = put(href, data)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(raw_result.json)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, raw_result.json, msg)

    return result


def delete_metadata(href=None):
    print("This function is deprecated. Please use the Client class.")
    _delete_metadata(href)


def _delete_metadata(href=None):
    """Delete metadata.

    'href' the relative href to the bundle. May not be None.

    Returns nothing.

    If the response status is not 204, throws an APIException."""

    # Argument error checking.
    assert href is not None

    raw_result = delete(href)

    if raw_result.status != 204:
        raise APIException(raw_result.status, raw_result.json)


def create_track(href=None, media_url=None, label=None,
                 audio_channel=None):
    print("This function is deprecated. Please use the Client class.")
    return _create_track(href, media_url, label, audio_channel)


def _create_track(href=None, media_url=None, label=None,
                  audio_channel=None):
    """Add a new track to a bundle.  Note that the total number of
    allowable tracks is limited. See the API documentation for details.

    'href' the relative href to the tracks list. May not be None.
    'media_url' public URL to media file. May not be None.
    'label' short name for the track. May be None.
    'audio_channel' the channel(s) to use in a stereo file. May be
    None. For details see the API documentation.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, or if the maximum number of
    tracks is exceeded, throws an APIException.  If the JSON to python
    data struct conversion fails, throws an APIDataException."""

    # Argument error checking.
    assert href is not None
    assert media_url is not None

    # Prepare the data we're going to write.
    data = None

    fields = {}
    fields['media_url'] = media_url
    if label is not None:
        fields['label'] = label
    if audio_channel is not None:
        fields['audio_channel'] = audio_channel

    if len(fields) > 0:
        data = fields

    raw_result = post(href, data)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(raw_result.json)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, raw_result.json, msg)

    return result


def get_track_list(href=None):
    print("This function is deprecated. Please use the Client class.")
    return _get_track_list(href)


def _get_track_list(href=None):
    """Get track list.

    'href' the relative href to the track list. May not be None.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Argument error checking.
    assert href is not None

    raw_result = get(href)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(raw_result.json)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, raw_result.json, msg)

    return result


def get_track(href=None):
    print("This function is deprecated. Please use the Client class.")
    return _get_track(href)


def _get_track(href=None):
    """Get a track.

    'href' the relative href to the track. May not be None.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Argument error checking.
    assert href is not None

    raw_result = get(href)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(raw_result.json)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, raw_result.json, msg)

    return result


def delete_track_at_index(href=None, index=None):
    print("This function is deprecated. Please use the Client class.")
    _delete_track_at_index(href, index)
    

def _delete_track_at_index(href=None, index=None):
    """Delete a track, or all the tracks.

    'href' the relative href to the track list. May not be None.
    'index' the index of the track to delete. If none is given,
    all tracks are deleted.

    Returns nothing.

    If the response status is not 204, throws an APIException."""

    # Argument error checking.
    assert href is not None

    # Deal with any parameters that need to be passed in.
    data = None

    fields = {}
    if index is not None:
        fields['track'] = index

    if len(fields) > 0:
        data = fields

    raw_result = delete(href, data)

    if raw_result.status != 204:
        raise APIException(raw_result.status, raw_result.json)


def delete_track(href=None):
    print("This function is deprecated. Please use the Client class.")
    _delete_track(href)
    

def _delete_track(href=None):
    """Delete a track.

    'href' the relative index of the track. May not be none.

    Returns nothing.

    If the response status is not 204, throws and APIException."""

    # Argument error checking.
    assert href is not None

    raw_result = delete(href)

    if raw_result.status != 204:
        raise APIException(raw_result.status, raw_result.json)


def search(href=None, query=None, query_fields=None, query_filter=None,
           limit=None, embed_items=None, embed_tracks=None,
           embed_metadata=None):
    print("This function is deprecated. Please use the Client class.")
    return _search(href, query, query_fields, query_filter,
                   limit, embed_items, embed_tracks, embed_metadata)


def _search(href=None, query=None, query_fields=None, query_filter=None,
            limit=None, embed_items=None, embed_tracks=None,
            embed_metadata=None):

    """Search a media collection.

    'href' the relative href to the bundle list to retriev. If None, the
    first bundle list will be returned.
    'query' See API docs for full description. May not be None.
    'query_fields' See API docs for full description. May be None.
    'query_filter' See API docs for full description. May be None.
    'limit' the maximum number of bundles to include in the result.
    'embed_items' whether or not to expand the bundle data into the result.
    'embed_tracks' whether or not to expand the bundle track data into
    the result.
    'embed_metadata' whether or not to expand the bundle metadata into
    the result.

    NB: providing values for 'limit', 'embed_*' will override either the
    API default or the values in the provided href.

    Returns a data structure equivalent to the JSON returned by the API.

    If the response status is not 2xx, throws an APIException.
    If the JSON to python data struct conversion fails, throws an
    APIDataException."""

    # Argument error checking.
    assert query is not None
    assert limit is None or limit > 0

    if href is None:
        j = _search_p1(query, query_fields, query_filter, limit, embed_items,
                       embed_tracks, embed_metadata)
    else:
        j = _search_pn(href, limit, embed_items, embed_tracks, embed_metadata)

    # Convert the JSON to a python data struct.

    result = None

    try:
        result = json.loads(j)
    except (ValueError) as exception:
        msg = 'Unable to convert JSON string to python data structure.'
        raise APIDataException(exception, j, msg)

    return result


def _search_p1(query=None, query_fields=None, query_filter=None, limit=None,
               embed_items=None, embed_tracks=None,
               embed_metadata=None):
    """Function called to retrieve the first page."""

    # Prepare the data we're going to include in our query.
    path = '/' + __api_version__ + '/' + SEARCH_PATH

    data = None
    fields = {}
    fields['query'] = query
    if query_fields is not None:
        fields['query_fields'] = query_fields
    if query_filter is not None:
        fields['filter'] = query_filter
    if limit is not None:
        fields['limit'] = limit
    embed = process_embed(embed_items=embed_items,
                          embed_tracks=embed_tracks,
                          embed_metadata=embed_metadata)
    if embed is not None:
        fields['embed'] = embed

    if len(fields) > 0:
        data = fields

    raw_result = get(path, data)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)
    else:
        result = raw_result.json

    return result


def _search_pn(href=None, limit=None,
               embed_items=None, embed_tracks=None, embed_metadata=None):
    """Function called to retrieve pages 2-n."""

    url_components = urllib.parse.urlparse(href)
    path = url_components.path
    data = urllib.parse.parse_qs(url_components.query)

    # Change all lists into discrete values.
    for key in data.keys():
        data[key] = data[key][0]

    # Deal with limit overriding.
    if limit is not None:
        data['limit'] = limit

    # Deal with embeds overriding.
    final_embed = process_embed_override(data.get('embed'),
                                         embed_items,
                                         embed_tracks,
                                         embed_metadata)
    if final_embed is not None:
        data['embed'] = final_embed

    raw_result = get(path, data)

    if raw_result.status < 200 or raw_result.status > 202:
        raise APIException(raw_result.status, raw_result.json)
    else:
        result = raw_result.json

    return result

#
# Functions to set the API key and perform basic HTTP operations.
#

def set_key(key):
    print("This function is deprecated. Please use the Client class.")
    _set_key(key)

def _set_key(key):
    """
    Set the API key.

    'key' the API key.  May not be None.
    """
    global KEY
    assert key is not None
    KEY = key

    # As a side-effect of setting the key, we initialize our HTTPS
    # connection pool. This method should now be called init().

    global CONN
    CONN = urllib3.HTTPSConnectionPool(__host__, maxsize=1,
                                       cert_reqs='CERT_REQUIRED',
                                       ca_certs=certifi.where())


def _get_headers():
    """Get all the headers we're going to need:

    1. Authorization
    2. Content-Type
    3. User-agent

    Note that the User-agent string contains the library name, the libary
    version, and the python version. This will help us track what people
    are using, and where we should concentrate our development efforst."""

    if KEY is None:
        raise APIConfigurationException('set_key() must be called before '
                                        'any API operations can be performed.')

    user_agent = __api_lib_name__ + '/' + __version__ + '/' + PYTHON_VERSION

    return {'Authorization': 'Bearer ' + KEY,
            'User-Agent': user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'}


def get(path, data=None):
    """Executes a GET.

    'path' may not be None. Should include the full path to the resource.
    'data' may be None or a dictionary. These values will be appended
    to the path as key/value pairs.

    Returns a named tuple that includes:

    status: the HTTP status code
    json: the returned JSON-HAL

    If the key was not set, throws an APIConfigurationException."""

    # Argument error checking.
    assert path is not None

    # Execute the request.
    response = CONN.request('GET', path, data, _get_headers())
                                       
    # Extract the result.
    response_status = response.status
    response_content = response.data.decode()

    return Result(status=response_status, json=response_content)


def post(path, data):
    """Executes a POST.

    'path' may not be None, should not inlude a version number, and
    should not include a leading '/'
    'data' may be None or a dictionary.

    Returns a named tuple that includes:

    status: the HTTP status code
    json: the returned JSON-HAL

    If the key was not set, throws an APIConfigurationException."""

    # Argument error checking.
    assert path is not None
    assert data is None or isinstance(data, dict)

    # Execute the request.
    if data is None:
        data = {}
    response = CONN.request_encode_body('POST', path, data,
                                        _get_headers(), False)

    # Extract the result.
    response_status = response.status
    response_content = response.data.decode()

    return Result(status=response_status, json=response_content)


def delete(path, data=None):
    """Executes a DELETE.

    'path' may not be None. Should include the full path to the resoure.
    'data' may be None or a dictionary.

    Returns a named tuple that includes:

    status: the HTTP status code
    json: the returned JSON-HAL

    If the key was not set, throws an APIConfigurationException."""

    # Argument error checking.
    assert path is not None
    assert data is None or isinstance(data, dict)

    # Execute the request.
    response = CONN.request('DELETE', path, data, _get_headers())
    
    # Extract the result.
    response_status = response.status
    response_content = response.data.decode()

    # return (status, json)
    return Result(status=response_status, json=response_content)


def put(path, data):
    """Executes a PUT.

    'path' may not be None. Should include the full path to the resoure.
    'data' may be None or a dictionary.

    Returns a named tuple that includes:

    status: the HTTP status code
    json: the returned JSON-HAL

    If the key was not set, throws an APIConfigurationException."""

    # Argument error checking.
    assert path is not None
    assert data is None or isinstance(data, dict)

    # Execute the request.
    if data is None:
        data = {}
    response = CONN.request_encode_body('PUT', path, data,
                                        _get_headers(), False)

    # Extract the result.
    response_status = response.status
    response_content = response.data.decode()

    return Result(status=response_status, json=response_content)

#
# Utility functions.
#

def process_embed(embed_items=None,
                  embed_tracks=None,
                  embed_metadata=None):
    print("This function is deprecated.")
    return _process_embed(embed_items, embed_tracks, embed_metadata)


def _process_embed(embed_items=None,
                   embed_tracks=None,
                   embed_metadata=None):
    """Returns an embed field value based on the parameters."""

    result = None

    embed = ''
    if embed_items:
        embed = 'items'
    if embed_tracks:
        if embed != '':
            embed += ','
        embed += 'tracks'
    if embed_metadata:
        if embed != '':
            embed += ','
        embed += 'metadata'

    if embed != '':
        result = embed

    return result


def process_embed_override(href_embed=None,
                           embed_items=None,
                           embed_tracks=None,
                           embed_metadata=None):
    print("This function is deprecated.")
    return _process_embed_override(href_embed, embed_items,
                                   embed_tracks, embed_metadata)

    
def _process_embed_override(href_embed=None,
                            embed_items=None,
                            embed_tracks=None,
                            embed_metadata=None):
    """Returns an embed field value based on the parameters."""
    # Our defaults are None, which are the API defaults.
    final_items = None
    final_tracks = None
    final_metadata = None

    # First, figure out what was embedded in the original href.
    # If any of the embeds are there, flip the final to True
    if href_embed:
        if 'items' in href_embed:
            final_items = True
        if 'tracks' in href_embed:
            final_tracks = True
        if 'metadata' in href_embed:
            final_metadata = True

    # Second, override the what we have.
    # None >> Do nothing
    # True >> Set to True
    # False >> Set to None
    if embed_items is not None:
        if embed_items is True:
            final_items = True
        else:
            final_items = None
    if embed_tracks is not None:
        if embed_tracks is True:
            final_tracks = True
        else:
            final_tracks = None
    if embed_metadata is not None:
        if embed_metadata is True:
            final_metadata = True
        else:
            final_metadata = None

    return process_embed(embed_items=final_items,
                         embed_tracks=final_tracks,
                         embed_metadata=final_metadata)

def get_embedded_items(result_collection):
    """
    Given a result_collection (returned by a previous API call that
    returns a collection, like get_bundle_list() or search()), return a
    list of embedded items with each item in the returned list
    considered a result object.

    'result_collection' a JSON object returned by a previous API
    call. The parameter 'embed_items' must have been True when the
    result_collection was originally requested.May not be None.

    Returns a list, which may be empty if no embedded items were found.
    """

    # Argument error checking.
    assert result_collection is not None

    result = []

    embedded_objects = result_collection.get('_embedded')
    if embedded_objects is not None:
        # Handle being passed a non-collection gracefully.
        result = embedded_objects.get('items', result)

    return result

def get_item_hrefs(result_collection):
    """
    Given a result_collection (returned by a previous API call that
    returns a collection, like get_bundle_list() or search()), return a
    list of item hrefs.

    'result_collection' a JSON object returned by a previous API
    call.

    Returns a list, which may be empty if no items were found.
    """

    # Argument error checking.
    assert result_collection is not None

    result = []

    links = result_collection.get('_links')
    if links is not None:
        items = links.get('items')
        if items is not None:
            for item in items:
                result.append(item.get('href'))

    return result
    

def get_link_href(result_object, link_relation):
    """
    Given a result_object (returned by a previous API call), return
    the link href for a link relation.
    
    'result_object' a JSON object returned by a previous API call. May not
    be None.
    'link_relation' the link relation for which href is required.
    
    Returns None if the link does not exist.
    """

    # Argument error checking.
    assert result_object is not None

    result = None

    link = result_object['_links'].get(link_relation)
    if link:
        result = link.get('href')

    return result

def get_embedded(result_object, link_relation):
    """
    Given a result_object (returned by a previous API call), return
    the embedded object for link_relation.  The returned object can be
    treated as a result object in its own right.
    
    'result_object' a JSON object returned by a previous API call.
    The link relation of teh embedded object must have been specified
    when the result_object was originally requested. May not be None.
    'link_relation' the link relation for which href is required. May
    not be None.
    
    Returns None if the embedded object does not exist.
    """

    # Argument error checking.
    assert result_object is not None
    assert link_relation is not None

    result = None
    
    embedded_object = result_object['_embedded']
    if embedded_object:
        result = embedded_object.get(link_relation)

    return result

