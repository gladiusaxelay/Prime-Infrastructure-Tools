#!/usr/bin/env python
#
#     PrimeAPI
#       v0.1
#
#     Christian Jaeckel (chjaecke@cisco.com)
#       May 2016
#
#     This class provides methods to facilitates
#       access to the Prime Infrastructure API.
#
#     REQUIREMENTS:
#       - Python requests library
#
#     WARNING:
#       Any use of these scripts and tools is at
#       your own risk. There is no guarantee that
#       they have been through thorough testing in a
#       comparable environment and we are not
#       responsible for any damage or data loss
#       incurred with their use.
#
import urllib.parse as urlparse
import xml.etree.ElementTree as ET
import requests
from base64 import b64encode
from time import sleep
from requests.packages.urllib3.exceptions import InsecureRequestWarning

"""
Default base URI of the Prime API
"""
DEFAULT_API_URI = "/webacs/api/v1/"

"""
Timer to make a pause of X seconds after each API request
"""
SLEEP_TIME = 0.1

class PrimeAPIError(Exception):
    """
    Generic error raised by the Prime API module.
    """


class PrimeAPI(object):

    def __init__(self, url, username, password):
        """
        Constructor of the PrimeAPI class.
        """
        self.base_url = urlparse.urljoin(url, DEFAULT_API_URI)
        self.username = username
        self.password = password

        # Disable HTTPS warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _parse(self, response):
        """
        Check API response if an error code was returned through the status code.

        :param response: Requests response to parse for errors.
        :return: Either raises an error or returns nothing if response is ok.
        """

        if response.status_code == 200:
            return
        elif response.status_code == 302:
            raise Exception("Incorrect credentials provided")
        elif response.status_code == 400:
            response_json = response.json()
            raise Exception("Invalid request: %s" % response_json["errorDocument"]["message"])
        elif response.status_code == 401:
            raise Exception("Unauthorized access")
        elif response.status_code == 403:
            raise Exception("Forbidden access to the REST API")
        elif response.status_code == 404:
            raise Exception("URL not found %s" % response.url)
        elif response.status_code == 406:
            raise Exception("The Accept header sent in the request does not match a supported type")
        elif response.status_code == 415:
            raise Exception("The Content-Type header sent in the request does not match a supported type")
        elif response.status_code == 500:
            raise Exception("An error has occurred during the API invocation")
        elif response.status_code == 502:
            raise Exception("The server is down or being upgraded")
        elif response.status_code == 503:
            raise Exception("The servers are up, but overloaded with requests. Try again later (rate limiting)")
        else:
            raise PrimeAPIError("Unknown Request Error, return code is %s" % response.status_code)


    def send_prime_request(self, ressource_url, type = "JSON"):
        """
        Constructor of the PrimeAPI class.

        :param ressource_url: Ressource URL of the API function including filtering arguments, type, etc.
                                Example: data/ConfigVersions.xml?.maxResults=%s&.firstResult=%s
        :param type: Response types include "XML" or "JSON". If not specified, then the response text is returned.
        :return: REST response either encoded as XML, JSON or in plain text.
        """

        # Base 64 encoding of username and password
        enc = b64encode(('%s:%s' % (self.username, self.password)).encode('latin1')).strip()

        auth = 'Basic ' + enc.decode('ascii')
        headers = {
            "authorization": auth,
            "cache-control": "no-cache",
            "Connection": "close"
        }

        # Send API request
        session = requests.Session()

        # Abort query if timeout of 10 sec is exceeded
        response = session.request("GET", self.base_url + ressource_url, timeout=10, verify=False, headers=headers)

        # Check if status code contains an error
        self._parse(response)

        # Sleep timer to prevent excessive requests
        sleep(SLEEP_TIME)

        if type == "JSON":
            return response.json()
        elif type == "XML":
            return ET.fromstring(response.content)
        else:
            return response.content
