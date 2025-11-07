# pycom0com

A Python wrapper for the com0com virtual serial port driver, providing an easy-to-use interface for creating and managing virtual COM port pairs on Windows

## Features

- 🚀 **Easy Installation** - Simple pip installation with automatic driver setup
- 🔧 **Complete API** - Full access to all com0com functionality
- 🛡️ **Admin Privileges Handling** - Automatic elevation when needed
- 📝 **Comprehensive Logging** - Detailed output capture and error handling
- 🔄 **Port Management** - Create, remove, and configure virtual port pairs
- ⚙️ **Parameter Control** - Fine-tune port behavior with extensive configuration options
- 🔍 **Port Discovery** - List existing ports and check busy names
- 🏷️ **Friendly Names** - Manage human-readable port names

## Installation

### Prerequisites

- Windows 7 or newer
- Python 3.7 or higher
- Administrator privileges (for driver installation and port management)

### Install from PyPI

```bash
pip install pycom0com
pycom0com-install
```

### Manual Installation

Install the Python package from git:
```bash
pip install git+https://github.com/StableKite/pycom0com
pycom0com-install
```

## Quick Start

```python
from pycom0com import Com0ComController, PortParameters

# Initialize controller
controller = Com0ComController(verbose=True)

# Create a virtual port pair
controller.install_pair(
    port_name_a="COM5",
    port_name_b="COM6",
    parameters_a=PortParameters(emu_br=True),
    parameters_b=PortParameters(emu_overrun=False)
)

# List all port pairs
pairs = controller.list_pairs()
for pair in pairs:
    print(f"Pair {pair.number}: {pair.port_a} <-> {pair.port_b}")

# Change port parameters
new_params = PortParameters(port_name="COM7", emu_noise=0.1)
controller.change_port("CNCA0", new_params)

# Remove the pair when done
controller.remove_pair(0)
```

## Complete Example

```python
from pycom0com import Com0ComController, PortParameters

def demonstrate_functionality():
    """Demonstrate full pycom0com functionality"""
    
    # Initialize with verbose output
    controller = Com0ComController(
        verbose=True,
        detail_prms=True,  # Show detailed parameters
        show_fnames=True   # Show friendly name activity
    )
    
    try:
        # 1. Check busy port names
        print("Checking busy COM ports...")
        busy_ports = controller.get_busy_names("COM?*")
        print(f"Busy ports: {busy_ports}")
        
        # 2. Create a virtual port pair with custom parameters
        print("\nCreating virtual port pair...")
        params_a = PortParameters(
            port_name="COM101",
            emu_br=True,           # Enable baud rate emulation
            emu_overrun=False,     # Disable overrun emulation
            plug_in_mode=True,     # Enable plug-in mode
            add_rtto=100           # Additional read timeout
        )
        
        params_b = PortParameters(
            port_name="COM102",
            emu_noise=0.05,        # Add 5% noise emulation
            exclusive_mode=True    # Exclusive port access
        )
        
        controller.install_pair(
            port_name_a="COM101",
            port_name_b="COM102",
            parameters_a=params_a,
            parameters_b=params_b,
            wait_timeout=10        # Wait up to 10 seconds
        )
        
        # 3. List all port pairs
        print("\nListing all port pairs...")
        pairs = controller.list_pairs()
        for pair in pairs:
            print(f"Pair {pair.number}:")
            print(f"  Port A: {pair.port_a} -> {pair.parameters_a}")
            print(f"  Port B: {pair.port_b} -> {pair.parameters_b}")
        
        # 4. Update friendly names
        print("\nUpdating friendly names...")
        controller.update_friendly_names()
        
        # 5. List friendly names
        print("\nFriendly names:")
        friendly_names = controller.list_friendly_names()
        for name_info in friendly_names:
            print(f"  {name_info.port_id}: {name_info.friendly_name}")
        
        # 6. Modify port parameters
        print("\nModifying port parameters...")
        new_params = PortParameters(
            port_name="COM201",
            emu_br=False,
            hidden_mode=True
        )
        controller.change_port("CNCA0", new_params)
        
        # 7. Demonstrate port communication (conceptual)
        print("\nPorts are ready for communication:")
        print("COM101 <-> COM102 - Virtual serial connection")
        
        # Keep ports for demonstration
        input("Press Enter to remove virtual ports...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        print("\nCleaning up...")
        controller.remove_pair(0)

if __name__ == "__main__":
    demonstrate_functionality()
```

## API Reference

### Com0ComController

Main controller class for managing virtual COM ports.

```python
controller = Com0ComController(
    silent=False,           # Suppress dialogs
    no_update=False,        # Don't update driver during install
    no_update_fnames=False, # Don't update friendly names
    show_fnames=False,      # Show friendly name activity
    detail_prms=False,      # Show detailed parameters
    verbose=False           # Enable verbose output
)
```

#### Methods

**Port Management**
- `install_pair()` - Create a new virtual port pair
- `remove_pair(pair_number)` - Remove a port pair
- `list_pairs()` - List all port pairs
- `change_port(port_id, parameters)` - Modify port parameters
- `disable_all_ports()` - Disable all ports
- `enable_all_ports()` - Enable all ports

**Driver Management**
- `preinstall_driver()` - Preinstall driver INF files
- `install_driver_only()` - Install/update driver only
- `update_driver()` - Update driver
- `reload_driver()` - Reload driver
- `uninstall_all()` - Remove all ports and driver
- `clean_inf_files()` - Clean old INF files

