import os
import tempfile
import subprocess
import shutil
import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class PyLuaHelper:
    """
    Python helper for loading Lua configuration files by running them with Lua interpreter and exporting requested tables to Python dictionaries.
    """

    def __init__(
        self,
        lua_config_script: str,
        export_vars: List[str] = None,
        pre_script: str = None,
        post_script: str = None,
        extra_strings: List[str] = None,
        work_dir: str = None,
        temp_dir: str = None,
        min_lua_version: str = None,
        max_lua_version: str = None,
        lua_binary: str = None,
        lua_args: List[str] = None,
    ):
        """
        Initialize PyLuaHelper with configuration options.

        Args:
            lua_config_script: Path to the main Lua configuration script
            export_vars: List of global variable names to export from Lua
            pre_script: Lua script to execute before main script
            post_script: Lua script to execute after main script
            extra_strings: Extra strings to add to loader.extra table
            work_dir: Working directory for Lua scripts
            result_name: Name of the dictionary to store exported variables
            temp_dir: Base directory for temporary files
            min_lua_version: Minimum required Lua version
            max_lua_version: Maximum allowed Lua version
            lua_binary: Path to specific Lua binary (optional, will be auto-detected if not provided)
            lua_args: Additional arguments to pass to Lua script (will be placed to loader.args)
        """
        self.lua_config_script = os.path.abspath(lua_config_script)
        self.export_vars = export_vars or []
        self.pre_script = pre_script
        self.post_script = post_script
        self.extra_strings = extra_strings or []
        self.work_dir = work_dir or os.path.dirname(self.lua_config_script)
        self.temp_dir = temp_dir
        self.min_lua_version = min_lua_version or "5.1.0"
        self.max_lua_version = max_lua_version or "5.4.999"
        self.lua_binary = lua_binary
        self.lua_args = lua_args or []
        self.lua_actual_version = None

        # Validate required files exist
        if not os.path.exists(self.lua_config_script):
            raise FileNotFoundError(
                f"Main config file not found: {self.lua_config_script}"
            )

        # Initialize internal state
        self._variables: Dict[str, str] = {}
        self._metadata: Dict[str, str] = {}
        self._export_list: List[str] = []

        # Initialize temporary directory
        self._setup_temp_dir()

        # Detect Lua binary
        if not self.lua_binary:
            self._detect_lua_binary()

        # Execute the Lua loader
        self._run_lua_loader()

        # Parse results
        self._parse_results()

        # Clean up temp directory
        self._cleanup()

    def _setup_temp_dir(self):
        """Setup temporary directory for storing exported variables."""
        if self.temp_dir:
            if not os.path.exists(self.temp_dir):
                raise ValueError(f"Temp directory does not exist: {self.temp_dir}")
            self.temp_dir = os.path.abspath(self.temp_dir)
        else:
            # Try to detect temp directory
            temp_dirs = [
                os.environ.get("TMPDIR"),
                "/tmp",
                os.environ.get("XDG_RUNTIME_DIR"),
            ]
            for target in temp_dirs:
                if target and os.path.exists(target):
                    try:
                        # Check if it's mounted on tmpfs
                        result = subprocess.run(
                            ["df", "-P", "-t", "tmpfs", target],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            self.temp_dir = target
                            break
                    except Exception:
                        continue
            if not self.temp_dir:
                self.temp_dir = "/tmp"

        # Create unique temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="lua-helper-", dir=self.temp_dir)
        self.meta_dir = os.path.join(self.temp_dir, "meta")
        self.data_dir = os.path.join(self.temp_dir, "data")
        os.makedirs(self.meta_dir)
        os.makedirs(self.data_dir)

    def _detect_lua_binary(self):
        """Detect appropriate Lua binary based on version requirements."""
        if self.lua_binary:
            # Use explicitly provided binary
            if not os.path.exists(self.lua_binary):
                raise FileNotFoundError(f"Lua binary not found: {self.lua_binary}")
            if self._validate_lua_version(self.lua_binary):
                self.lua_binary = os.path.abspath(self.lua_binary)
                return
            else:
                raise ValueError(
                    f"Lua binary does not meet version requirements: {self.lua_binary}"
                )

        # Probe for available Lua binaries
        lua_hints = ["lua", "lua5.4", "lua54", "lua5.3", "lua53", "lua5.2", "lua52", "lua5.1", "lua51"]
        for hint in lua_hints:
            try:
                lua_path = shutil.which(hint)
                if lua_path and self._validate_lua_version(lua_path):
                    self.lua_binary = os.path.abspath(lua_path)
                    return
            except Exception:
                continue

        raise RuntimeError("Failed to detect compatible Lua interpreter")

    def _validate_lua_version(self, lua_binary: str) -> bool:
        """Validate Lua binary version against requirements and return actual version."""
        try:
            result = subprocess.run(
                [lua_binary, "-v"], capture_output=True, text=True, timeout=5
            )
            version_match = re.match(
                r"^Lua\s+(\d+)\.(\d+)\.(\d+)", result.stderr or result.stdout
            )
            if not version_match:
                return False

            act_version = [int(x) for x in version_match.groups()]
            min_version = [int(x) for x in self.min_lua_version.split(".")]
            max_version = [int(x) for x in self.max_lua_version.split(".")]

            # Check version range
            for i, (act, min_v, max_v) in enumerate(
                zip(act_version, min_version, max_version)
            ):
                if not (min_v <= act <= max_v):
                    return False

            # Store the actual version if validation passes
            self.lua_actual_version = act_version
            return True
        except Exception:
            return False

    def _run_lua_loader(self):
        """Execute the Lua loader script with appropriate parameters."""
        # Build command line arguments
        cmd = [self.lua_binary, os.path.join(os.path.dirname(__file__), "loader.lua")]

        # Add version info
        cmd.extend(
            [
                "-ver",
                str(self.lua_actual_version[0]),
                str(self.lua_actual_version[1]),
                str(self.lua_actual_version[2]),
            ]
        )

        # Add configuration parameters
        cmd.extend(["-c", self.lua_config_script])

        # Add export variables
        for var in self.export_vars:
            cmd.extend(["-e", var])

        # Add pre script
        if self.pre_script:
            cmd.extend(["-pre", self.pre_script])

        # Add post script
        if self.post_script:
            cmd.extend(["-post", self.post_script])

        # Add extra strings
        for extra in self.extra_strings:
            cmd.extend(["-ext", extra])

        # Add work directory
        cmd.extend(["-w", self.work_dir])

        # Add temp directory
        cmd.extend(["-t", self.temp_dir])

        # Add -- separator
        cmd.append("--")

        # Add additional Lua arguments
        cmd.extend(self.lua_args)

        # Execute the command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            print(result.stdout, end="")
            print(result.stderr, end="")
            if result.returncode != 0:
                raise RuntimeError(
                    f"Lua loader failed with error code {result.returncode}"
                )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Lua loader timed out")

    def _parse_results(self):
        """Parse exported variables from temporary files."""
        # Read the list of exported variables
        try:
            self._export_list = os.listdir(self.data_dir)
        except Exception:
            self._export_list = []

        # Load each variable
        for filename in self._export_list:
            try:
                # Read data
                with open(os.path.join(self.data_dir, filename), "rb") as f:
                    self._variables[filename] = f.read().decode(
                        "utf-8", errors="ignore"
                    )

                # Read metadata
                with open(os.path.join(self.meta_dir, filename), "rb") as f:
                    self._metadata[filename] = f.read().decode("utf-8", errors="ignore")
            except Exception:
                # Skip problematic files
                continue

    def _cleanup(self):
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass

    def __getitem__(self, key: str) -> str:
        """Get item from exported variables dictionary."""
        return self._variables.get(key, "")

    def __contains__(self, key: str) -> bool:
        """Check if variable is available."""
        return key in self._metadata and self._metadata[key] != ""

    def __iter__(self):
        """Iterate over exported variable names."""
        return iter(self._variables)

    def __len__(self) -> int:
        """Get number of exported variables."""
        return len(self._variables)

    def keys(self) -> List[str]:
        """Get list of exported variable names."""
        return list(self._variables.keys())

    def values(self) -> List[str]:
        """Get list of exported variable values."""
        return list(self._variables.values())

    def items(self) -> List[tuple]:
        """Get list of (name, value) tuples."""
        return list(self._variables.items())

    def get(self, key: str, default: str = None) -> str:
        """Get variable value with default."""
        return self._variables.get(key, default)

    def get_int(self, key: str, default: int = None) -> int:
        """Get variable value as integer with defaults on type conversion error."""
        try:
            return int(self._variables.get(key, default))
        except ValueError:
            if default is not None:
                return int(default)
            raise

    def get_float(self, key: str, default: float = None) -> float:
        """Get variable value as float with defaults on type conversion error."""
        try:
            return float(self._variables.get(key, default))
        except ValueError:
            if default is not None:
                return float(default)
            raise

    def get_table_start(self, key: str) -> int:
        """Get start indexed element index of table if variable is a table and indexed (keyless) elements present, 0 if no indexed elements present"""
        if key in self._metadata:
            match = re.match(r"^table:(.*):(.*)", self._metadata[key])
            if match:
                return int(match.group(1))
        return 0

    def get_table_end(self, key: str) -> int:
        """Get end position of table if variable is a table, last indexable element is less than this number"""
        if key in self._metadata:
            match = re.match(r"^table:(.*):(.*)", self._metadata[key])
            if match:
                return int(match.group(2))
        return 0

    def get_table_seq(self, key: str) -> List[int]:
        """Get sequence of table indices if variable is a table with indexed elements."""
        start = self.get_table_start(key)
        end = self.get_table_end(key)
        if start == 0:
            return []
        return list(range(start, end))

    def __repr__(self) -> str:
        """String representation."""
        return f"PyLuaHelper({len(self._variables)} variables)"

    def __str__(self) -> str:
        """String representation."""
        return f"PyLuaHelper with {len(self._variables)} exported variables"
