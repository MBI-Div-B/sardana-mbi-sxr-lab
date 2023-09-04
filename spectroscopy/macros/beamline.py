from sardana.macroserver.macro import Macro, macro, imacro, Type
import tango
from time import sleep


@macro()
def fix(self):
    self.execMacro("laser_ready_mode")
    self.execMacro("tape_off")
    self.execMacro("target_off")


@macro()
def switch_to_mte(self):
    self.output("switching to mte ccd detector...")
    # self.output("driving ccd in")
    # self.execMacro("ccd_in")
    self.output("switching measurement group to pilc_mte")
    self.execMacro("set_meas", "spectroscopy")
    self.output("switching PiLCTimerCtrl.TriggerMode to 2")
    pilc = self.getController("PiLCTimerCtrl_spec")
    pilc.write_attribute("triggermode", 2)
    self.output(f"triggermode = %d" % pilc.read_attribute("triggermode").value)
    self.output("exporting acqconf to check mte CamTemp")
    # args are boolean: checkTape, checkTarget, checkCamTemp, startTape, stopTape, startTarget, stopTarget, autoModeLaser, darkModeLaser, autoShutterPump
    self.execMacro("acqconf", 1, 1, 1, 1, 1, 1, 1, 1, 0, 0)
    self.output("don't forget to switch\nLaVue Tango Events -> Attributes to rsxs mte")
