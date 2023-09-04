from sardana.macroserver.macro import imacro, macro, Type, Optional, Macro
from tango import DeviceProxy
import numpy as np
from time import sleep

@macro()
def laser_on(self):
    """Macro laser_on"""
    ds = self.getEnv("TangoDevices")
    is_enabled = DeviceProxy(ds['thindisk_thorlabsSC10_seed']).enabled
    if is_enabled:
        self.warning("The seed shutter is still enabled! Can not flip mirror!")
        return
    proxy = DeviceProxy(ds['thindisk_thorlabsMFF100_compressor'])
    proxy.Open()
    self.output("Laser mirror opened!")


@macro()
def laser_off(self):
    """Macro laser_off"""
    ds = self.getEnv("TangoDevices")
    is_enabled = DeviceProxy(ds['thindisk_thorlabsSC10_seed']).enabled
    if is_enabled:
        self.warning("The seed shutter is still enabled! Can not flip mirror!")
        return
    proxy = DeviceProxy(ds['thindisk_thorlabsMFF100_compressor'])
    proxy.Close()
    self.output("Laser mirror closed!")


@macro()
def laser_state(self):
    """Macro laser_state"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thindisk_thorlabsMFF100_compressor'])
    self.output(proxy.mffstate)


@macro()
def probe_on(self):
    """Macro laser_on"""
    ds = self.getEnv("TangoDevices")
    is_enabled = DeviceProxy(ds['thindisk_thorlabsSC10_seed']).enabled
    if is_enabled:
        self.warning("The seed shutter is still enabled! Can not flip mirror!")
        return
    proxy = DeviceProxy(ds['thorlabsMFF100_probe'])
    proxy.Open() # not inverted for rsxs!!
    self.output("Probe mirror open!")


@macro()
def probe_off(self):
    """Macro laser_off"""
    ds = self.getEnv("TangoDevices")
    is_enabled = DeviceProxy(ds['thindisk_thorlabsSC10_seed']).enabled
    if is_enabled:
        self.warning("The seed shutter is still enabled! Can not flip mirror!")
        return
    proxy = DeviceProxy(ds['thorlabsMFF100_probe'])
    proxy.Close() # not inverted for rsxs!!
    self.output("Probe mirror closed!")


@macro()
def probe_state(self):
    """Macro probe_state"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thorlabsMFF100_probe'])
    return proxy.mffstate

@macro()
def pump_on(self):
    """Macro pump_on"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thorlabsMFF100_pump'])
    proxy.Open()  # inverted in tango in that way it is right
    self.output("Pump mirror open!")


@macro()
def pump_off(self):
    """Macro pump_off"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thorlabsMFF100_pump'])
    proxy.Close()  # same as above
    self.output("Pump mirror closed!")


@macro()
def pump_state(self):
    """Macro pump_state"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thorlabsMFF100_pump'])
    self.output("Pump flip mount state: %s" % proxy.state())

@macro()
def shutter_enable(self):
    """Macro shutter_enable"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thindisk_thorlabsSC10_seed'])
    proxy.enable()
    self.output("Laser shutter ENABLED!")


@macro()
def shutter_disable(self):
    """Macro shutter_disable"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thindisk_thorlabsSC10_seed'])
    proxy.disable()
    self.output("Laser shutter DISABLED!")


@macro()
def shutter_manual(self):
    """Macro shutter_manual"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thindisk_thorlabsSC10_seed'])
    proxy.mode = 0
    self.output("Laser shutter in MANUAL mode!")


@macro()
def shutter_external(self):
    """Macro shutter_external"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thindisk_thorlabsSC10_seed'])
    proxy.mode = 4
    self.output("Laser shutter in EXTERNAL mode!")


@macro([["output", Type.Boolean, True, "output result"]])
def shutter_is_open(self, output):
    """Macro shutter_is_open"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thindisk_thorlabsSC10_seed'])
    is_open = proxy.open
    if output:
        self.output(is_open)
    return is_open


