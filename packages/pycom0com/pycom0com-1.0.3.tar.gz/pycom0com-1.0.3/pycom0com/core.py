"""
pycom0com - Python bindings for com0com virtual serial ports
"""

from pathlib import Path
from warnings import warn
from os import getcwd, chdir
from types import TracebackType
from typing import Optional, Type
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple, NamedTuple
from ctypes import byref, create_string_buffer, POINTER, windll, \
    c_bool, WinDLL, c_void_p, c_int, c_uint, c_char_p



class Com0ComError(Exception):
    """
    Base exception for com0com errors
    """

class AdminRequiredError(Com0ComError):
    """
    Administrator privileges required
    """

class Com0ComWarning(Warning):
    """
    com0com warning
    """


@dataclass(slots = True)
class PortParameters:
    """
    Virtual COM port parameters
    
    Attributes:
        port_name (Optional[str]):
            Name of the virtual port (e.g., "COM1")
        emu_br (Optional[bool]): Enable baud rate emulation
        emu_overrun (Optional[bool]): Enable overrun emulation  
        emu_noise (Optional[float]): Noise level for emulation
        add_rtto (Optional[int]): Additional read total timeout constant
        add_rito (Optional[int]): Additional read interval timeout
        plug_in_mode (Optional[bool]): Enable plug-in mode
        exclusive_mode (Optional[bool]): Enable exclusive mode
        hidden_mode (Optional[bool]): Enable hidden mode
        all_data_bits (Optional[bool]): Enable all data bits
        cts (Optional[str]): CTS signal configuration
        dsr (Optional[str]): DSR signal configuration
        dcd (Optional[str]): DCD signal configuration
        ri (Optional[str]): RI signal configuration
        real_port_name (Optional[str]): Real port name for COM class
    """

    port_name: Optional[str] = None
    emu_br: Optional[bool] = None
    emu_overrun: Optional[bool] = None
    emu_noise: Optional[float] = None
    add_rtto: Optional[int] = None
    add_rito: Optional[int] = None
    plug_in_mode: Optional[bool] = None
    exclusive_mode: Optional[bool] = None
    hidden_mode: Optional[bool] = None
    all_data_bits: Optional[bool] = None
    cts: Optional[str] = None
    dsr: Optional[str] = None
    dcd: Optional[str] = None
    ri: Optional[str] = None
    real_port_name: Optional[str] = None

    def to_string(self) -> str:
        """
        Convert parameters to com0com string format
        
        Returns:
            params_string (str): Parameters as com0com-compatible string
        """

        params = []
        
        if self.port_name is not None:
            params.append(f"PortName={self.port_name}")
        if self.emu_br is not None:
            params.append(f"EmuBR={"yes" if self.emu_br else "no"}")
        if self.emu_overrun is not None:
            params.append(f"EmuOverrun={"yes" if self.emu_overrun else "no"}")
        if self.emu_noise is not None:
            params.append(f"EmuNoise={self.emu_noise}")
        if self.add_rtto is not None:
            params.append(f"AddRTTO={self.add_rtto}")
        if self.add_rito is not None:
            params.append(f"AddRITO={self.add_rito}")
        if self.plug_in_mode is not None:
            params.append(f"PlugInMode={"yes" if self.plug_in_mode else "no"}")
        if self.exclusive_mode is not None:
            params.append(f"ExclusiveMode={"yes" if self.exclusive_mode else "no"}")
        if self.hidden_mode is not None:
            params.append(f"HiddenMode={"yes" if self.hidden_mode else "no"}")
        if self.all_data_bits is not None:
            params.append(f"AllDataBits={"yes" if self.all_data_bits else "no"}")
        if self.cts is not None:
            params.append(f"cts={self.cts}")
        if self.dsr is not None:
            params.append(f"dsr={self.dsr}")
        if self.dcd is not None:
            params.append(f"dcd={self.dcd}")
        if self.ri is not None:
            params.append(f"ri={self.ri}")
        if self.real_port_name is not None:
            params.append(f"RealPortName={self.real_port_name}")
            
        return ",".join(params) if params else "-"
    

    @classmethod
    def from_string(cls, params_str: str) -> 'PortParameters':
        """
        Create a PortParameters object from a com0com parameter string
        
        Args:
            params_str: Parameter string in "Key1=Value1,Key2=Value2" format 
        Returns:
            PortParameters: Object with parsed parameters
        """

        params = cls()
        
        if not params_str or params_str in ["-", "*"]:
            return params
            
        for part in params_str.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # Convert types and set values
                if key == "PortName":
                    params.port_name = value
                elif key == "EmuBR":
                    params.emu_br = value.lower() == "yes"
                elif key == "EmuOverrun":
                    params.emu_overrun = value.lower() == "yes"
                elif key == "EmuNoise":
                    params.emu_noise = float(value)
                elif key == "AddRTTO":
                    params.add_rtto = int(value)
                elif key == "AddRITO":
                    params.add_rito = int(value)
                elif key == "PlugInMode":
                    params.plug_in_mode = value.lower() == "yes"
                elif key == "ExclusiveMode":
                    params.exclusive_mode = value.lower() == "yes"
                elif key == "HiddenMode":
                    params.hidden_mode = value.lower() == "yes"
                elif key == "AllDataBits":
                    params.all_data_bits = value.lower() == "yes"
                elif key == "cts":
                    params.cts = value
                elif key == "dsr":
                    params.dsr = value
                elif key == "dcd":
                    params.dcd = value
                elif key == "ri":
                    params.ri = value
                elif key == "RealPortName":
                    params.real_port_name = value
                    
        return params
    

    def __repr__(self) -> str:
        """
        Return a string representation showing only non-None fields
        """

        non_none_fields = []
        for slot in getattr(self, "__slots__", []):
            value = getattr(self, slot)
            if value is not None:
                non_none_fields.append(f"{slot}={value!r}")
        
        if non_none_fields:
            return f"PortParameters({", ".join(non_none_fields)})"
        else:
            return "PortParameters()"


    def __dir__(self) -> List[str]:
        """
        Return list of attributes, filtering out None fields in interactive environments
        """

        return sorted([attr for attr in getattr(self, "__slots__", []) if getattr(self, attr, None) is not None])