**Information**
- `get_busy_names(pattern)` - Get list of busy port names
- `list_friendly_names()` - Get friendly names for ports
- `update_friendly_names()` - Update friendly names

### PortParameters

Configuration class for virtual port behavior.

```python
params = PortParameters(
    port_name="COM1",       # Port name (e.g., "COM1")
    emu_br=True,            # Baud rate emulation
    emu_overrun=False,      # Overrun emulation
    emu_noise=0.1,          # Noise level (0.0-1.0)
    add_rtto=100,           # Additional read total timeout
    add_rito=50,            # Additional read interval timeout
    plug_in_mode=True,      # Plug-in mode
    exclusive_mode=False,   # Exclusive access mode
    hidden_mode=False,      # Hidden mode
    all_data_bits=True,     # All data bits mode
    cts="rts",              # CTS signal behavior
    dsr="dtr",              # DSR signal behavior
    dcd="none",             # DCD signal behavior
    ri="none",              # RI signal behavior
    real_port_name="COM5"   # Real port name for COM class
)
```

### Data Structures

**PortPairInfo**
```python
PortPairInfo(
    number=0,  # Pair number
    port_a="CNCA0",  # First port ID
    port_b="CNCB0",  # Second port ID
    parameters_a={...},  # Port A parameters
    parameters_b={...}  # Port B parameters
)
```

**CommandResult**
```python
CommandResult(
    success=True,  # Operation success
    output="Operation complete",  # Command output
    return_code=0  # Return code
)
```

**FriendlyNameInfo**
```python
FriendlyNameInfo(
    port_id="CNCA0",  # Port identifier
    friendly_name="Virtual COM Port"  # Human-readable name
)
```

## Advanced Usage

### Custom Installation Options

```python
# Silent installation without user prompts
controller = Com0ComController(silent=True)

# Install without driver updates
controller.install_pair(
    port_name_a="COM5",
    port_name_b="COM6",
    parameters_a=PortParameters(),
    parameters_b=PortParameters()
)

# Later update the driver separately
controller.install_driver_only()
```

### Error Handling

```python
from pycom0com import Com0ComController, Com0ComError, AdminRequiredError

try:
    controller = Com0ComController()
    controller.install_pair("COM5", "COM6")
    
except AdminRequiredError:
    print("Administrator privileges required. Run as admin.")
    
except Com0ComError as e:
    print(f"Com0Com error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Port Communication Example

```python
import serial
from pycom0com import Com0ComController
import threading
import time

def setup_virtual_ports():
    """Set up virtual ports for testing"""
    controller = Com0ComController(silent=True)
    
    # Create a virtual port pair
    controller.install_pair("COM501", "COM502")
    
    return controller

def serial_reader(port_name):
    """Read from a serial port"""
    try:
        with serial.Serial(port_name, 9600, timeout=1) as ser:
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"Received on {port_name}: {data}")
                time.sleep(0.1)
    except Exception as e:
        print(f"Reader error: {e}")

def serial_writer(port_name):
    """Write to a serial port"""
    try:
        with serial.Serial(port_name, 9600, timeout=1) as ser:
            for i in range(5):
                message = f"Message {i} from {port_name}\n"
                ser.write(message.encode())
                print(f"Sent: {message.strip()}")
                time.sleep(1)
    except Exception as e:
        print(f"Writer error: {e}")

# Set up virtual ports
controller = setup_virtual_ports()

# Start communication threads
reader_thread = threading.Thread(target=serial_reader, args=("COM501",))
writer_thread = threading.Thread(target=serial_writer, args=("COM502",))

reader_thread.start()
writer_thread.start()

writer_thread.join()
reader_thread.join()

# Cleanup
controller.remove_pair(0)
```

## Troubleshooting

### Common Issues

**1. Administrator Privileges Required**
```
AdminRequiredError: Administrator privileges required for this operation
```
Solution: Run your script as administrator or use an elevated command prompt.

**2. Driver Not Found**
```
Com0ComError: setup.dll not found
```
Solution: Ensure com0com is installed or use `pycom0com-install` to install it automatically.

**3. Port Already in Use**
```
Com0ComError: Port name COM5 is already used
```
Solution: Choose a different port name or check which ports are busy using `get_busy_names()`.

**4. Installation Fails**
- Check Windows Event Viewer for driver installation logs
- Ensure no antivirus is blocking driver installation
- Try running installation with `silent=False` to see detailed prompts

### Debug Mode

Enable verbose output for debugging:

```python
controller = Com0ComController(
    verbose=True,
    detail_prms=True,
    show_fnames=True
)
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup

1. Clone the repository
2. Install development dependencies:
```bash
pip install -e ".[dev]"
```
3. Run tests:
```bash
pytest
```

## License

This project is licensed under the GPL2 License

## Acknowledgments

- [com0com](https://sourceforge.net/projects/com0com/) - The virtual serial port driver this package wraps
- [pyserial](https://github.com/pyserial/pyserial) - For serial communication examples

## Support

If you encounter any problems or have questions:

1. Check the [troubleshooting](#troubleshooting) section
2. Search [existing issues](https://github.com/StableKite/pycom0com/issues)
3. Create a new issue with detailed information about your problem

---

**Note**: This package requires the com0com driver to be installed on your system. The package will attempt to install it automatically, but you may need to allow driver installation in Windows.
```