# ESP32 MicroPython Interactive Flashing Tool

A comprehensive, user-friendly Python tool for flashing MicroPython firmware to ESP32 devices with automatic device detection, firmware detection, and interactive menu navigation.

## 🚀 Features

- 🐍 **Conda Environment Management**: Automatic conda environment detection and setup guidance
- 🔍 **Automatic Device Detection**: Detects ESP32-C3, ESP32-S3, ESP32-C6, and generic ESP32 devices
- 🔬 **Current Firmware Detection**: Identifies existing firmware before flashing to prevent accidental overwrites
- ⚠️ **Overwrite Protection**: Interactive confirmation with detailed firmware information display
- 🌐 **Online Firmware Selection**: Downloads latest MicroPython firmware versions automatically
- 📁 **Local Firmware Support**: Use existing local firmware files
- ⚡ **Automated Flashing**: Handles erase and flash operations with baud rate fallback
- 🧪 **Connection Testing**: Verifies MicroPython installation after flashing
- ⌨️ **Arrow Key Navigation**: Intuitive menu navigation with persistent information display

## 📋 Supported ESP32 Devices

- **ESP32-C3**: Wi-Fi + Bluetooth 5 LE, Single Core, 160MHz
- **ESP32-S3**: Wi-Fi + Bluetooth, Dual Core, 240MHz  
- **ESP32-C6**: Wi-Fi 6 + Bluetooth 5 LE, Single Core, 160MHz
- **ESP32 (Generic)**: Wi-Fi + Bluetooth, Dual Core, 240MHz

## 🛠️ Requirements

- Python 3.7+
- Conda or Miniconda
- ESP32 development board
- USB data cable (not charge-only)
- Internet connection (for firmware downloads)

## 📦 Dependencies

The tool automatically installs required packages:
- `esptool` - ESP32 programming tool
- `pyserial` - Serial communication
- `requests` - HTTP requests for firmware downloads

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/shreyashguptas/micropython-on-esp32.git
cd micropython-on-esp32
```

### 2. Create Conda Environment
```bash
conda create -n esp32-dev python=3.11 -y
conda activate esp32-dev
```

### 3. Install Dependencies
```bash
pip install esptool pyserial requests
```

### 4. Run the Tool
```bash
python esptool.py
```

## 📖 How It Works

The tool follows this comprehensive workflow:

### 1. **Conda Environment Check**
- Verifies you're in a conda environment
- Provides setup instructions if not
- Ensures proper Python environment for ESP32 development

### 2. **Device Detection**
- Scans for connected ESP32 devices
- Identifies device model (C3, S3, C6, Generic)
- Allows manual port entry if needed
- Shows unsupported device warning for unknown variants

### 3. **Current Firmware Detection**
- Connects to ESP32 and detects existing firmware
- Identifies MicroPython, ESP-IDF, Arduino, or other firmware
- Extracts version information and platform details
- Shows raw detection output for debugging

### 4. **Firmware Overwrite Confirmation**
- Displays current firmware information persistently
- Warns about data loss when overwriting
- Shows detailed detection results while you decide
- Allows cancellation to preserve current setup

### 5. **Firmware Selection**
- Fetches latest MicroPython versions from official repository
- Offers stable and development versions
- Supports local firmware files
- Uses correct firmware URLs for each ESP32 variant

### 6. **Flashing Process**
- Erases flash memory completely
- Flashes MicroPython firmware
- Handles baud rate fallback if needed
- Provides progress feedback

### 7. **Verification**
- Tests MicroPython connection
- Verifies installation success
- Provides connection instructions

## 🎯 Usage Examples

### Basic Usage
```bash
python esptool.py
```

### Manual Port Entry
If automatic detection fails, the tool allows manual port entry:
- Enter port: `/dev/tty.usbmodem114301` (macOS/Linux)
- Enter port: `COM3` (Windows)
- Device model: `esp32c3`, `esp32s3`, `esp32c6`, or `esp32`

### Local Firmware
The tool supports using local `.bin` files:
- Place firmware files in the working directory
- Select "📁 Use local firmware file" option
- Choose from available `.bin` files

## 🔧 Menu Navigation

- **↑/↓ Arrow Keys**: Navigate through menu options
- **Enter**: Select current option
- **'q'**: Quit the program
- **Ctrl+C**: Force exit

## 📁 File Structure

```
micropython-on-esp32/
├── esptool.py              # Main interactive flashing tool
├── README.md               # This documentation
├── README_esptool.md       # Detailed tool documentation
├── test_micropython.py     # MicroPython connection test script
└── *.bin                   # Downloaded firmware files
```

## 🐛 Troubleshooting

### Device Not Detected
1. Ensure USB cable supports data (not charge-only)
2. Check device appears in `/dev/tty.*` (macOS/Linux) or `COM*` (Windows)
3. Try different USB port
4. Press RESET button on ESP32
5. Use manual port entry option

### Flashing Fails
1. Put ESP32 in boot mode (hold BOOT, press RESET, release BOOT)
2. Try different USB cable
3. Check for other programs using the serial port
4. Tool automatically retries with slower baud rate

### Connection Test Fails
1. Wait 5-10 seconds after flashing
2. Press RESET button on ESP32
3. Check port is not busy
4. Verify MicroPython is running

## 🔗 Connecting to MicroPython

After successful flashing, connect to MicroPython:

### Using Screen (Recommended)
```bash
screen /dev/tty.usbmodem114301 115200
# Exit: Ctrl+A then K, then Y
```

### Using Python Script
```bash
python test_micropython.py
```

### Using Thonny IDE
1. Install: `pip install thonny`
2. Open Thonny
3. Tools → Options → Interpreter
4. Select "MicroPython (ESP32)"
5. Set Port to your device port
6. Click "Stop/Restart backend"

## 📚 Additional Resources

- [MicroPython Official Website](https://micropython.org/)
- [ESP32 MicroPython Documentation](https://docs.micropython.org/en/latest/esp32/)
- [ESP32-C3 MicroPython Guide](https://docs.micropython.org/en/latest/esp32c3/)
- [ESP32-S3 MicroPython Guide](https://docs.micropython.org/en/latest/esp32s3/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is open source. Please check the license file for details.

## 🏷️ Version History

- **v1.0.0** (December 2024): Initial release with ESP32-C3, S3, C6 support
- Added automatic device detection
- Added firmware detection and overwrite protection
- Added interactive menu navigation
- Added comprehensive error handling

---

**Created**: December 2024  
**Compatible with**: macOS, Linux, Windows  
**ESP32 Models**: ESP32, ESP32-C3, ESP32-S3, ESP32-C6