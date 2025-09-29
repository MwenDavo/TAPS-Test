from logging import DEBUG, getLogger
from typing import TYPE_CHECKING

from beamngpy.connection import CommBase
from beamngpy.logging import LOGGER_ID

from beamngpy.types import Float3, StrDict

if TYPE_CHECKING:
    from beamngpy.beamng import BeamNGpy
    from beamngpy.vehicle import Vehicle

__all__ = ["TAPS"]


class TAPS(CommBase):
    def __init(self, name: str,
               bng: BeamNGpy,
               vehicle: Vehicle,
               gfx_update_time: float = 0.0,
               physics_update_time: float = 0.01,
               is_send_immediately: bool = False,
               is_visualised: bool = True,
               ):
        super().__init__(bng, vehicle)

        self.logger = getLogger(f"{LOGGER_ID}.TAPS")
        self.logger.setLevel(DEBUG)

        # Cache some properties we will need later.
        self.name = name
        self.is_send_immediately = is_send_immediately
        self.vehicle = vehicle

        # Create and initialise this sensor in the simulation.
        self._open_TAPS(
            name,
            vehicle,
            gfx_update_time,
            physics_update_time,
            is_send_immediately,
            is_visualised
        )

        # Fetch the unique Id number (in the simulator) for this GPS sensor.  We will need this later.
        self.sensorId = self._get_TAPS_id()

        self.logger.debug("TAPS - sensor created: " f"{self.name}")

    def remove(self) -> None:
        """
        Removes this sensor from the simulation.
        """
        # Remove this sensor from the simulation.
        self._close_TAPS()
        self.logger.debug("TAPS - sensor removed: " f"{self.name}")

    def poll(self) -> StrDict:
        """
        Gets the most-recent readings for this sensor.
        Note: if this sensor was created with a negative update rate, then there may have been no readings taken.

        Returns:
            A dictionary containing the sensor readings data.  Depending on the set poll timings, there may be multiple readings.  The data in each reading, by key, is as follows:
            time: the time at which the reading was taken, in seconds.
            x: the world-space X-axis position of the sensor, at the time of the reading, in meters.
            y: the world-space Y-axis position of the sensor, at the time of the reading, in meters.
            lon: the longitude of the sensor, relative to the set origin, in degrees.
            lat: the latitude of the sensor, relative to the set origin, in degrees.
        """
        # Send and receive a request for readings data from this sensor.
        readings_data = []
        if self.is_send_immediately:
            # Get the most-recent single reading from vlua.
            readings_data = self._poll_GPS_VE()
        else:
            # Get the bulk data from ge lua.
            readings_data = self._poll_GPS_GE()

        self.logger.debug(
            "TAPS - sensor readings received from simulation: " f"{self.name}"
        )
        return readings_data

    def send_ad_hoc_poll_request(self) -> int:
        """
        Sends an ad-hoc polling request to the simulator. This will be executed by the simulator immediately, but will take time to process, so the
        result can be queried after some time has passed. To check if it has been processed, we first call the is_ad_hoc_poll_request_ready() function,
        then call the collect_ad_hoc_poll_request() function to retrieve the sensor reading.

        Returns:
            A unique Id number for the ad-hoc request.
        """
        self.logger.debug("TAPS - ad-hoc polling request sent: " f"{self.name}")
        return int(
            self.send_recv_ge(
                "SendAdHocRequestTAPS", name=self.name, vid=self.vehicle.vid
            )["data"]
        )

    def is_ad_hoc_poll_request_ready(self, request_id: int) -> bool:
        """
        Checks if a previously-issued ad-hoc polling request has been processed and is ready to collect.

        Args:
            request_id (int): The unique Id number of the ad-hoc request. This was returned from the simulator upon sending the ad-hoc polling request.

        Returns:
            A flag which indicates if the ad-hoc polling request is complete.
        """
        self.logger.debug(
            "TAPS - ad-hoc polling request checked for completion: " f"{self.name}"
        )
        return self.send_recv_ge("IsAdHocPollRequestReadyTAPS", requestId=request_id)[
            "data"
        ]

    def collect_ad_hoc_poll_request(self, request_id: int) -> StrDict:
        """
        Collects a previously-issued ad-hoc polling request, if it has been processed.

        Args:
            request_id: The unique Id number of the ad-hoc request. This was returned from the simulator upon sending the ad-hoc polling request.

        Returns:
            The readings data.
        """
        readings = self.send_recv_ge(
            "CollectAdHocPollRequestTAPS", requestId=request_id
        )["data"]
        self.logger.debug(
            "TAPS - ad-hoc polling request returned and processed: " f"{self.name}"
        )
        return readings

    def set_requested_update_time(self, requested_update_time: float) -> None:
        """
        Sets the current 'requested update time' value for this sensor.

        Args:
            requested_update_time: The new requested update time.
        """
        self.send_ack_ge(
            "SetTAPSRequestedUpdateTime",
            ack="CompletedSetTAPSRequestedUpdateTime",
            name=self.name,
            vid=self.vehicle.vid,
            GFXUpdateTime=requested_update_time,
        )

    def set_is_visualised(self, is_visualised: bool) -> None:
        """
        Sets whether this sensor is to be visualised or not.

        Args:
            is_visualised: A flag which indicates if this sensor is to be visualised or not.
        """
        self.send_ack_ge(
            "SetTAPSIsVisualised",
            ack="CompletedSetTAPSIsVisualised",
            name=self.name,
            vid=self.vehicle.vid,
            isVisualised=is_visualised,
        )

    def _get_TAPS_id(self) -> int:
        return int(self.send_recv_ge("GetTAPSId", name=self.name)["data"])

    def _open_TAPS(
        self,
        name: str,
        vehicle: Vehicle,
        gfx_update_time: float,
        physics_update_time: float,
        is_send_immediately: bool,
        is_visualised: bool,
    ) -> None:
        data: StrDict = dict()
        data["name"] = name
        data["vid"] = vehicle.vid
        data["GFXUpdateTime"] = gfx_update_time
        data["physicsUpdateTime"] = physics_update_time
        data["isSendImmediately"] = is_send_immediately
        data["isVisualised"] = is_visualised
        self.send_ack_ge(type="OpenTAPS", ack="OpenedTAPS", **data)
        self.logger.info(f'Opened TAPS sensor: "{name}"')

    def _close_TAPS(self) -> None:
        self.send_ack_ge(
            type="CloseTAPS", ack="ClosedTAPS", name=self.name, vid=self.vehicle.vid
        )
        self.logger.info(f'Closed TAPS sensor: "{self.name}"')

    def _poll_TAPS_GE(self) -> StrDict:
        return self.send_recv_ge("PollTAPSGE", name=self.name)["data"]

    def _poll_TAPS_VE(self) -> StrDict:
        return self.send_recv_veh("PollTAPSVE", name=self.name, sensorId=self.sensorId)[
            "data"
        ]