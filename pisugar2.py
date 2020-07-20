# Gets status of Pisugar2 - requires installing the PiSugar-Power-Manager
# curl http://cdn.pisugar.com/release/Pisugar-power-manager.sh | sudo bash
#
# based on https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/ups_lite.py
# https://www.tindie.com/products/pisugar/pisugar2-battery-for-raspberry-pi-zero/
import logging

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import time


class PiSugar(plugins.Plugin):
    __author__ = "10230718+tisboyo@users.noreply.github.com"
    __version__ = "0.0.1"
    __license__ = "GPL3"
    __description__ = "A plugin that will add a voltage indicator for the PiSugar 2"

    def __init__(self):
        self.ps = None
        self.charge_indicator = False

    def on_loaded(self):
        # Load here so it doesn't attempt to load if the plugin is not enabled
        from pisugar2 import PiSugar2

        self.ps = PiSugar2()
        logging.info("[pisugar2] plugin loaded.")

    def on_ui_setup(self, ui):
        ui.add_element(
            "bat",
            LabeledValue(
                color=BLACK,
                label="BAT",
                value="0%/0V",
                position=(ui.width() / 2 + 15, 0),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element("bat")

    def on_ui_update(self, ui):
        capacity = int(self.ps.get_battery_percentage().value)
        if self.ps.get_charging_status().value and not self.charge_indicator:
            self.charge_indicator = True
            ui.set("bat", "CHG")

        else:
            self.charge_indicator = False
            ui.set("bat", str(capacity) + "%")

        if capacity <= self.options["shutdown"]:
            logging.info(
                f"[pisugar2] Empty battery (<= {self.options['shutdown']}): shuting down"
            )
            ui.update(force=True, new_data={"status": "Battery exhausted, bye ..."})
            time.sleep(3)
            pwnagotchi.shutdown()
