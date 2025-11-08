from typing_extensions import override
from masterpiece import Plugin, Composite
from .shellymotion_simulator import ShellyMotionSimulator
from .shellyplusaddon_simulator import ShellyPlusAddOnSimulator

# from .shelly1g3 import Shelly1G3
# from .shellypro3em import ShellyPro3EM
# from .shellymotion import ShellyMotion


class ShellyPlugin(Plugin):
    """Plugin class for installing and instantiating Shelly's into the host application."""

    enable_motion_simulator: bool = False  # motion sensor
    enable_plusaddon_simulator: bool = False  # temperature and humidity sensors

    def __init__(self, name: str = "openweather_map") -> None:
        """Create systemstatus object."""
        super().__init__(name)

    @override
    def install(self, app: Composite) -> None:
        if self.enable_motion_simulator:
            app.add(ShellyMotionSimulator())
        if self.enable_plusaddon_simulator:
            app.add(ShellyPlusAddOnSimulator())