@macro([["output", Type.Boolean, True, "output result"]])
def shutter_is_enabled(self, output):
    """Macro shutter_is_enabled"""
    ds = self.getEnv("TangoDevices")
    proxy = DeviceProxy(ds['thindisk_thorlabsSC10_seed'])
    is_enabled = proxy.enabled
    if output:
        self.output(is_enabled)
    return is_enabled


@imacro()
def laser_aligment_mode(self):
    """
    Macro to align the laser.
    If aborted by answering 'n', the laser will enter sleep mode for safety.
    If answered by 'y', the option is given to open the probe beam shutter.

    To abort                     answer:  n
    To align only the probe beam answer:  y => y
    To align only the probe beam answer:  y => n

    """

    answer = ""
    while answer not in ["y", "n"]:
        answer = self.input(
            "Are you sure you want the full beam on the laser table? (n)?"
        )
    if answer == "n":
        self.output("Macro accidentally called. Entering sleep mode.")
        self.execMacro("laser_sleep_mode")
    else:
        self.execMacro("pump_off")
        answer = ""
        while answer not in ["y", "n"]:
            self.output("The pump shutter was closed.")
            answer = self.input("Do you want the full probe beam on the target (n)?")
        self.execMacro("shutter_disable")
        if answer == "n":
            self.execMacro("probe_off")
            self.output("Full probe beam on probe beam dump in 3s:")
        else:
            self.execMacro("probe_on")
            self.output("Full probe beam on target in 3s:")
        self.execMacro("laser_on")

        for i in range(3):
            self.output((i + 1) * ".")
            sleep(1)
        self.execMacro("shutter_manual")
        self.execMacro("shutter_enable")
        self.output("You may now open the pump shutter again.")


@macro()
def laser_sleep_mode(self):
    """
    Macro to dump the full beam into the beam dump
    inside the compressor, while keeping the laser seeeded.
    Example use cases include:
        - Before switching the laser on in the morning
        - Lunch time
        - Exchanging or examining components
        - End of the day / measurement time
    """
    self.execMacro("shutter_disable")
    self.execMacro("shutter_manual")
    self.execMacro("probe_off")
    self.execMacro("laser_off")
    sleep(0.4)
    self.execMacro("shutter_enable")
    self.output(
        "Probe is closed. Laser is seeded, but dumped inside the compressor housing."
    )


@macro()
def laser_ready_mode(self):
    """
    Macro to set the laser shutter and the flip mirrors
    into a mode where a scan can be started.
    The full probe beam is sent to the probe beam dump.
    The pump is not altered.
    Make sure the pump is set correctly
    before executing this macro!
    """
    self.execMacro("shutter_disable")
    self.execMacro("probe_off")
    # self.execMacro('pump_off')
    self.execMacro("laser_on")
    sleep(0.4)
    self.execMacro("shutter_manual")
    self.execMacro("shutter_enable")


@macro()
def laser_scan_mode(self):
    """
    Macro laser_scan_mode.
    Usually only executed by a pre scan hook.

    The probe flip mount will be opened.
    The seed is closed and waiting for an external trigger.

    The pump shutter is not altered!
    Make sure the pump is set correctly
    before executing this macro!
    """
    self.execMacro("shutter_disable")
    self.execMacro("shutter_external")
    self.execMacro("probe_on")
    # self.execMacro('pump_on')
    sleep(1)
    self.execMacro("shutter_enable")


@macro()
def laser_dark_mode(self):
    """
    To acquire a dark image, one wants to trigger the laser,
    but not let the probe laser onto the target.
    Macro laser_dark_mode.
    Usually only executed by a pre scan hook.

    The probe flip mount will NOT be opened.
    The seed is closed and waiting for an external trigger.

    The pump shutter is not altered!
    Make sure the pump is set correctly
    before executing this macro!
    """
    self.execMacro("shutter_disable")
    self.execMacro("shutter_external")
    sleep(1)
    self.execMacro("shutter_enable")
