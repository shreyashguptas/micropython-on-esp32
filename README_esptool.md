# ESP32 MicroPython Interactive Flashing Tool

## Overview

The `esptool.py` script provides an interactive, menu-driven interface for flashing MicroPython to ESP32 devices. It automatically handles conda environment management, device detection, firmware selection, and the flashing process.

## Features

- 🐍 **Conda Environment Selection**: Choose from existing environments or create new ones
- 🔍 **Automatic Device Detection**: Automatically detects connected ESP32 devices
- 🔬 **Current Firmware Detection**: Identifies existing firmware before flashing
- ⚠️ **Overwrite Protection**: Warns before overwriting existing installations
- 🌐 **Online Firmware Selection**: Download latest MicroPython firmware versions
- 📁 **Local Firmware Support**: Use existing local firmware files
- ⚡ **Automated Flashing**: Handles erase and flash operations
- 🧪 **Connection Testing**: Verifies MicroPython installation
- ⌨️ **Arrow Key Navigation**: Intuitive menu navigation

## Usage

### Basic Usage

```bash
cd ~/Documents/esp-tinkering
python esptool.py
```

### What the Script Does

1. **Conda Environment Check**: 
   - Checks if you're already in a conda environment
   - If not, provides setup instructions and exits
   - If yes, continues with ESP32 detection

2. **Device Detection**:
   - Scans for connected ESP32 devices
   - Identifies device model (ESP32, ESP32-C3, ESP32-S3, ESP32-C6)
   - Allows manual port entry if needed

3. **Current Firmware Detection**:
   - Automatically detects what firmware is currently installed
   - Identifies MicroPython, ESP-IDF, Arduino, or other firmware
   - Shows version information and platform details

4. **Firmware Overwrite Confirmation**:
   - Warns user about overwriting existing firmware
   - Shows detailed information about current installation
   - Allows user to cancel if they want to keep current firmware

5. **Firmware Selection**:
   - Fetches latest MicroPython versions from web
   - Allows selection of stable/development versions
   - Supports local firmware files

6. **Flashing Process**:
   - Erases flash memory
   - Flashes MicroPython firmware
   - Handles baud rate fallback if needed

7. **Verification**:
   - Tests MicroPython connection
   - Provides connection instructions

## Menu Navigation

- **↑/↓ Arrow Keys**: Navigate through menu options
- **Enter**: Select current option
- **'q'**: Quit the program
- **Ctrl+C**: Force exit

## Supported Devices

- ESP32 (Generic)
- ESP32-C3
- ESP32-S3
- ESP32-C6

## Requirements

- Python 3.7+
- Conda or Miniconda
- ESP32 development board
- USB data cable (not charge-only)

## Dependencies

The script automatically installs required packages:
- `esptool` - ESP32 flashing tool
- `pyserial` - Serial communication
- `requests` - HTTP requests for firmware downloads

## Troubleshooting

### No Devices Detected
- Ensure ESP32 is connected via USB
- Check cable supports data (not charge-only)
- Try different USB port
- Press RESET button on ESP32

### Flashing Fails
- Try different USB cable
- Use different USB port
- Press RESET button before flashing
- Script automatically tries slower baud rate

### Environment Issues
- Ensure conda is installed and in PATH
- Create new environment if existing ones have issues
- Script will install required packages automatically

## Example Output

```
🚀 ESP32 MicroPython Flashing Tool
==================================================

============================================================
  🐍 ARE YOU DOING THIS IN A CONDA ENVIRONMENT? 🐍
============================================================
✅ You are currently in conda environment: esp32-dev
✅ Proceeding with ESP32 device detection...

🔍 Detecting ESP32 devices...
📋 Found 1 ESP32 device(s)

==================================================
  Select ESP32 Device
==================================================
  ▶ /dev/tty.usbmodem114301 (ESP32-C3)
    ➕ Enter port manually
==================================================

🌐 Fetching available MicroPython firmware versions...

==================================================
  Select MicroPython Firmware for ESP32-C3
==================================================
  ▶ esp32c3-20241220-v1.26.1.bin (Latest Stable)
    esp32c3-20241220-v1.26.1.bin (Previous Stable)
    esp32c3-20241220-v1.26.1.bin (Development)
    📁 Use local firmware file
==================================================

⚡ Flashing MicroPython to /dev/tty.usbmodem114301...
🧹 Erasing flash memory...
✅ Flash erased successfully
📤 Flashing MicroPython firmware...
✅ MicroPython flashed successfully!

🧪 Testing MicroPython connection on /dev/tty.usbmodem114301...
✅ MicroPython connection successful!

🎉 MicroPython installation completed successfully!
📁 Working directory: /Users/user/Documents/esp-tinkering
📱 Device: /dev/tty.usbmodem114301 (esp32c3)
💾 Firmware: esp32c3-20241220-v1.26.1.bin

🔗 To connect to MicroPython:
   screen /dev/tty.usbmodem114301 115200
   # Or use Thonny IDE with port: /dev/tty.usbmodem114301
```

### If Not in Conda Environment

```
============================================================
  🐍 ARE YOU DOING THIS IN A CONDA ENVIRONMENT? 🐍
============================================================
❌ You are NOT in a conda environment!

📋 You need to set up a conda environment first.

🔧 Here are the commands you need to run:
--------------------------------------------------
# Create a new conda environment for ESP32 development
conda create -n esp32-dev python=3.11 -y

# Activate the environment
conda activate esp32-dev

# Install required packages
pip install esptool pyserial requests

# Then run this script again
python esptool.py
--------------------------------------------------

==================================================
  Are you already in a conda environment?
==================================================
  ▶ Yes, I'm already in a conda environment
    No, I need to set up conda first
==================================================
```

## Next Steps

After successful flashing:

1. **Connect to MicroPython**:
   ```bash
   screen /dev/tty.usbmodem114301 115200
   ```

2. **Test basic functionality**:
   ```python
   import machine
   import time
   
   # Blink built-in LED
   led = machine.Pin(8, machine.Pin.OUT)
   for i in range(10):
       led.on()
       time.sleep(0.5)
       led.off()
       time.sleep(0.5)
   ```

3. **Start your MicroPython projects**!

---

**Created**: December 2024  
**Compatible with**: macOS, Linux, Windows  
**ESP32 Models**: ESP32, ESP32-C3, ESP32-S3, ESP32-C6