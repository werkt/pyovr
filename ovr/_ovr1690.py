"""
Python module "ovr"
Python bindings for Oculus Rift SDK version 1.69.0

Works on Windows only at the moment (just like Oculus Rift SDK...)
"""

import ctypes
from ctypes import * #@UnusedWildImport
import math
import platform
import os


OVR_PTR_SIZE = sizeof(c_voidp) # distinguish 32 vs 64 bit python

# Load Oculus runtime library (only tested on Windows)
# 1) Figure out name of library to load

if hasattr(os, 'add_dll_directory'):
    OVR_PATH = os.path.join(os.getenv("OculusBase"), "Support", "oculus-runtime")
    os.add_dll_directory(OVR_PATH)

_libname = "OVRRT32_1" # 32-bit python
if OVR_PTR_SIZE == 8:
    _libname = "OVRRT64_1" # 64-bit python
if platform.system().startswith("Win"):
    _libname = "Lib"+_libname # i.e. "LibOVRRT32_1"
# Load library
try:
    libovr = CDLL(_libname)
except:
    print("Is Oculus Runtime 1.69 installed on this machine?")
    raise


ENUM_TYPE = c_int32 # Hopefully a close enough guess...

OVR_ON64_FIELD = lambda field : [field] if OVR_PTR_SIZE == 8 else []
# OVR_ON32 is unused

class HmdStruct(Structure):
    "Used as an opaque pointer to an OVR session."
    pass

class TextureSwapChainData(Structure):
    pass

class MirrorTextureData(Structure):
    pass


# Signature of the logging callback function pointer type.
#
# \param[in] userData is an arbitrary value specified by the user of ovrInitParams.
# \param[in] level is one of the ovrLogLevel constants.
# \param[in] message is a UTF8-encoded null-terminated string.
# \see ovrInitParams ovrLogLevel, ovr_Initialize
#
# typedef void (OVR_CDECL* ovrLogCallback)(POINTER(c_uint) userData, int level, const char* message);
LogCallback = CFUNCTYPE(None, POINTER(c_uint), c_int, c_char_p)


def POINTER(obj):
    p = ctypes.POINTER(obj)

    # Convert None to a real NULL pointer to work around bugs
    # in how ctypes handles None on 64-bit platforms
    if not isinstance(p.from_param, classmethod):
        def from_param(cls, x):
            if x is None:
                return cls()
            else:
                return x
        p.from_param = classmethod(from_param)

    return p


def byref(obj):
    "Referencing None should result in None, at least for initialize method"
    b = None if obj is None else ctypes.byref(obj)
    return b

ovrFalse = c_char(chr(0).encode('utf-8')) # note potential conflict with Python built in symbols
ovrTrue = c_char(chr(1).encode('utf-8'))

def toOvrBool(arg):
    # One tricky case:
    if arg == chr(0).encode('utf-8'):
        return ovrFalse
    # Remainder are easy cases:
    if bool(arg):
        return ovrTrue
    else:
        return ovrFalse

def fromOvrBool(arg):
    return arg != ovrFalse.value

class OculusFunctionError(RuntimeError):
    """
    OculusFunctionError is a custom exception type for when OVR functions return a failure code.
    Such a specific exception type allows more precise exception handling that does just raising Exception().
    """
    pass

def _checkResult(ovrResult, functionName):
    "Raises an exception if a function returns an error code"
    if not FAILURE(ovrResult):
        return # Function succeeded, so carry on
    msg = "Call to function ovr.%s() failed. Error code %d." % (
        functionName, ovrResult)
    try:
        errorInfo = getLastErrorInfo()
        msg += " %s (%d)" % (errorInfo.ErrorString.decode("utf-8"), errorInfo.Result)
    except:
        msg += " And, annoyingly, getLastErrorInfo() failed too."
    raise OculusFunctionError(msg)

### BEGIN Declarations from C header file OVR_Version.h ###


# Translated from header file OVR_Version.h line 17
PRODUCT_VERSION = 1 # Product version doesn't participate in semantic versioning.


# Translated from header file OVR_Version.h line 18
MAJOR_VERSION = 1 # If you change these values then you need to also make sure to change


# Translated from header file OVR_Version.h line 20
MINOR_VERSION = 69 #


# Translated from header file OVR_Version.h line 21
PATCH_VERSION = 0 


# Translated from header file OVR_Version.h line 22
BUILD_NUMBER = 0 # This is the ((product * 100) + major) version of the service that the DLL is compatible with.


# Translated from header file OVR_Version.h line 29
DLL_COMPATIBLE_VERSION = 101 


# Translated from header file OVR_Version.h line 31
FEATURE_VERSION = 0 # "Major.Minor.Patch"


# Translated from header file OVR_Version.h line 35
VERSION_STRING = b"%d.%d.%d" % (MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION)


# Translated from header file OVR_Version.h line 40
DETAILED_VERSION_STRING = b"%d.%d.%d.%d" % (MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, BUILD_NUMBER)


# Translated from header file OVR_Version.h line 51
FILE_DESCRIPTION_STRING = b"dev build"


### END Declarations from C header file OVR_Version.h ###


### BEGIN Declarations from C header file OVR_CAPI_Keys.h ###


# Translated from header file OVR_CAPI_Keys.h line 13
KEY_USER = b"User" # string


# Translated from header file OVR_CAPI_Keys.h line 15
KEY_NAME = b"Name" # string


# Translated from header file OVR_CAPI_Keys.h line 17
KEY_GENDER = b"Gender" # string "Male", "Female", or "Unknown"


# Translated from header file OVR_CAPI_Keys.h line 18
DEFAULT_GENDER = b"Unknown" 


# Translated from header file OVR_CAPI_Keys.h line 20
KEY_PLAYER_HEIGHT = b"PlayerHeight" # float meters


# Translated from header file OVR_CAPI_Keys.h line 21
DEFAULT_PLAYER_HEIGHT = 1.778 


# Translated from header file OVR_CAPI_Keys.h line 23
KEY_EYE_HEIGHT = b"EyeHeight" # float meters


# Translated from header file OVR_CAPI_Keys.h line 24
DEFAULT_EYE_HEIGHT = 1.675 


# Translated from header file OVR_CAPI_Keys.h line 26
KEY_NECK_TO_EYE_DISTANCE = b"NeckEyeDistance" # float[2] meters


# Translated from header file OVR_CAPI_Keys.h line 27
DEFAULT_NECK_TO_EYE_HORIZONTAL = 0.0805 


# Translated from header file OVR_CAPI_Keys.h line 28
DEFAULT_NECK_TO_EYE_VERTICAL = 0.075 


# Translated from header file OVR_CAPI_Keys.h line 30
KEY_EYE_TO_NOSE_DISTANCE = b"EyeToNoseDist" # float[2] meters


# Translated from header file OVR_CAPI_Keys.h line 34
PERF_HUD_MODE = b"PerfHudMode" # int, allowed values are defined in enum ovrPerfHudMode


# Translated from header file OVR_CAPI_Keys.h line 36
LAYER_HUD_MODE = b"LayerHudMode" # int, allowed values are defined in enum ovrLayerHudMode


# Translated from header file OVR_CAPI_Keys.h line 37
LAYER_HUD_CURRENT_LAYER = b"LayerHudCurrentLayer" # int, The layer to show


# Translated from header file OVR_CAPI_Keys.h line 38
LAYER_HUD_SHOW_ALL_LAYERS = b"LayerHudShowAll" # bool, Hide other layers when hud enabled


# Translated from header file OVR_CAPI_Keys.h line 40
DEBUG_HUD_STEREO_MODE = b"DebugHudStereoMode" # int, see enum ovrDebugHudStereoMode


# Translated from header file OVR_CAPI_Keys.h line 41
DEBUG_HUD_STEREO_GUIDE_INFO_ENABLE = b"DebugHudStereoGuideInfoEnable" # bool


# Translated from header file OVR_CAPI_Keys.h line 42
DEBUG_HUD_STEREO_GUIDE_SIZE = b"DebugHudStereoGuideSize2f" # float[2]


# Translated from header file OVR_CAPI_Keys.h line 43
DEBUG_HUD_STEREO_GUIDE_POSITION = b"DebugHudStereoGuidePosition3f" # float[3]


# Translated from header file OVR_CAPI_Keys.h line 44
DEBUG_HUD_STEREO_GUIDE_YAWPITCHROLL = b"DebugHudStereoGuideYawPitchRoll3f" # float[3]


# Translated from header file OVR_CAPI_Keys.h line 45
DEBUG_HUD_STEREO_GUIDE_COLOR = b"DebugHudStereoGuideColor4f" # float[4]


### END Declarations from C header file OVR_CAPI_Keys.h ###


### BEGIN Declarations from C header file OVR_ErrorCode.h ###


# Translated from header file OVR_ErrorCode.h line 16
# API call results are represented at the highest level by a single ovrResult.
Result = c_int32 


# Translated from header file OVR_ErrorCode.h line 26
def SUCCESS(result):
    return result >= 0


# Translated from header file OVR_ErrorCode.h line 36
def UNQUALIFIED_SUCCESS(result):
    return result == Success


# Translated from header file OVR_ErrorCode.h line 42
def FAILURE(result):
    return not SUCCESS(result)


# Translated from header file OVR_ErrorCode.h line 48
SuccessType = ENUM_TYPE
# This is a general success result. Use OVR_SUCCESS to test for success.
Success = 0


# Translated from header file OVR_ErrorCode.h line 54
# Public success types
# Success is a value greater or equal to 0, while all error types are negative values.
SuccessTypes = ENUM_TYPE
# Returned from a call to SubmitFrame. The call succeeded, but what the app
# rendered will not be visible on the HMD. Ideally the app should continue
# calling SubmitFrame, but not do any rendering. When the result becomes
# ovrSuccess, rendering should continue as usual.
Success_NotVisible = 1000
# Boundary is invalid due to sensor change or was not setup.
Success_BoundaryInvalid = 1001
# Device is not available for the requested operation.
Success_DeviceUnavailable = 1002


# Translated from header file OVR_ErrorCode.h line 71
# Public error types
ErrorType = ENUM_TYPE
#****************#
# General errors #
#****************#
# Failure to allocate memory.
Error_MemoryAllocationFailure = -1000
# Invalid ovrSession parameter provided.
Error_InvalidSession = -1002
# The operation timed out.
Error_Timeout = -1003
# The system or component has not been initialized.
Error_NotInitialized = -1004
# Invalid parameter provided. See error info or log for details.
Error_InvalidParameter = -1005
# Generic service error. See error info or log for details.
Error_ServiceError = -1006
# The given HMD doesn't exist.
Error_NoHmd = -1007
# Function call is not supported on this hardware/software
Error_Unsupported = -1009
# Specified device type isn't available.
Error_DeviceUnavailable = -1010
# The headset was in an invalid orientation for the requested
# operation (e.g. vertically oriented during ovr_RecenterPose).
Error_InvalidHeadsetOrientation = -1011
# The client failed to call ovr_Destroy on an active session before calling ovr_Shutdown.
# Or the client crashed.
Error_ClientSkippedDestroy = -1012
# The client failed to call ovr_Shutdown or the client crashed.
Error_ClientSkippedShutdown = -1013
#< The service watchdog discovered a deadlock.
Error_ServiceDeadlockDetected = -1014
#< Function call is invalid for object's current state
Error_InvalidOperation = -1015
#< Increase size of output array
Error_InsufficientArraySize = -1016
# There is not any external camera information stored by ovrServer.
Error_NoExternalCameraInfo = -1017
# Tracking is lost when ovr_GetDevicePoses() is called.
Error_LostTracking = -1018
#***********************************************#
# Audio error range, reserved for Audio errors. #
#***********************************************#
# Failure to find the specified audio device.
Error_AudioDeviceNotFound = -2001
# Generic COM error.
Error_AudioComError = -2002
#************************#
# Initialization errors. #
#************************#
# Generic initialization error.
Error_Initialize = -3000
# Couldn't load LibOVRRT.
Error_LibLoad = -3001
# LibOVRRT version incompatibility.
Error_LibVersion = -3002
# Couldn't connect to the OVR Service.
Error_ServiceConnection = -3003
# OVR Service version incompatibility.
Error_ServiceVersion = -3004
# The operating system version is incompatible.
Error_IncompatibleOS = -3005
# Unable to initialize the HMD display.
Error_DisplayInit = -3006
# Unable to start the server. Is it already running?
Error_ServerStart = -3007
# Attempting to re-initialize with a different version.
Error_Reinitialization = -3008
# Chosen rendering adapters between client and service do not match
Error_MismatchedAdapters = -3009
# Calling application has leaked resources
Error_LeakingResources = -3010
# Client version too old to connect to service
Error_ClientVersion = -3011
# The operating system is out of date.
Error_OutOfDateOS = -3012
# The graphics driver is out of date.
Error_OutOfDateGfxDriver = -3013
# The graphics hardware is not supported
Error_IncompatibleGPU = -3014
# No valid VR display system found.
Error_NoValidVRDisplaySystem = -3015
# Feature or API is obsolete and no longer supported.
Error_Obsolete = -3016
# No supported VR display system found, but disabled or driverless adapter found.
Error_DisabledOrDefaultAdapter = -3017
# The system is using hybrid graphics (Optimus, etc...), which is not support.
Error_HybridGraphicsNotSupported = -3018
# Initialization of the DisplayManager failed.
Error_DisplayManagerInit = -3019
# Failed to get the interface for an attached tracker
Error_TrackerDriverInit = -3020
# LibOVRRT signature check failure.
Error_LibSignCheck = -3021
# LibOVRRT path failure.
Error_LibPath = -3022
# LibOVRRT symbol resolution failure.
Error_LibSymbols = -3023
# Failed to connect to the service because remote connections to the service are not allowed.
Error_RemoteSession = -3024
# Vulkan initialization error.
Error_InitializeVulkan = -3025
#******************#
# Rendering errors #
#******************#
# In the event of a system-wide graphics reset or cable unplug this is returned to the app.
Error_DisplayLost = -6000
# ovr_CommitTextureSwapChain was called too many times on a texture swapchain without
# calling submit to use the chain.
Error_TextureSwapChainFull = -6001
# The ovrTextureSwapChain is in an incomplete or inconsistent state.
# Ensure ovr_CommitTextureSwapChain was called at least once first.
Error_TextureSwapChainInvalid = -6002
# Graphics device has been reset (TDR, etc...)
Error_GraphicsDeviceReset = -6003
# HMD removed from the display adapter
Error_DisplayRemoved = -6004
# Content protection is not available for the display.
Error_ContentProtectionNotAvailable = -6005
# Application declared itself as an invisible type and is not allowed to submit frames.
Error_ApplicationInvisible = -6006
# The given request is disallowed under the current conditions.
Error_Disallowed = -6007
# Display portion of HMD is plugged into an incompatible port (ex: IGP)
Error_DisplayPluggedIncorrectly = -6008
#**************#
# Fatal errors #
#**************#
#< A runtime exception occurred. The application is required to shutdown LibOVR and
# re-initialize it before this error state will be cleared.
Error_RuntimeException = -7000
#********************#
# Calibration errors #
#********************#
# Result of a missing calibration block
Error_NoCalibration = -9000
# Result of an old calibration block
Error_OldVersion = -9001
# Result of a bad calibration block due to lengths
Error_MisformattedBlock = -9002
#**************#
# Other errors #
#**************#


# Translated from header file OVR_ErrorCode.h line 280
class ErrorInfo(Structure):
    """
    Provides information about the last error.
    \see ovr_GetLastErrorInfo
    """
    _fields_ = [
        # The result from the last API call that generated an error ovrResult.
        ("Result", Result), 
        # A UTF8-encoded null-terminated English string describing the problem.
        # The format of this string is subject to change in future versions.
        ("ErrorString", c_char * 512), 
    ]

    def __repr__(self):
        return "ovr.ErrorInfo(%s, %s)" % (self.Result, self.ErrorString)


### END Declarations from C header file OVR_ErrorCode.h ###


### BEGIN Declarations from C header file OVR_CAPI.h ###


# Translated from header file OVR_CAPI.h line 263
Bool = c_char  #< Boolean type


# Translated from header file OVR_CAPI.h line 270
class Colorf(Structure):
    "A RGBA color with normalized float components."
    _pack_ = 4
    _fields_ = [
        ("r", c_float),  
        ("g", c_float),  
        ("b", c_float),  
        ("a", c_float),  
    ]

    def __repr__(self):
        return "ovr.Colorf(%s, %s, %s, %s)" % (self.r, self.g, self.b, self.a)


# Translated from header file OVR_CAPI.h line 273
class Vector2i(Structure):
    "A 2D vector with integer components."
    _pack_ = 4
    _fields_ = [
        ("x", c_int),  
        ("y", c_int),  
    ]

    def __repr__(self):
        return "ovr.Vector2i(%s, %s)" % (self.x, self.y)

    def __len__(self):
        "number of items in this container"
        return len(self._fields_)

    def __getitem__(self, key):
        "access contained elements"
        if isinstance(key, slice):
            return [self[ii] for ii in range(*key.indices(len(self)))]
        else:
            return getattr(self, self._fields_[key][0])


# Translated from header file OVR_CAPI.h line 276
class Sizei(Structure):
    "A 2D size with integer components."
    _pack_ = 4
    _fields_ = [
        ("w", c_int),  
        ("h", c_int),  
    ]

    def __repr__(self):
        return "ovr.Sizei(%s, %s)" % (self.w, self.h)

    def __len__(self):
        "number of items in this container"
        return len(self._fields_)

    def __getitem__(self, key):
        "access contained elements"
        if isinstance(key, slice):
            return [self[ii] for ii in range(*key.indices(len(self)))]
        else:
            return getattr(self, self._fields_[key][0])


# Translated from header file OVR_CAPI.h line 279
class Recti(Structure):
    """
    A 2D rectangle with a position and size.
    All components are integers.
    """
    _pack_ = 4
    _fields_ = [
        ("Pos", Vector2i), 
        ("Size", Sizei), 
    ]

    def __repr__(self):
        return "ovr.Recti(%s, %s)" % (self.Pos, self.Size)


# Translated from header file OVR_CAPI.h line 286
class Quatf(Structure):
    "A quaternion rotation."
    _pack_ = 4
    _fields_ = [
        ("x", c_float),  
        ("y", c_float),  
        ("z", c_float),  
        ("w", c_float),  
    ]

    def __repr__(self):
        return "ovr.Quatf(%s, %s, %s, %s)" % (self.x, self.y, self.z, self.w)

    def __len__(self):
        "number of items in this container"
        return len(self._fields_)

    def __getitem__(self, key):
        "access contained elements"
        if isinstance(key, slice):
            return [self[ii] for ii in range(*key.indices(len(self)))]
        else:
            return getattr(self, self._fields_[key][0])

    def getEulerAngles(self, axis1=0, axis2=1, axis3=2, rotate_direction=1, handedness=1):
        assert(axis1 != axis2)
        assert(axis1 != axis3)
        assert(axis2 != axis3)
        Q = [ self.x, self.y, self.z ]  # Quaternion components x,y,z
        ww  = self.w*self.w;
        Q11 = Q[axis1]*Q[axis1]
        Q22 = Q[axis2]*Q[axis2]
        Q33 = Q[axis3]*Q[axis3]
        psign = -1.0
        # Determine whether even permutation
        if ((axis1 + 1) % 3 == axis2) and ((axis2 + 1) % 3 == axis3):
            psign = 1.0
        s2 = psign * 2.0 * (psign*self.w*Q[axis2] + Q[axis1]*Q[axis3])
        SingularityRadius = 1e-10
        D = rotate_direction # CCW rotation
        S = handedness # Right handed coordinate system
        if s2 < -1.0 + SingularityRadius:
            # South pole singularity
            a = 0.0
            b = -S*D*math.pi/2
            c = S*D*math.atan2(2.0*(psign*Q[axis1]*Q[axis2] + self.w*Q[axis3]),
                           ww + Q22 - Q11 - Q33 )
        elif s2 > 1.0 - SingularityRadius:
            # North pole singularity
            a = 0.0
            b = S*D*math.pi/2
            c = S*D*math.atan2(2.0*(psign*Q[axis1]*Q[axis2] + self.w*Q[axis3]),
                           ww + Q22 - Q11 - Q33)
        else:
            a = -S*D*math.atan2(-2.0*(self.w*Q[axis1] - psign*Q[axis2]*Q[axis3]),
                            ww + Q33 - Q11 - Q22)
            b = S*D*math.asin(s2)
            c = S*D*math.atan2(2.0*(self.w*Q[axis3] - psign*Q[axis1]*Q[axis2]),
                           ww + Q11 - Q22 - Q33)     
        return a, b, c


# Translated from header file OVR_CAPI.h line 289
class Vector2f(Structure):
    "A 2D vector with float components."
    _pack_ = 4
    _fields_ = [
        ("x", c_float),  
        ("y", c_float),  
    ]

    def __repr__(self):
        return "ovr.Vector2f(%s, %s)" % (self.x, self.y)

    def __len__(self):
        "number of items in this container"
        return len(self._fields_)

    def __getitem__(self, key):
        "access contained elements"
        if isinstance(key, slice):
            return [self[ii] for ii in range(*key.indices(len(self)))]
        else:
            return getattr(self, self._fields_[key][0])


# Translated from header file OVR_CAPI.h line 292
class Vector3f(Structure):
    "A 3D vector with float components."
    _pack_ = 4
    _fields_ = [
        ("x", c_float),  
        ("y", c_float),  
        ("z", c_float),  
    ]

    def __repr__(self):
        return "ovr.Vector3f(%s, %s, %s)" % (self.x, self.y, self.z)

    def __len__(self):
        "number of items in this container"
        return len(self._fields_)

    def __getitem__(self, key):
        "access contained elements"
        if isinstance(key, slice):
            return [self[ii] for ii in range(*key.indices(len(self)))]
        else:
            return getattr(self, self._fields_[key][0])


