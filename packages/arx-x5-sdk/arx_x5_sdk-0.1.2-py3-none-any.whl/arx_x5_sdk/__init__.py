"""ARX X5 SDK Python bindings."""

import ctypes
import importlib.util
import os
from enum import IntEnum
from pathlib import Path

# Find the .so file in the package directory
_package_dir = Path(__file__).parent.absolute()
so_files = list(_package_dir.glob("arx_x5_sdk*.so"))

if not so_files:
    raise ImportError(
        f"Could not find arx_x5_sdk*.so in {_package_dir}. "
        f"Make sure to build the extension with: pip install -e . or python setup.py build_ext"
    )

# Find and preload libarx_x5_src.so from the same directory
lib_path = _package_dir / "libarx_x5_src.so"
arm64_lib_path = _package_dir / "libarx_x5_src-arm64.so"

# Try to load the appropriate library
loaded = False
for lib in [lib_path, arm64_lib_path]:
    if lib.exists():
        try:
            # Add package dir to LD_LIBRARY_PATH
            if "LD_LIBRARY_PATH" in os.environ:
                if str(_package_dir) not in os.environ["LD_LIBRARY_PATH"]:
                    os.environ["LD_LIBRARY_PATH"] = f"{_package_dir}:{os.environ['LD_LIBRARY_PATH']}"
            else:
                os.environ["LD_LIBRARY_PATH"] = str(_package_dir)
            
            ctypes.CDLL(str(lib), mode=ctypes.RTLD_GLOBAL)
            loaded = True
            break
        except OSError:
            continue

if not loaded:
    raise ImportError(
        f"Could not load C++ library. Looked for: {lib_path} or {arm64_lib_path}"
    )

# Load the extension module
spec = importlib.util.spec_from_file_location("arx_x5_sdk", so_files[0])
if not spec or not spec.loader:
    raise ImportError(f"Could not load {so_files[0]}")

_arx_x5_sdk_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_arx_x5_sdk_module)

# Expose C_ArxInterface
C_ArxInterface = _arx_x5_sdk_module.C_ArxInterface


class ArmType(IntEnum):
    """
    Enum for ARX arm types.
    
    Uses IntEnum so values can be passed directly to C++ interface.
    """
    FOLLOWER = 0      # Regular follower arm (x5.urdf)
    LEADER = 1        # Leader/master arm (x5_master.urdf)
    X5_2025 = 2       # X5 2025 model (x5_2025.urdf)


def get_urdf_path(urdf_name: str = "x5_2025.urdf") -> str:
    """
    Get the path to a URDF file included in the package.

    Args:
        urdf_name: Name of the URDF file (default: "x5_2025.urdf")
                  Options: "x5.urdf", "x5_master.urdf", "x5_2025.urdf"

    Returns:
        str: Full path to the URDF file

    Raises:
        FileNotFoundError: If the URDF file doesn't exist
    """
    urdf_path = _package_dir / "urdf" / urdf_name
    if not urdf_path.exists():
        raise FileNotFoundError(f"URDF file not found: {urdf_path}")
    return str(urdf_path)


def get_urdf_path_by_type(arm_type: ArmType | int) -> str:
    """
    Get the URDF path based on arm type.

    Args:
        arm_type: Arm type, either ArmType enum or integer:
                 - ArmType.FOLLOWER (0): Follower arm (x5.urdf)
                 - ArmType.LEADER (1): Leader arm (x5_master.urdf)
                 - ArmType.X5_2025 (2): X5 2025 model (x5_2025.urdf)

    Returns:
        str: Full path to the corresponding URDF file

    Raises:
        ValueError: If arm_type is not valid
        FileNotFoundError: If the URDF file doesn't exist
    """
    # Convert to int if ArmType enum is passed
    arm_type_int = int(arm_type)
    
    urdf_map = {
        ArmType.FOLLOWER: "x5.urdf",
        ArmType.LEADER: "x5_master.urdf",
        ArmType.X5_2025: "x5_2025.urdf",
    }
    
    if arm_type_int not in [t.value for t in ArmType]:
        raise ValueError(
            f"Invalid arm_type: {arm_type}. "
            f"Must be ArmType.FOLLOWER (0), ArmType.LEADER (1), or ArmType.X5_2025 (2)"
        )
    
    return get_urdf_path(urdf_map[ArmType(arm_type_int)])


class ArxInterface(C_ArxInterface):
    """
    Convenience wrapper for C_ArxInterface that automatically selects URDF based on arm type.
    
    This class provides a simpler API by automatically selecting the correct URDF file
    based on the arm_type parameter.
    
    Example:
        >>> interface = ArxInterface("can0", ArmType.X5_2025)
        >>> interface = ArxInterface("can0", arm_type=ArmType.FOLLOWER)
    """
    
    def __init__(self, can_port: str, arm_type: ArmType | int = ArmType.X5_2025):
        """
        Initialize ARX interface with automatic URDF selection.
        
        Args:
            can_port: CAN port name (e.g., "can0", "can1")
            arm_type: Arm type enum or integer (default: ArmType.X5_2025):
                     - ArmType.FOLLOWER (0): Follower arm (x5.urdf)
                     - ArmType.LEADER (1): Leader arm (x5_master.urdf)
                     - ArmType.X5_2025 (2): X5 2025 model (x5_2025.urdf)
        """
        urdf_path = get_urdf_path_by_type(arm_type)
        super().__init__(urdf_path, can_port, int(arm_type))


__all__ = ["C_ArxInterface", "ArxInterface", "ArmType", "get_urdf_path", "get_urdf_path_by_type"]
