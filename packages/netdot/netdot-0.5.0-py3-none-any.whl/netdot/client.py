import logging
from contextlib import AbstractContextManager
from typing import Any, Dict, List

import requests
import urllib3

from . import config, exceptions, parse, trace, utils, validate

logger = logging.getLogger(__name__)


# TODO Eventually collapse v1 into the "Client" class below -- or make this into a different layer entirely
class Client_v1(AbstractContextManager):
    """NetDot Client_v1 (to be deprecated) -- provides access to NetDot data directly as dicts."""

    def __init__(self, server, username, password, verify_ssl=None, timeout=None):
        """Connect to a Netdot Server to begin making API requests.
        
        Args:
            server (str): The URL of the Netdot server.
            username (str): The username to login to Netdot with.
            password (str): The password to login to Netdot with.
            verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to (not config.SKIP_SSL).
            timeout (int|tuple, optional): The number of seconds to wait for a response from the API server. Defaults to (config.CONNECT_TIMEOUT, config.TIMEOUT,).
        """
        self.user = username
        self.timeout = timeout or tuple([config.CONNECT_TIMEOUT, config.TIMEOUT])
        self.http = requests.session()
        self.http.verify = verify_ssl or (not config.SKIP_SSL)
        self.http.headers.update(
            {
                'User_Agent': 'Netdot::Client::REST/self.version',
                'Accept': 'text/xml; version=1.0',
            }
        )

        # Setup URLs
        self.server = server
        self.base_url = f'{server}/rest'
        self.login_url = f'{server}/NetdotLogin'
        self.logout_url = f'{server}/logout.html'

        # Actually login (and load a test page)
        self._login(username, utils.HiddenString(password))

    def __exit__(self):  # pragma: no cover
        self.logout()

    def _login(self, username, password):
        """Log into the NetDot API with provided credentials.
        Stores the generated cookies to be reused in future API calls.
        """
        params = {
            'destination': 'index.html',
            'credential_0': username,
            'credential_1': password,
            'permanent_session': 1,
        }
        try:
            response = self.http.post(self.login_url, data=params, timeout=self.timeout)
        except ConnectionError:
            raise exceptions.NetdotLoginError(
                f'Unable to reach to Netdot server: {self.server} (Maybe you need to use a VPN?)'
            )
        if response.status_code != 200:
            raise exceptions.NetdotLoginError(
                f'Login failed. Most likely caused by invalid credentials for user: {username}'
            )

    def logout(self):
        """
        Logout of the NetDot API (and cleanup local http session)
        """
        self.http.post(self.logout_url, timeout=self.timeout)
        self.http.close()

    @staticmethod
    def validate_response(response):
        Client.warn_if_carp_croak(response)
        logger.debug(f'HTTP Response: {response}')
        response.raise_for_status()

    @staticmethod
    def warn_if_carp_croak(response):
        if response.text and 'Carp::croak' in response.text:
            lines = response.text.split('\n')
            for line_num in range(len(lines)):
                if 'Carp::croak' in lines[line_num]:
                    logger.warning('Response includes possible error:' 
                                   + '\n'.join(lines[line_num-3:line_num]))

    def get_xml(self, url):
        """
        This function provides a simple interface
        into the "GET" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url

        Usage:
          response = netdot.Client.get_xml("/url")

        Returns:
          XML string output from Netdot
        """
        response = self.http.get(self.base_url + url, timeout=self.timeout)
        self.validate_response(response)
        return response.content

    def get(self, url_path, **url_params):
        """
        This function delegates to get_xml() and parses the
        response xml to return a dict

        Arguments:
          url -- Url to append to the base url

        Usage:
          dict = netdot.Client.get("/url")
          dict = netdot.Client.get("/url", depth=2)

        Returns:
          Result as a multi-level dictionary on success.
        """
        final_url = url_path
        if url_params:
            url_params_list = list()
            for field, value in url_params.items():
                url_params_list.append(f'{field}={value}')
            url_params_str = '&'.join(url_params_list)
            final_url = f'{url_path}?{url_params_str}'
        return parse.RESTful_XML(self.get_xml(final_url))

    def get_objects_by_filter(self, object, field, value, **url_params):
        """
        Returns a multi-level dict of an objects (device, interface, rr, person)
        filtered by an object field/attribute
        Arguments:
          object -- NetDot object ID
          field -- NetDot field/attribute of object
          value -- The value to select from the field.

        Returns:
          List[Dict]: List of objects that match the filter.
        """
        url_params[field] = value
        return self.get(f'/{object}', **url_params)

    def post(self, url, data):
        """
        This function provides a simple interface
        into the "POST" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url
          data -- dict of key/value pairs that the form requires

        Usage:
          response = netdot.Client.post("/url", {form-data})

        Returns:
          Result as a multi-level dictionary on success
        """
        response = self.http.post(self.base_url + url, data=data, timeout=self.timeout)
        self.validate_response(response)
        validate.RESTful_XML(response.content)
        return parse.RESTful_XML(response.content)

    def delete(self, url):
        """
        This function provides a simple interface
        into the "HTTP/1.0 DELETE" function by handling the authentication
        cookies as well as the required headers and base_url for
        each request.

        Arguments:
          url -- Url to append to the base url

        Usage:
          response = netdot.Client.delete("/url")

        Returns:
          Result as an empty multi-level dictionary
        """
        response = self.http.delete(self.base_url + url, timeout=self.timeout)
        self.validate_response(response)
        return response.content

    def create_object(self, object, data):
        """
        Create object record when it's parameters are known.
        Parameters are passed as key:value pairs in a dictionary

        Arguments:
          data -- key:value pairs applicable for an object:
                  (e.g. a device below)
                name:                 'devicename'
                snmp_managed:         '0 or 1'
                snmp_version:         '1 or 2 or 3'
                community:            'SNMP community'
                snmp_polling:         '0 or 1'
                canautoupdate:        '0 or 1'
                collect_arp:          '0 or 1'
                collect_fwt:          '0 or 1'
                collect_stp:          '0 or 1'
                info:                 'Description string'

        Usage:
          response = netdot.Client.create_device("device",
                                                 {'name':'my-device',
                                                  'snmp_managed':'1',
                                                  'snmp_version':'2',
                                                  'community':'public',
                                                  'snmp_polling':'1',
                                                  'canautoupdate':'1',
                                                  'collect_arp':'1',
                                                  'collect_fwt':'1',
                                                  'collect_stp':'1',
                                                  'info':'My Server'}

        Returns:
          Created record as a multi-level dictionary.
        """
        return self.post("/" + object, data)

    def delete_object_by_id(self, object, id):
        """
        This function deletes an object record by it's id

        Arguments:
          object -- 'device', 'vlan', etc...
          id  -- Object ID

        Usage:
          response = netdot.Client.delete_object_by_id("device", "id")

        Returns:
        """
        return self.delete(f'/{object}/{id}')