# Translated from header file OVR_CAPI.h line 295
class Matrix4f(Structure):
    "A 4x4 matrix with float elements."
    _pack_ = 4
    _fields_ = [
        ("M", (c_float * 4) * 4),  
    ]

    def __repr__(self):
        return "ovr.Matrix4f(%s)" % (self.M)

    def __len__(self):
        "number of items in this container"
        return 16

    def __getitem__(self, key):
        "access contained elements as a single flat list"
        i = int(key/4)
        j = key % 4
        return self.M[j][i]


# Translated from header file OVR_CAPI.h line 298
class Posef(Structure):
    """
    Position and orientation together.
    The coordinate system used is right-handed Cartesian.
    """
    _pack_ = 4
    _fields_ = [
        ("Orientation", Quatf), 
        ("Position", Vector3f), 
    ]

    def __repr__(self):
        return "ovr.Posef(%s, %s)" % (self.Orientation, self.Position)


# Translated from header file OVR_CAPI.h line 305
class PoseStatef(Structure):
    """
    A full pose (rigid body) configuration with first and second derivatives.
    
    Body refers to any object for which ovrPoseStatef is providing data.
    It can be the HMD, Touch controller, sensor or something else. The context
    depends on the usage of the struct.
    """
    _pack_ = 8
    _fields_ = [
        ("ThePose", Posef),  #< Position and orientation.
        ("AngularVelocity", Vector3f),  #< Angular velocity in radians per second.
        ("LinearVelocity", Vector3f),  #< Velocity in meters per second.
        ("AngularAcceleration", Vector3f),  #< Angular acceleration in radians per second per second.
        ("LinearAcceleration", Vector3f),  #< Acceleration in meters per second per second.
        ("pad0", c_char * 4),  #< \internal struct pad.
        ("TimeInSeconds", c_double),  #< Absolute time that this pose refers to. \see ovr_GetTimeInSeconds
    ]

    def __repr__(self):
        return "ovr.PoseStatef(%s, %s, %s, %s, %s, %s)" % (self.ThePose, self.AngularVelocity, self.LinearVelocity, self.AngularAcceleration, self.LinearAcceleration, self.TimeInSeconds)


# Translated from header file OVR_CAPI.h line 320
class FovPort(Structure):
    """
    Describes the up, down, left, and right angles of the field of view.
    
    Field Of View (FOV) tangent of the angle units.
    \note For a standard 90 degree vertical FOV, we would
    have: { UpTan = tan(90 degrees / 2), DownTan = tan(90 degrees / 2) }.
    """
    _pack_ = 4
    _fields_ = [
        ("UpTan", c_float),  #< Tangent of the angle between the viewing vector and top edge of the FOV.
        ("DownTan", c_float),  #< Tangent of the angle between the viewing vector and bottom edge of the FOV.
        ("LeftTan", c_float),  #< Tangent of the angle between the viewing vector and left edge of the FOV.
        ("RightTan", c_float),  #< Tangent of the angle between the viewing vector and right edge of the FOV.
    ]

    def __repr__(self):
        return "ovr.FovPort(%s, %s, %s, %s)" % (self.UpTan, self.DownTan, self.LeftTan, self.RightTan)


# Translated from header file OVR_CAPI.h line 335
# Enumerates all HMD types that we support.
#
# The currently released developer kits are ovrHmd_DK1 and ovrHmd_DK2.
# The other enumerations are for internal use only.
HmdType = ENUM_TYPE
Hmd_None = 0
Hmd_DK1 = 3
Hmd_DKHD = 4
Hmd_DK2 = 6
Hmd_CB = 8
Hmd_Other = 9
Hmd_E3_2015 = 10
Hmd_ES06 = 11
Hmd_ES09 = 12
Hmd_ES11 = 13
Hmd_CV1 = 14
Hmd_RiftS = 16
Hmd_Quest = 19
Hmd_Quest2 = 20


# Translated from header file OVR_CAPI.h line 355
# HMD capability bits reported by device.
#
HmdCaps = ENUM_TYPE
# Read-only flags
# <B>(read only)</B> Specifies that the HMD is a virtual debug device.
HmdCap_DebugDevice = 0x0010


# Translated from header file OVR_CAPI.h line 367
# Tracking capability bits reported by the device.
# Used with ovr_GetTrackingCaps.
TrackingCaps = ENUM_TYPE
TrackingCap_Orientation = 0x0010 #< Supports orientation tracking (IMU).
TrackingCap_MagYawCorrection = 0x0020 #< Supports yaw drift correction.
TrackingCap_Position = 0x0040 #< Supports positional tracking.


# Translated from header file OVR_CAPI.h line 376
# Specifies which eye is being used for rendering.
# This type explicitly does not include a third "NoStereo" monoscopic option,
# as such is not required for an HMD-centered API.
EyeType = ENUM_TYPE
Eye_Left = 0 #< The left eye, from the viewer's perspective.
Eye_Right = 1 #< The right eye, from the viewer's perspective.
Eye_Count = 2 #< \internal Count of enumerated elements.


# Translated from header file OVR_CAPI.h line 386
# Specifies the coordinate system ovrTrackingState returns tracking poses in.
# Used with ovr_SetTrackingOriginType()
TrackingOrigin = ENUM_TYPE
# \brief Tracking system origin reported at eye (HMD) height
# \details Prefer using this origin when your application requires
# matching user's current physical head pose to a virtual head pose
# without any regards to a the height of the floor. Cockpit-based,
# or 3rd-person experiences are ideal candidates.
# When used, all poses in ovrTrackingState are reported as an offset
# transform from the profile calibrated or recentered HMD pose.
# It is recommended that apps using this origin type call ovr_RecenterTrackingOrigin
# prior to starting the VR experience, but notify the user before doing so
# to make sure the user is in a comfortable pose, facing a comfortable
# direction.
TrackingOrigin_EyeLevel = 0
# \brief Tracking system origin reported at floor height
# \details Prefer using this origin when your application requires the
# physical floor height to match the virtual floor height, such as
# standing experiences.
# When used, all poses in ovrTrackingState are reported as an offset
# transform from the profile calibrated floor pose. Calling ovr_RecenterTrackingOrigin
# will recenter the X & Z axes as well as yaw, but the Y-axis (i.e. height) will continue
# to be reported using the floor height as the origin for all poses.
TrackingOrigin_FloorLevel = 1
TrackingOrigin_Count = 2 #< \internal Count of enumerated elements.


# Translated from header file OVR_CAPI.h line 416
class GraphicsLuid(Structure):
    """
    Identifies a graphics device in a platform-specific way.
    For Windows this is a LUID type.
    """
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Public definition reserves space for graphics API-specific implementation
        ("Reserved", c_char * 8), 
    ]

    def __repr__(self):
        return "ovr.GraphicsLuid(%s)" % (self.Reserved)


# Translated from header file OVR_CAPI.h line 423
class HmdDesc(Structure):
    "This is a complete descriptor of the HMD."
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        ("Type", HmdType),  #< The type of HMD.
    ] + OVR_ON64_FIELD(("pad0", c_char * 4)) + [ #< \internal struct paddding.
        ("ProductName", c_char * 64),  #< UTF8-encoded product identification string (e.g. "Oculus Rift DK1").
        ("Manufacturer", c_char * 64),  #< UTF8-encoded HMD manufacturer identification string.
        ("VendorId", c_short),  #< HID (USB) vendor identifier of the device.
        ("ProductId", c_short),  #< HID (USB) product identifier of the device.
        ("SerialNumber", c_char * 24),  #< HMD serial number.
        ("FirmwareMajor", c_short),  #< HMD firmware major version.
        ("FirmwareMinor", c_short),  #< HMD firmware minor version.
        ("AvailableHmdCaps", c_uint),  #< Available ovrHmdCaps bits.
        ("DefaultHmdCaps", c_uint),  #< Default ovrHmdCaps bits.
        ("AvailableTrackingCaps", c_uint),  #< Available ovrTrackingCaps bits.
        ("DefaultTrackingCaps", c_uint),  #< Default ovrTrackingCaps bits.
        ("DefaultEyeFov", FovPort * Eye_Count),  #< Defines the recommended FOVs for the HMD.
        ("MaxEyeFov", FovPort * Eye_Count),  #< Defines the maximum FOVs for the HMD.
        ("Resolution", Sizei),  #< Resolution of the full HMD screen (both eyes) in pixels.
        ("DisplayRefreshRate", c_float),  #< Refresh rate of the display in cycles per second.
    ] + OVR_ON64_FIELD(("pad1", c_char * 4))  #< \internal struct paddding.

    def __repr__(self):
        return "ovr.HmdDesc(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.Type, self.ProductName, self.Manufacturer, self.VendorId, self.ProductId, self.SerialNumber, self.FirmwareMajor, self.FirmwareMinor, self.AvailableHmdCaps, self.DefaultHmdCaps, self.AvailableTrackingCaps, self.DefaultTrackingCaps, self.DefaultEyeFov, self.MaxEyeFov, self.Resolution, self.DisplayRefreshRate)


# Translated from header file OVR_CAPI.h line 445
# Used as an opaque pointer to an OVR session.
Session = POINTER(HmdStruct) 


# Translated from header file OVR_CAPI.h line 449
ProcessId = c_uint32 


# Translated from header file OVR_CAPI.h line 472
# Bit flags describing the current status of sensor tracking.
#  The values must be the same as in enum StatusBits
#
# \see ovrTrackingState
#
StatusBits = ENUM_TYPE
Status_OrientationTracked = 0x0001 #< Orientation is currently tracked (connected & in use).
Status_PositionTracked = 0x0002 #< Position is currently tracked (false if out of range).


# Translated from header file OVR_CAPI.h line 483
class TrackerDesc(Structure):
    """
     Specifies the description of a single sensor.
    
    \see ovr_GetTrackerDesc
    """
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        ("FrustumHFovInRadians", c_float),  #< Sensor frustum horizontal field-of-view (if present).
        ("FrustumVFovInRadians", c_float),  #< Sensor frustum vertical field-of-view (if present).
        ("FrustumNearZInMeters", c_float),  #< Sensor frustum near Z (if present).
        ("FrustumFarZInMeters", c_float),  #< Sensor frustum far Z (if present).
    ]

    def __repr__(self):
        return "ovr.TrackerDesc(%s, %s, %s, %s)" % (self.FrustumHFovInRadians, self.FrustumVFovInRadians, self.FrustumNearZInMeters, self.FrustumFarZInMeters)


# Translated from header file OVR_CAPI.h line 494
#  Specifies sensor flags.
#
#  /see ovrTrackerPose
#
TrackerFlags = ENUM_TYPE
Tracker_Connected = 0x0020 #< The sensor is present, else the sensor is absent or offline.
Tracker_PoseTracked = 0x0004 #< The sensor has a valid pose, else the pose is unavailable.
#< This will only be set if ovrTracker_Connected is set.


# Translated from header file OVR_CAPI.h line 504
class TrackerPose(Structure):
    """
     Specifies the pose for a single sensor.
    """
    _pack_ = 8
    _fields_ = [
        ("TrackerFlags", c_uint),  #< ovrTrackerFlags.
        ("Pose", Posef),  #< The sensor's pose. This pose includes sensor tilt (roll and pitch).
        #< For a leveled coordinate system use LeveledPose.
        ("LeveledPose", Posef),  #< The sensor's leveled pose, aligned with gravity. This value includes
        #< pos and yaw of the sensor, but not roll and pitch. It can be used as
        #< a reference point to render real-world objects in the correct location.
        ("pad0", c_char * 4),  #< \internal struct pad.
    ]

    def __repr__(self):
        return "ovr.TrackerPose(%s, %s, %s)" % (self.TrackerFlags, self.Pose, self.LeveledPose)


# Translated from header file OVR_CAPI.h line 516
class TrackingState(Structure):
    """
    Tracking state at a given absolute time (describes predicted HMD pose, etc.).
    Returned by ovr_GetTrackingState.
    
    \see ovr_GetTrackingState
    """
    _pack_ = 8
    _fields_ = [
        # Predicted head pose (and derivatives) at the requested absolute time.
        ("HeadPose", PoseStatef), 
        # HeadPose tracking status described by ovrStatusBits.
        ("StatusFlags", c_uint), 
        # The most recent calculated pose for each hand when hand controller tracking is present.
        # HandPoses[ovrHand_Left] refers to the left hand and HandPoses[ovrHand_Right] to the right.
        # These values can be combined with ovrInputState for complete hand controller information.
        ("HandPoses", PoseStatef * 2), 
        # HandPoses status flags described by ovrStatusBits.
        # Only ovrStatus_OrientationTracked and ovrStatus_PositionTracked are reported.
        ("HandStatusFlags", c_uint * 2), 
        # The pose of the origin captured during calibration.
        # Like all other poses here, this is expressed in the space set by ovr_RecenterTrackingOrigin,
        # or ovr_SpecifyTrackingOrigin and so will change every time either of those functions are
        # called. This pose can be used to calculate where the calibrated origin lands in the new
        # recentered space. If an application never calls ovr_RecenterTrackingOrigin or
        # ovr_SpecifyTrackingOrigin, expect this value to be the identity pose and as such will point
        # respective origin based on ovrTrackingOrigin requested when calling ovr_GetTrackingState.
        ("CalibratedOrigin", Posef), 
    ]

    def __repr__(self):
        return "ovr.TrackingState(%s, %s, %s, %s, %s)" % (self.HeadPose, self.StatusFlags, self.HandPoses, self.HandStatusFlags, self.CalibratedOrigin)


# Translated from header file OVR_CAPI.h line 549
class EyeRenderDesc(Structure):
    """
    Rendering information for each eye. Computed by ovr_GetRenderDesc() based on the
    specified FOV. Note that the rendering viewport is not included
    here as it can be specified separately and modified per frame by
    passing different Viewport values in the layer structure.
    
    \see ovr_GetRenderDesc
    """
    _pack_ = 4
    _fields_ = [
        ("Eye", EyeType),  #< The eye index to which this instance corresponds.
        ("Fov", FovPort),  #< The field of view.
        ("DistortedViewport", Recti),  #< Distortion viewport.
        ("PixelsPerTanAngleAtCenter", Vector2f),  #< How many display pixels will fit in tan(angle) = 1.
        ("HmdToEyePose", Posef),  #< Translation of each eye, in meters.
    ]

    def __repr__(self):
        return "ovr.EyeRenderDesc(%s, %s, %s, %s, %s)" % (self.Eye, self.Fov, self.DistortedViewport, self.PixelsPerTanAngleAtCenter, self.HmdToEyePose)


# Translated from header file OVR_CAPI.h line 564
class TimewarpProjectionDesc(Structure):
    """
    Projection information for ovrLayerEyeFovDepth.
    
    Use the utility function ovrTimewarpProjectionDesc_FromProjection to
    generate this structure from the application's projection matrix.
    
    \see ovrLayerEyeFovDepth, ovrTimewarpProjectionDesc_FromProjection
    """
    _pack_ = 4
    _fields_ = [
        ("Projection22", c_float),  #< Projection matrix element [2][2].
        ("Projection23", c_float),  #< Projection matrix element [2][3].
        ("Projection32", c_float),  #< Projection matrix element [3][2].
    ]

    def __repr__(self):
        return "ovr.TimewarpProjectionDesc(%s, %s, %s)" % (self.Projection22, self.Projection23, self.Projection32)


# Translated from header file OVR_CAPI.h line 577
class ViewScaleDesc(Structure):
    """
    Contains the data necessary to properly calculate position info for various layer types.
    - HmdToEyeOffset is the same value pair provided in ovrEyeRenderDesc.
    - HmdSpaceToWorldScaleInMeters is used to scale player motion into in-application units.
      In other words, it is how big an in-application unit is in the player's physical meters.
      For example, if the application uses inches as its units then HmdSpaceToWorldScaleInMeters
      would be 0.0254.
      Note that if you are scaling the player in size, this must also scale. So if your application
      units are inches, but you're shrinking the player to half their normal size, then
      HmdSpaceToWorldScaleInMeters would be 0.0254*2.0.
    
    \see ovrEyeRenderDesc, ovr_SubmitFrame
    """
    _pack_ = 4
    _fields_ = [
        ("HmdToEyePose", Posef * Eye_Count),  #< Translation of each eye.
        ("HmdSpaceToWorldScaleInMeters", c_float),  #< Ratio of viewer units to meter units.
    ]

    def __repr__(self):
        return "ovr.ViewScaleDesc(%s, %s)" % (self.HmdToEyeOffset, self.HmdSpaceToWorldScaleInMeters)


# Translated from header file OVR_CAPI.h line 597
# The type of texture resource.
#
# \see ovrTextureSwapChainDesc
#
TextureType = ENUM_TYPE
Texture_2D = 0 #< 2D textures.
Texture_2D_External = Texture_2D + 1 #< External 2D texture. Not used on PC
Texture_Cube = Texture_2D_External + 1 #< Cube maps.
Texture_Count = Texture_Cube + 1 


# Translated from header file OVR_CAPI.h line 609
# The bindings required for texture swap chain.
#
# All texture swap chains are automatically bindable as shader
# input resources since the Oculus runtime needs this to read them.
#
# \see ovrTextureSwapChainDesc
#
TextureBindFlags = ENUM_TYPE
TextureBind_None = 0 
# The application can write into the chain with pixel shader.
TextureBind_DX_RenderTarget = 0x0001
# The application can write to the chain with compute shader.
TextureBind_DX_UnorderedAccess = 0x0002
# The chain buffers can be bound as depth and/or stencil buffers.
# This flag cannot be combined with ovrTextureBind_DX_RenderTarget.
TextureBind_DX_DepthStencil = 0x0004


# Translated from header file OVR_CAPI.h line 632
# The format of a texture.
#
# \see ovrTextureSwapChainDesc
#
TextureFormat = ENUM_TYPE
OVR_FORMAT_UNKNOWN = 0
OVR_FORMAT_B5G6R5_UNORM = 1 #< Not currently supported on PC. Requires a DirectX 11.1 device.
OVR_FORMAT_B5G5R5A1_UNORM = 2 #< Not currently supported on PC. Requires a DirectX 11.1 device.
OVR_FORMAT_B4G4R4A4_UNORM = 3 #< Not currently supported on PC. Requires a DirectX 11.1 device.
OVR_FORMAT_R8G8B8A8_UNORM = 4
OVR_FORMAT_R8G8B8A8_UNORM_SRGB = 5
OVR_FORMAT_B8G8R8A8_UNORM = 6
OVR_FORMAT_B8G8R8A8_UNORM_SRGB = 7 #< Not supported for OpenGL applications
OVR_FORMAT_B8G8R8X8_UNORM = 8 #< Not supported for OpenGL applications
OVR_FORMAT_B8G8R8X8_UNORM_SRGB = 9 #< Not supported for OpenGL applications
OVR_FORMAT_R16G16B16A16_FLOAT = 10
OVR_FORMAT_R11G11B10_FLOAT = 25 #< Introduced in v1.10
# Depth formats
OVR_FORMAT_D16_UNORM = 11
OVR_FORMAT_D24_UNORM_S8_UINT = 12
OVR_FORMAT_D32_FLOAT = 13
OVR_FORMAT_D32_FLOAT_S8X24_UINT = 14
# Added in 1.5 compressed formats can be used for static layers
OVR_FORMAT_BC1_UNORM = 15
OVR_FORMAT_BC1_UNORM_SRGB = 16
OVR_FORMAT_BC2_UNORM = 17
OVR_FORMAT_BC2_UNORM_SRGB = 18
OVR_FORMAT_BC3_UNORM = 19
OVR_FORMAT_BC3_UNORM_SRGB = 20
OVR_FORMAT_BC6H_UF16 = 21
OVR_FORMAT_BC6H_SF16 = 22
OVR_FORMAT_BC7_UNORM = 23
OVR_FORMAT_BC7_UNORM_SRGB = 24
OVR_FORMAT_ENUMSIZE = 0x7fffffff #< \internal Force type int32_t.


# Translated from header file OVR_CAPI.h line 671
# Misc flags overriding particular
#   behaviors of a texture swap chain
#
# \see ovrTextureSwapChainDesc
#
TextureFlags = ENUM_TYPE
TextureMisc_None = 0 
# Vulkan and DX only: The underlying texture is created with a TYPELESS equivalent
# of the format specified in the texture desc. The SDK will still access the
# texture using the format specified in the texture desc, but the app can
# create views with different formats if this is specified.
TextureMisc_DX_Typeless = 0x0001
# DX only: Allow generation of the mip chain on the GPU via the GenerateMips
# call. This flag requires that RenderTarget binding also be specified.
TextureMisc_AllowGenerateMips = 0x0002
# Texture swap chain contains protected content, and requires
# HDCP connection in order to display to HMD. Also prevents
# mirroring or other redirection of any frame containing this contents
TextureMisc_ProtectedContent = 0x0004


# Translated from header file OVR_CAPI.h line 697
class TextureSwapChainDesc(Structure):
    """
    Description used to create a texture swap chain.
    
    \see ovr_CreateTextureSwapChainDX
    \see ovr_CreateTextureSwapChainGL
    """
    _fields_ = [
        ("Type", TextureType), 
        ("Format", TextureFormat), 
        ("ArraySize", c_int),  #< Only supported with ovrTexture_2D. Not supported on PC at this time.
        ("Width", c_int), 
        ("Height", c_int), 
        ("MipLevels", c_int), 
        ("SampleCount", c_int),  #< Current only supported on depth textures
        ("StaticImage", Bool),  #< Not buffered in a chain. For images that don't change
        ("MiscFlags", c_uint),  #< ovrTextureFlags
        ("BindFlags", c_uint),  #< ovrTextureBindFlags. Not used for GL.
    ]

    def __repr__(self):
        return "ovr.TextureSwapChainDesc(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.Type, self.Format, self.ArraySize, self.Width, self.Height, self.MipLevels, self.SampleCount, self.StaticImage, self.MiscFlags, self.BindFlags)