class PortPairInfo(NamedTuple):
    """
    Information about a virtual port pair
    
    Attributes:
        number (int): Pair number identifier
        port_a (str): First port identifier (e.g., "CNCA0")
        port_b (str): Second port identifier (e.g., "CNCB0") 
        parameters_a (PortParameters): Parameters for first port
        parameters_b (PortParameters): Parameters for second port
    """

    number: int
    port_a: str
    port_b: str
    parameters_a: PortParameters
    parameters_b: PortParameters


@dataclass(slots = True)
class PortPair:
    """
    Pair of virtual COM ports
    """

    number: int
    port_a: str
    port_b: str
    parameters_a: PortParameters
    parameters_b: PortParameters

    def __str__(self):
        return f"Pair {self.number}: {self.port_a} <-> {self.port_b}"
    
    def to_info(self) -> PortPairInfo:
        """
        Convert to NamedTuple version

        port_pair_info (PortPairInfo): NamedTuple version of structure
        """

        return PortPairInfo(
            number = self.number,
            port_a = self.port_a,
            port_b = self.port_b,
            parameters_a = self.parameters_a,
            parameters_b = self.parameters_b
        )


class CommandResult(NamedTuple):
    """
    Result of a com0com command execution
    
    Attributes:
        success (bool): Whether command completed successfully
        output (str): Command output text
        return_code (int): Process return code
    """

    success: bool
    output: str
    return_code: int


class FriendlyNameInfo(NamedTuple):
    """
    Friendly name information for a port
    
    Attributes:
        port_id (str): Port identifier (e.g., "CNCA0")
        friendly_name (str): Human-readable port name
    """

    port_id: str
    friendly_name: str


