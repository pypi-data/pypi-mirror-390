# Stubbed sequencer.py for schedule maker package
from functools import wraps
from typing import Dict, Type, Optional
from . import sequencer_validator as Validator

def action_method(
        type: str,
        category: str,
        description: str,
        position: int,
        display_name: str,
        duration: str,
        validators: dict[str, Type[Validator.BaseClass]],
        timeline_name: Optional[str] = None
):
    def decorator(func):
        @wraps(func)
        def wrapper (*args, **kwargs):
            return func(*args, **kwargs)
        setattr(wrapper, '__is_action_method__', True)
        setattr(wrapper, 'category', category)
        setattr(wrapper, 'type', type)
        setattr(wrapper, 'description', description)
        setattr(wrapper, 'position', position)
        setattr(wrapper, 'display_name', display_name or func.__name__)
        setattr(wrapper, 'duration', duration)
        setattr(wrapper, 'validators', validators)
        setattr(wrapper, 'timeline_name', timeline_name or display_name or func.__name__)
        return wrapper
    return decorator

class Sequencer:

    @action_method(
        category="TIME",
        position=1,
        display_name="Wait Seconds",
        type="WAIT_SECONDS",
        description="Waits for a given number of seconds.",
        duration="wait_time",
        validators={
            "wait_time": Validator.IntPositive,
            "telescope": Validator.TelescopeWithNone
            }
    )
    def wait_for_seconds(self, wait_time, telescope):
        pass
    @action_method(
        category="TIME",
        position=2,
        display_name="Wait Timestamp",
        type="WAIT_TIMESTAMP",
        description="Waits till the given timestamp in UTC is reached.",
        duration="",
        validators={
            "wait_timestamp": Validator.Timestamp,
            "telescope": Validator.TelescopeWithNone
        }
    )
    def wait_for_timestamp(self, wait_timestamp, telescope):
        pass
    @action_method(
        category="INITIALIZE",
        position=1,
        display_name="Initialize PLC",
        type="INITIALIZE_PLC",
        description="Initializes the PLC system.",
        duration="300",
        validators={}
    )
    def initialize_PLC_system(self):
        pass
    @action_method(
        category="INITIALIZE",
        position=2,
        display_name="Initialize Unit",
        type="INITIALIZE_UNIT",
        description="Initializes a given telescope with its dome.",
        duration="300",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def initialize_unit(self, telescope):
        pass
    @action_method(
        category="INITIALIZE",
        position=3,
        display_name="Initialize Telescope",
        type="INITIALIZE_TELESCOPE",
        description="Initializes a given telescope.",
        duration="120",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def initialize_telescope(self, telescope):
        pass
    @action_method(
        category="INITIALIZE",
        position=4,
        display_name="Initialize Dome",
        type="INITIALIZE_DOME",
        description="Initializes the dome for a given telescope.",
        duration="120",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def initialize_dome(self, telescope):
        pass
    @action_method(
        category="INITIALIZE",
        position=5,
        display_name="System Wakeup",
        type="SYSTEM_WAKEUP",
        description="Wakes up the system.",
        duration="300",
        validators={}
    )
    def system_wakeup(self):
        pass
    @action_method(
        category="INITIALIZE",
        position=6,
        display_name="System Sleep",
        type="SYSTEM_SLEEP",
        description="Puts the system in sleepmode.",
        duration="300",
        validators={}
    )
    def system_sleep(self):
        pass
    @action_method(
        category="DOME",
        position=1,
        display_name="Open Dome",
        type="OPEN_DOME",
        description="Opens the dome of the telescope.",
        duration="90",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def open_dome(self, telescope):
        pass
    @action_method(
        category="DOME",
        position=2,
        display_name="Move Dome",
        type="MOVE_DOME",
        description="Moves the dome to the desired azimuth.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "azimuth": Validator.Azimuth
        }
    )
    def move_dome(self, telescope, azimuth):
        pass
    @action_method(
        category="DOME",
        position=3,
        display_name="Dome Track Start",
        type="DOME_TRACK_START",
        description="Starts the dome tracking for a given telescope.",
        duration="60",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def dome_start_tracking_telescope(self, telescope):
        pass
    @action_method(
        category="DOME",
        position=4,
        display_name="Dome Track Stop",
        type="DOME_TRACK_STOP",
        description="Stops the dome tracking for a given telescope.",
        duration="60",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def dome_stop_tracking_telescope(self, telescope):
        pass
    @action_method(
        category="DOME",
        position=5,
        display_name="Park Dome",
        type="PARK_DOME",
        description="Parks the dome for a given telescope.",
        duration="90",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def park_dome(self, telescope):
        pass
    @action_method(
        category="DOME",
        position=6,
        display_name="Close Dome",
        type="CLOSE_DOME",
        description="Closes the dome for a given telescope.",
        duration="90",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def close_dome(self, telescope):
        pass
    @action_method(
        category="DOME",
        position=7,
        display_name="Open All Domes",
        type="OPEN_DOMES",
        description="Opens all dome shutters.",
        duration="300",
        validators={}
    )
    def open_all_domes(self):
        pass
    @action_method(
        category="DOME",
        position=8,
        display_name="Close All Domes",
        type="CLOSE_DOMES",
        description="Closes all dome shutters.",
        duration="300",
        validators={}
    )
    def close_all_domes(self):
        pass
    @action_method(
        category="DOME",
        position=9,
        display_name="Stop All Domes",
        type="STOP_DOMES",
        description="Stops all domes from moving.",
        duration="60",
        validators={}
    )
    def stop_domes(self):
        pass
    @action_method(
        category="TELESCOPE",
        position=1,
        display_name="Open Telescope",
        type="OPEN_TELESCOPE",
        description="Opens the cover of a given telescope.",
        duration="60",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def open_telescope(self, telescope):
        pass
    @action_method(
        category="TELESCOPE",
        position=2,
        display_name="Close Telescope",
        type="CLOSE_TELESCOPE",
        description="Closes the cover of a given telescope.",
        duration="60",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def close_telescope(self, telescope):
        pass
    @action_method(
        category="TELESCOPE",
        position=3,
        display_name="Telescope Track Start",
        type="TELESCOPE_TRACK_START",
        description="Starts the telescope tracking for a given telescope.",
        duration="60",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def telescope_start_tracking(self, telescope):
        pass
    @action_method(
        category="TELESCOPE",
        position=4,
        display_name="Telescope Track Stop",
        type="TELESCOPE_TRACK_STOP",
        description="Stops the telescope tracking for a given telescope.",
        duration="60",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def telescope_stop_tracking(self, telescope):
        pass
    @action_method(
        category="TELESCOPE",
        position=5,
        display_name="Park Telescope",
        type="PARK_TELESCOPE",
        description="Parks a given telescope.",
        duration="90",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def park_telescope(self, telescope):
        pass
    @action_method(
        category="TELESCOPE",
        position=6,
        display_name="Move Nasmyth Port",
        type="MOVE_NASMYTH",
        description="Changes the Nasmyth port of a given telescope.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "nasmyth_port": Validator.NasmythPort
        }
    )
    def move_nasmyth(self, telescope, nasmyth_port):
        pass
    @action_method(
        category="FOCUSER",
        position=1,
        display_name="Move Focus",
        type="MOVE_FOCUS",
        description="Moves the secondary mirror of the telescope to the desired position.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "focallength": Validator.FocalLength
        }
    )
    def move_focus(self, telescope, focallength):
        pass
    @action_method(
        category="CAMERA",
        position=1,
        display_name="Get Camera Temperature",
        type="GET_CAMERA_TEMPERATURE",
        description="Gets the current temperature of the camera for a given telescope.",
        duration="60",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def get_camera_temperature (self, telescope):
        pass
    @action_method(
        category="CAMERA",
        position=2,
        display_name="Set Camera Temperature",
        type="SET_CAMERA_TEMPERATURE",
        description="Sets the target temperature of the camera for a given telescope.",
        duration="60",
        validators={
            "telescope": Validator.Telescope,
            "temperature": Validator.TemperatureDefault
        }
    )
    def set_camera_temperature (self, telescope, temperature):
        pass
    @action_method(
        category="START/END",
        position=1,
        display_name="Night Start",
        type="NIGHT_START",
        description="Activates the telescope and the dome at a certain time.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "wait_timestamp": Validator.Timestamp,
            "nasmyth_port": Validator.NasmythPort
        }
    )
    def night_start (self,telescope, wait_timestamp, nasmyth_port):
        pass
    @action_method(
        category="START/END",
        position=2,
        display_name="Night End",
        type="NIGHT_END",
        description="Disactivates the telescope and the dome, and eventually warms the camera.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "temperature": Validator.Int,
            "temperature_step": Validator.Int,
            "temperature_delay": Validator.Int
        }
    )
    def night_end (
        self,
        telescope,
        temperature,
        temperature_step,
        temperature_delay
        ):
        pass
    @action_method(
        category="UNIT",
        position=1,
        display_name="Park Unit",
        type="PARK_UNIT",
        description="Parks a given telescope unit (telescope and dome).",
        duration="90",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def park_unit(self, telescope):
        pass
    @action_method(
        category="UNIT",
        position=2,
        display_name="Close Unit",
        type="CLOSE_UNIT",
        description="Closes a given telescope unit (telescope and dome) by parking it.",
        duration="90",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def close_unit(self, telescope):
        pass
    @action_method(
        category="UNIT",
        position=3,
        display_name="Open Unit",
        type="OPEN_UNIT",
        description="Opens a given telescope unit (telescope and dome).",
        duration="90",
        validators={
            "telescope": Validator.Telescope
        }
    )
    def open_unit(self, telescope):
        pass
    @action_method(
        category="UNIT",
        position=4,
        display_name="Park All Units",
        type="PARK_ALL_UNITS",
        description="Parks all telescope units (telescopes and domes).",
        duration="300",
        validators={}
    )
    def park_all_units(self):
        pass
    @action_method(
        category="TELESCOPE",
        position=1,
        display_name="Move Telescope",
        type="MOVE_TELESCOPE",
        description="Moves a given telescope to the desired RA and DEC coordinates, including proper motion effects.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "RA": Validator.Ra,
            "DEC": Validator.Dec,
            "pm_RA": Validator.Float,
            "pm_DEC": Validator.Float,
            "ref_epoch": Validator.Float,
            "filter_slot": Validator.FilterWheel,
        }
    )
    def move_telescope (
        self,
        telescope,
        RA,
        DEC,
        pm_RA,
        pm_DEC,
        ref_epoch,
        filter_slot
        ):
        pass
    @action_method(
        category="CAMERA",
        position=1,
        display_name="Set Camera Ambient",
        type="SET_CAMERA_AMBIENT",
        description="Sets the camera temperature back to ambient temperature in steps.",
        duration="60",
        validators={
            "telescope": Validator.Telescope,
            "temperature_step": Validator.Int,
            "temperature_delay": Validator.Int,
            "temperature": Validator.Int
        }
    )
    def set_camera_ambient(
        self,
        telescope,
        temperature_step,
        temperature_delay,
        temperature
        ):
        pass
    @action_method(
        category="FLATS",
        position=1,
        display_name="Take Flats",
        type="TAKE_FLATS",
        description="Takes a series of flat images to create a flat master.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "exp_time": Validator.IntPositive,
            "exp_number": Validator.IntPositive,
            "ALT": Validator.Altitude,
            "AZI": Validator.Azimuth,
            "binning": Validator.Binning,
            "gain": Validator.Int,
            "offset": Validator.Int,
            "filter_slot": Validator.FilterWheel,
            "flat_median": Validator.FlatMedian,
            "flat_range": Validator.FlatRange,
            "focallength": Validator.FocalLength
        }
    )
    def take_flats(
        self,
        telescope,
        exp_time,
        exp_number,
        ALT,
        AZI,
        binning,
        gain,
        offset,
        filter_slot,
        flat_median,
        flat_range,
        focallength
    ):
        pass
    @action_method(
        category="AUTOFOCUSER",
        position=1,
        display_name="Focus",
        type="FOCUS",
        description="Finds the best focus position by taking a series of images with different focus positions and analyzing the resulting images.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "object_name": Validator.ObjectName,
            "RA": Validator.Ra,
            "DEC": Validator.Dec,
            "pm_RA": Validator.Float,
            "pm_DEC": Validator.Float,
            "ref_epoch": Validator.Float,
            "filter_slot": Validator.FilterWheel,
            "testing": Validator.Bool
        }
    )
    def autofocuser(
        self,
        telescope,
        object_name,
        RA,
        DEC,
        pm_RA,
        pm_DEC,
        ref_epoch,
        filter_slot,
        testing
    ):
        pass
    @action_method(
        category="MODEL_VERIFICATION",
        position=2,
        display_name="Model Verification",
        type="MODEL_VERIFICATION",
        description="Verifies the pointing model of the telescope by taking images at a series of points on the sky and analyzing the pointing accuracy.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "points": Validator.Int,
            "circles": Validator.Int,
            "exposure_time": Validator.IntPositive,
            "gain": Validator.Int,
            "offset": Validator.Int,
            "binning": Validator.Binning,
            "filter_slot": Validator.FilterWheel
        }
    )
    def model_verification(
        self,
        telescope,
        points,
        circles,
        exposure_time,
        gain,
        offset,
        binning,
        filter_slot
    ):
        pass
    @action_method(
        category="OBSERVING",
        position=1,
        display_name="Observe",
        timeline_name="Observe <object_name> for <exp_number>x <exp_time>s",
        type="OBSERVE",
        description="Takes a series of images of a given object, including moving the telescope and filterwheel, and running the platesolver to ensure accurate pointing.",
        duration="exp_time * exp_number * 2",
        validators={
            "telescope": Validator.Telescope,
            "object_name": Validator.ObjectName,
            "exp_time": Validator.IntPositive,
            "exp_number": Validator.IntPositive,
            "until_timestamp": Validator.Timestamp,
            "RA": Validator.Ra,
            "DEC": Validator.Dec,
            "mechanical_angle": Validator.MechanicalAngle,
            "pm_RA": Validator.Float,
            "pm_DEC": Validator.Float,
            "ref_epoch": Validator.Float,
            "filter_slot": Validator.FilterWheel,
            "gain": Validator.Int,
            "offset": Validator.Int,
            "binning": Validator.Binning
        }
    )
    def observe (
        self,
        telescope,
        object_name,
        exp_time,
        exp_number,
        until_timestamp,
        RA,
        DEC,
        mechanical_angle ,
        pm_RA,
        pm_DEC,
        ref_epoch,
        filter_slot,
        gain,
        offset,
        binning
    ):
        pass
    @action_method(
        category="OBSERVING",
        position=2,
        display_name="Take Darks",
        type="TAKE_DARKS",
        description="Takes a series of dark images with the camera.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "exp_time": Validator.IntPositive,
            "exp_number": Validator.IntPositive,
            "gain": Validator.Int,
            "offset": Validator.Int,
            "binning": Validator.Binning
        }
    )
    def take_darks (
        self,
        telescope,
        exp_time,
        exp_number,
        gain,
        offset,
        binning
    ):
        pass
    @action_method(
        category="OBSERVING",
        position=3,
        display_name="Take Exposures",
        type="TAKE_EXPOSURES",
        description="Takes a series of images of a given object, including moving the telescope and filterwheel, but without running the platesolver.",
        duration="90",
        validators={
            "telescope": Validator.Telescope,
            "object_name": Validator.ObjectName,
            "exp_time": Validator.IntPositive,
            "exp_number": Validator.IntPositive,
            "until_timestamp": Validator.Timestamp,
            "RA": Validator.Ra,
            "DEC": Validator.Dec,
            "mechanical_angle": Validator.MechanicalAngle,
            "pm_RA": Validator.Float,
            "pm_DEC": Validator.Float,
            "ref_epoch": Validator.Float,
            "filter_slot": Validator.FilterWheel,
            "gain": Validator.Int,
            "offset": Validator.Int,
            "binning": Validator.Binning
        }
    )
    def take_exposures(
        self,
        telescope,
        object_name,
        exp_time,
        exp_number,
        until_timestamp,
        RA,
        DEC,
        mechanical_angle ,
        pm_RA,
        pm_DEC,
        ref_epoch,
        filter_slot,
        gain,
        offset,
        binning
    ):
        pass