# Translated from header file OVR_CAPI.h line 716
class MirrorTextureDesc(Structure):
    """
    Description used to create a mirror texture.
    
    \see ovr_CreateMirrorTextureDX
    \see ovr_CreateMirrorTextureWithOptionsDX
    \see ovr_CreateMirrorTextureGL
    \see ovr_CreateMirrorTextureWithOptionsGL
    \see ovr_CreateMirrorTextureWithOptionsVk
    """
    _fields_ = [
        ("Format", TextureFormat), 
        ("Width", c_int), 
        ("Height", c_int), 
        ("MiscFlags", c_uint),  #< ovrTextureFlags
        ("MirrorOptions", c_uint),  #< ovrMirrorOptions
    ]

    def __repr__(self):
        return "ovr.MirrorTextureDesc(%s, %s, %s, %s, %s)" % (self.Format, self.Width, self.Height, self.MiscFlags, self.MirrorOptions)


# Translated from header file OVR_CAPI.h line 732
TextureSwapChain = POINTER(TextureSwapChainData) 


# Translated from header file OVR_CAPI.h line 733
MirrorTexture = POINTER(MirrorTextureData) 


# Translated from header file OVR_CAPI.h line 737
# Describes button input types.
# Button inputs are combined; that is they will be reported as pressed if they are
# pressed on either one of the two devices.
# The ovrButton_Up/Down/Left/Right map to both XBox D-Pad and directional buttons.
# The ovrButton_Enter and ovrButton_Return map to Start and Back controller buttons, respectively.
Button = ENUM_TYPE
# A button on XBox controllers and right Touch controller. Select button on Oculus Remote.
Button_A = 0x00000001
# B button on XBox controllers and right Touch controller. Back button on Oculus Remote.
Button_B = 0x00000002
# Right thumbstick on XBox controllers and Touch controllers. Not present on Oculus Remote.
Button_RThumb = 0x00000004
# Right shoulder button on XBox controllers. Not present on Touch controllers or Oculus Remote.
Button_RShoulder = 0x00000008
# X button on XBox controllers and left Touch controller. Not present on Oculus Remote.
Button_X = 0x00000100
# Y button on XBox controllers and left Touch controller. Not present on Oculus Remote.
Button_Y = 0x00000200
# Left thumbstick on XBox controllers and Touch controllers. Not present on Oculus Remote.
Button_LThumb = 0x00000400
# Left shoulder button on XBox controllers. Not present on Touch controllers or Oculus Remote.
Button_LShoulder = 0x00000800
# Up button on XBox controllers and Oculus Remote. Not present on Touch controllers.
Button_Up = 0x00010000
# Down button on XBox controllers and Oculus Remote. Not present on Touch controllers.
Button_Down = 0x00020000
# Left button on XBox controllers and Oculus Remote. Not present on Touch controllers.
Button_Left = 0x00040000
# Right button on XBox controllers and Oculus Remote. Not present on Touch controllers.
Button_Right = 0x00080000
# Start on XBox 360 controller. Menu on XBox One controller and Left Touch controller.
# Should be referred to as the Menu button in user-facing documentation.
Button_Enter = 0x00100000
# Back on Xbox 360 controller. View button on XBox One controller. Not present on Touch
# controllers or Oculus Remote.
Button_Back = 0x00200000
# Volume button on Oculus Remote. Not present on XBox or Touch controllers.
Button_VolUp = 0x00400000
# Volume button on Oculus Remote. Not present on XBox or Touch controllers.
Button_VolDown = 0x00800000
# Home button on XBox controllers. Oculus button on Touch controllers and Oculus Remote.
Button_Home = 0x01000000
# Bit mask of all buttons that are for private usage by Oculus
Button_Private = Button_VolUp | Button_VolDown | Button_Home
# Bit mask of all buttons on the right Touch controller
Button_RMask = Button_A | Button_B | Button_RThumb | Button_RShoulder
# Bit mask of all buttons on the left Touch controller
Button_LMask = Button_X | Button_Y | Button_LThumb | Button_LShoulder | Button_Enter


# Translated from header file OVR_CAPI.h line 810
# Describes touch input types.
# These values map to capacitive touch values reported ovrInputState::Touch.
# Some of these values are mapped to button bits for consistency.
Touch = ENUM_TYPE
Touch_A = Button_A
Touch_B = Button_B
Touch_RThumb = Button_RThumb
Touch_RThumbRest = 0x00000008
Touch_RIndexTrigger = 0x00000010
# Bit mask of all the button touches on the right controller
Touch_RButtonMask = Touch_A | Touch_B | Touch_RThumb | Touch_RThumbRest | Touch_RIndexTrigger,
Touch_X = Button_X
Touch_Y = Button_Y
Touch_LThumb = Button_LThumb
Touch_LThumbRest = 0x00000800
Touch_LIndexTrigger = 0x00001000
# Bit mask of all the button touches on the left controller
Touch_LButtonMask = Touch_X | Touch_Y | Touch_LThumb | Touch_LThumbRest | Touch_LIndexTrigger
# Finger pose state
# Derived internally based on distance, proximity to sensors and filtering.
Touch_RIndexPointing = 0x00000020
Touch_RThumbUp = 0x00000040
Touch_LIndexPointing = 0x00002000
Touch_LThumbUp = 0x00004000
# Bit mask of all right controller poses
Touch_RPoseMask = Touch_RIndexPointing | Touch_RThumbUp
# Bit mask of all left controller poses
Touch_LPoseMask = Touch_LIndexPointing | Touch_LThumbUp


# Translated from header file OVR_CAPI.h line 850
class TouchHapticsDesc(Structure):
    """
    Describes the Touch Haptics engine.
    Currently, those values will NOT change during a session.
    """
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Haptics engine frequency/sample-rate, sample time in seconds equals 1.0/sampleRateHz
        ("SampleRateHz", c_int), 
        # Size of each Haptics sample, sample value range is [0, 2^(Bytes*8)-1]
        ("SampleSizeInBytes", c_int), 
        # Queue size that would guarantee Haptics engine would not starve for data
        # Make sure size doesn't drop below it for best results
        ("QueueMinSizeToAvoidStarvation", c_int), 
        # Minimum, Maximum and Optimal number of samples that can be sent to Haptics through
        # ovr_SubmitControllerVibration
        ("SubmitMinSamples", c_int), 
        ("SubmitMaxSamples", c_int), 
        ("SubmitOptimalSamples", c_int), 
    ]

    def __repr__(self):
        return "ovr.TouchHapticsDesc(%s, %s, %s, %s, %s, %s)" % (self.SampleRateHz, self.SampleSizeInBytes, self.QueueMinSizeToAvoidStarvation, self.SubmitMinSamples, self.SubmitMaxSamples, self.SubmitOptimalSamples)


# Translated from header file OVR_CAPI.h line 869
# Specifies which controller is connected; multiple can be connected at once.
ControllerType = ENUM_TYPE
ControllerType_None = 0x0000
ControllerType_LTouch = 0x0001
ControllerType_RTouch = 0x0002
ControllerType_Touch = (ControllerType_LTouch | ControllerType_RTouch)
ControllerType_Remote = 0x0004
ControllerType_XBox = 0x0010
ControllerType_Object0 = 0x0100
ControllerType_Object1 = 0x0200
ControllerType_Object2 = 0x0400
ControllerType_Object3 = 0x0800
ControllerType_Active = 0xffffffff #< Operate on or query whichever controller is active.


# Translated from header file OVR_CAPI.h line 889
# Haptics buffer submit mode
HapticsBufferSubmitMode = ENUM_TYPE
# Enqueue buffer for later playback
HapticsBufferSubmit_Enqueue = 0 


# Translated from header file OVR_CAPI.h line 895
class HapticsBuffer(Structure):
    "Haptics buffer descriptor, contains amplitude samples used for Touch vibration"
    _fields_ = [
        # Samples stored in opaque format
        ("Samples", c_void_p), 
        # Number of samples
        ("SamplesCount", c_int), 
        # How samples are submitted to the hardware
        ("SubmitMode", HapticsBufferSubmitMode), 
    ]

    def __repr__(self):
        return "ovr.HapticsBuffer(%s, %s, %s)" % (self.Samples, self.SamplesCount, self.SubmitMode)


# Translated from header file OVR_CAPI.h line 905
class HapticsPlaybackState(Structure):
    "State of the Haptics playback for Touch vibration"
    _fields_ = [
        # Remaining space available to queue more samples
        ("RemainingQueueSpace", c_int), 
        # Number of samples currently queued
        ("SamplesQueued", c_int), 
    ]

    def __repr__(self):
        return "ovr.HapticsPlaybackState(%s, %s)" % (self.RemainingQueueSpace, self.SamplesQueued)


# Translated from header file OVR_CAPI.h line 914
# Position tracked devices
TrackedDeviceType = ENUM_TYPE
TrackedDevice_None = 0x0000
TrackedDevice_HMD = 0x0001
TrackedDevice_LTouch = 0x0002
TrackedDevice_RTouch = 0x0004
TrackedDevice_Touch = (TrackedDevice_LTouch | TrackedDevice_RTouch)
TrackedDevice_Object0 = 0x0010
TrackedDevice_Object1 = 0x0020
TrackedDevice_Object2 = 0x0040
TrackedDevice_Object3 = 0x0080
TrackedDevice_All = 0xFFFF


# Translated from header file OVR_CAPI.h line 930
# Boundary types that specified while using the boundary system
BoundaryType = ENUM_TYPE
# Outer boundary - closely represents user setup walls
Boundary_Outer = 0x0001
# Play area - safe rectangular area inside outer boundary which can optionally be used to
# restrict user interactions and motion.
Boundary_PlayArea = 0x0100


# Translated from header file OVR_CAPI.h line 940
class BoundaryLookAndFeel(Structure):
    "Boundary system look and feel"
    _fields_ = [
        # Boundary color (alpha channel is ignored)
        ("Color", Colorf), 
    ]

    def __repr__(self):
        return "ovr.BoundaryLookAndFeel(%s)" % (self.Color)


# Translated from header file OVR_CAPI.h line 946
class BoundaryTestResult(Structure):
    "Provides boundary test information"
    _fields_ = [
        # True if the boundary system is being triggered. Note that due to fade in/out effects this may
        # not exactly match visibility.
        ("IsTriggering", Bool), 
        # Distance to the closest play area or outer boundary surface.
        ("ClosestDistance", c_float), 
        # Closest point on the boundary surface.
        ("ClosestPoint", Vector3f), 
        # Unit surface normal of the closest boundary surface.
        ("ClosestPointNormal", Vector3f), 
    ]

    def __repr__(self):
        return "ovr.BoundaryTestResult(%s, %s, %s, %s)" % (self.IsTriggering, self.ClosestDistance, self.ClosestPoint, self.ClosestPointNormal)


# Translated from header file OVR_CAPI.h line 962
# Provides names for the left and right hand array indexes.
#
# \see ovrInputState, ovrTrackingState
#
HandType = ENUM_TYPE
Hand_Left = 0
Hand_Right = 1
Hand_Count = 2


# Translated from header file OVR_CAPI.h line 973
class InputState(Structure):
    """
    ovrInputState describes the complete controller input state, including Oculus Touch,
    and XBox gamepad. If multiple inputs are connected and used at the same time,
    their inputs are combined.
    """
    _fields_ = [
        # System type when the controller state was last updated.
        ("TimeInSeconds", c_double), 
        # Values for buttons described by ovrButton.
        ("Buttons", c_uint), 
        # Touch values for buttons and sensors as described by ovrTouch.
        ("Touches", c_uint), 
        # Left and right finger trigger values (ovrHand_Left and ovrHand_Right), in range 0.0 to 1.0f.
        # Returns 0 if the value would otherwise be less than 0.1176, for ovrControllerType_XBox.
        # This has been formally named simply "Trigger". We retain the name IndexTrigger for backwards
        # code compatibility.
        # User-facing documentation should refer to it as the Trigger.
        ("IndexTrigger", c_float * Hand_Count), 
        # Left and right hand trigger values (ovrHand_Left and ovrHand_Right), in the range 0.0 to 1.0f.
        # This has been formally named "Grip Button". We retain the name HandTrigger for backwards code
        # compatibility.
        # User-facing documentation should refer to it as the Grip Button or simply Grip.
        ("HandTrigger", c_float * Hand_Count), 
        # Horizontal and vertical thumbstick axis values (ovrHand_Left and ovrHand_Right), in the range
        # of -1.0f to 1.0f.
        # Returns a deadzone (value 0) per each axis if the value on that axis would otherwise have been
        # between -.2746 to +.2746, for ovrControllerType_XBox
        ("Thumbstick", Vector2f * Hand_Count), 
        # The type of the controller this state is for.
        ("ControllerType", ControllerType), 
        # Left and right finger trigger values (ovrHand_Left and ovrHand_Right), in range 0.0 to 1.0f.
        # Does not apply a deadzone.  Only touch applies a filter.
        # This has been formally named simply "Trigger". We retain the name IndexTrigger for backwards
        # code compatibility.
        # User-facing documentation should refer to it as the Trigger.
        ("IndexTriggerNoDeadzone", c_float * Hand_Count), 
        # Left and right hand trigger values (ovrHand_Left and ovrHand_Right), in the range 0.0 to 1.0f.
        # Does not apply a deadzone. Only touch applies a filter.
        # This has been formally named "Grip Button". We retain the name HandTrigger for backwards code
        # compatibility.
        # User-facing documentation should refer to it as the Grip Button or simply Grip.
        ("HandTriggerNoDeadzone", c_float * Hand_Count), 
        # Horizontal and vertical thumbstick axis values (ovrHand_Left and ovrHand_Right), in the range
        # -1.0f to 1.0f
        # Does not apply a deadzone or filter.
        ("ThumbstickNoDeadzone", Vector2f * Hand_Count), 
        # Left and right finger trigger values (ovrHand_Left and ovrHand_Right), in range 0.0 to 1.0f.
        # No deadzone or filter
        # This has been formally named "Grip Button". We retain the name HandTrigger for backwards code
        # compatibility.
        # User-facing documentation should refer to it as the Grip Button or simply Grip.
        ("IndexTriggerRaw", c_float * Hand_Count), 
        # Left and right hand trigger values (ovrHand_Left and ovrHand_Right), in the range 0.0 to 1.0f.
        # No deadzone or filter
        # This has been formally named "Grip Button". We retain the name HandTrigger for backwards code
        # compatibility.
        # User-facing documentation should refer to it as the Grip Button or simply Grip.
        ("HandTriggerRaw", c_float * Hand_Count), 
        # Horizontal and vertical thumbstick axis values (ovrHand_Left and ovrHand_Right), in the range
        # -1.0f to 1.0f
        # No deadzone or filter
        ("ThumbstickRaw", Vector2f * Hand_Count), 
    ]

    def __repr__(self):
        return "ovr.InputState(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.TimeInSeconds, self.Buttons, self.Touches, self.IndexTrigger, self.HandTrigger, self.Thumbstick, self.ControllerType, self.IndexTriggerNoDeadzone, self.HandTriggerNoDeadzone, self.ThumbstickNoDeadzone, self.IndexTriggerRaw, self.HandTriggerRaw, self.ThumbstickRaw)


# Translated from header file OVR_CAPI.h line 1047
class CameraIntrinsics(Structure):
    ""
    _fields_ = [
        # Time in seconds from last change to the parameters
        ("LastChangedTime", c_double), 
        # Angles of all 4 sides of viewport
        ("FOVPort", FovPort), 
        # Near plane of the virtual camera used to match the external camera
        ("VirtualNearPlaneDistanceMeters", c_float), 
        # Far plane of the virtual camera used to match the external camera
        ("VirtualFarPlaneDistanceMeters", c_float), 
        # Height in pixels of image sensor
        ("ImageSensorPixelResolution", Sizei), 
        # The lens distortion matrix of camera
        ("LensDistortionMatrix", Matrix4f), 
        # How often, in seconds, the exposure is taken
        ("ExposurePeriodSeconds", c_double), 
        # length of the exposure time
        ("ExposureDurationSeconds", c_double), 
    ]

    def __repr__(self):
        return "ovr.CameraIntrinsics(%s, %s, %s, %s, %s, %s, %s, %s)" % (self.LastChangedTime, self.FOVPort, self.VirtualNearPlaneDistanceMeters, self.VirtualFarPlaneDistanceMeters, self.ImageSensorPixelResolution, self.LensDistortionMatrix, self.ExposurePeriodSeconds, self.ExposureDurationSeconds)


# Translated from header file OVR_CAPI.h line 1074
CameraStatusFlags = ENUM_TYPE
# Initial state of camera
CameraStatus_None = 0x0
# Bit set when the camera is connected to the system
CameraStatus_Connected = 0x1
# Bit set when the camera is undergoing calibration
CameraStatus_Calibrating = 0x2
# Bit set when the camera has tried & failed calibration
CameraStatus_CalibrationFailed = 0x4
# Bit set when the camera has tried & passed calibration
CameraStatus_Calibrated = 0x8


# Translated from header file OVR_CAPI.h line 1092
class CameraExtrinsics(Structure):
    ""
    _fields_ = [
        # Time in seconds from last change to the parameters.
        # For instance, if the pose changes, or a camera exposure happens, this struct will be updated.
        ("LastChangedTimeSeconds", c_double), 
        # Current Status of the camera, a mix of bits from ovrCameraStatusFlags
        ("CameraStatusFlags", c_uint), 
        # Which Tracked device, if any, is the camera rigidly attached to
        # If set to ovrTrackedDevice_None, then the camera is not attached to a tracked object.
        # If the external camera moves while unattached (i.e. set to ovrTrackedDevice_None), its Pose
        # won't be updated
        ("AttachedToDevice", TrackedDeviceType), 
        # The relative Pose of the External Camera.
        # If AttachedToDevice is ovrTrackedDevice_None, then this is a absolute pose in tracking space
        ("RelativePose", Posef), 
        # The time, in seconds, when the last successful exposure was taken
        ("LastExposureTimeSeconds", c_double), 
        # Estimated exposure latency to get from the exposure time to the system
        ("ExposureLatencySeconds", c_double), 
        # Additional latency to get from the exposure time of the real camera to match the render time
        # of the virtual camera
        ("AdditionalLatencySeconds", c_double), 
    ]

    def __repr__(self):
        return "ovr.CameraExtrinsics(%s, %s, %s, %s, %s, %s, %s)" % (self.LastChangedTimeSeconds, self.CameraStatusFlags, self.AttachedToDevice, self.RelativePose, self.LastExposureTimeSeconds, self.ExposureLatencySeconds, self.AdditionalLatencySeconds)


# Translated from header file OVR_CAPI.h line 1122
EXTERNAL_CAMERA_NAME_SIZE = 32 


# Translated from header file OVR_CAPI.h line 1123
class ExternalCamera(Structure):
    ""
    _fields_ = [
        ("Name", c_char * EXTERNAL_CAMERA_NAME_SIZE),
        ("Intrinsics", CameraIntrinsics), 
        ("Extrinsics", CameraExtrinsics), 
    ]

    def __repr__(self):
        return "ovr.ExternalCamera(%s, %s, %s)" % (self.Name, self.Intrinsics, self.Extrinsics)


# Translated from header file OVR_CAPI.h line 1132
# Initialization flags.
#
# \see ovrInitParams, ovr_Initialize
#
InitFlags = ENUM_TYPE
# When a debug library is requested, a slower debugging version of the library will
# run which can be used to help solve problems in the library and debug application code.
Init_Debug = 0x00000001
# When a version is requested, the LibOVR runtime respects the RequestedMinorVersion
# field and verifies that the RequestedMinorVersion is supported. Normally when you
# specify this flag you simply use OVR_MINOR_VERSION for ovrInitParams::RequestedMinorVersion,
# though you could use a lower version than OVR_MINOR_VERSION to specify previous
# version behavior.
Init_RequestVersion = 0x00000004
# This client will not be visible in the HMD.
# Typically set by diagnostic or debugging utilities.
Init_Invisible = 0x00000010
# This client will alternate between VR and 2D rendering.
# Typically set by game engine editors and VR-enabled web browsers.
Init_MixedRendering = 0x00000020
# This client is aware of ovrSessionStatus focus states (e.g. ovrSessionStatus::HasInputFocus),
# and responds to them appropriately (e.g. pauses and stops drawing hands when lacking focus).
Init_FocusAware = 0x00000040
# These bits are writable by user code.
Init_WritableBits = 0x00ffffff


# Translated from header file OVR_CAPI.h line 1168
# Logging levels
#
# \see ovrInitParams, ovrLogCallback
#
LogLevel = ENUM_TYPE
LogLevel_Debug = 0 #< Debug-level log event.
LogLevel_Info = 1 #< Info-level log event.
LogLevel_Error = 2 #< Error-level log event.


# Translated from header file OVR_CAPI.h line 1189
class InitParams(Structure):
    """
    Parameters for ovr_Initialize.
    
    \see ovr_Initialize
    """
    _pack_ = 8
    _fields_ = [
        # Flags from ovrInitFlags to override default behavior.
        # Use 0 for the defaults.
        ("Flags", c_uint32), 
        # Requests a specific minor version of the LibOVR runtime.
        # Flags must include ovrInit_RequestVersion or this will be ignored and OVR_MINOR_VERSION
        # will be used. If you are directly calling the LibOVRRT version of ovr_Initialize
        # in the LibOVRRT DLL then this must be valid and include ovrInit_RequestVersion.
        ("RequestedMinorVersion", c_uint32), 
        # User-supplied log callback function, which may be called at any time
        # asynchronously from multiple threads until ovr_Shutdown completes.
        # Use NULL to specify no log callback.
        ("LogCallback", LogCallback), 
        # User-supplied data which is passed as-is to LogCallback. Typically this
        # is used to store an application-specific pointer which is read in the
        # callback function.
        ("UserData", POINTER(c_uint)), 
        # Relative number of milliseconds to wait for a connection to the server
        # before failing. Use 0 for the default timeout.
        ("ConnectionTimeoutMS", c_uint32), 
    ] + OVR_ON64_FIELD(("pad0", c_char * 4))  #< \internal

    def __repr__(self):
        return "ovr.InitParams(%s, %s, %s, %s, %s)" % (self.Flags, self.RequestedMinorVersion, self.LogCallback, self.UserData, self.ConnectionTimeoutMS)