class Client(Client_v1):
    """NetDot Client (v2) -- provides access to NetDot data directly as dicts."""
    def __init__(self, *args, times_to_retry=3, trace_downloads=None, trace_threshold_bytes=None, **kwargs):
        self._retries = times_to_retry
        self._retries_config = urllib3.Retry(total=times_to_retry)
        self._trace_downloads = trace_downloads or config.TRACE_DOWNLOADS
        self._download_tracer: trace.DownloadTracer
        if trace_downloads:
            self.enable_trace_downloads(trace_threshold_bytes or config.TRACE_THRESHOLD)
        super().__init__(*args, **kwargs)

    @property
    def netdot_url(self) -> str:
        return self.server

    def disable_trace_downloads(self):
        """Disable download tracing feature."""
        self._trace_downloads = False

    def enable_trace_downloads(self, threshold_bytes=None):
        """Enable (and reset) the DownloadTracer object associated to this Netdot Client. (resetting it back to '0 bytes downloaded')

        Args:
            threshold_bytes (bool, optional): How many bytes to wait between log messages. Defaults to config.TRACE_THRESHOLD.
        """
        self._trace_downloads = True
        self._download_tracer = trace.DownloadTracer('Netdot', threshold_bytes or config.TRACE_THRESHOLD)

    def get_xml(self, url_path: str) -> bytes:
        #
        # Override get_xml to decorate it with a 'download tracker'.
        #
        ENCODING = 'UTF-8'
        response = super().get_xml(url_path)
        if self._trace_downloads:
            self._download_tracer.trace(len(response))
        try:
            return response.decode(ENCODING)
        except UnicodeDecodeError: 
            logger.exception(f'Unable to decode {ENCODING} data: {response}')
            return response

    def get(self, url_path: str, **url_params) -> Dict:
        """Get some data from Netdot REST API.

        Arguments:
            url_path: Path to append to the base url.

        Returns:
            Dict: Result as a multi-level dictionary on success.
        """
        return self._get_with_retries(
            url_path, times_to_retry=self._retries, **url_params
        )

    def delete_object_by_id(self, object: str, id: str):
        response = super().delete_object_by_id(object, id)
        if response.strip() != b'':  # pragma no cover
            # Defensive Programming: delete will never return any data.
            raise exceptions.NetdotDeleteError(
                f"Unable to delete {object} with id {id}. (delete returned a response)", response=response
            )

    def _get_with_retries(self, url_path: str, times_to_retry: int, **url_params):
        """Wrapper around super().get. Retry the get request if it fails."""
        try:
            return super().get(url_path, **url_params)
        except (requests.exceptions.RequestException, urllib3.exceptions.ProtocolError) as e:
            if hasattr(e.response, 'status_code') and e.response.status_code == 404:
                raise e  # No need to retry for HTTP 404 responses
            if times_to_retry > 0:
                logger.exception(
                    f'Request to "{url_path}" failed due to: "{e}". (Will retry {times_to_retry} more times)'
                )
                return self._get_with_retries(
                    url_path, times_to_retry - 1, **url_params
                )
            else:
                raise e

    def get_objects_by_filter(
        self, table: str, column: str, search_term: Any, **url_params
    ) -> List[Dict]:
        """Filter records from a table. Retrieve all the records from the "table" that match the
        provided "search_term", for "column".

        Args:
            table (str): The table name of the table to be searched (in CamelCase).
            column (str): The column name of the column to be searched.
            search_term (Any): The particular id/str/value you are looking for in the table.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: For any HTTP errors. (error details can be found in Netdot's apache server logs)

        Returns:
            List: A list of any objects that match "search_term" for "column" in "table".
        """
        data = super().get_objects_by_filter(table, column, search_term, **url_params)
        # API returns a 1-item dictionary with table name as "the key" and list of results as "the value".
        # We only want to return the list of results.
        core_data = data[table]
        return list(core_data.values())

    def get_object_by_id(self, table: str, id: int, **url_params) -> Dict:
        """Retrieve the object from 'table' with the given 'id'.

        Args:
            table (str): The table name of the table to be searched (in CamelCase).
            id (int): The particular id you are looking for in the table.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: For any HTTP errors. (error details can be found in Netdot's apache server logs)
        """
        objects = self.get_objects_by_filter(table, 'id', id, **url_params)
        if len(objects) > 1:  # pragma: no cover
            # Defensive programming: This is very unlikely to happen.
            raise exceptions.NetdotRESTError(f'Found multiple {utils.pluralize(table)} with id={id}', response=objects)
        if len(objects) < 1:  # pragma: no cover
            # Defensive programming: This is unreachable, since a HTTP 404 occurs first.
            # So, an HTTPError will be raised before this code can ever run.
            raise exceptions.NetdotRESTError(f'Unable to find {table} with id: {id}')
        return objects[0]

    def get_all(self, table: str, **url_params) -> List:
        all_data = self.get(f'/{table}', **url_params)
        if all_data:
            all_data = all_data[table]
            all_objects = list(all_data.values())
            return all_objects
        else:  # pragma: no cover
            # Defensive programming: This is unreachable, since a HTTP 404 occurs first.
            # So, an HTTPError will be raised before this code can ever run.
            return list()