class _Com0ComOutputInterceptor:
    """
    Intercepts com0com DLL output to capture it in memory
    """
    
    def __init__(self, verbose: bool = True):
        self.kernel32 = WinDLL("kernel32")
        self.original_stdout = None
        self.original_stderr = None
        self.read_handle = None
        self.write_handle = None
        self.output_buffer = []
        
        # Configure function types
        self.kernel32.CreatePipe.restype = c_bool
        self.kernel32.CreatePipe.argtypes = [POINTER(c_void_p), POINTER(c_void_p), c_void_p, c_uint]
        
        self.kernel32.SetStdHandle.restype = c_bool
        self.kernel32.SetStdHandle.argtypes = [c_uint, c_void_p]
        
        self.kernel32.GetStdHandle.restype = c_void_p
        self.kernel32.GetStdHandle.argtypes = [c_uint]
        
        self.kernel32.ReadFile.restype = c_bool
        self.kernel32.ReadFile.argtypes = [c_void_p, c_void_p, c_uint, POINTER(c_uint), c_void_p]

        if verbose:
            self.get_output = self._get_output_with_print


    def __enter__(self):
        """
        Start output interception
        
        Returns:
            self_instance (Com0ComOutputInterceptor):
                Self instance for context management
        """

        self._setup_pipes()

        return self


    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
        ) -> bool:
        """
        Stop output interception and restore original handles
        
        Args:
            exc_type (Optional[Type[BaseException]]):
                Exception type if exception occurred
            exc_val (Optional[BaseException]):
                Exception value if exception occurred  
            exc_tb (Optional[TracebackType]):
                Exception traceback if exception occurred
            
        Returns:
            is_accessible (bool): False to not suppress exceptions
        """

        self._restore_std_handles()
        output = self._read_remaining_output()
        self.output_buffer.append(output)

        return False


    def _setup_pipes(self):
        """
        Create pipes for output interception
        """

        # Create anonymous pipe
        read_handle = c_void_p()
        write_handle = c_void_p()
        
        if not self.kernel32.CreatePipe(
                byref(read_handle),
                byref(write_handle),
                None,  # Default security
                0  # Default buffer size
            ):
            raise Com0ComError("Failed to create output interception pipe")
        
        self.read_handle = read_handle
        self.write_handle = write_handle
        
        # Save original handles
        self.original_stdout = self.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        self.original_stderr = self.kernel32.GetStdHandle(-12)  # STD_ERROR_HANDLE
        
        # Set our pipes as standard outputs
        self.kernel32.SetStdHandle(-11, self.write_handle)  # STD_OUTPUT_HANDLE
        self.kernel32.SetStdHandle(-12, self.write_handle)  # STD_ERROR_HANDLE


    def _restore_std_handles(self):
        """
        Restore original standard handles
        """

        if self.original_stdout:
            self.kernel32.SetStdHandle(-11, self.original_stdout)
        if self.original_stderr:
            self.kernel32.SetStdHandle(-12, self.original_stderr)
        
        # Close pipe handles
        if self.write_handle:
            self.kernel32.CloseHandle(self.write_handle)


    def _read_remaining_output(self) -> str:
        """
        Read all remaining output from pipe
        
        Returns:
            output (str): Remaining output text
        """

        if not self.read_handle:
            return ""
        
        output = ""
        buffer = create_string_buffer(4096)
        bytes_read = c_uint(0)
        
        while True:
            # Try to read data
            if self.kernel32.ReadFile(
                self.read_handle,
                buffer,
                4096,
                byref(bytes_read),
                None
            ) and bytes_read.value > 0:
                output += buffer.raw[:bytes_read.value].decode("utf-8", errors = "ignore")
            else:
                break
        
        # Close read handle
        if self.read_handle:
            self.kernel32.CloseHandle(self.read_handle)
            self.read_handle = None
        
        return output


    def get_output(self) -> str:
        """
        Get all intercepted output
        
        Returns:
            output (str): Combined output text
        """

        output = "".join(self.output_buffer)
        self.output_buffer.clear()

        return output


    def _get_output_with_print(self) -> str:
        """
        Get intercepted output and print it
        
        Returns:
            output (str): Combined output text
        """

        output = "".join(self.output_buffer)
        self.output_buffer.clear()
        print(output)

        return output