# Translated from header file OVR_CAPI.h line 1231
libovr.ovr_Initialize.restype = Result
libovr.ovr_Initialize.argtypes = [POINTER(InitParams)]
def initialize(params):
    """
    Initializes LibOVR
    
    Initialize LibOVR for application usage. This includes finding and loading the LibOVRRT
    shared library. No LibOVR API functions, other than ovr_GetLastErrorInfo and ovr_Detect, can
    be called unless ovr_Initialize succeeds. A successful call to ovr_Initialize must be eventually
    followed by a call to ovr_Shutdown. ovr_Initialize calls are idempotent.
    Calling ovr_Initialize twice does not require two matching calls to ovr_Shutdown.
    If already initialized, the return value is ovr_Success.
    
    LibOVRRT shared library search order:
         -# Current working directory (often the same as the application directory).
         -# Module directory (usually the same as the application directory,
            but not if the module is a separate shared library).
         -# Application directory
         -# Development directory (only if OVR_ENABLE_DEVELOPER_SEARCH is enabled,
            which is off by default).
         -# Standard OS shared library search location(s) (OS-specific).
    
    \param params Specifies custom initialization options. May be NULL to indicate default options
           when using the CAPI shim. If you are directly calling the LibOVRRT version of
           ovr_Initialize in the LibOVRRT DLL then this must be valid and
           include ovrInit_RequestVersion.
    \return Returns an ovrResult indicating success or failure. In the case of failure, use
            ovr_GetLastErrorInfo to get more information. Example failed results include:
        - ovrError_Initialize: Generic initialization error.
        - ovrError_LibLoad: Couldn't load LibOVRRT.
        - ovrError_LibVersion: LibOVRRT version incompatibility.
        - ovrError_ServiceConnection: Couldn't connect to the OVR Service.
        - ovrError_ServiceVersion: OVR Service version incompatibility.
        - ovrError_IncompatibleOS: The operating system version is incompatible.
        - ovrError_DisplayInit: Unable to initialize the HMD display.
        - ovrError_ServerStart:  Unable to start the server. Is it already running?
        - ovrError_Reinitialization: Attempted to re-initialize with a different version.
    
    <b>Example code</b>
        \code{.cpp}
            ovrInitParams initParams = { ovrInit_RequestVersion, OVR_MINOR_VERSION, NULL, 0, 0 };
            ovrResult result = ovr_Initialize(&initParams);
            if(OVR_FAILURE(result)) {
                ovrErrorInfo errorInfo;
                ovr_GetLastErrorInfo(&errorInfo);
                DebugLog("ovr_Initialize failed: %s", errorInfo.ErrorString);
                return false;
            }
            [...]
        \endcode
    
    \see ovr_Shutdown
    """
    # Beginning with OVR SDK 1.8, we need to specify the library version here
    if params is None:
        params = InitParams()
        params.Flags = Init_RequestVersion
        params.RequestedMinorVersion = MINOR_VERSION
        params.ConnectionTimeoutMS = 0
    result = libovr.ovr_Initialize(byref(params))
    _checkResult(result, "initialize")
    return result


# Translated from header file OVR_CAPI.h line 1282
libovr.ovr_Shutdown.restype = None
def shutdown():
    """
    Shuts down LibOVR
    
    A successful call to ovr_Initialize must be eventually matched by a call to ovr_Shutdown.
    After calling ovr_Shutdown, no LibOVR functions can be called except ovr_GetLastErrorInfo
    or another ovr_Initialize. ovr_Shutdown invalidates all pointers, references, and created
    objects
    previously returned by LibOVR functions. The LibOVRRT shared library can be unloaded by
    ovr_Shutdown.
    
    \see ovr_Initialize
    """
    libovr.ovr_Shutdown()


# Translated from header file OVR_CAPI.h line 1295
libovr.ovr_GetLastErrorInfo.restype = None
libovr.ovr_GetLastErrorInfo.argtypes = [POINTER(ErrorInfo)]
def getLastErrorInfo():
    """
    Returns information about the most recent failed return value by the
    current thread for this library.
    
    This function itself can never generate an error.
    The last error is never cleared by LibOVR, but will be overwritten by new errors.
    Do not use this call to determine if there was an error in the last API
    call as successful API calls don't clear the last ovrErrorInfo.
    To avoid any inconsistency, ovr_GetLastErrorInfo should be called immediately
    after an API function that returned a failed ovrResult, with no other API
    functions called in the interim.
    
    \param[out] errorInfo The last ovrErrorInfo for the current thread.
    
    \see ovrErrorInfo
    """
    errorInfo = ErrorInfo()
    libovr.ovr_GetLastErrorInfo(byref(errorInfo))
    return errorInfo


# Translated from header file OVR_CAPI.h line 1312
libovr.ovr_GetVersionString.restype = c_char_p
def getVersionString():
    """
    Returns the version string representing the LibOVRRT version.
    
    The returned string pointer is valid until the next call to ovr_Shutdown.
    
    Note that the returned version string doesn't necessarily match the current
    OVR_MAJOR_VERSION, etc., as the returned string refers to the LibOVRRT shared
    library version and not the locally compiled interface version.
    
    The format of this string is subject to change in future versions and its contents
    should not be interpreted.
    
    \return Returns a UTF8-encoded null-terminated version string.
    """
    result = libovr.ovr_GetVersionString()
    return result


# Translated from header file OVR_CAPI.h line 1327
libovr.ovr_TraceMessage.restype = c_int
libovr.ovr_TraceMessage.argtypes = [c_int, c_char_p]
def traceMessage(level, message):
    """
    Writes a message string to the LibOVR tracing mechanism (if enabled).
    
    This message will be passed back to the application via the ovrLogCallback if
    it was registered.
    
    \param[in] level One of the ovrLogLevel constants.
    \param[in] message A UTF8-encoded null-terminated string.
    \return returns the strlen of the message or a negative value if the message is too large.
    
    \see ovrLogLevel, ovrLogCallback
    """
    result = libovr.ovr_TraceMessage(level, message)
    return result


# Translated from header file OVR_CAPI.h line 1340
libovr.ovr_IdentifyClient.restype = Result
libovr.ovr_IdentifyClient.argtypes = [c_char_p]
def identifyClient(identity):
    """
    Identify client application info.
    
    The string is one or more newline-delimited lines of optional info
    indicating engine name, engine version, engine plugin name, engine plugin
    version, engine editor. The order of the lines is not relevant. Individual
    lines are optional. A newline is not necessary at the end of the last line.
    Call after ovr_Initialize and before the first call to ovr_Create.
    Each value is limited to 20 characters. Key names such as 'EngineName:'
    'EngineVersion:' do not count towards this limit.
    
    \param[in] identity Specifies one or more newline-delimited lines of optional info:
                EngineName: %s\n
                EngineVersion: %s\n
                EnginePluginName: %s\n
                EnginePluginVersion: %s\n
                EngineEditor: <boolean> ('true' or 'false')\n
    
    <b>Example code</b>
        \code{.cpp}
        ovr_IdentifyClient("EngineName: Unity\n"
                           "EngineVersion: 5.3.3\n"
                           "EnginePluginName: OVRPlugin\n"
                           "EnginePluginVersion: 1.2.0\n"
                           "EngineEditor: true");
        \endcode
    """
    result = libovr.ovr_IdentifyClient(identity)
    _checkResult(result, "identifyClient")
    return result


# Translated from header file OVR_CAPI.h line 1374
libovr.ovr_GetHmdDesc.restype = HmdDesc
libovr.ovr_GetHmdDesc.argtypes = [Session]
def getHmdDesc(session):
    """
    Returns information about the current HMD.
    
    ovr_Initialize must be called prior to calling this function,
    otherwise ovrHmdDesc::Type will be set to ovrHmd_None without
    checking for the HMD presence.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create() or NULL.
    
    \return Returns an ovrHmdDesc. If invoked with NULL session argument, ovrHmdDesc::Type
            set to ovrHmd_None indicates that the HMD is not connected.
    """
    result = libovr.ovr_GetHmdDesc(session)
    return result


# Translated from header file OVR_CAPI.h line 1387
libovr.ovr_GetTrackerCount.restype = c_uint
libovr.ovr_GetTrackerCount.argtypes = [Session]
def getTrackerCount(session):
    """
    Returns the number of attached trackers.
    
    The number of trackers may change at any time, so this function should be called before use
    as opposed to once on startup.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    
    \return Returns unsigned int count.
    """
    result = libovr.ovr_GetTrackerCount(session)
    return result


# Translated from header file OVR_CAPI.h line 1398
libovr.ovr_GetTrackerDesc.restype = TrackerDesc
libovr.ovr_GetTrackerDesc.argtypes = [Session, c_uint]
def getTrackerDesc(session, trackerDescIndex):
    """
    Returns a given attached tracker description.
    
    ovr_Initialize must have first been called in order for this to succeed, otherwise the returned
    trackerDescArray will be zero-initialized. The data returned by this function can change at
    runtime.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    
    \param[in] trackerDescIndex Specifies a tracker index. The valid indexes are in the
               range of 0 to the tracker count returned by ovr_GetTrackerCount.
    
    \return Returns ovrTrackerDesc. An empty ovrTrackerDesc will be returned if
              trackerDescIndex is out of range.
    
    \see ovrTrackerDesc, ovr_GetTrackerCount
    """
    result = libovr.ovr_GetTrackerDesc(session, trackerDescIndex)
    return result


# Translated from header file OVR_CAPI.h line 1417
libovr.ovr_Create.restype = Result
libovr.ovr_Create.argtypes = [POINTER(Session), POINTER(GraphicsLuid)]
def create():
    """
    Creates a handle to a VR session.
    
    Upon success the returned ovrSession must be eventually freed with ovr_Destroy when it is no
    longer needed.
    A second call to ovr_Create will result in an error return value if the previous session has not
    been destroyed.
    
    \param[out] pSession Provides a pointer to an ovrSession which will be written to upon success.
    \param[out] pLuid Provides a system specific graphics adapter identifier that locates which
    graphics adapter has the HMD attached. This must match the adapter used by the application
    or no rendering output will be possible. This is important for stability on multi-adapter
    systems. An
    application that simply chooses the default adapter will not run reliably on multi-adapter
    systems.
    \return Returns an ovrResult indicating success or failure. Upon failure
            the returned ovrSession will be NULL.
    
    <b>Example code</b>
        \code{.cpp}
            ovrSession session;
            ovrGraphicsLuid luid;
            ovrResult result = ovr_Create(&session, &luid);
            if(OVR_FAILURE(result))
               ...
        \endcode
    
    \see ovr_Destroy
    """
    pSession = Session()
    pLuid = GraphicsLuid()
    result = libovr.ovr_Create(byref(pSession), byref(pLuid))
    _checkResult(result, "create")
    return pSession, pLuid


# Translated from header file OVR_CAPI.h line 1447
libovr.ovr_Destroy.restype = None
libovr.ovr_Destroy.argtypes = [Session]
def destroy(session):
    """
    Destroys the session.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \see ovr_Create
    """
    libovr.ovr_Destroy(session)


# Translated from header file OVR_CAPI.h line 1456
class SessionStatus(Structure):
    """
    Specifies status information for the current session.
    
    \see ovr_GetSessionStatus
    """
    _fields_ = [
        ("IsVisible", Bool),  #< True if the process has VR focus and thus is visible in the HMD.
        ("HmdPresent", Bool),  #< True if an HMD is present.
        ("HmdMounted", Bool),  #< True if the HMD is on the user's head.
        ("DisplayLost", Bool),  #< True if the session is in a display-lost state. See ovr_SubmitFrame.
        ("ShouldQuit", Bool),  #< True if the application should initiate shutdown.
        ("ShouldRecenter", Bool),  #< True if UX has requested re-centering. Must call
        #< ovr_ClearShouldRecenterFlag, ovr_RecenterTrackingOrigin or
        #< ovr_SpecifyTrackingOrigin
    ]

    def __repr__(self):
        return "ovr.SessionStatus(%s, %s, %s, %s, %s, %s)" % (self.IsVisible, self.HmdPresent, self.HmdMounted, self.DisplayLost, self.ShouldQuit, self.ShouldRecenter)


# Translated from header file OVR_CAPI.h line 1473
libovr.ovr_GetSessionStatus.restype = Result
libovr.ovr_GetSessionStatus.argtypes = [Session, POINTER(SessionStatus)]
def getSessionStatus(session):
    """
    Returns status information for the application.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[out] sessionStatus Provides an ovrSessionStatus that is filled in.
    
    \return Returns an ovrResult indicating success or failure. In the case of
            failure, use ovr_GetLastErrorInfo to get more information.
             Return values include but aren't limited to:
        - ovrSuccess: Completed successfully.
        - ovrError_ServiceConnection: The service connection was lost and the application
           must destroy the session.
    """
    sessionStatus = SessionStatus()
    result = libovr.ovr_GetSessionStatus(session, byref(sessionStatus))
    _checkResult(result, "getSessionStatus")
    return sessionStatus


# Translated from header file OVR_CAPI.h line 1501
libovr.ovr_SetTrackingOriginType.restype = Result
libovr.ovr_SetTrackingOriginType.argtypes = [Session, TrackingOrigin]
def setTrackingOriginType(session, origin):
    """
    Sets the tracking origin type
    
    When the tracking origin is changed, all of the calls that either provide
    or accept ovrPosef will use the new tracking origin provided.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] origin Specifies an ovrTrackingOrigin to be used for all ovrPosef
    
    \return Returns an ovrResult indicating success or failure. In the case of failure, use
            ovr_GetLastErrorInfo to get more information.
    
    \see ovrTrackingOrigin, ovr_GetTrackingOriginType
    """
    result = libovr.ovr_SetTrackingOriginType(session, origin)
    _checkResult(result, "setTrackingOriginType")
    return result


# Translated from header file OVR_CAPI.h line 1516
libovr.ovr_GetTrackingOriginType.restype = TrackingOrigin
libovr.ovr_GetTrackingOriginType.argtypes = [Session]
def getTrackingOriginType(session):
    """
    Gets the tracking origin state
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    
    \return Returns the ovrTrackingOrigin that was either set by default, or previous set by the
    application.
    
    \see ovrTrackingOrigin, ovr_SetTrackingOriginType
    """
    result = libovr.ovr_GetTrackingOriginType(session)
    return result


# Translated from header file OVR_CAPI.h line 1526
libovr.ovr_RecenterTrackingOrigin.restype = Result
libovr.ovr_RecenterTrackingOrigin.argtypes = [Session]
def recenterTrackingOrigin(session):
    """
    Re-centers the sensor position and orientation.
    
    This resets the (x,y,z) positional components and the yaw orientation component of the
    tracking space for the HMD and controllers using the HMD's current tracking pose.
    If the caller requires some tweaks on top of the HMD's current tracking pose, consider using
    ovr_SpecifyTrackingOrigin instead.
    
    The roll and pitch orientation components are always determined by gravity and cannot
    be redefined. All future tracking will report values relative to this new reference position.
    If you are using ovrTrackerPoses then you will need to call ovr_GetTrackerPose after
    this, because the sensor position(s) will change as a result of this.
    
    The headset cannot be facing vertically upward or downward but rather must be roughly
    level otherwise this function will fail with ovrError_InvalidHeadsetOrientation.
    
    For more info, see the notes on each ovrTrackingOrigin enumeration to understand how
    recenter will vary slightly in its behavior based on the current ovrTrackingOrigin setting.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    
    \return Returns an ovrResult indicating success or failure. In the case of failure, use
            ovr_GetLastErrorInfo to get more information. Return values include but aren't limited
            to:
        - ovrSuccess: Completed successfully.
        - ovrError_InvalidHeadsetOrientation: The headset was facing an invalid direction when
          attempting recentering, such as facing vertically.
    
    \see ovrTrackingOrigin, ovr_GetTrackerPose, ovr_SpecifyTrackingOrigin
    """
    result = libovr.ovr_RecenterTrackingOrigin(session)
    _checkResult(result, "recenterTrackingOrigin")
    return result


# Translated from header file OVR_CAPI.h line 1557
libovr.ovr_SpecifyTrackingOrigin.restype = Result
libovr.ovr_SpecifyTrackingOrigin.argtypes = [Session, Posef]
def specifyTrackingOrigin(session, originPose):
    """
    Allows manually tweaking the sensor position and orientation.
    
    This function is similar to ovr_RecenterTrackingOrigin in that it modifies the
    (x,y,z) positional components and the yaw orientation component of the tracking space for
    the HMD and controllers.
    
    While ovr_RecenterTrackingOrigin resets the tracking origin in reference to the HMD's
    current pose, ovr_SpecifyTrackingOrigin allows the caller to explicitly specify a transform
    for the tracking origin. This transform is expected to be an offset to the most recent
    recentered origin, so calling this function repeatedly with the same originPose will keep
    nudging the recentered origin in that direction.
    
    There are several use cases for this function. For example, if the application decides to
    limit the yaw, or translation of the recentered pose instead of directly using the HMD pose
    the application can query the current tracking state via ovr_GetTrackingState, and apply
    some limitations to the HMD pose because feeding this pose back into this function.
    Similarly, this can be used to "adjust the seating position" incrementally in apps that
    feature seated experiences such as cockpit-based games.
    
    This function can emulate ovr_RecenterTrackingOrigin as such:
        ovrTrackingState ts = ovr_GetTrackingState(session, 0.0, ovrFalse);
        ovr_SpecifyTrackingOrigin(session, ts.HeadPose.ThePose);
    
    The roll and pitch orientation components are determined by gravity and cannot be redefined.
    If you are using ovrTrackerPoses then you will need to call ovr_GetTrackerPose after
    this, because the sensor position(s) will change as a result of this.
    
    For more info, see the notes on each ovrTrackingOrigin enumeration to understand how
    recenter will vary slightly in its behavior based on the current ovrTrackingOrigin setting.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] originPose Specifies a pose that will be used to transform the current tracking
    origin.
    
    \return Returns an ovrResult indicating success or failure. In the case of failure, use
            ovr_GetLastErrorInfo to get more information. Return values include but aren't limited
            to:
        - ovrSuccess: Completed successfully.
        - ovrError_InvalidParameter: The heading direction in originPose was invalid,
            such as facing vertically. This can happen if the caller is directly feeding the pose
            of a position-tracked device such as an HMD or controller into this function.
    
    \see ovrTrackingOrigin, ovr_GetTrackerPose, ovr_RecenterTrackingOrigin
    """
    result = libovr.ovr_SpecifyTrackingOrigin(session, originPose)
    _checkResult(result, "specifyTrackingOrigin")
    return result


# Translated from header file OVR_CAPI.h line 1603
libovr.ovr_ClearShouldRecenterFlag.restype = None
libovr.ovr_ClearShouldRecenterFlag.argtypes = [Session]
def clearShouldRecenterFlag(session):
    """
    Clears the ShouldRecenter status bit in ovrSessionStatus.
    
    Clears the ShouldRecenter status bit in ovrSessionStatus, allowing further recenter requests to
    be detected. Since this is automatically done by ovr_RecenterTrackingOrigin and
    ovr_SpecifyTrackingOrigin, this function only needs to be called when application is doing
    its own re-centering logic.
    """
    libovr.ovr_ClearShouldRecenterFlag(session)


# Translated from header file OVR_CAPI.h line 1611
libovr.ovr_GetTrackingState.restype = TrackingState
libovr.ovr_GetTrackingState.argtypes = [Session, c_double, Bool]
def getTrackingState(session, absTime, latencyMarker):
    """
    Returns tracking state reading based on the specified absolute system time.
    
    Pass an absTime value of 0.0 to request the most recent sensor reading. In this case
    both PredictedPose and SamplePose will have the same value.
    
    This may also be used for more refined timing of front buffer rendering logic, and so on.
    This may be called by multiple threads.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] absTime Specifies the absolute future time to predict the return
               ovrTrackingState value. Use 0 to request the most recent tracking state.
    \param[in] latencyMarker Specifies that this call is the point in time where
               the "App-to-Mid-Photon" latency timer starts from. If a given ovrLayer
               provides "SensorSampleTime", that will override the value stored here.
    \return Returns the ovrTrackingState that is predicted for the given absTime.
    
    \see ovrTrackingState, ovr_GetEyePoses, ovr_GetTimeInSeconds
    """
    result = libovr.ovr_GetTrackingState(session, absTime, toOvrBool(latencyMarker))
    return result


# Translated from header file OVR_CAPI.h line 1632
libovr.ovr_GetDevicePoses.restype = Result
libovr.ovr_GetDevicePoses.argtypes = [Session, POINTER(TrackedDeviceType), c_int, c_double, POINTER(PoseStatef)]
def getDevicePoses(session, deviceTypes, absTime):
    """
    Returns an array of poses, where each pose matches a device type provided by the deviceTypes
    array parameter.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] deviceTypes Array of device types to query for their poses.
    \param[in] deviceCount Number of queried poses. This number must match the length of the
    outDevicePoses and deviceTypes array.
    \param[in] absTime Specifies the absolute future time to predict the return
                ovrTrackingState value. Use 0 to request the most recent tracking state.
    \param[out] outDevicePoses Array of poses, one for each device type in deviceTypes arrays.
    
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and
            true upon success.
    """
    deviceCount = len(deviceTypes)
    outDevicePoses = (PoseStatef * deviceCount)()
    deviceTypes = (TrackedDeviceType * deviceCount)(*[deviceType for deviceType in deviceTypes])
    result = libovr.ovr_GetDevicePoses(session, byref(deviceTypes), deviceCount, absTime, byref(outDevicePoses))
    if result == Error_LostTracking:
        return None
    _checkResult(result, "getDevicePoses")
    return outDevicePoses


