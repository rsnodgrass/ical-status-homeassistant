"""
Support for Flo Water Security System

SENSORS:
flowrate (gpm)
pressure (psi)
temp (F)
total_flow (cumulative for day)
last health test timestamp

SWITCHES:
mode (home/away/sleep)
water status (on/off)
"""
import logging

from homeassistant.components.sensor import DOMAIN

from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, CONF_NAME, CONF_TIMEOUT
)
from homeassistant.helpers import aiohttp_client, config_validation as cv

from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

FLO_HASS_SLUG = 'flowater'

# pylint: disable=unused-argument
def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Setup the Flo Water Security System integration."""

    name = config[CONF_NAME]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    flo_service = FloService(username, password, 30)
    sensors = FloService.hass_sensors()

    # execute any callback after entities have been created
    add_entities_callback(sensors)

    hass.data[FLO_HASS_SLUG] = {}
    hass.data[FLO_HASS_SLUG]['sensors'] = []
    hass.data[FLO_HASS_SLUG]['sensors'].extend(sensors)

class FloService():
    def __init__(self, username, password, refresh_interval):

        self._auth_token = None
        self._username = username
        self._password = password

        self._refresh_interval = refresh_interval
        self._last_update_timestamp = 0

        self._sensors = {}

    def _get_authentication_token(self):
        if not self._token:

            # authenticate to the Flo API
            #   POST https://api.meetflo.com/api/v1/users/auth
            #   Payload: {username: "your@email.com", password: "1234"}
            _LOGGER.debug("Authenticating to Flo with account %s (refresh interval %d seconds)",
                          self._username, self._refresh_interval)

            auth_url = 'https://api.meetflo.com/api/v1/users/auth'
            payload = {
                'username': self._username,
                'password': self._password
            }
            response = requests.Request('POST', auth_url, data=json.dumps(payload)).prepare()
            # Response: { "token":"caJhb.....",
            #             "tokenPayload": { "user": { "user_id":"9aab2ced-c495-4884-ac52-b63f3008b6c7","email":"your@email.com"},
            #                               "timestamp": 1559246133 },
            #             "tokenExpiration": 86400,
            #             "timeNow": 1559226161 }

            _LOGGER.debug("Flo authentication of %s received %s", self._username, response.json())
            self._auth_token = response.json()['token']

        return self._auth_token

    def trigger_update(self):
        elapsed_time = datetime.datetime.now() - self._last_update_timestamp

        # only refresh the Flo data if the refresh interval has passed
        if elapsed_time.total_seconds() >= self._refresh_interval:
            self._update_state_from_service()
            self._last_update_timestamp = datetime.datetime.now()

    def _flo_get_request(self, url)
         headers = { 'authorization': auth_token }
         response = requests.Request('GET', url, headers=headers).prepare()
         _LOGGER.info("Flo GET %s : %s", url, response.content)
         return response

    def _update_state_from_service(self):
        token = self._get_authentication_token()

        response = self._flo_get_request('https://api.meetflo.com/api/v1/icds/me')
        # Response: { "is_paired":true,
        #             "device_id":"a0b405bfe487",
        #             "id":"2faf8cd6-a8eb-4b63-bd1a-33298a26eca8",
        #             "location_id":"e7b2833a-f2cb-a4b1-ace2-36c21075d493" }
        json = response.json()
 
        # FIXME: support multiple devices!
        self._sensor = FloSensor(icd_id, json)
        self._sensors[ json['device_id'] = self._sensor
        
        self._update_sensor( self._sensor )

    def _update_sensor(self, sensor)
        # for each Flo device, request the latest data
        # FIXME: does it require from=? add from= based on timeNow returned from auth?  or is this UTC timestamp?
        waterflow_url = 'https://api.meetflo.com/api/v1/waterflow/measurement/icd/' + 
                        sensor.flo_id() + '/last_day?from=1559246263815'
        response = self._flo_get_request(waterflow_url)
        # Response: [ {
        #               "average_flowrate": 0,
        #               "average_pressure": 86.0041294012751,
        #               "average_temperature": 68,
        #               "did": "606405bfe487",
        #               "total_flow": 0,
        #               "time": "2019-05-30T07:00:00.000Z"
        #             }, {}, ... ]
        json = response.json()

                       # FIXME

        self._sensor.update_state(state, last_activity_timestamp)


    # return all the known sensors
    def sensors(self):
        return self._sensors.values()

# pylint: disable=too-many-instance-attributes
class FloSensor(Entity):
    """Sensor representation of a Flo Water Security System"""

    def __init__(self, flo_icd_id, json):
        self._flo_icd_id = flo_icd_Id
        self._json = json
        self._area_name = None

    @property
    def integration(self):
        """Return the Integration ID"""
        return self._integration

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return flo_icd_id


    @property
    def flo_id(self) -> str:
        """Return Flo sensor id."""
        return flo_icd_id

    @property
    def name(self):
        """Return the display name of this sensor"""
        return self._name

    @property
    def device_state_attributes(self):
        """Return device specific state attributes"""
        attr = {ATTR_INTEGRATION_ID: self._integration}
        if self._area_name:
            attr[ATTR_AREA_NAME] = self._area_name
        return attr

    @property
    def state(self):
        """State of the device"""
        return self._state

    def update_state(self, state):
        """Update state"""
        self._state = state