class Com0ComController:
    """
    Controller for managing com0com virtual serial ports
    
    Args:
        silent (bool): Suppress dialogs if possible
        no_update (bool): Do not update driver during install
        no_update_fnames (bool): Do not update friendly names  
        show_fnames (bool): Show friendly names activity
        detail_prms (bool): Show detailed parameters
        verbose (bool): Enable verbose output
    """
    
    def __init__(
            self, 
            silent: bool = False, 
            no_update: bool = False,
            no_update_fnames: bool = False,
            show_fnames: bool = False,
            detail_prms: bool = False,
            verbose: bool = False
        ):
        self.bin_path = Path(__file__).parent / "bin"
        self.silent = silent
        self.no_update = no_update
        self.no_update_fnames = no_update_fnames
        self.show_fnames = show_fnames
        self.detail_prms = detail_prms
        self._interceptor = _Com0ComOutputInterceptor(verbose)
        self.setup_dll = self._load_setup_dll()


    def _load_setup_dll(self) -> WinDLL:
        """
        Load setup.dll from bin directory
        
        Returns:
            win_dll (WinDLL): Loaded setup.dll instance
            
        Raises:
            Com0ComError: If DLL not found or cannot be loaded
        """

        dll_path = self.bin_path / "setup.dll"
        if not dll_path.exists():
            raise Com0ComError(f"setup.dll not found. Install driver using \"pycom0com-_install\"")
        
        try:
            # Load DLL with explicit path
            dll = WinDLL(str(dll_path))
            # Configure MainA signature according to setup.cpp
            dll.MainA.argtypes = [c_char_p, c_char_p]
            dll.MainA.restype = c_int
            return dll
        except Exception as e:
            raise Com0ComError(f"Error loading setup.dll: {e}")


    def _is_admin(self) -> bool:
        """
        Check if current process has administrator privileges
        
        Returns:
            is_admin (bool): True if running as administrator
        """

        try:
            return windll.shell32.IsUserAnAdmin()
        except:
            return False


    def _build_command_line(self, command: str, wait_timeout: int = 0) -> str:
        """
        Build command line with options
        
        Args:
            command (str): Base command to execute
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_line_options (str): Full command line with options
        """

        options = []
        
        if self.silent:
            options.append("--silent")
        if self.no_update:
            options.append("--no-update")
        if self.no_update_fnames:
            options.append("--no-update-fnames")
        if self.show_fnames:
            options.append("--show-fnames")
        if self.detail_prms:
            options.append("--detail-prms")
        if wait_timeout > 0:
            options.append(f"--wait {wait_timeout}")
            
        return " ".join(options + [command]) if options else command


    def _run_command(self, command: str, wait_timeout: int = 0, demand_admin: bool = True) -> Tuple[int, str]:
        """
        Execute command through setup.dll with output interception
        
        Args:
            command (str): Command to execute
            wait_timeout (int): Wait timeout in seconds
            demand_admin (bool): demand administrator rights
        Returns:
            code_and_output (Tuple[int, str]):
                Return code and command output
            
        Raises:
            AdminRequiredError:
                If administrator privileges required but not available
        """

        if demand_admin and not self._is_admin():
            raise AdminRequiredError("Administrator privileges required for this operation")

        # Build full command with output redirection
        full_command = self._build_command_line(command, wait_timeout)
        
        # Change current directory to bin folder
        original_cwd = getcwd()
        chdir(str(self.bin_path))
        
        # Use output interceptor to capture console output
        with self._interceptor:
            result = self.setup_dll.MainA(b"pycom0com", full_command.encode("utf-8"))

        output = self._interceptor.get_output()
        
        # Return to original directory
        chdir(original_cwd)

        return result, output


    def _handle_command_result(self, result: int, output: str, operation: str) -> str:
        """
        Handle command execution result and generate exceptions or warnings
        
        Args:
            result (int): Command return code
            output (str): Command output text
            operation (str): Description of operation being performed
        Returns:
            cleaned_text (str): Cleaned output text
            
        Raises:
            Com0ComError: If command failed with error
        """

        # Clean output from dialog messages
        pos = output.find("\r\nDIALOG: {\r\n")
        if pos != -1:
            output = output[13:output.rfind("}") - 2].replace("\r\n", " ")

        # Check for critical errors
        lines = output.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for error messages
            if "ERROR:" in line.upper():
                error_msg = line.split("ERROR:", 1)[1].strip()
                raise Com0ComError(f"com0com error during {operation}: {error_msg}")
            
            # Check for critical problems
            if "cannot find" in line.lower() or "failed" in line.lower():
                if "file" in line.lower():
                    raise Com0ComError(f"File error during {operation}: {line}")

        # Handle return codes
        if result == 0:
            # Success
            return output
        elif result == 1:
            # Warning - operation completed with caveats
            warn(f"Warning during {operation}: {output}", Com0ComWarning)
            return output
        else:
            # Critical error
            raise Com0ComError(f"Failed to execute {operation}. Error code: {result}. Output: {output}")


    def install_pair(
            self,
            port_name_a: Optional[str] = None,
            port_name_b: Optional[str] = None,
            pair_number: Optional[int] = None,
            parameters_a: Optional[PortParameters] = None,
            parameters_b: Optional[PortParameters] = None,
            wait_timeout: int = 0
        ) -> CommandResult:
        """
        Install a pair of virtual ports
        
        Args:
            port_name_a (Optional[str]): Name for first port
            port_name_b (Optional[str]): Name for second port  
            pair_number (Optional[int]): Specific pair number to use
            parameters_a (Optional[PortParameters]):
                Parameters for first port
            parameters_b (Optional[PortParameters]):
                Parameters for second port
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        # Prepare port parameters
        if parameters_a is None:
            parameters_a = PortParameters()
        if parameters_b is None:
            parameters_b = PortParameters()
            
        # Set port names if provided
        if port_name_a is not None:
            parameters_a.port_name = port_name_a
        if port_name_b is not None:
            parameters_b.port_name = port_name_b
            
        params_a_str = parameters_a.to_string()
        params_b_str = parameters_b.to_string()
        
        if pair_number is not None:
            cmd = f"install {pair_number} \"{params_a_str}\" \"{params_b_str}\""
        else:
            cmd = f"install \"{params_a_str}\" \"{params_b_str}\""
        
        result, output = self._run_command(cmd, wait_timeout)
        cleaned_output = self._handle_command_result(result, output, "port pair installation")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def remove_pair(self, pair_number: int, wait_timeout: int = 0) -> CommandResult:
        """
        Remove a port pair
        
        Args:
            pair_number (int): Number of pair to remove
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command(f"remove {pair_number}", wait_timeout)
        cleaned_output = self._handle_command_result(result, output, f"port pair {pair_number} removal")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def list_pairs(self) -> List[PortPairInfo]:
        """
        Get list of all port pairs
        
        Returns:
            pairs_list (List[PortPairInfo]):
                List of port pair information
        """

        result, output = self._run_command("list", demand_admin = False)
        cleaned_output = self._handle_command_result(result, output, "port list retrieval")

        pairs = self._parse_list_output(cleaned_output)
        # Convert to named tuples for fixed field names
        return [
            PortPairInfo(
                number = pair.number,
                port_a = pair.port_a,
                port_b = pair.port_b,
                parameters_a = pair.parameters_a,
                parameters_b = pair.parameters_b
            )
            for pair in pairs
        ]


    def _parse_list_output(self, output: str) -> List[PortPair]:
        """
        Parse output of list command
        
        Args:
            output (str): Raw output from list command
        Returns:
            parsed_pairs (List[PortPair]): Parsed port pairs
        """

        pairs = []
        lines = output.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for port lines (CNCA0, CNCB0 etc.)
            if line.startswith("CNCA") or line.startswith("CNCB"):
                parts = line.split()
                if len(parts) >= 2:
                    port_id = parts[0]  # CNCA0 or CNCB0
                    pair_num = int(port_id[4:])  # extract number
                    is_port_a = port_id.startswith("CNCA")
                    
                    # Find existing pair or create new one
                    pair = next((p for p in pairs if p.number == pair_num), None)
                    if not pair:
                        pair = PortPair(pair_num, "", "", PortParameters(), PortParameters())
                        pairs.append(pair)
                    
                    # Parse parameters
                    params_str = " ".join(parts[1:])
                    params = self._parse_parameters(params_str)
                    
                    if is_port_a:
                        pair.port_a = port_id
                        pair.parameters_a = params
                    else:
                        pair.port_b = port_id
                        pair.parameters_b = params
        
        return pairs


    def _parse_parameters(self, params_str: str) -> PortParameters:
        """
        Parse port parameter string
        
        Args:
            params_str (str): Parameter string from com0com
        Returns:
            PortParameters: Parsed parameters object
        """

        return PortParameters.from_string(params_str)


    def change_port(self, port_id: str, parameters: PortParameters, wait_timeout: int = 0) -> CommandResult:
        """
        Change port parameters
        
        Args:
            port_id (str): Port identifier to change
            parameters (PortParameters): New port parameters
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        params_str = parameters.to_string()
        result, output = self._run_command(f"change {port_id} \"{params_str}\"", wait_timeout, demand_admin = False)
        cleaned_output = self._handle_command_result(result, output, f"port {port_id} modification")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def disable_all_ports(self, wait_timeout: int = 0) -> CommandResult:
        """
        Disable all ports in current hardware profile
        
        Args:
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command("disable all", wait_timeout)
        cleaned_output = self._handle_command_result(result, output, "port disabling")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def enable_all_ports(self, wait_timeout: int = 0) -> CommandResult:
        """
        Enable all ports in current hardware profile
        
        Args:
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command("enable all", wait_timeout, demand_admin = False)
        cleaned_output = self._handle_command_result(result, output, "port enabling")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def preinstall_driver(self, wait_timeout: int = 0) -> CommandResult:
        """
        Preinstall driver INF files
        
        Args:
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command("preinstall", wait_timeout)
        cleaned_output = self._handle_command_result(result, output, "driver preinstallation")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def update_driver(self, wait_timeout: int = 0) -> CommandResult:
        """
        Update driver
        
        Args:
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command("update", wait_timeout)
        cleaned_output = self._handle_command_result(result, output, "driver update")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def reload_driver(self, wait_timeout: int = 0) -> CommandResult:
        """
        Reload driver
        
        Args:
            wait_timeout (int): Wait timeout in seconds
            
        Returns:
            command_result (CommandResult): Command execution result
        """
        result, output = self._run_command("reload", wait_timeout)
        cleaned_output = self._handle_command_result(result, output, "driver reload")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def uninstall_all(self, wait_timeout: int = 0) -> CommandResult:
        """
        Remove all ports and driver
        
        Args:
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command("uninstall", wait_timeout)
        cleaned_output = self._handle_command_result(result, output, "complete uninstallation")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def clean_inf_files(self, wait_timeout: int = 0) -> CommandResult:
        """
        Clean old INF files
        
        Args:
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command("infclean", wait_timeout, demand_admin = False)
        cleaned_output = self._handle_command_result(result, output, "INF file cleanup")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def get_busy_names(self, pattern: str = "COM?*") -> List[str]:
        """
        Get list of busy names matching pattern via DLL
        
        Args:
            pattern (str): Pattern to match names against
        Returns:
            names_list (List[str]): List of busy port names
        """

        result, output = self._run_command(f"busynames {pattern}", demand_admin = False)
        cleaned_output = self._handle_command_result(result, output, "busy names retrieval")
        
        # Parse output - each line contains one busy name
        busy_names = []
        for line in cleaned_output.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("ComDB:") and not line.startswith("ERROR"):
                busy_names.append(line)
        
        return busy_names


    def update_friendly_names(self, wait_timeout: int = 0) -> CommandResult:
        """
        Update friendly names
        
        Args:
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command("updatefnames", wait_timeout, demand_admin = False)
        cleaned_output = self._handle_command_result(result, output, "friendly names update")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )


    def list_friendly_names(self) -> List[FriendlyNameInfo]:
        """
        Get list of friendly names via DLL
        
        Returns:
            names_list (List[FriendlyNameInfo]):
                List of port friendly name information
        """

        result, output = self._run_command("listfnames", demand_admin = False)
        cleaned_output = self._handle_command_result(result, output, "friendly names retrieval")
        
        # Parse output in format "port_id: friendly_name"
        names = []
        for line in cleaned_output.strip().split("\n"):
            space_pos = line.find(' ')
            if space_pos != -1:
                port_id = line[:space_pos]
                friendly_name = line[space_pos + 14:-1]
                # Ignore service lines
                if port_id and not port_id.startswith("ComDB") and not port_id.startswith("ERROR"):
                    names.append(FriendlyNameInfo(
                        port_id = port_id,
                        friendly_name = friendly_name
                    ))
        
        return names


    def install_driver_only(self, wait_timeout: int = 0) -> CommandResult:
        """
        Install/update driver only without creating ports
        
        Args:
            wait_timeout (int): Wait timeout in seconds
        Returns:
            command_result (CommandResult): Command execution result
        """

        result, output = self._run_command("install", wait_timeout)
        cleaned_output = self._handle_command_result(result, output, "driver installation/update")
        
        return CommandResult(
            success = result == 0,
            output = cleaned_output,
            return_code = result
        )