# Translated from header file OVR_CAPI.h line 1655
libovr.ovr_GetTrackerPose.restype = TrackerPose
libovr.ovr_GetTrackerPose.argtypes = [Session, c_uint]
def getTrackerPose(session, trackerPoseIndex):
    """
    Returns the ovrTrackerPose for the given attached tracker.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] trackerPoseIndex Index of the tracker being requested.
    
    \return Returns the requested ovrTrackerPose. An empty ovrTrackerPose will be returned if
    trackerPoseIndex is out of range.
    
    \see ovr_GetTrackerCount
    """
    result = libovr.ovr_GetTrackerPose(session, trackerPoseIndex)
    return result


# Translated from header file OVR_CAPI.h line 1668
libovr.ovr_GetInputState.restype = Result
libovr.ovr_GetInputState.argtypes = [Session, ControllerType, POINTER(InputState)]
def getInputState(session, controllerType):
    """
    Returns the most recent input state for controllers, without positional tracking info.
    
    \param[out] inputState Input state that will be filled in.
    \param[in] ovrControllerType Specifies which controller the input will be returned for.
    \return Returns ovrSuccess if the new state was successfully obtained.
    
    \see ovrControllerType
    """
    inputState = InputState()
    result = libovr.ovr_GetInputState(session, controllerType, byref(inputState))
    _checkResult(result, "getInputState")
    return inputState


# Translated from header file OVR_CAPI.h line 1679
libovr.ovr_GetConnectedControllerTypes.restype = c_uint
libovr.ovr_GetConnectedControllerTypes.argtypes = [Session]
def getConnectedControllerTypes(session):
    """
    Returns controller types connected to the system OR'ed together.
    
    \return A bitmask of ovrControllerTypes connected to the system.
    
    \see ovrControllerType
    """
    result = libovr.ovr_GetConnectedControllerTypes(session)
    return result


# Translated from header file OVR_CAPI.h line 1687
libovr.ovr_GetTouchHapticsDesc.restype = TouchHapticsDesc
libovr.ovr_GetTouchHapticsDesc.argtypes = [Session, ControllerType]
def getTouchHapticsDesc(session, controllerType):
    """
    Gets information about Haptics engine for the specified Touch controller.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] controllerType The controller to retrieve the information from.
    
    \return Returns an ovrTouchHapticsDesc.
    """
    result = libovr.ovr_GetTouchHapticsDesc(session, controllerType)
    return result


# Translated from header file OVR_CAPI.h line 1697
libovr.ovr_SetControllerVibration.restype = Result
libovr.ovr_SetControllerVibration.argtypes = [Session, ControllerType, c_float, c_float]
def setControllerVibration(session, controllerType, frequency, amplitude):
    """
    Sets constant vibration (with specified frequency and amplitude) to a controller.
    Note: ovr_SetControllerVibration cannot be used interchangeably with
    ovr_SubmitControllerVibration.
    
    This method should be called periodically, vibration lasts for a maximum of 2.5 seconds.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] controllerType The controller to set the vibration to.
    \param[in] frequency Vibration frequency. Supported values are: 0.0 (disabled), 0.5 and 1.0. Non
    valid values will be clamped.
    \param[in] amplitude Vibration amplitude in the [0.0, 1.0] range.
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: The call succeeded and a result was returned.
        - ovrSuccess_DeviceUnavailable: The call succeeded but the device referred to by
        controllerType is not available.
    """
    result = libovr.ovr_SetControllerVibration(session, controllerType, frequency, amplitude)
    _checkResult(result, "setControllerVibration")
    return result


# Translated from header file OVR_CAPI.h line 1721
libovr.ovr_SubmitControllerVibration.restype = Result
libovr.ovr_SubmitControllerVibration.argtypes = [Session, ControllerType, POINTER(HapticsBuffer)]
def submitControllerVibration(session, controllerType, buffer_):
    """
    Submits a Haptics buffer (used for vibration) to Touch (only) controllers.
    Note: ovr_SubmitControllerVibration cannot be used interchangeably with
    ovr_SetControllerVibration.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] controllerType Controller where the Haptics buffer will be played.
    \param[in] buffer Haptics buffer containing amplitude samples to be played.
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: The call succeeded and a result was returned.
        - ovrSuccess_DeviceUnavailable: The call succeeded but the device referred to by
        controllerType is not available.
    
    \see ovrHapticsBuffer
    """
    result = libovr.ovr_SubmitControllerVibration(session, controllerType, byref(buffer_))
    _checkResult(result, "submitControllerVibration")
    return result


# Translated from header file OVR_CAPI.h line 1742
libovr.ovr_GetControllerVibrationState.restype = Result
libovr.ovr_GetControllerVibrationState.argtypes = [Session, ControllerType, POINTER(HapticsPlaybackState)]
def getControllerVibrationState(session, controllerType, outState):
    """
    Gets the Haptics engine playback state of a specific Touch controller.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] controllerType Controller where the Haptics buffer wil be played.
    \param[in] outState State of the haptics engine.
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: The call succeeded and a result was returned.
        - ovrSuccess_DeviceUnavailable: The call succeeded but the device referred to by
        controllerType is not available.
    
    \see ovrHapticsPlaybackState
    """
    result = libovr.ovr_GetControllerVibrationState(session, controllerType, byref(outState))
    _checkResult(result, "getControllerVibrationState")
    return result


# Translated from header file OVR_CAPI.h line 1761
libovr.ovr_TestBoundary.restype = Result
libovr.ovr_TestBoundary.argtypes = [Session, TrackedDeviceType, BoundaryType, POINTER(BoundaryTestResult)]
def testBoundary(session, deviceBitmask, boundaryType):
    """
    Tests collision/proximity of position tracked devices (e.g. HMD and/or Touch) against the
    Boundary System.
    Note: this method is similar to ovr_BoundaryTestPoint but can be more precise as it may take
    into account device acceleration/momentum.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] deviceBitmask Bitmask of one or more tracked devices to test.
    \param[in] boundaryType Must be either ovrBoundary_Outer or ovrBoundary_PlayArea.
    \param[out] outTestResult Result of collision/proximity test, contains information such as
    distance and closest point.
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: The call succeeded and a result was returned.
        - ovrSuccess_BoundaryInvalid: The call succeeded but the result is not a valid boundary due
        to not being set up.
        - ovrSuccess_DeviceUnavailable: The call succeeded but the device referred to by
        deviceBitmask is not available.
    
    \see ovrBoundaryTestResult
    """
    outTestResult = BoundaryTestResult()
    result = libovr.ovr_TestBoundary(session, deviceBitmask, boundaryType, byref(outTestResult))
    _checkResult(result, "testBoundary")
    return outTestResult


# Translated from header file OVR_CAPI.h line 1788
libovr.ovr_TestBoundaryPoint.restype = Result
libovr.ovr_TestBoundaryPoint.argtypes = [Session, POINTER(Vector3f), BoundaryType, POINTER(BoundaryTestResult)]
def testBoundaryPoint(session, point, singleBoundaryType):
    """
    Tests collision/proximity of a 3D point against the Boundary System.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] point 3D point to test.
    \param[in] singleBoundaryType Must be either ovrBoundary_Outer or ovrBoundary_PlayArea to test
    against
    \param[out] outTestResult Result of collision/proximity test, contains information such as
    distance and closest point.
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: The call succeeded and a result was returned.
        - ovrSuccess_BoundaryInvalid: The call succeeded but the result is not a valid boundary due
        to not being set up.
    
    \see ovrBoundaryTestResult
    """
    outTestResult = BoundaryTestResult()
    result = libovr.ovr_TestBoundaryPoint(session, byref(point), singleBoundaryType, byref(outTestResult))
    _checkResult(result, "testBoundaryPoint")
    return outTestResult


# Translated from header file OVR_CAPI.h line 1811
libovr.ovr_SetBoundaryLookAndFeel.restype = Result
libovr.ovr_SetBoundaryLookAndFeel.argtypes = [Session, POINTER(BoundaryLookAndFeel)]
def setBoundaryLookAndFeel(session, lookAndFeel):
    """
    Sets the look and feel of the Boundary System.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] lookAndFeel Look and feel parameters.
    \return Returns ovrSuccess upon success.
    \see ovrBoundaryLookAndFeel
    """
    result = libovr.ovr_SetBoundaryLookAndFeel(session, byref(lookAndFeel))
    _checkResult(result, "setBoundaryLookAndFeel")
    return result


# Translated from header file OVR_CAPI.h line 1821
libovr.ovr_ResetBoundaryLookAndFeel.restype = Result
libovr.ovr_ResetBoundaryLookAndFeel.argtypes = [Session]
def resetBoundaryLookAndFeel(session):
    """
    Resets the look and feel of the Boundary System to its default state.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \return Returns ovrSuccess upon success.
    \see ovrBoundaryLookAndFeel
    """
    result = libovr.ovr_ResetBoundaryLookAndFeel(session)
    _checkResult(result, "resetBoundaryLookAndFeel")
    return result


# Translated from header file OVR_CAPI.h line 1829
libovr.ovr_GetBoundaryGeometry.restype = Result
libovr.ovr_GetBoundaryGeometry.argtypes = [Session, BoundaryType, POINTER(Vector3f), POINTER(c_int)]
def getBoundaryGeometry(session, boundaryType):
    """
    Gets the geometry of the Boundary System's "play area" or "outer boundary" as 3D floor points.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] boundaryType Must be either ovrBoundary_Outer or ovrBoundary_PlayArea.
    \param[out] outFloorPoints Array of 3D points (in clockwise order) defining the boundary at
    floor height (can be NULL to retrieve only the number of points).
    \param[out] outFloorPointsCount Number of 3D points returned in the array.
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: The call succeeded and a result was returned.
        - ovrSuccess_BoundaryInvalid: The call succeeded but the result is not a valid boundary due
        to not being set up.
    """
    outFloorPoints = Vector3f()
    outFloorPointsCount = c_int()
    result = libovr.ovr_GetBoundaryGeometry(session, boundaryType, byref(outFloorPoints), byref(outFloorPointsCount))
    _checkResult(result, "getBoundaryGeometry")
    return outFloorPoints, outFloorPointsCount


# Translated from header file OVR_CAPI.h line 1849
libovr.ovr_GetBoundaryDimensions.restype = Result
libovr.ovr_GetBoundaryDimensions.argtypes = [Session, BoundaryType, POINTER(Vector3f)]
def getBoundaryDimensions(session, boundaryType):
    """
    Gets the dimension of the Boundary System's "play area" or "outer boundary".
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] boundaryType Must be either ovrBoundary_Outer or ovrBoundary_PlayArea.
    \param[out] outDimensions Dimensions of the axis aligned bounding box that encloses the area in
    meters (width, height and length).
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: The call succeeded and a result was returned.
        - ovrSuccess_BoundaryInvalid: The call succeeded but the result is not a valid boundary due
        to not being set up.
    """
    outDimensions = Vector3f()
    result = libovr.ovr_GetBoundaryDimensions(session, boundaryType, byref(outDimensions))
    _checkResult(result, "getBoundaryDimensions")
    return outDimensions


# Translated from header file OVR_CAPI.h line 1867
libovr.ovr_GetBoundaryVisible.restype = Result
libovr.ovr_GetBoundaryVisible.argtypes = [Session, POINTER(Bool)]
def getBoundaryVisible(session):
    """
    Returns if the boundary is currently visible.
    Note: visibility is false if the user has turned off boundaries, otherwise, it's true if
    the app has requested boundaries to be visible or if any tracked device is currently
    triggering it. This may not exactly match rendering due to fade-in and fade-out effects.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[out] outIsVisible ovrTrue, if the boundary is visible.
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: Result was successful and a result was returned.
        - ovrSuccess_BoundaryInvalid: The call succeeded but the result is not a valid boundary due
        to not being set up.
    """
    outIsVisible = Bool()
    result = libovr.ovr_GetBoundaryVisible(session, byref(outIsVisible))
    _checkResult(result, "getBoundaryVisible")
    return outIsVisible


# Translated from header file OVR_CAPI.h line 1882
libovr.ovr_RequestBoundaryVisible.restype = Result
libovr.ovr_RequestBoundaryVisible.argtypes = [Session, Bool]
def requestBoundaryVisible(session, visible):
    """
    Requests boundary to be visible.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] visible forces the outer boundary to be visible. An application can't force it
               to be invisible, but can cancel its request by passing false.
    \return Returns ovrSuccess upon success.
    """
    result = libovr.ovr_RequestBoundaryVisible(session, toOvrBool(visible))
    _checkResult(result, "requestBoundaryVisible")
    return result


# Translated from header file OVR_CAPI.h line 1900
#  Specifies the maximum number of layers supported by ovr_SubmitFrame.
#
#  /see ovr_SubmitFrame
#
MaxLayerCount = 16


# Translated from header file OVR_CAPI.h line 1906
# Describes layer types that can be passed to ovr_SubmitFrame.
# Each layer type has an associated struct, such as ovrLayerEyeFov.
#
# \see ovrLayerHeader
#
LayerType = ENUM_TYPE
# Layer is disabled.
LayerType_Disabled = 0
# Described by ovrLayerEyeFov.
LayerType_EyeFov = 1
# Described by ovrLayerEyeFovDepth.
LayerType_EyeFovDepth = 2
# Described by ovrLayerQuad. Previously called ovrLayerType_QuadInWorld.
LayerType_Quad = 3
# enum 4 used to be ovrLayerType_QuadHeadLocked. Instead, use ovrLayerType_Quad with
# ovrLayerFlag_HeadLocked.
# Described by ovrLayerEyeMatrix.
LayerType_EyeMatrix = 5


# Translated from header file OVR_CAPI.h line 1933
# Identifies flags used by ovrLayerHeader and which are passed to ovr_SubmitFrame.
#
# \see ovrLayerHeader
#
LayerFlags = ENUM_TYPE
# ovrLayerFlag_HighQuality enables 4x anisotropic sampling during the composition of the layer.
# The benefits are mostly visible at the periphery for high-frequency & high-contrast visuals.
# For best results consider combining this flag with an ovrTextureSwapChain that has mipmaps and
# instead of using arbitrary sized textures, prefer texture sizes that are powers-of-two.
# Actual rendered viewport and doesn't necessarily have to fill the whole texture.
LayerFlag_HighQuality = 0x01
# ovrLayerFlag_TextureOriginAtBottomLeft: the opposite is TopLeft.
# Generally this is false for D3D, true for OpenGL.
LayerFlag_TextureOriginAtBottomLeft = 0x02
# Mark this surface as "headlocked", which means it is specified
# relative to the HMD and moves with it, rather than being specified
# relative to sensor/torso space and remaining still while the head moves.
# What used to be ovrLayerType_QuadHeadLocked is now ovrLayerType_Quad plus this flag.
# However the flag can be applied to any layer type to achieve a similar effect.
LayerFlag_HeadLocked = 0x04


# Translated from header file OVR_CAPI.h line 1958
class LayerHeader(Structure):
    """
    Defines properties shared by all ovrLayer structs, such as ovrLayerEyeFov.
    
    ovrLayerHeader is used as a base member in these larger structs.
    This struct cannot be used by itself except for the case that Type is ovrLayerType_Disabled.
    
    \see ovrLayerType, ovrLayerFlags
    """
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        ("Type", LayerType),  #< Described by ovrLayerType.
        ("Flags", c_uint),  #< Described by ovrLayerFlags.
        ("Reserved", c_char * 128),
    ]

    def __repr__(self):
        return "ovr.LayerHeader(%s, %s)" % (self.Type, self.Flags)


# Translated from header file OVR_CAPI.h line 1970
class LayerEyeFov(Structure):
    """
    Describes a layer that specifies a monoscopic or stereoscopic view.
    This is the kind of layer that's typically used as layer 0 to ovr_SubmitFrame,
    as it is the kind of layer used to render a 3D stereoscopic view.
    
    Three options exist with respect to mono/stereo texture usage:
       - ColorTexture[0] and ColorTexture[1] contain the left and right stereo renderings,
         respectively.
         Viewport[0] and Viewport[1] refer to ColorTexture[0] and ColorTexture[1], respectively.
       - ColorTexture[0] contains both the left and right renderings, ColorTexture[1] is NULL,
         and Viewport[0] and Viewport[1] refer to sub-rects with ColorTexture[0].
       - ColorTexture[0] contains a single monoscopic rendering, and Viewport[0] and
         Viewport[1] both refer to that rendering.
    
    \see ovrTextureSwapChain, ovr_SubmitFrame
    """
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Header.Type must be ovrLayerType_EyeFov.
        ("Header", LayerHeader), 
        # ovrTextureSwapChains for the left and right eye respectively.
        # The second one of which can be NULL for cases described above.
        ("ColorTexture", TextureSwapChain * Eye_Count), 
        # Specifies the ColorTexture sub-rect UV coordinates.
        # Both Viewport[0] and Viewport[1] must be valid.
        ("Viewport", Recti * Eye_Count), 
        # The viewport field of view.
        ("Fov", FovPort * Eye_Count), 
        # Specifies the position and orientation of each eye view, with position specified in meters.
        # RenderPose will typically be the value returned from ovr_CalcEyePoses,
        # but can be different in special cases if a different head pose is used for rendering.
        ("RenderPose", Posef * Eye_Count), 
        # Specifies the timestamp when the source ovrPosef (used in calculating RenderPose)
        # was sampled from the SDK. Typically retrieved by calling ovr_GetTimeInSeconds
        # around the instant the application calls ovr_GetTrackingState
        # The main purpose for this is to accurately track app tracking latency.
        ("SensorSampleTime", c_double), 
    ]

    def __repr__(self):
        return "ovr.LayerEyeFov(%s, %s, %s, %s, %s, %s)" % (self.Header, self.ColorTexture, self.Viewport, self.Fov, self.RenderPose, self.SensorSampleTime)

class LayerEyeFovDepth(Structure):
    """
    Describes a layer that specifies a monoscopic or stereoscopic view,
    with depth textures in addition to color textures. This is typically used to support
    positional time warp. This struct is the same as ovrLayerEyeFov, but with the addition
    of DepthTexture and ProjectionDesc.
   
    ProjectionDesc can be created using ovrTimewarpProjectionDesc_FromProjection.
   
    Three options exist with respect to mono/stereo texture usage:
       - ColorTexture[0] and ColorTexture[1] contain the left and right stereo renderings,
         respectively.
         Viewport[0] and Viewport[1] refer to ColorTexture[0] and ColorTexture[1], respectively.
       - ColorTexture[0] contains both the left and right renderings, ColorTexture[1] is NULL,
         and Viewport[0] and Viewport[1] refer to sub-rects with ColorTexture[0].
       - ColorTexture[0] contains a single monoscopic rendering, and Viewport[0] and
         Viewport[1] both refer to that rendering.
   
    \see ovrTextureSwapChain, ovr_SubmitFrame
    """
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Header.Type must be ovrLayerType_EyeFovDepth.
        ("Header", LayerHeader),
        # ovrTextureSwapChains for the left and right eye respectively.
        # The second one of which can be NULL for cases described above.
        ("ColorTexture", TextureSwapChain * Eye_Count),
        # Specifies the ColorTexture sub-rect UV coordinates.
        # Both Viewport[0] and Viewport[1] must be valid.
        ("Viewport", Recti * Eye_Count),
        # The viewport field of view.
        ("Fov", FovPort * Eye_Count),
        # Specifies the position and orientation of each eye view, with position specified in meters.
        # RenderPose will typically be the value returned from ovr_CalcEyePoses,
        # but can be different in special cases if a different head pose is used for rendering.
        ("RenderPose", Posef * Eye_Count),
        # Specifies the timestamp when the source ovrPosef (used in calculating RenderPose)
        # was sampled from the SDK. Typically retrieved by calling ovr_GetTimeInSeconds
        # around the instant the application calls ovr_GetTrackingState
        # The main purpose for this is to accurately track app tracking latency.
        ("SensorSampleTime", c_double),
        # Depth texture for depth composition with overlays
        # Must map 1:1 to the ColorTexture.
        ("DepthTexture", TextureSwapChain * Eye_Count),
        # Specifies how to convert DepthTexture information into meters.
        # \see ovrTimewarpProjectionDesc_FromProjection
        ("ProjectionDesc", TimewarpProjectionDesc),
    ]


# Translated from header file OVR_CAPI.h line 2014
class LayerEyeMatrix(Structure):
    """
    Describes a layer that specifies a monoscopic or stereoscopic view.
    This uses a direct 3x4 matrix to map from view space to the UV coordinates.
    It is essentially the same thing as ovrLayerEyeFov but using a much
    lower level. This is mainly to provide compatibility with specific apps.
    Unless the application really requires this flexibility, it is usually better
    to use ovrLayerEyeFov.
    
    Three options exist with respect to mono/stereo texture usage:
       - ColorTexture[0] and ColorTexture[1] contain the left and right stereo renderings,
         respectively.
         Viewport[0] and Viewport[1] refer to ColorTexture[0] and ColorTexture[1], respectively.
       - ColorTexture[0] contains both the left and right renderings, ColorTexture[1] is NULL,
         and Viewport[0] and Viewport[1] refer to sub-rects with ColorTexture[0].
       - ColorTexture[0] contains a single monoscopic rendering, and Viewport[0] and
         Viewport[1] both refer to that rendering.
    
    \see ovrTextureSwapChain, ovr_SubmitFrame
    """
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Header.Type must be ovrLayerType_EyeMatrix.
        ("Header", LayerHeader), 
        # ovrTextureSwapChains for the left and right eye respectively.
        # The second one of which can be NULL for cases described above.
        ("ColorTexture", TextureSwapChain * Eye_Count), 
        # Specifies the ColorTexture sub-rect UV coordinates.
        # Both Viewport[0] and Viewport[1] must be valid.
        ("Viewport", Recti * Eye_Count), 
        # Specifies the position and orientation of each eye view, with position specified in meters.
        # RenderPose will typically be the value returned from ovr_CalcEyePoses,
        # but can be different in special cases if a different head pose is used for rendering.
        ("RenderPose", Posef * Eye_Count), 
        # Specifies the mapping from a view-space vector
        # to a UV coordinate on the textures given above.
        # P = (x,y,z,1)*Matrix
        # TexU  = P.x/P.z
        # TexV  = P.y/P.z
        ("Matrix", Matrix4f * Eye_Count), 
        # Specifies the timestamp when the source ovrPosef (used in calculating RenderPose)
        # was sampled from the SDK. Typically retrieved by calling ovr_GetTimeInSeconds
        # around the instant the application calls ovr_GetTrackingState
        # The main purpose for this is to accurately track app tracking latency.
        ("SensorSampleTime", c_double), 
    ]

    def __repr__(self):
        return "ovr.LayerEyeMatrix(%s, %s, %s, %s, %s, %s)" % (self.Header, self.ColorTexture, self.Viewport, self.RenderPose, self.Matrix, self.SensorSampleTime)


