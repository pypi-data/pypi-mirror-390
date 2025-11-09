import json
import time

from typing import Any, Dict, cast
from typing_extensions import override
from masterpiece.mqtt import MqttMsg
from juham_core import Juham, MasterPieceThread, JuhamThread

from .shelly import Shelly


class ShellyMotionSimulatorThread(MasterPieceThread):
    """Thread simulating Shelly Plus 1 wifi relay with four temperature
    sensors."""

    def __init__(self, topic: str = "", interval: float = 60) -> None:
        """Construct thread for simulating data from Shelly motion sensors.

        Args:
            topic (str, optional): MQTT topic to post the sensor readings. Defaults to None.
            interval (float, optional): Interval specifying how often the sensor is read. Defaults to 60 seconds.
        """
        super().__init__(None)
        self.shelly_topic: str = topic
        self.interval: float = interval

    @override
    def update_interval(self) -> float:
        return self.interval

    @override
    def update(self) -> bool:
        super().update()

        m: dict[str, Any] = {
            "tmp": {"value": 22.5},  # Room temperature value
            "sensor": {
                "vibration": True,  # Vibration status
                "motion": False,  # Motion status
            },
            "unixtime": int(time.time()),
        }

        msg = json.dumps(m)
        self.publish(self.shelly_topic, msg, 1, True)
        return True


class ShellyMotionSimulator(JuhamThread, Shelly):
    """Simulator for Shelly Motion 2 - a wifi motion sensor. Spawns a thread
    to generate MQTT messages as if they origin from the actual Shelly motion sensor"""

    workerThreadId = ShellyMotionSimulatorThread.get_class_id()
    shelly_topic = "shellies/shellymotion2/info"
    update_interval = 60

    def __init__(
        self,
        name: str = "shellymotionsensor",
        topic: str = "",
        interval: float = 60,
    ) -> None:
        """Create Shelly motion sensor simulator.

        Args:
            name (str, optional): Name of the object. Defaults to 'shellymotionsensor'.
            topic (str, optional): MQTT topic to publish motion sensor events. Defaults to None.
            interval (float, optional): interval between events, in seconds. Defaults to None.
        """
        super().__init__(name)
        self.active_liter_lpm = -1
        self.update_ts = None
        if topic:
            self.topic = topic
        if interval:
            self.interval = interval

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.shelly_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.shelly_topic:
            em = json.loads(msg.payload.decode())
            self.on_sensor(em)
        else:
            super().on_message(client, userdata, msg)

    def on_sensor(self, em: dict[str, Any]) -> None:
        """Handle data coming from the Shelly motion sensors.

        Simply log the event to indicate the presense of simulated device.
        Args:
            em (dict): data from the sensor
        """
        self.debug(f"Motion sensor sensor {em}")

    @override
    def run(self) -> None:
        self.worker = cast(
            ShellyMotionSimulatorThread,
            Juham.instantiate(ShellyMotionSimulatorThread.get_class_id()),
        )
        self.worker.shelly_topic = self.shelly_topic
        self.worker.interval = self.update_interval
        super().run()

    @override
    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        data["_shellymotionsimulator"] = {"shelly_topic": self.shelly_topic}
        return data

    @override
    def from_dict(self, data: Dict[str, Any]) -> None:
        super().from_dict(data)
        if "_shellymotionsimulator" in data:
            for key, value in data["_shellymotionsimulator"].items():
                setattr(self, key, value)