if __name__ == "__main__":
    """
    Practical example and test of Com0ComController functionality
    Creates virtual port pairs, tests operations, and cleans up everything
    """

    from sys import exit

    print("=== Com0Com Virtual Port Management Test ===\n")
    
    # Initialize controller
    try:
        controller = Com0ComController(verbose = False)
        print("✓ Com0ComController initialized successfully")
    except Com0ComError as e:
        print(f"✗ Failed to initialize controller: {e}")
        print("  Make sure com0com is installed and setup.dll is in bin folder")
        exit(-1)
    
    # Check admin rights
    if not controller._is_admin():
        print("✗ Administrator privileges required for this test")
        print("  Please run the script as administrator")
        exit(-1)
    
    # Store created pairs for cleanup
    created_pairs = []
    
    try:
        print("\n1. Getting current port pairs list:")
        current_pairs = controller.list_pairs()
        print(f"   Found {len(current_pairs)} existing port pairs")
        for pair in current_pairs:
            print(f"     {pair.port_a} <-> {pair.port_b}")
        
        # Find available pair number
        existing_numbers = {pair.number for pair in current_pairs}
        test_pair_number = 0
        while test_pair_number in existing_numbers:
            test_pair_number += 1
        
        print(f"\n2. Creating test port pair with number {test_pair_number}:")
        
        # Create port parameters for testing
        params_a = PortParameters(
            port_name = f"COM{test_pair_number * 2 + 1}",  # Use odd numbers for port A
            emu_br = True,
            emu_overrun = False,
            plug_in_mode = True
        )
        
        params_b = PortParameters(
            port_name = f"COM{test_pair_number * 2 + 2}",  # Use even numbers for port B  
            emu_br = True,
            emu_noise = 0.1,
            exclusive_mode = False
        )
        
        print(f"   Port A: {params_a!r}")
        print(f"   Port B: {params_b!r}")
        
        # Install the pair
        result = controller.install_pair(
            pair_number = test_pair_number,
            parameters_a = params_a,
            parameters_b = params_b,
            wait_timeout = 5
        )
        
        if result.success:
            print("   ✓ Port pair created successfully")
            created_pairs.append(test_pair_number)
        else:
            print(f"   ✗ Failed to create port pair: {result.output}")
            exit(-1)
        
        print("\n3. Verifying port pair creation:")
        updated_pairs = controller.list_pairs()
        test_pair = next((p for p in updated_pairs if p.number == test_pair_number), None)
        
        if test_pair:
            print(f"   ✓ Found created pair: {test_pair.port_a} <-> {test_pair.port_b}")
            print(f"     Port A params: {test_pair.parameters_a}")
            print(f"     Port B params: {test_pair.parameters_b}")
        else:
            print("   ✗ Created pair not found in list")
            exit(-1)
        
        print("\n4. Testing port modification:")
        # Modify port A parameters
        new_params = PortParameters(
            emu_overrun = True,
            emu_noise = 0.2,
            plug_in_mode = False
        )
        
        result = controller.change_port(
            port_id = test_pair.port_a,
            parameters = new_params,
            wait_timeout = 3
        )
        
        if result.success:
            print(f"   ✓ Port {test_pair.port_a} modified successfully")
        else:
            print(f"   ✗ Failed to modify port: {result.output}")
        
        print("\n5. Testing friendly names operations:")
        # Update friendly names
        result = controller.update_friendly_names(wait_timeout = 3)
        if result.success:
            print("   ✓ Friendly names updated successfully")
        
        # List friendly names
        friendly_names = controller.list_friendly_names()
        test_friendly_names = [
            name for name in friendly_names if test_pair.port_a in name.port_id or test_pair.port_b in name.port_id
        ]
        
        if test_friendly_names:
            print("   Found friendly names for test ports:")
            for name_info in test_friendly_names:
                print(f"     {name_info.port_id}: {name_info.friendly_name}")
        else:
            print("   No friendly names found for test ports")
        
        print("\n6. Testing busy names detection:")
        busy_names = controller.get_busy_names("COM*")
        test_busy = [name for name in busy_names 
                    if name in [f"COM{test_pair_number * 2 + 1}", f"COM{test_pair_number * 2 + 2}"]]
        
        if test_busy:
            print("   Test port names found in busy list:")
            for name in test_busy:
                print(f"     {name}")
        else:
            print("   Test port names not found in busy list (might be virtual only)")
        
        print("\n7. Testing disable/enable operations:")
        # Disable all ports
        result = controller.disable_all_ports(wait_timeout=3)
        if result.success:
            print("   ✓ All ports disabled successfully")
            # Re-enable all ports
            result = controller.enable_all_ports(wait_timeout=3)
            if result.success:
                print("   ✓ All ports enabled successfully")
            else:
                print("   ✗ Failed to enable ports")
        else:
            print("   ✗ Failed to disable ports")
        
        # Test completed successfully
        print(f"\n✓ All tests completed successfully!")
        
    except Com0ComError as e:
        print(f"\n✗ Error during testing: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    finally:
        # Cleanup: remove all created pairs
        print(f"\n8. Cleanup: Removing test port pairs...")
        for pair_number in created_pairs:
            try:
                result = controller.remove_pair(pair_number, wait_timeout=3)
                if result.success:
                    print(f"   ✓ Removed port pair {pair_number}")
                else:
                    print(f"   ✗ Failed to remove port pair {pair_number}: {result.output}")
            except Exception as e:
                print(f"   ✗ Error removing pair {pair_number}: {e}")
        
        # Final verification
        final_pairs = controller.list_pairs()
        remaining_test_pairs = [p for p in final_pairs if p.number in created_pairs]
        
        if not remaining_test_pairs:
            print("   ✓ All test port pairs successfully removed")
        else:
            print(f"   ✗ {len(remaining_test_pairs)} test port pairs remain in system")
            for pair in remaining_test_pairs:
                print(f"     {pair.port_a} <-> {pair.port_b}")
        
        print(f"\n=== Test completed ===")
        print(f"Created and removed {len(created_pairs)} port pairs")