# Translated from header file OVR_CAPI.h line 2064
class LayerQuad(Structure):
    """
    Describes a layer of Quad type, which is a single quad in world or viewer space.
    It is used for ovrLayerType_Quad. This type of layer represents a single
    object placed in the world and not a stereo view of the world itself.
    
    A typical use of ovrLayerType_Quad is to draw a television screen in a room
    that for some reason is more convenient to draw as a layer than as part of the main
    view in layer 0. For example, it could implement a 3D popup GUI that is drawn at a
    higher resolution than layer 0 to improve fidelity of the GUI.
    
    Quad layers are visible from both sides; they are not back-face culled.
    
    \see ovrTextureSwapChain, ovr_SubmitFrame
    """
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Header.Type must be ovrLayerType_Quad.
        ("Header", LayerHeader), 
        # Contains a single image, never with any stereo view.
        ("ColorTexture", TextureSwapChain), 
        # Specifies the ColorTexture sub-rect UV coordinates.
        ("Viewport", Recti), 
        # Specifies the orientation and position of the center point of a Quad layer type.
        # The supplied direction is the vector perpendicular to the quad.
        # The position is in real-world meters (not the application's virtual world,
        # the physical world the user is in) and is relative to the "zero" position
        # set by ovr_RecenterTrackingOrigin unless the ovrLayerFlag_HeadLocked flag is used.
        ("QuadPoseCenter", Posef), 
        # Width and height (respectively) of the quad in meters.
        ("QuadSize", Vector2f), 
    ]

    def __repr__(self):
        return "ovr.LayerQuad(%s, %s, %s, %s, %s)" % (self.Header, self.ColorTexture, self.Viewport, self.QuadPoseCenter, self.QuadSize)


# Translated from header file OVR_CAPI.h line 2101
class Layer_Union(Union):
    """
    Union that combines ovrLayer types in a way that allows them
    to be used in a polymorphic way.
    """
    _fields_ = [
        ("Header", LayerHeader), 
        ("EyeFov", LayerEyeFov), 
        ("Quad", LayerQuad), 
    ]

    def __repr__(self):
        return "ovr.Layer_Union(%s, %s, %s)" % (self.Header, self.EyeFov, self.Quad)


# Translated from header file OVR_CAPI.h line 2128
libovr.ovr_GetTextureSwapChainLength.restype = Result
libovr.ovr_GetTextureSwapChainLength.argtypes = [Session, TextureSwapChain, POINTER(c_int)]
def getTextureSwapChainLength(session, chain):
    """
    Gets the number of buffers in an ovrTextureSwapChain.
    
    \param[in]  session Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  chain Specifies the ovrTextureSwapChain for which the length should be retrieved.
    \param[out] out_Length Returns the number of buffers in the specified chain.
    
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error.
    
    \see ovr_CreateTextureSwapChainDX, ovr_CreateTextureSwapChainGL
    """
    out_Length = c_int()
    result = libovr.ovr_GetTextureSwapChainLength(session, chain, byref(out_Length))
    _checkResult(result, "getTextureSwapChainLength")
    return out_Length


# Translated from header file OVR_CAPI.h line 2141
libovr.ovr_GetTextureSwapChainCurrentIndex.restype = Result
libovr.ovr_GetTextureSwapChainCurrentIndex.argtypes = [Session, TextureSwapChain, POINTER(c_int)]
def getTextureSwapChainCurrentIndex(session, chain):
    """
    Gets the current index in an ovrTextureSwapChain.
    
    \param[in]  session Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  chain Specifies the ovrTextureSwapChain for which the index should be retrieved.
    \param[out] out_Index Returns the current (free) index in specified chain.
    
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error.
    
    \see ovr_CreateTextureSwapChainDX, ovr_CreateTextureSwapChainGL
    """
    out_Index = c_int()
    result = libovr.ovr_GetTextureSwapChainCurrentIndex(session, chain, byref(out_Index))
    _checkResult(result, "getTextureSwapChainCurrentIndex")
    return out_Index


# Translated from header file OVR_CAPI.h line 2154
libovr.ovr_GetTextureSwapChainDesc.restype = Result
libovr.ovr_GetTextureSwapChainDesc.argtypes = [Session, TextureSwapChain, POINTER(TextureSwapChainDesc)]
def getTextureSwapChainDesc(session, chain):
    """
    Gets the description of the buffers in an ovrTextureSwapChain
    
    \param[in]  session Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  chain Specifies the ovrTextureSwapChain for which the description
                      should be retrieved.
    \param[out] out_Desc Returns the description of the specified chain.
    
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error.
    
    \see ovr_CreateTextureSwapChainDX, ovr_CreateTextureSwapChainGL
    """
    out_Desc = TextureSwapChainDesc()
    result = libovr.ovr_GetTextureSwapChainDesc(session, chain, byref(out_Desc))
    _checkResult(result, "getTextureSwapChainDesc")
    return out_Desc


# Translated from header file OVR_CAPI.h line 2171
libovr.ovr_CommitTextureSwapChain.restype = Result
libovr.ovr_CommitTextureSwapChain.argtypes = [Session, TextureSwapChain]
def commitTextureSwapChain(session, chain):
    """
    Commits any pending changes to an ovrTextureSwapChain, and advances its current index
    
    \param[in]  session Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  chain Specifies the ovrTextureSwapChain to commit.
    
    \note When Commit is called, the texture at the current index is considered ready for use by the
    runtime, and further writes to it should be avoided. The swap chain's current index is advanced,
    providing there's room in the chain. The next time the SDK dereferences this texture swap chain,
    it will synchronize with the app's graphics context and pick up the submitted index, opening up
    room in the swap chain for further commits.
    
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error.
            Failures include but aren't limited to:
        - ovrError_TextureSwapChainFull: ovr_CommitTextureSwapChain was called too many times on a
            texture swapchain without calling submit to use the chain.
    
    \see ovr_CreateTextureSwapChainDX, ovr_CreateTextureSwapChainGL
    """
    result = libovr.ovr_CommitTextureSwapChain(session, chain)
    _checkResult(result, "commitTextureSwapChain")
    return result


# Translated from header file OVR_CAPI.h line 2192
libovr.ovr_DestroyTextureSwapChain.restype = None
libovr.ovr_DestroyTextureSwapChain.argtypes = [Session, TextureSwapChain]
def destroyTextureSwapChain(session, chain):
    """
    Destroys an ovrTextureSwapChain and frees all the resources associated with it.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] chain Specifies the ovrTextureSwapChain to destroy. If it is NULL then
               this function has no effect.
    
    \see ovr_CreateTextureSwapChainDX, ovr_CreateTextureSwapChainGL
    """
    libovr.ovr_DestroyTextureSwapChain(session, chain)


# Translated from header file OVR_CAPI.h line 2207
libovr.ovr_DestroyMirrorTexture.restype = None
libovr.ovr_DestroyMirrorTexture.argtypes = [Session, MirrorTexture]
def destroyMirrorTexture(session, mirrorTexture):
    """
    Destroys a mirror texture previously created by one of the mirror texture creation functions.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] mirrorTexture Specifies the ovrTexture to destroy. If it is NULL then
               this function has no effect.
    
    \see ovr_CreateMirrorTextureDX, ovr_CreateMirrorTextureGL
    """
    libovr.ovr_DestroyMirrorTexture(session, mirrorTexture)


# Translated from header file OVR_CAPI.h line 2218
libovr.ovr_GetFovTextureSize.restype = Sizei
libovr.ovr_GetFovTextureSize.argtypes = [Session, EyeType, FovPort, c_float]
def getFovTextureSize(session, eye, fov, pixelsPerDisplayPixel):
    """
    Calculates the recommended viewport size for rendering a given eye within the HMD
    with a given FOV cone.
    
    Higher FOV will generally require larger textures to maintain quality.
    Apps packing multiple eye views together on the same texture should ensure there are
    at least 8 pixels of padding between them to prevent texture filtering and chromatic
    aberration causing images to leak between the two eye views.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] eye Specifies which eye (left or right) to calculate for.
    \param[in] fov Specifies the ovrFovPort to use.
    \param[in] pixelsPerDisplayPixel Specifies the ratio of the number of render target pixels
               to display pixels at the center of distortion. 1.0 is the default value. Lower
               values can improve performance, higher values give improved quality.
    
    <b>Example code</b>
        \code{.cpp}
            ovrHmdDesc hmdDesc = ovr_GetHmdDesc(session);
            ovrSizei eyeSizeLeft  = ovr_GetFovTextureSize(session, ovrEye_Left,
            hmdDesc.DefaultEyeFov[ovrEye_Left],  1.0f);
            ovrSizei eyeSizeRight = ovr_GetFovTextureSize(session, ovrEye_Right,
            hmdDesc.DefaultEyeFov[ovrEye_Right], 1.0f);
        \endcode
    
    \return Returns the texture width and height size.
    """
    result = libovr.ovr_GetFovTextureSize(session, eye, fov, pixelsPerDisplayPixel)
    return result


# Translated from header file OVR_CAPI.h line 2251
libovr.ovr_GetRenderDesc2.restype = EyeRenderDesc
libovr.ovr_GetRenderDesc2.argtypes = [Session, EyeType, FovPort]
def getRenderDesc(session, eyeType, fov):
    """
    Computes the distortion viewport, view adjust, and other rendering parameters for
    the specified eye.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] eyeType Specifies which eye (left or right) for which to perform calculations.
    \param[in] fov Specifies the ovrFovPort to use.
    
    \return Returns the computed ovrEyeRenderDesc for the given eyeType and field of view.
    
    \see ovrEyeRenderDesc
    """
    result = libovr.ovr_GetRenderDesc2(session, eyeType, fov)
    return result


libovr.ovr_WaitToBeginFrame.restype = Result
libovr.ovr_WaitToBeginFrame.argtypes = [Session, c_longlong]
def waitToBeginFrame(session, frameIndex):
    """
    Waits until surfaces are available and it is time to begin rendering the frame.  Must be
    called before ovr_BeginFrame, but not necessarily from the same thread.

    \param[in] session Specifies an ovrSession previously returned by ovr_Create.

    \param[in] frameIndex Specifies the targeted application frame index.

    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: command completed successfully.
        - ovrSuccess_NotVisible: rendering of a previous frame completed successfully but was not
          displayed on the HMD, usually because another application currently has ownership of the
          HMD. Applications receiving this result should stop rendering new content and call
          ovr_GetSessionStatus to detect visibility.
        - ovrError_DisplayLost: The session has become invalid (such as due to a device removal)
          and the shared resources need to be released (ovr_DestroyTextureSwapChain), the session
          needs to destroyed (ovr_Destroy) and recreated (ovr_Create), and new resources need to be
          created (ovr_CreateTextureSwapChainXXX). The application's existing private graphics
          resources do not need to be recreated unless the new ovr_Create call returns a different
          GraphicsLuid.

    \see ovr_BeginFrame, ovr_EndFrame, ovr_GetSessionStatus
    """
    result = libovr.ovr_WaitToBeginFrame(session, frameIndex)
    _checkResult(result, "waitToBeginFrame")
    return result


libovr.ovr_BeginFrame.restype = Result
libovr.ovr_BeginFrame.argtypes = [Session, c_longlong]
def beginFrame(session, frameIndex):
    """
    Called from render thread before application begins rendering.  Must be called after
    ovr_WaitToBeginFrame and before ovr_EndFrame, but not necessarily from the same threads.

    \param[in] session Specifies an ovrSession previously returned by ovr_Create.

    \param[in] frameIndex Specifies the targeted application frame index.  It must match what was
           passed to ovr_WaitToBeginFrame.

    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: command completed successfully.
        - ovrError_DisplayLost: The session has become invalid (such as due to a device removal)
          and the shared resources need to be released (ovr_DestroyTextureSwapChain), the session
          needs to destroyed (ovr_Destroy) and recreated (ovr_Create), and new resources need to be
          created (ovr_CreateTextureSwapChainXXX). The application's existing private graphics
          resources do not need to be recreated unless the new ovr_Create call returns a different
          GraphicsLuid.

    \see ovr_WaitToBeginFrame, ovr_EndFrame
    """
    result = libovr.ovr_BeginFrame(session, frameIndex)
    return result


libovr.ovr_EndFrame.restype = Result
libovr.ovr_EndFrame.argtypes = [Session, c_longlong, POINTER(ViewScaleDesc), POINTER(POINTER(LayerHeader)), c_uint]
def endFrame(session, frameIndex, viewScaleDesc, layerPtrList):
    """
    Called from render thread after application has finished rendering.  Must be called after
    ovr_BeginFrame, but not necessarily from the same thread.  Submits layers for distortion and
    display, which will happen asynchronously.

    \param[in] session Specifies an ovrSession previously returned by ovr_Create.

    \param[in] frameIndex Specifies the targeted application frame index.  It must match what was
           passed to ovr_BeginFrame.

    \param[in] viewScaleDesc Provides additional information needed only if layerPtrList contains
           an ovrLayerType_Quad. If NULL, a default version is used based on the current
           configuration and a 1.0 world scale.

    \param[in] layerPtrList Specifies a list of ovrLayer pointers, which can include NULL entries to
           indicate that any previously shown layer at that index is to not be displayed.
           Each layer header must be a part of a layer structure such as ovrLayerEyeFov or
           ovrLayerQuad, with Header.Type identifying its type. A NULL layerPtrList entry in the
           array indicates the absence of the given layer.

    \param[in] layerCount Indicates the number of valid elements in layerPtrList. The maximum
           supported layerCount is not currently specified, but may be specified in a future
           version.

    - Layers are drawn in the order they are specified in the array, regardless of the layer type.

    - Layers are not remembered between successive calls to ovr_EndFrame. A layer must be
      specified in every call to ovr_EndFrame or it won't be displayed.

    - If a layerPtrList entry that was specified in a previous call to ovr_EndFrame is
      passed as NULL or is of type ovrLayerType_Disabled, that layer is no longer displayed.

    - A layerPtrList entry can be of any layer type and multiple entries of the same layer type
      are allowed. No layerPtrList entry may be duplicated (i.e. the same pointer as an earlier
      entry).

    <b>Example code</b>
        \code{.cpp}
            ovrLayerEyeFov  layer0;
            ovrLayerQuad    layer1;
              ...
            ovrLayerHeader* layers[2] = { &layer0.Header, &layer1.Header };
            ovrResult result = ovr_EndFrame(session, frameIndex, nullptr, layers, 2);
        \endcode

    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: rendering completed successfully.
        - ovrError_DisplayLost: The session has become invalid (such as due to a device removal)
          and the shared resources need to be released (ovr_DestroyTextureSwapChain), the session
          needs to destroyed (ovr_Destroy) and recreated (ovr_Create), and new resources need to be
          created (ovr_CreateTextureSwapChainXXX). The application's existing private graphics
          resources do not need to be recreated unless the new ovr_Create call returns a different
          GraphicsLuid.
        - ovrError_TextureSwapChainInvalid: The ovrTextureSwapChain is in an incomplete or
          inconsistent state. Ensure ovr_CommitTextureSwapChain was called at least once first.

    \see ovr_WaitToBeginFrame, ovr_BeginFrame, ovrViewScaleDesc, ovrLayerHeader
    """
    layerCount = len(layerPtrList)
    layerPtrList = (POINTER(LayerHeader) * layerCount)(*[ctypes.pointer(i) for i in layerPtrList])
    result = libovr.ovr_EndFrame(session, frameIndex, byref(viewScaleDesc), byref(layerPtrList), layerCount)
    _checkResult(result, "endFrame")
    return result


# Translated from header file OVR_CAPI.h line 2265
libovr.ovr_SubmitFrame2.restype = Result
libovr.ovr_SubmitFrame2.argtypes = [Session, c_longlong, POINTER(ViewScaleDesc), POINTER(POINTER(LayerHeader)), c_uint]
def submitFrame(session, frameIndex, viewScaleDesc, layerPtrList):
    """
    Submits layers for distortion and display.
    
    ovr_SubmitFrame triggers distortion and processing which might happen asynchronously.
    The function will return when there is room in the submission queue and surfaces
    are available. Distortion might or might not have completed.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    
    \param[in] frameIndex Specifies the targeted application frame index, or 0 to refer to one frame
           after the last time ovr_SubmitFrame was called.
    
    \param[in] viewScaleDesc Provides additional information needed only if layerPtrList contains
           an ovrLayerType_Quad. If NULL, a default version is used based on the current
           configuration and a 1.0 world scale.
    
    \param[in] layerPtrList Specifies a list of ovrLayer pointers, which can include NULL entries to
           indicate that any previously shown layer at that index is to not be displayed.
           Each layer header must be a part of a layer structure such as ovrLayerEyeFov or
           ovrLayerQuad,
           with Header.Type identifying its type. A NULL layerPtrList entry in the array indicates
           the
           absence of the given layer.
    
    \param[in] layerCount Indicates the number of valid elements in layerPtrList. The maximum
           supported layerCount is not currently specified, but may be specified in a future
           version.
    
    - Layers are drawn in the order they are specified in the array, regardless of the layer type.
    
    - Layers are not remembered between successive calls to ovr_SubmitFrame. A layer must be
      specified in every call to ovr_SubmitFrame or it won't be displayed.
    
    - If a layerPtrList entry that was specified in a previous call to ovr_SubmitFrame is
      passed as NULL or is of type ovrLayerType_Disabled, that layer is no longer displayed.
    
    - A layerPtrList entry can be of any layer type and multiple entries of the same layer type
      are allowed. No layerPtrList entry may be duplicated (i.e. the same pointer as an earlier
      entry).
    
    <b>Example code</b>
        \code{.cpp}
            ovrLayerEyeFov  layer0;
            ovrLayerQuad    layer1;
              ...
            ovrLayerHeader* layers[2] = { &layer0.Header, &layer1.Header };
            ovrResult result = ovr_SubmitFrame(session, frameIndex, nullptr, layers, 2);
        \endcode
    
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success. Return values include but aren't limited to:
        - ovrSuccess: rendering completed successfully.
        - ovrSuccess_NotVisible: rendering completed successfully but was not displayed on the HMD,
          usually because another application currently has ownership of the HMD. Applications
          receiving
          this result should stop rendering new content, but continue to call ovr_SubmitFrame
          periodically
          until it returns a value other than ovrSuccess_NotVisible. Applications should not loop on
          calls to ovr_SubmitFrame in order to detect visibility; instead ovr_GetSessionStatus
          should be used.
          Similarly, appliations should not call ovr_SubmitFrame with zero layers to detect
          visibility.
        - ovrError_DisplayLost: The session has become invalid (such as due to a device removal)
          and the shared resources need to be released (ovr_DestroyTextureSwapChain), the session
          needs to
          destroyed (ovr_Destroy) and recreated (ovr_Create), and new resources need to be created
          (ovr_CreateTextureSwapChainXXX). The application's existing private graphics resources do
          not
          need to be recreated unless the new ovr_Create call returns a different GraphicsLuid.
        - ovrError_TextureSwapChainInvalid: The ovrTextureSwapChain is in an incomplete or
        inconsistent state.
          Ensure ovr_CommitTextureSwapChain was called at least once first.
    
    \see ovr_GetPredictedDisplayTime, ovrViewScaleDesc, ovrLayerHeader, ovr_GetSessionStatus
    """
    layerCount = len(layerPtrList)
    layerPtrList = (POINTER(LayerHeader) * layerCount)(*[ctypes.pointer(i) for i in layerPtrList])
    result = libovr.ovr_SubmitFrame2(session, frameIndex, byref(viewScaleDesc), byref(layerPtrList), layerCount)
    _checkResult(result, "submitFrame")
    return result


# Translated from header file OVR_CAPI.h line 2355
class PerfStatsPerCompositorFrame(Structure):
    """
    
    Contains the performance stats for a given SDK compositor frame
    
    All of the 'int' typed fields can be reset via the ovr_ResetPerfStats call.
    """
    _pack_ = 4
    _fields_ = [
        # Vsync Frame Index - increments with each HMD vertical synchronization signal (i.e. vsync or
        # refresh rate)
        # If the compositor drops a frame, expect this value to increment more than 1 at a time.
        ("HmdVsyncIndex", c_int), 
        #
        # Application stats
        #
        # Index that increments with each successive ovr_SubmitFrame call
        ("AppFrameIndex", c_int), 
        # If the app fails to call ovr_SubmitFrame on time, then expect this value to increment with
        # each missed frame
        ("AppDroppedFrameCount", c_int), 
        # Motion-to-photon latency for the application
        # This value is calculated by either using the SensorSampleTime provided for the ovrLayerEyeFov
        # or if that
        # is not available, then the call to ovr_GetTrackingState which has latencyMarker set to ovrTrue
        ("AppMotionToPhotonLatency", c_float), 
        # Amount of queue-ahead in seconds provided to the app based on performance and overlap of
        # CPU and  GPU utilization. A value of 0.0 would mean the CPU & GPU workload is being completed
        # in 1 frame's worth of time, while 11 ms (on the CV1) of queue ahead would indicate that the
        # app's CPU workload for the next frame is overlapping the GPU workload for the current frame.
        ("AppQueueAheadTime", c_float), 
        # Amount of time in seconds spent on the CPU by the app's render-thread that calls
        # ovr_SubmitFram.  Measured as elapsed time between from when app regains control from
        # ovr_SubmitFrame to the next time the app calls ovr_SubmitFrame.
        ("AppCpuElapsedTime", c_float), 
        # Amount of time in seconds spent on the GPU by the app.
        # Measured as elapsed time between each ovr_SubmitFrame call using GPU timing queries.
        ("AppGpuElapsedTime", c_float), 
        #
        # SDK Compositor stats
        #
        # Index that increments each time the SDK compositor completes a distortion and timewarp pass
        # Since the compositor operates asynchronously, even if the app calls ovr_SubmitFrame too late,
        # the compositor will kick off for each vsync.
        ("CompositorFrameIndex", c_int), 
        # Increments each time the SDK compositor fails to complete in time
        # This is not tied to the app's performance, but failure to complete can be related to other
        # factors such as OS capabilities, overall available hardware cycles to execute the compositor
        # in time and other factors outside of the app's control.
        ("CompositorDroppedFrameCount", c_int), 
        # Motion-to-photon latency of the SDK compositor in seconds.
        # This is the latency of timewarp which corrects the higher app latency as well as dropped app
        # frames.
        ("CompositorLatency", c_float), 
        # The amount of time in seconds spent on the CPU by the SDK compositor. Unless the
        # VR app is utilizing all of the CPU cores at their peak performance, there is a good chance the
        # compositor CPU times will not affect the app's CPU performance in a major way.
        ("CompositorCpuElapsedTime", c_float), 
        # The amount of time in seconds spent on the GPU by the SDK compositor. Any time spent on the
        # compositor will eat away from the available GPU time for the app.
        ("CompositorGpuElapsedTime", c_float), 
        # The amount of time in seconds spent from the point the CPU kicks off the compositor to the
        # point in time the compositor completes the distortion & timewarp on the GPU. In the event the
        # GPU time is not available, expect this value to be -1.0f.
        ("CompositorCpuStartToGpuEndElapsedTime", c_float), 
        # The amount of time in seconds left after the compositor is done on the GPU to the associated
        # V-Sync time. In the event the GPU time is not available, expect this value to be -1.0f.
        ("CompositorGpuEndToVsyncElapsedTime", c_float), 
        #
        # Async Spacewarp stats (ASW)
        #
        # Will be true if ASW is active for the given frame such that the application is being forced
        # into half the frame-rate while the compositor continues to run at full frame-rate.
        ("AswIsActive", Bool), 
        # Increments each time ASW it activated where the app was forced in and out of
        # half-rate rendering.
        ("AswActivatedToggleCount", c_int), 
        # Accumulates the number of frames presented by the compositor which had extrapolated
        # ASW frames presented.
        ("AswPresentedFrameCount", c_int), 
        # Accumulates the number of frames that the compositor tried to present when ASW is
        # active but failed.
        ("AswFailedFrameCount", c_int), 
    ]

    def __repr__(self):
        return "ovr.PerfStatsPerCompositorFrame(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.HmdVsyncIndex, self.AppFrameIndex, self.AppDroppedFrameCount, self.AppMotionToPhotonLatency, self.AppQueueAheadTime, self.AppCpuElapsedTime, self.AppGpuElapsedTime, self.CompositorFrameIndex, self.CompositorDroppedFrameCount, self.CompositorLatency, self.CompositorCpuElapsedTime, self.CompositorGpuElapsedTime, self.CompositorCpuStartToGpuEndElapsedTime, self.CompositorGpuEndToVsyncElapsedTime, self.AswIsActive, self.AswActivatedToggleCount, self.AswPresentedFrameCount, self.AswFailedFrameCount)


# Translated from header file OVR_CAPI.h line 2458
#
# Maximum number of frames of performance stats provided back to the caller of ovr_GetPerfStats
#
MaxProvidedFrameStats = 5


# Translated from header file OVR_CAPI.h line 2463
class PerfStats(Structure):
    """
    
    This is a complete descriptor of the performance stats provided by the SDK
    
    \see ovr_GetPerfStats, ovrPerfStatsPerCompositorFrame
    """
    _pack_ = 4
    _fields_ = [
        # FrameStatsCount will have a maximum value set by ovrMaxProvidedFrameStats
        # If the application calls ovr_GetPerfStats at the native refresh rate of the HMD
        # then FrameStatsCount will be 1. If the app's workload happens to force
        # ovr_GetPerfStats to be called at a lower rate, then FrameStatsCount will be 2 or more.
        # If the app does not want to miss any performance data for any frame, it needs to
        # ensure that it is calling ovr_SubmitFrame and ovr_GetPerfStats at a rate that is at least:
        # "HMD_refresh_rate / ovrMaxProvidedFrameStats". On the Oculus Rift CV1 HMD, this will
        # be equal to 18 times per second.
        #
        # The performance entries will be ordered in reverse chronological order such that the
        # first entry will be the most recent one.
        ("FrameStats", PerfStatsPerCompositorFrame * MaxProvidedFrameStats), 
        ("FrameStatsCount", c_int), 
        # If the app calls ovr_GetPerfStats at less than 18 fps for CV1, then AnyFrameStatsDropped
        # will be ovrTrue and FrameStatsCount will be equal to ovrMaxProvidedFrameStats.
        ("AnyFrameStatsDropped", Bool), 
        # AdaptiveGpuPerformanceScale is an edge-filtered value that a caller can use to adjust
        # the graphics quality of the application to keep the GPU utilization in check. The value
        # is calculated as: (desired_GPU_utilization / current_GPU_utilization)
        # As such, when this value is 1.0, the GPU is doing the right amount of work for the app.
        # Lower values mean the app needs to pull back on the GPU utilization.
        # If the app is going to directly drive render-target resolution using this value, then
        # be sure to take the square-root of the value before scaling the resolution with it.
        # Changing render target resolutions however is one of the many things an app can do
        # increase or decrease the amount of GPU utilization.
        # Since AdaptiveGpuPerformanceScale is edge-filtered and does not change rapidly
        # (i.e. reports non-1.0 values once every couple of seconds) the app can make the
        # necessary adjustments and then keep watching the value to see if it has been satisfied.
        ("AdaptiveGpuPerformanceScale", c_float), 
        # Will be true if Async Spacewarp (ASW) is available for this system which is dependent on
        # several factors such as choice of GPU, OS and debug overrides
        ("AswIsAvailable", Bool), 
        # Contains the Process ID of the VR application the stats are being polled for
        # If an app continues to grab perf stats even when it is not visible, then expect this
        # value to point to the other VR app that has grabbed focus (i.e. became visible)
        ("VisibleProcessId", ProcessId), 
    ]

    def __repr__(self):
        return "ovr.PerfStats(%s, %s, %s, %s, %s, %s)" % (self.FrameStats, self.FrameStatsCount, self.AnyFrameStatsDropped, self.AdaptiveGpuPerformanceScale, self.AswIsAvailable, self.VisibleProcessId)


# Translated from header file OVR_CAPI.h line 2512
libovr.ovr_GetPerfStats.restype = Result
libovr.ovr_GetPerfStats.argtypes = [Session, POINTER(PerfStats)]
def getPerfStats(session):
    """
    Retrieves performance stats for the VR app as well as the SDK compositor.
    
    This function will return stats for the VR app that is currently visible in the HMD
    regardless of what VR app is actually calling this function.
    
    If the VR app is trying to make sure the stats returned belong to the same application,
    the caller can compare the VisibleProcessId with their own process ID. Normally this will
    be the case if the caller is only calling ovr_GetPerfStats when ovr_GetSessionStatus has
    IsVisible flag set to be true.
    
    If the VR app calling ovr_GetPerfStats is actually the one visible in the HMD,
    then new perf stats will only be populated after a new call to ovr_SubmitFrame.
    That means subsequent calls to ovr_GetPerfStats after the first one without calling
    ovr_SubmitFrame will receive a FrameStatsCount of zero.
    
    If the VR app is not visible, or was initially marked as ovrInit_Invisible, then each call
    to ovr_GetPerfStats will immediately fetch new perf stats from the compositor without
    a need for the ovr_SubmitFrame call.
    
    Even though invisible VR apps do not require ovr_SubmitFrame to be called to gather new
    perf stats, since stats are generated at the native refresh rate of the HMD (i.e. 90 Hz
    for CV1), calling it at a higher rate than that would be unnecessary.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[out] outStats Contains the performance stats for the application and SDK compositor
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success.
    
    \see ovrPerfStats, ovrPerfStatsPerCompositorFrame, ovr_ResetPerfStats
    """
    outStats = PerfStats()
    result = libovr.ovr_GetPerfStats(session, byref(outStats))
    _checkResult(result, "getPerfStats")
    return outStats


# Translated from header file OVR_CAPI.h line 2544
libovr.ovr_ResetPerfStats.restype = Result
libovr.ovr_ResetPerfStats.argtypes = [Session]
def resetPerfStats(session):
    """
    Resets the accumulated stats reported in each ovrPerfStatsPerCompositorFrame back to zero.
    
    Only the integer values such as HmdVsyncIndex, AppDroppedFrameCount etc. will be reset
    as the other fields such as AppMotionToPhotonLatency are independent timing values updated
    per-frame.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
            upon success.
    
    \see ovrPerfStats, ovrPerfStatsPerCompositorFrame, ovr_GetPerfStats
    """
    result = libovr.ovr_ResetPerfStats(session)
    _checkResult(result, "resetPerfStats")
    return result


# Translated from header file OVR_CAPI.h line 2558
libovr.ovr_GetPredictedDisplayTime.restype = c_double
libovr.ovr_GetPredictedDisplayTime.argtypes = [Session, c_longlong]
def getPredictedDisplayTime(session, frameIndex):
    """
    Gets the time of the specified frame midpoint.
    
    Predicts the time at which the given frame will be displayed. The predicted time
    is the middle of the time period during which the corresponding eye images will
    be displayed.
    
    The application should increment frameIndex for each successively targeted frame,
    and pass that index to any relevant OVR functions that need to apply to the frame
    identified by that index.
    
    This function is thread-safe and allows for multiple application threads to target
    their processing to the same displayed frame.
    
    In the even that prediction fails due to various reasons (e.g. the display being off
    or app has yet to present any frames), the return value will be current CPU time.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] frameIndex Identifies the frame the caller wishes to target.
               A value of zero returns the next frame index.
    \return Returns the absolute frame midpoint time for the given frameIndex.
    \see ovr_GetTimeInSeconds
    """
    result = libovr.ovr_GetPredictedDisplayTime(session, frameIndex)
    return result


# Translated from header file OVR_CAPI.h line 2582
libovr.ovr_GetTimeInSeconds.restype = c_double
def getTimeInSeconds():
    """
    Returns global, absolute high-resolution time in seconds.
    
    The time frame of reference for this function is not specified and should not be
    depended upon.
    
    \return Returns seconds as a floating point value.
    \see ovrPoseStatef, ovrFrameTiming
    """
    result = libovr.ovr_GetTimeInSeconds()
    return result


# Translated from header file OVR_CAPI.h line 2594
# Performance HUD enables the HMD user to see information critical to
# the real-time operation of the VR application such as latency timing,
# and CPU & GPU performance metrics
#
#     App can toggle performance HUD modes as such:
#     \code{.cpp}
#         ovrPerfHudMode PerfHudMode = ovrPerfHud_LatencyTiming;
#         ovr_SetInt(session, OVR_PERF_HUD_MODE, (int)PerfHudMode);
#     \endcode
#
PerfHudMode = ENUM_TYPE
PerfHud_Off = 0 #< Turns off the performance HUD
PerfHud_PerfSummary = 1 #< Shows performance summary and headroom
PerfHud_LatencyTiming = 2 #< Shows latency related timing info
PerfHud_AppRenderTiming = 3 #< Shows render timing info for application
PerfHud_CompRenderTiming = 4 #< Shows render timing info for OVR compositor
PerfHud_AswStats = 6 #< Shows Async Spacewarp-specific info
PerfHud_VersionInfo = 5 #< Shows SDK & HMD version Info
PerfHud_Count = 7 #< \internal Count of enumerated elements.


# Translated from header file OVR_CAPI.h line 2616
# Layer HUD enables the HMD user to see information about a layer
#
#     App can toggle layer HUD modes as such:
#     \code{.cpp}
#         ovrLayerHudMode LayerHudMode = ovrLayerHud_Info;
#         ovr_SetInt(session, OVR_LAYER_HUD_MODE, (int)LayerHudMode);
#     \endcode
#
LayerHudMode = ENUM_TYPE
LayerHud_Off = 0 #< Turns off the layer HUD
LayerHud_Info = 1 #< Shows info about a specific layer


# Translated from header file OVR_CAPI.h line 2632
# Debug HUD is provided to help developers gauge and debug the fidelity of their app's
# stereo rendering characteristics. Using the provided quad and crosshair guides,
# the developer can verify various aspects such as VR tracking units (e.g. meters),
# stereo camera-parallax properties (e.g. making sure objects at infinity are rendered
# with the proper separation), measuring VR geometry sizes and distances and more.
#
#     App can toggle the debug HUD modes as such:
#     \code{.cpp}
#         ovrDebugHudStereoMode DebugHudMode = ovrDebugHudStereo_QuadWithCrosshair;
#         ovr_SetInt(session, OVR_DEBUG_HUD_STEREO_MODE, (int)DebugHudMode);
#     \endcode
#
# The app can modify the visual properties of the stereo guide (i.e. quad, crosshair)
# using the ovr_SetFloatArray function. For a list of tweakable properties,
# see the OVR_DEBUG_HUD_STEREO_GUIDE_* keys in the OVR_CAPI_Keys.h header file.
DebugHudStereoMode = ENUM_TYPE
# Turns off the Stereo Debug HUD.
DebugHudStereo_Off = 0
# Renders Quad in world for Stereo Debugging.
DebugHudStereo_Quad = 1
# Renders Quad+crosshair in world for Stereo Debugging
DebugHudStereo_QuadWithCrosshair = 2
# Renders screen-space crosshair at infinity for Stereo Debugging
DebugHudStereo_CrosshairAtInfinity = 3
# \internal Count of enumerated elements
DebugHudStereo_Count = DebugHudStereo_CrosshairAtInfinity + 1 


# Translated from header file OVR_CAPI.h line 2676
libovr.ovr_GetExternalCameras.restype = Result
libovr.ovr_GetExternalCameras.argtypes = [Session, POINTER(ExternalCamera), POINTER(c_uint)]
def getExternalCameras(session, cameras, inoutCameraCount):
    """
    Returns the number of camera properties of all cameras
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in out] supply the array capacity, will return the actual # of cameras defined
    \param[in out] cameras the array.  If null or *inoutCameraCount is too small, will return
                   ovrError_InsufficientArraySize
    \return Returns the ids of external cameras the system knows about. Returns
               ovrError_NoExternalCameraInfo if there is not any eternal camera information.
    """
    result = libovr.ovr_GetExternalCameras(session, byref(cameras), byref(inoutCameraCount))
    _checkResult(result, "getExternalCameras")
    return result


# Translated from header file OVR_CAPI.h line 2689
libovr.ovr_SetExternalCameraProperties.restype = Result
libovr.ovr_SetExternalCameraProperties.argtypes = [Session, c_char_p, POINTER(CameraIntrinsics), POINTER(CameraExtrinsics)]
def setExternalCameraProperties(session, name, intrinsics, extrinsics):
    """
    Sets the camera intrinsics and/or extrinsics stored for the cameraName camera
    Names must be < 32 characters and null-terminated.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] name Specifies which camera to set the intrinsics or extrinsics for
    \param[in] intrinsics Contains the intrinsic parameters to set, can be null
    \param[in] extrinsics Contains the extrinsic parameters to set, can be null
    \return Returns ovrSuccess or an ovrError code
    """
    result = libovr.ovr_SetExternalCameraProperties(session, name, byref(intrinsics), byref(extrinsics))
    _checkResult(result, "setExternalCameraProperties")
    return result


# Translated from header file OVR_CAPI.h line 2718
libovr.ovr_GetBool.restype = Bool
libovr.ovr_GetBool.argtypes = [Session, c_char_p, Bool]
def getBool(session, propertyName, defaultVal):
    """
    Reads a boolean property.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid for only the call.
    \param[in] defaultVal specifes the value to return if the property couldn't be read.
    \return Returns the property interpreted as a boolean value. Returns defaultVal if
            the property doesn't exist.
    """
    result = libovr.ovr_GetBool(session, propertyName, toOvrBool(defaultVal))
    return result


# Translated from header file OVR_CAPI.h line 2728
libovr.ovr_SetBool.restype = Bool
libovr.ovr_SetBool.argtypes = [Session, c_char_p, Bool]
def setBool(session, propertyName, value):
    """
    Writes or creates a boolean property.
    If the property wasn't previously a boolean property, it is changed to a boolean property.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] value The value to write.
    \return Returns true if successful, otherwise false. A false result should only occur if the
    property
            name is empty or if the property is read-only.
    """
    result = libovr.ovr_SetBool(session, propertyName, toOvrBool(value))
    return result


# Translated from header file OVR_CAPI.h line 2740
libovr.ovr_GetInt.restype = c_int
libovr.ovr_GetInt.argtypes = [Session, c_char_p, c_int]
def getInt(session, propertyName, defaultVal):
    """
    Reads an integer property.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] defaultVal Specifes the value to return if the property couldn't be read.
    \return Returns the property interpreted as an integer value. Returns defaultVal if
            the property doesn't exist.
    """
    result = libovr.ovr_GetInt(session, propertyName, defaultVal)
    return result


# Translated from header file OVR_CAPI.h line 2749
libovr.ovr_SetInt.restype = Bool
libovr.ovr_SetInt.argtypes = [Session, c_char_p, c_int]
def setInt(session, propertyName, value):
    """
    Writes or creates an integer property.
    
    If the property wasn't previously a boolean property, it is changed to an integer property.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] value The value to write.
    \return Returns true if successful, otherwise false. A false result should only occur if the
            property name is empty or if the property is read-only.
    """
    result = libovr.ovr_SetInt(session, propertyName, value)
    return result


# Translated from header file OVR_CAPI.h line 2760
libovr.ovr_GetFloat.restype = c_float
libovr.ovr_GetFloat.argtypes = [Session, c_char_p, c_float]
def getFloat(session, propertyName, defaultVal):
    """
    Reads a float property.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] defaultVal specifes the value to return if the property couldn't be read.
    \return Returns the property interpreted as an float value. Returns defaultVal if
            the property doesn't exist.
    """
    result = libovr.ovr_GetFloat(session, propertyName, defaultVal)
    return result


# Translated from header file OVR_CAPI.h line 2770
libovr.ovr_SetFloat.restype = Bool
libovr.ovr_SetFloat.argtypes = [Session, c_char_p, c_float]
def setFloat(session, propertyName, value):
    """
    Writes or creates a float property.
    If the property wasn't previously a float property, it's changed to a float property.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] value The value to write.
    \return Returns true if successful, otherwise false. A false result should only occur if the
            property name is empty or if the property is read-only.
    """
    result = libovr.ovr_SetFloat(session, propertyName, value)
    return result


# Translated from header file OVR_CAPI.h line 2781
libovr.ovr_GetFloatArray.restype = c_uint
libovr.ovr_GetFloatArray.argtypes = [Session, c_char_p, POINTER(c_float), c_uint]
def getFloatArray(session, propertyName, values, valuesCapacity):
    """
    Reads a float array property.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] values An array of float to write to.
    \param[in] valuesCapacity Specifies the maximum number of elements to write to the values array.
    \return Returns the number of elements read, or 0 if property doesn't exist or is empty.
    """
    result = libovr.ovr_GetFloatArray(session, propertyName, byref(values), valuesCapacity)
    return result


# Translated from header file OVR_CAPI.h line 2795
libovr.ovr_SetFloatArray.restype = Bool
libovr.ovr_SetFloatArray.argtypes = [Session, c_char_p, POINTER(c_float), c_uint]
def setFloatArray(session, propertyName, values, valuesSize):
    """
    Writes or creates a float array property.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] values An array of float to write from.
    \param[in] valuesSize Specifies the number of elements to write.
    \return Returns true if successful, otherwise false. A false result should only occur if the
            property name is empty or if the property is read-only.
    """
    result = libovr.ovr_SetFloatArray(session, propertyName, byref(values), valuesSize)
    return result


# Translated from header file OVR_CAPI.h line 2810
libovr.ovr_GetString.restype = c_char_p
libovr.ovr_GetString.argtypes = [Session, c_char_p, c_char_p]
def getString(session, propertyName, defaultVal):
    """
    Reads a string property.
    Strings are UTF8-encoded and null-terminated.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] defaultVal Specifes the value to return if the property couldn't be read.
    \return Returns the string property if it exists. Otherwise returns defaultVal, which can be
            specified as NULL. The return memory is guaranteed to be valid until next call to
            ovr_GetString or until the session is destroyed, whichever occurs first.
    """
    result = libovr.ovr_GetString(session, propertyName, defaultVal)
    return result


# Translated from header file OVR_CAPI.h line 2822
libovr.ovr_SetString.restype = Bool
libovr.ovr_SetString.argtypes = [Session, c_char_p, c_char_p]
def setString(session, propertyName, value):
    """
    Writes or creates a string property.
    Strings are UTF8-encoded and null-terminated.
    
    \param[in] session Specifies an ovrSession previously returned by ovr_Create.
    \param[in] propertyName The name of the property, which needs to be valid only for the call.
    \param[in] value The string property, which only needs to be valid for the duration of the call.
    \return Returns true if successful, otherwise false. A false result should only occur if the
            property name is empty or if the property is read-only.
    """
    result = libovr.ovr_SetString(session, propertyName, value)
    return result


### END Declarations from C header file OVR_CAPI.h ###


### BEGIN Declarations from C header file OVR_CAPI_GL.h ###


# Translated from header file OVR_CAPI_GL.h line 13
libovr.ovr_CreateTextureSwapChainGL.restype = Result
libovr.ovr_CreateTextureSwapChainGL.argtypes = [Session, POINTER(TextureSwapChainDesc), POINTER(TextureSwapChain)]
def createTextureSwapChainGL(session, desc):
    """
    Creates a TextureSwapChain suitable for use with OpenGL.
    
    \param[in]  session Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  desc Specifies the requested texture properties.
                See notes for more info about texture format.
    \param[out] out_TextureSwapChain Returns the created ovrTextureSwapChain,
                which will be valid upon a successful return value, else it will be NULL.
                This texture swap chain must be eventually destroyed via
                 ovr_DestroyTextureSwapChain before destroying the session with ovr_Destroy.
    
    \return Returns an ovrResult indicating success or failure. In the case of failure, use
            ovr_GetLastErrorInfo to get more information.
    
    \note The \a format provided should be thought of as the format the distortion compositor will
          use when reading the contents of the texture. To that end, it is highly recommended
          that the application requests texture swap chain formats that are in sRGB-space
          (e.g. OVR_FORMAT_R8G8B8A8_UNORM_SRGB) as the distortion compositor does sRGB-correct
          rendering. Furthermore, the app should then make sure "glEnable(GL_FRAMEBUFFER_SRGB);"
          is called before rendering into these textures. Even though it is not recommended,
          if the application would like to treat the texture as a linear format and do
          linear-to-gamma conversion in GLSL, then the application can avoid
          calling "glEnable(GL_FRAMEBUFFER_SRGB);", but should still pass in an sRGB variant for
          the \a format. Failure to do so will cause the distortion compositor to apply incorrect
          gamma conversions leading to gamma-curve artifacts.
    
    \see ovr_GetTextureSwapChainLength
    \see ovr_GetTextureSwapChainCurrentIndex
    \see ovr_GetTextureSwapChainDesc
    \see ovr_GetTextureSwapChainBufferGL
    \see ovr_DestroyTextureSwapChain
    """
    out_TextureSwapChain = TextureSwapChain()
    result = libovr.ovr_CreateTextureSwapChainGL(session, byref(desc), byref(out_TextureSwapChain))
    _checkResult(result, "createTextureSwapChainGL")
    return out_TextureSwapChain


# Translated from header file OVR_CAPI_GL.h line 50
libovr.ovr_GetTextureSwapChainBufferGL.restype = Result
libovr.ovr_GetTextureSwapChainBufferGL.argtypes = [Session, TextureSwapChain, c_int, POINTER(c_uint)]
def getTextureSwapChainBufferGL(session, chain, index):
    """
    Get a specific buffer within the chain as a GL texture name
    
    \param[in]  session Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  chain Specifies an ovrTextureSwapChain previously returned
                by ovr_CreateTextureSwapChainGL
    \param[in]  index Specifies the index within the chain to retrieve.
                Must be between 0 and length (see ovr_GetTextureSwapChainLength)
                or may pass -1 to get the buffer at the CurrentIndex location.
                (Saving a call to GetTextureSwapChainCurrentIndex)
    \param[out] out_TexId Returns the GL texture object name associated with
                the specific index requested
    
    \return Returns an ovrResult indicating success or failure.
            In the case of failure, use ovr_GetLastErrorInfo to get more information.
    """
    out_TexId = c_uint()
    result = libovr.ovr_GetTextureSwapChainBufferGL(session, chain, index, byref(out_TexId))
    _checkResult(result, "getTextureSwapChainBufferGL")
    return out_TexId


# Translated from header file OVR_CAPI_GL.h line 72
libovr.ovr_CreateMirrorTextureGL.restype = Result
libovr.ovr_CreateMirrorTextureGL.argtypes = [Session, POINTER(MirrorTextureDesc), POINTER(MirrorTexture)]
def createMirrorTextureGL(session, desc):
    """
    Creates a Mirror Texture which is auto-refreshed to mirror Rift contents produced by this
    application.
    
    A second call to ovr_CreateMirrorTextureGL for a given ovrSession before destroying
    the first one is not supported and will result in an error return.
    
    \param[in]  session Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  desc Specifies the requested mirror texture description.
    \param[out] out_MirrorTexture Specifies the created ovrMirrorTexture, which will be
                valid upon a successful return value, else it will be NULL.
                This texture must be eventually destroyed via ovr_DestroyMirrorTexture before
                destroying the session with ovr_Destroy.
    
    \return Returns an ovrResult indicating success or failure. In the case of failure, use
            ovr_GetLastErrorInfo to get more information.
    
    \note The \a format provided should be thought of as the format the distortion compositor will
          use when writing into the mirror texture. It is highly recommended that mirror textures
           are requested as sRGB formats because the distortion compositor does sRGB-correct
          rendering. If the application requests a non-sRGB format (e.g. R8G8B8A8_UNORM) as the
          mirror texture, then the application might have to apply a manual linear-to-gamma
          conversion when reading from the mirror texture. Failure to do so can result in
           incorrect gamma conversions leading to gamma-curve artifacts and color banding.
    
    \see ovr_GetMirrorTextureBufferGL
    \see ovr_DestroyMirrorTexture
    """
    out_MirrorTexture = MirrorTexture()
    result = libovr.ovr_CreateMirrorTextureGL(session, byref(desc), byref(out_MirrorTexture))
    _checkResult(result, "createMirrorTextureGL")
    return out_MirrorTexture


# Translated from header file OVR_CAPI_GL.h line 105
libovr.ovr_GetMirrorTextureBufferGL.restype = Result
libovr.ovr_GetMirrorTextureBufferGL.argtypes = [Session, MirrorTexture, POINTER(c_uint)]
def getMirrorTextureBufferGL(session, mirrorTexture):
    """
    Get a the underlying buffer as a GL texture name
    
    \param[in]  session Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  mirrorTexture Specifies an ovrMirrorTexture previously returned
                 by ovr_CreateMirrorTextureGL
    \param[out] out_TexId Specifies the GL texture object name associated with the mirror texture
    
    \return Returns an ovrResult indicating success or failure. In the case of failure, use
            ovr_GetLastErrorInfo to get more information.
    """
    out_TexId = c_uint()
    result = libovr.ovr_GetMirrorTextureBufferGL(session, mirrorTexture, byref(out_TexId))
    _checkResult(result, "getMirrorTextureBufferGL")
    return out_TexId


### END Declarations from C header file OVR_CAPI_GL.h ###


### BEGIN Declarations from C header file OVR_CAPI_Util.h ###


# Translated from header file OVR_CAPI_Util.h line 15
# Enumerates modifications to the projection matrix based on the application's needs.
#
# \see ovrMatrix4f_Projection
#
ProjectionModifier = ENUM_TYPE
# Use for generating a default projection matrix that is:
# * Right-handed.
# * Near depth values stored in the depth buffer are smaller than far depth values.
# * Both near and far are explicitly defined.
# * With a clipping range that is (0 to w).
Projection_None = 0x00
# Enable if using left-handed transformations in your application.
Projection_LeftHanded = 0x01
# After the projection transform is applied, far values stored in the depth buffer will be less
# than closer depth values.
# NOTE: Enable only if the application is using a floating-point depth buffer for proper
# precision.
Projection_FarLessThanNear = 0x02
# When this flag is used, the zfar value pushed into ovrMatrix4f_Projection() will be ignored
# NOTE: Enable only if ovrProjection_FarLessThanNear is also enabled where the far clipping
# plane will be pushed to infinity.
Projection_FarClipAtInfinity = 0x04
# Enable if the application is rendering with OpenGL and expects a projection matrix with a
# clipping range of (-w to w).
# Ignore this flag if your application already handles the conversion from D3D range (0 to w) to
# OpenGL.
Projection_ClipRangeOpenGL = 0x08


# Translated from header file OVR_CAPI_Util.h line 48
class DetectResult(Structure):
    """
    Return values for ovr_Detect.
    
    \see ovr_Detect
    """
    _pack_ = 8
    _fields_ = [
        # Is ovrFalse when the Oculus Service is not running.
        #   This means that the Oculus Service is either uninstalled or stopped.
        #   IsOculusHMDConnected will be ovrFalse in this case.
        # Is ovrTrue when the Oculus Service is running.
        #   This means that the Oculus Service is installed and running.
        #   IsOculusHMDConnected will reflect the state of the HMD.
        ("IsOculusServiceRunning", Bool), 
        # Is ovrFalse when an Oculus HMD is not detected.
        #   If the Oculus Service is not running, this will be ovrFalse.
        # Is ovrTrue when an Oculus HMD is detected.
        #   This implies that the Oculus Service is also installed and running.
        ("IsOculusHMDConnected", Bool), 
        ("pad0", c_char * 6),  #< \internal struct padding
    ]

    def __repr__(self):
        return "ovr.DetectResult(%s, %s)" % (self.IsOculusServiceRunning, self.IsOculusHMDConnected)


# Translated from header file OVR_CAPI_Util.h line 73
# Modes used to generate Touch Haptics from audio PCM buffer.
#
HapticsGenMode = ENUM_TYPE
# Point sample original signal at Haptics frequency
HapticsGenMode_PointSample = 0 
HapticsGenMode_Count = HapticsGenMode_PointSample + 1 


# Translated from header file OVR_CAPI_Util.h line 81
class AudioChannelData(Structure):
    """
    Store audio PCM data (as 32b float samples) for an audio channel.
    Note: needs to be released with ovr_ReleaseAudioChannelData to avoid memory leak.
    """
    _fields_ = [
        # Samples stored as floats [-1.0f, 1.0f].
        ("Samples", POINTER(c_float)), 
        # Number of samples
        ("SamplesCount", c_int), 
        # Frequency (e.g. 44100)
        ("Frequency", c_int), 
    ]

    def __repr__(self):
        return "ovr.AudioChannelData(%s, %s, %s)" % (self.Samples, self.SamplesCount, self.Frequency)


# Translated from header file OVR_CAPI_Util.h line 95
class HapticsClip(Structure):
    """
    Store a full Haptics clip, which can be used as data source for multiple ovrHapticsBuffers.
    """
    _fields_ = [
        # Samples stored in opaque format
        ("Samples", c_void_p), 
        # Number of samples
        ("SamplesCount", c_int), 
    ]

    def __repr__(self):
        return "ovr.HapticsClip(%s, %s)" % (self.Samples, self.SamplesCount)


# Translated from header file OVR_CAPI_Util.h line 105
libovr.ovr_Detect.restype = DetectResult
libovr.ovr_Detect.argtypes = [c_int]
def detect(timeoutMilliseconds):
    """
    Detects Oculus Runtime and Device Status
    
    Checks for Oculus Runtime and Oculus HMD device status without loading the LibOVRRT
    shared library.  This may be called before ovr_Initialize() to help decide whether or
    not to initialize LibOVR.
    
    \param[in] timeoutMilliseconds Specifies a timeout to wait for HMD to be attached or 0 to poll.
    
    \return Returns an ovrDetectResult object indicating the result of detection.
    
    \see ovrDetectResult
    """
    result = libovr.ovr_Detect(timeoutMilliseconds)
    return result


# Translated from header file OVR_CAPI_Util.h line 122
HMD_CONNECTED_EVENT_NAME = b"OculusHMDConnected"


# Translated from header file OVR_CAPI_Util.h line 125
libovr.ovrMatrix4f_Projection.restype = Matrix4f
libovr.ovrMatrix4f_Projection.argtypes = [FovPort, c_float, c_float, c_uint]
def matrix4f_Projection(fov, znear, zfar, projectionModFlags):
    """
    Used to generate projection from ovrEyeDesc::Fov.
    
    \param[in] fov Specifies the ovrFovPort to use.
    \param[in] znear Distance to near Z limit.
    \param[in] zfar Distance to far Z limit.
    \param[in] projectionModFlags A combination of the ovrProjectionModifier flags.
    
    \return Returns the calculated projection matrix.
    
    \see ovrProjectionModifier
    """
    result = libovr.ovrMatrix4f_Projection(fov, znear, zfar, projectionModFlags)
    return result


# Translated from header file OVR_CAPI_Util.h line 139
libovr.ovrTimewarpProjectionDesc_FromProjection.restype = TimewarpProjectionDesc
libovr.ovrTimewarpProjectionDesc_FromProjection.argtypes = [Matrix4f, c_uint]
def timewarpProjectionDesc_FromProjection(projection, projectionModFlags):
    """
    Extracts the required data from the result of ovrMatrix4f_Projection.
    
    \param[in] projection Specifies the project matrix from which to
               extract ovrTimewarpProjectionDesc.
    \param[in] projectionModFlags A combination of the ovrProjectionModifier flags.
    \return Returns the extracted ovrTimewarpProjectionDesc.
    \see ovrTimewarpProjectionDesc
    """
    result = libovr.ovrTimewarpProjectionDesc_FromProjection(projection, projectionModFlags)
    return result


# Translated from header file OVR_CAPI_Util.h line 150
libovr.ovrMatrix4f_OrthoSubProjection.restype = Matrix4f
libovr.ovrMatrix4f_OrthoSubProjection.argtypes = [Matrix4f, Vector2f, c_float, c_float]
def matrix4f_OrthoSubProjection(projection, orthoScale, orthoDistance, HmdToEyeOffsetX):
    """
    Generates an orthographic sub-projection.
    
    Used for 2D rendering, Y is down.
    
    \param[in] projection The perspective matrix that the orthographic matrix is derived from.
    \param[in] orthoScale Equal to 1.0f / pixelsPerTanAngleAtCenter.
    \param[in] orthoDistance Equal to the distance from the camera in meters, such as 0.8m.
    \param[in] HmdToEyeOffsetX Specifies the offset of the eye from the center.
    
    \return Returns the calculated projection matrix.
    """
    result = libovr.ovrMatrix4f_OrthoSubProjection(projection, orthoScale, orthoDistance, HmdToEyeOffsetX)
    return result


# Translated from header file OVR_CAPI_Util.h line 168
libovr.ovr_CalcEyePoses.restype = None
libovr.ovr_CalcEyePoses.argtypes = [Posef, Vector3f * 2, Posef * 2]
def calcEyePoses(headPose, hmdToEyeOffset):
    """
    Computes offset eye poses based on headPose returned by ovrTrackingState.
    
    \param[in] headPose Indicates the HMD position and orientation to use for the calculation.
    \param[in] hmdToEyeOffset Can be ovrEyeRenderDesc.HmdToEyeOffset returned from
               ovr_GetRenderDesc. For monoscopic rendering, use a vector that is the average
               of the two vectors for both eyes.
    \param[out] outEyePoses If outEyePoses are used for rendering, they should be passed to
                ovr_SubmitFrame in ovrLayerEyeFov::RenderPose or ovrLayerEyeFovDepth::RenderPose.
    """
    outEyePoses = (Posef * Eye_Count)()
    libovr.ovr_CalcEyePoses(headPose, hmdToEyeOffset, outEyePoses)
    return outEyePoses


# Translated from header file OVR_CAPI_Util.h line 180
libovr.ovr_GetEyePoses.restype = None
libovr.ovr_GetEyePoses.argtypes = [Session, c_longlong, Bool, Vector3f * 2, Posef * 2, POINTER(c_double)]
def getEyePoses(session, frameIndex, latencyMarker, hmdToEyeOffset, outEyePoses):
    """
    Returns the predicted head pose in outHmdTrackingState and offset eye poses in outEyePoses.
    
    This is a thread-safe function where caller should increment frameIndex with every frame
    and pass that index where applicable to functions called on the rendering thread.
    Assuming outEyePoses are used for rendering, it should be passed as a part of ovrLayerEyeFov.
    The caller does not need to worry about applying HmdToEyeOffset to the returned outEyePoses
    variables.
    
    \param[in]  hmd Specifies an ovrSession previously returned by ovr_Create.
    \param[in]  frameIndex Specifies the targeted frame index, or 0 to refer to one frame after
                the last time ovr_SubmitFrame was called.
    \param[in]  latencyMarker Specifies that this call is the point in time where
                the "App-to-Mid-Photon" latency timer starts from. If a given ovrLayer
                provides "SensorSampleTimestamp", that will override the value stored here.
    \param[in]  hmdToEyeOffset Can be ovrEyeRenderDesc.HmdToEyeOffset returned from
                ovr_GetRenderDesc. For monoscopic rendering, use a vector that is the average
                of the two vectors for both eyes.
    \param[out] outEyePoses The predicted eye poses.
    \param[out] outSensorSampleTime The time when this function was called. May be NULL, in which
    case it is ignored.
    """
    outSensorSampleTime = c_double()
    libovr.ovr_GetEyePoses(session, frameIndex, toOvrBool(latencyMarker), hmdToEyeOffset, outEyePoses, byref(outSensorSampleTime))
    return outSensorSampleTime


# Translated from header file OVR_CAPI_Util.h line 210
libovr.ovrPosef_FlipHandedness.restype = None
libovr.ovrPosef_FlipHandedness.argtypes = [POINTER(Posef), POINTER(Posef)]
def posef_FlipHandedness(inPose):
    """
    Tracking poses provided by the SDK come in a right-handed coordinate system. If an application
    is passing in ovrProjection_LeftHanded into ovrMatrix4f_Projection, then it should also use
    this function to flip the HMD tracking poses to be left-handed.
    
    While this utility function is intended to convert a left-handed ovrPosef into a right-handed
    coordinate system, it will also work for converting right-handed to left-handed since the
    flip operation is the same for both cases.
    
    \param[in]  inPose that is right-handed
    \param[out] outPose that is requested to be left-handed (can be the same pointer to inPose)
    """
    outPose = Posef()
    libovr.ovrPosef_FlipHandedness(byref(inPose), byref(outPose))
    return outPose


# Translated from header file OVR_CAPI_Util.h line 223
libovr.ovr_ReadWavFromBuffer.restype = Result
libovr.ovr_ReadWavFromBuffer.argtypes = [POINTER(AudioChannelData), c_void_p, c_int, c_int]
def readWavFromBuffer(inputData, dataSizeInBytes, stereoChannelToUse):
    """
    Reads an audio channel from Wav (Waveform Audio File) data.
    Input must be a byte buffer representing a valid Wav file. Audio samples from the specified
    channel are read,
    converted to float [-1.0f, 1.0f] and returned through ovrAudioChannelData.
    
    Supported formats: PCM 8b, 16b, 32b and IEEE float (little-endian only).
    
    \param[out] outAudioChannel output audio channel data.
    \param[in] inputData a binary buffer representing a valid Wav file data.
    \param[in] dataSizeInBytes size of the buffer in bytes.
    \param[in] stereoChannelToUse audio channel index to extract (0 for mono).
    """
    outAudioChannel = AudioChannelData()
    result = libovr.ovr_ReadWavFromBuffer(byref(outAudioChannel), inputData, dataSizeInBytes, stereoChannelToUse)
    _checkResult(result, "readWavFromBuffer")
    return outAudioChannel


# Translated from header file OVR_CAPI_Util.h line 242
libovr.ovr_GenHapticsFromAudioData.restype = Result
libovr.ovr_GenHapticsFromAudioData.argtypes = [POINTER(HapticsClip), POINTER(AudioChannelData), HapticsGenMode]
def genHapticsFromAudioData(audioChannel, genMode):
    """
    Generates playable Touch Haptics data from an audio channel.
    
    \param[out] outHapticsClip generated Haptics clip.
    \param[in] audioChannel input audio channel data.
    \param[in] genMode mode used to convert and audio channel data to Haptics data.
    """
    outHapticsClip = HapticsClip()
    result = libovr.ovr_GenHapticsFromAudioData(byref(outHapticsClip), byref(audioChannel), genMode)
    _checkResult(result, "genHapticsFromAudioData")
    return outHapticsClip


# Translated from header file OVR_CAPI_Util.h line 254
libovr.ovr_ReleaseAudioChannelData.restype = None
libovr.ovr_ReleaseAudioChannelData.argtypes = [POINTER(AudioChannelData)]
def releaseAudioChannelData(audioChannel):
    """
    Releases memory allocated for ovrAudioChannelData. Must be called to avoid memory leak.
    \param[in] audioChannel pointer to an audio channel
    """
    libovr.ovr_ReleaseAudioChannelData(byref(audioChannel))


# Translated from header file OVR_CAPI_Util.h line 259
libovr.ovr_ReleaseHapticsClip.restype = None
libovr.ovr_ReleaseHapticsClip.argtypes = [POINTER(HapticsClip)]
def releaseHapticsClip(hapticsClip):
    """
    Releases memory allocated for ovrHapticsClip. Must be called to avoid memory leak.
    \param[in] hapticsClip pointer to a haptics clip
    """
    libovr.ovr_ReleaseHapticsClip(byref(hapticsClip))


### END Declarations from C header file OVR_CAPI_Util.h ###


# Run test program
if __name__ == "__main__":
    # Transcribed from initial example at 
    # https://developer.oculus.com/documentation/pcsdk/latest/concepts/dg-sensor/
    initialize(None)
    hmd, luid = create()
    desc = getHmdDesc(hmd)
    print(desc.Resolution)
    print(desc.ProductName)
    # Query the HMD for the current tracking state.
    ts  = getTrackingState(hmd, getTimeInSeconds())
    if ts.StatusFlags & (Status_OrientationTracked | Status_PositionTracked):
        pose = ts.HeadPose
        print(pose.ThePose)
        # TODO:

    destroy(hmd)
    shutdown()
