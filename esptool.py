#!/usr/bin/env python3
"""
Interactive ESP32 MicroPython Flashing Tool
Provides a menu-driven interface for flashing MicroPython to ESP32 devices
"""

import os
import sys
import subprocess
import json
import requests
import time
import glob
from pathlib import Path

# Check if required packages are installed
def check_dependencies():
    """Check and install required dependencies"""
    required_packages = ['requests', 'esptool']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        for package in missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        print("✅ Dependencies installed successfully!")

class MenuSelector:
    """Interactive menu selector with arrow key navigation"""
    
    def __init__(self):
        self.current_index = 0
        self.items = []
        self.title = ""
    
    def display_menu(self, title, items, current_index=0):
        """Display interactive menu"""
        self.title = title
        self.items = items
        self.current_index = current_index
        
        while True:
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print(f"\n{'='*60}")
            print(f"  {title}")
            print(f"{'='*60}")
            
            for i, item in enumerate(items):
                if i == current_index:
                    print(f"  ▶ {item}")
                else:
                    print(f"    {item}")
            
            print(f"\n{'='*60}")
            print("  Use ↑/↓ arrows to navigate, Enter to select, 'q' to quit")
            print(f"{'='*60}")
            
            # Get user input
            try:
                import tty
                import termios
                
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                    
                    if ch == '\x1b':  # ESC sequence
                        ch += sys.stdin.read(2)
                    
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
                if ch == '\x1b[A':  # Up arrow
                    current_index = (current_index - 1) % len(items)
                elif ch == '\x1b[B':  # Down arrow
                    current_index = (current_index + 1) % len(items)
                elif ch == '\r' or ch == '\n':  # Enter
                    return current_index
                elif ch == 'q' or ch == '\x03':  # 'q' or Ctrl+C
                    print("\nExiting...")
                    sys.exit(0)
                    
            except (ImportError, OSError):
                # Fallback for systems without termios
                print("\nArrow key navigation not available. Using number selection:")
                for i, item in enumerate(items):
                    print(f"  {i+1}. {item}")
                
                while True:
                    try:
                        choice = input(f"\nSelect option (1-{len(items)}, 'q' to quit): ").strip()
                        if choice.lower() == 'q':
                            sys.exit(0)
                        choice_num = int(choice) - 1
                        if 0 <= choice_num < len(items):
                            return choice_num
                        else:
                            print(f"Please enter a number between 1 and {len(items)}")
                    except ValueError:
                        print("Please enter a valid number")
                    except KeyboardInterrupt:
                        print("\nExiting...")
                        sys.exit(0)

class ESPToolManager:
    """Main ESP32 flashing manager"""
    
    def __init__(self):
        self.menu = MenuSelector()
        self.device_port = None
        self.device_model = None
        self.firmware_file = None
        self.working_dir = Path.home() / "Documents" / "esp-tinkering"
        
    def ensure_working_directory(self):
        """Ensure working directory exists"""
        self.working_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(self.working_dir)
        print(f"✅ Working directory: {self.working_dir}")
    
    def check_conda_environment(self):
        """Check if user is in a conda environment and provide setup instructions if not"""
        print("\n" + "="*60)
        print("  🐍 ARE YOU DOING THIS IN A CONDA ENVIRONMENT? 🐍")
        print("="*60)
        
        # Check if we're in a conda environment
        conda_env = os.environ.get('CONDA_DEFAULT_ENV')
        
        if conda_env and conda_env != 'base':
            print(f"✅ You are currently in conda environment: {conda_env}")
            print("✅ Proceeding with ESP32 device detection...")
            return True
        else:
            print("❌ You are NOT in a conda environment!")
            print("\n📋 You need to set up a conda environment first.")
            print("\n🔧 Here are the commands you need to run:")
            print("-" * 50)
            print("# Create a new conda environment for ESP32 development")
            print("conda create -n esp32-dev python=3.11 -y")
            print("")
            print("# Activate the environment")
            print("conda activate esp32-dev")
            print("")
            print("# Install required packages")
            print("pip install esptool pyserial requests")
            print("")
            print("# Then run this script again")
            print("python esptool.py")
            print("-" * 50)
            
            # Ask if they want to continue anyway
            options = ["Yes, I'm already in a conda environment", "No, I need to set up conda first"]
            selected_index = self.menu.display_menu(
                "Are you already in a conda environment?", 
                options
            )
            
            if selected_index == 0:
                print("✅ Continuing with ESP32 device detection...")
                return True
            else:
                print("\n👋 Please set up your conda environment first, then run this script again.")
                print("📝 Copy and paste the commands above to get started.")
                return False
    
    def detect_esp32_devices(self):
        """Detect connected ESP32 devices"""
        print("\n🔍 Detecting ESP32 devices...")
        
        # Get list of serial ports
        if os.name == 'posix':  # macOS/Linux
            ports = glob.glob('/dev/tty.*')
        else:  # Windows
            ports = glob.glob('COM*')
        
        esp32_ports = []
        device_info = []
        
        for port in ports:
            # Skip non-ESP32 ports (but allow usbmodem as that's common for ESP32)
            if any(skip in port.lower() for skip in ['bluetooth', 'debug']) and 'usbmodem' not in port.lower():
                continue
            
            # Try to detect ESP32 chip
            try:
                result = subprocess.run([
                    'esptool', '--port', port, 'chip-id'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    esp32_ports.append(port)
                    # Parse chip type from output
                    output = result.stdout.lower()
                    if 'esp32-c3' in output or 'esp32c3' in output:
                        device_info.append(f"{port} (ESP32-C3)")
                    elif 'esp32-s3' in output or 'esp32s3' in output:
                        device_info.append(f"{port} (ESP32-S3)")
                    elif 'esp32-c6' in output or 'esp32c6' in output:
                        device_info.append(f"{port} (ESP32-C6)")
                    elif 'esp32' in output and 'esp32-c3' not in output and 'esp32-s3' not in output and 'esp32-c6' not in output:
                        device_info.append(f"{port} (ESP32)")
                    else:
                        device_info.append(f"{port} (ESP32 - Unknown variant)")
                        
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                # Port exists but might not be ESP32 or not responding
                continue
        
        if not esp32_ports:
            print("❌ No ESP32 devices detected!")
            print("Make sure your ESP32 is connected via USB and try again.")
            return False
        
        print(f"📋 Found {len(esp32_ports)} ESP32 device(s)")
        
        # Add manual port entry option
        device_info.append("➕ Enter port manually")
        
        selected_index = self.menu.display_menu(
            "Select ESP32 Device", 
            device_info
        )
        
        if selected_index == len(device_info) - 1:
            # Manual port entry
            self.device_port = input("Enter device port (e.g., /dev/tty.usbmodem114301): ").strip()
            self.device_model = input("Enter device model (esp32, esp32c3, esp32s3, esp32c6): ").strip().lower()
        else:
            # Extract port and model from selection
            selected_device = device_info[selected_index]
            self.device_port = selected_device.split(' (')[0]
            model_part = selected_device.split(' (')[1].rstrip(')')
            if 'esp32-c3' in model_part.lower() or 'esp32c3' in model_part.lower():
                self.device_model = 'esp32c3'
            elif 'esp32-s3' in model_part.lower() or 'esp32s3' in model_part.lower():
                self.device_model = 'esp32s3'
            elif 'esp32-c6' in model_part.lower() or 'esp32c6' in model_part.lower():
                self.device_model = 'esp32c6'
            else:
                self.device_model = 'esp32'
        
        print(f"✅ Selected device: {self.device_port} ({self.device_model})")
        
        # Check if device model is supported
        supported_models = ['esp32c3', 'esp32s3', 'esp32c6', 'esp32']
        if self.device_model not in supported_models:
            print(f"\n❌ Unsupported ESP32 variant detected: {self.device_model}")
            print("🔧 Currently this tool only supports:")
            print("   • ESP32-C3")
            print("   • ESP32-S3") 
            print("   • ESP32-C6")
            print("   • ESP32 (Generic)")
            print("\n💡 Please use a supported ESP32 variant or check for tool updates.")
            return False
        
        return True
    
    def detect_current_firmware(self):
        """Detect what firmware is currently installed on the ESP32"""
        print(f"\n🔍 Detecting current firmware on {self.device_port}...")
        
        try:
            # Try to connect and get firmware info
            import serial
            import time
            
            ser = serial.Serial(self.device_port, 115200, timeout=3)
            time.sleep(2)  # Wait for connection to stabilize
            
            # Clear any existing data
            ser.reset_input_buffer()
            
            # Send commands to detect firmware
            detection_commands = [
                b'\r\n',  # Get prompt
                b'import sys\r\n',  # Import sys module
                b'print(sys.version)\r\n',  # Get version info
                b'print(sys.implementation)\r\n',  # Get implementation details
                b'print(sys.platform)\r\n',  # Get platform info
            ]
            
            firmware_info = {
                'is_micropython': False,
                'version': 'Unknown',
                'implementation': 'Unknown',
                'platform': 'Unknown',
                'raw_output': ''
            }
            
            for cmd in detection_commands:
                ser.write(cmd)
                time.sleep(0.5)
                response = ser.read_all().decode('utf-8', errors='ignore')
                firmware_info['raw_output'] += response
            
            ser.close()
            
            # Parse the response to determine firmware type
            output_lower = firmware_info['raw_output'].lower()
            
            if 'micropython' in output_lower:
                firmware_info['is_micropython'] = True
                
                # Extract version information
                lines = firmware_info['raw_output'].split('\n')
                for line in lines:
                    if 'micropython' in line.lower() and 'version' in line.lower():
                        firmware_info['version'] = line.strip()
                    elif 'implementation' in line.lower():
                        firmware_info['implementation'] = line.strip()
                    elif 'platform' in line.lower():
                        firmware_info['platform'] = line.strip()
                        
            elif 'esp32' in output_lower or 'esp-idf' in output_lower:
                firmware_info['is_micropython'] = False
                firmware_info['version'] = 'ESP-IDF or other ESP32 firmware'
                
            elif 'arduino' in output_lower:
                firmware_info['is_micropython'] = False
                firmware_info['version'] = 'Arduino firmware'
                
            else:
                firmware_info['version'] = 'Unknown firmware or no response'
            
            return firmware_info
            
        except Exception as e:
            print(f"⚠️  Could not detect current firmware: {e}")
            return {
                'is_micropython': False,
                'version': 'Detection failed',
                'implementation': 'Unknown',
                'platform': 'Unknown',
                'raw_output': f'Error: {e}'
            }
    
    def confirm_firmware_overwrite(self, firmware_info):
        """Ask user to confirm overwriting existing firmware"""
        options = [
            "Yes, proceed with flashing MicroPython",
            "No, keep the current firmware"
        ]
        
        current_index = 0
        
        while True:
            # Clear screen and show persistent information
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print(f"\n{'='*80}")
            print(f"  📋 CURRENT FIRMWARE DETECTION RESULTS")
            print(f"{'='*80}")
            print(f"  • Firmware Type: {'MicroPython' if firmware_info['is_micropython'] else 'Other'}")
            print(f"  • Version: {firmware_info['version']}")
            print(f"  • Platform: {firmware_info['platform']}")
            
            if firmware_info['is_micropython']:
                print(f"\n  ⚠️  MicroPython is already installed on this device!")
                print(f"     This will overwrite your existing MicroPython installation.")
                print(f"     Any files or programs stored on the device will be lost.")
            else:
                print(f"\n  ⚠️  Non-MicroPython firmware detected!")
                print(f"     This will replace the current firmware with MicroPython.")
                print(f"     Any existing programs or data will be lost.")
            
            print(f"\n  🔧 Raw Detection Output:")
            print(f"  {'-'*76}")
            # Format the raw output with proper indentation
            formatted_output = firmware_info['raw_output'].replace('\n', '\n  ')
            print(f"  {formatted_output}")
            print(f"  {'-'*76}")
            
            print(f"\n{'='*80}")
            print(f"  Do you want to overwrite the current firmware?")
            print(f"{'='*80}")
            
            # Display menu options with selection indicator
            for i, option in enumerate(options):
                if i == current_index:
                    print(f"  ▶ {option}")
                else:
                    print(f"    {option}")
            
            print(f"\n{'='*80}")
            print(f"  Use ↑/↓ arrows to navigate, Enter to select, 'q' to quit")
            print(f"{'='*80}")
            
            # Get user input
            try:
                import tty
                import termios
                
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                    
                    if ch == '\x1b':  # ESC sequence
                        ch += sys.stdin.read(2)
                    
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
                if ch == '\x1b[A':  # Up arrow
                    current_index = (current_index - 1) % len(options)
                    continue
                elif ch == '\x1b[B':  # Down arrow
                    current_index = (current_index + 1) % len(options)
                    continue
                elif ch == '\r' or ch == '\n':  # Enter
                    choice = current_index
                elif ch == 'q' or ch == '\x03':  # 'q' or Ctrl+C
                    print("\nExiting...")
                    sys.exit(0)
                else:
                    continue
                    
            except (ImportError, OSError):
                # Fallback for systems without termios
                try:
                    choice_input = input(f"\nSelect option (1-{len(options)}, 'q' to quit): ").strip()
                    if choice_input.lower() == 'q':
                        sys.exit(0)
                    choice = int(choice_input) - 1
                    if choice < 0 or choice >= len(options):
                        print(f"Please enter a number between 1 and {len(options)}")
                        continue
                except ValueError:
                    print("Please enter a valid number")
                    continue
                except KeyboardInterrupt:
                    print("\nExiting...")
                    sys.exit(0)
            
            if choice == 0:
                return True
            elif choice == 1:
                print("\n👋 Keeping current firmware. Exiting...")
                return False
    
    def get_firmware_versions(self):
        """Get available MicroPython firmware versions"""
        print("\n🌐 Fetching available MicroPython firmware versions...")
        
        try:
            # Define correct firmware URLs for each ESP32 variant
            firmware_options = []
            
            if self.device_model == 'esp32c3':
                firmware_options = [
                    "ESP32_GENERIC_C3-20250911-v1.26.1.bin (Latest Stable)",
                    "ESP32_GENERIC_C3-20241220-v1.26.1.bin (Previous Stable)",
                    "ESP32_GENERIC_C3-20250911-v1.26.1.bin (Development)"
                ]
            elif self.device_model == 'esp32s3':
                firmware_options = [
                    "ESP32_GENERIC_S3-20250911-v1.26.1.bin (Latest Stable)",
                    "ESP32_GENERIC_S3-20241220-v1.26.1.bin (Previous Stable)",
                    "ESP32_GENERIC_S3-20250911-v1.26.1.bin (Development)"
                ]
            elif self.device_model == 'esp32c6':
                firmware_options = [
                    "ESP32_GENERIC_C6-20250911-v1.26.1.bin (Latest Stable)",
                    "ESP32_GENERIC_C6-20241220-v1.26.1.bin (Previous Stable)",
                    "ESP32_GENERIC_C6-20250911-v1.26.1.bin (Development)"
                ]
            else:  # esp32
                firmware_options = [
                    "ESP32_GENERIC-20250911-v1.26.1.bin (Latest Stable)",
                    "ESP32_GENERIC-20241220-v1.26.1.bin (Previous Stable)",
                    "ESP32_GENERIC-20250911-v1.26.1.bin (Development)"
                ]
            
            # Add option to use local file
            firmware_options.append("📁 Use local firmware file")
            
            selected_index = self.menu.display_menu(
                f"Select MicroPython Firmware for {self.device_model.upper()}", 
                firmware_options
            )
            
            if selected_index == len(firmware_options) - 1:
                # Use local file
                local_files = list(Path('.').glob('*.bin'))
                if local_files:
                    local_options = [str(f) for f in local_files]
                    file_index = self.menu.display_menu("Select Local Firmware File", local_options)
                    self.firmware_file = local_options[file_index]
                else:
                    print("❌ No local .bin files found!")
                    return False
            else:
                # Download firmware
                firmware_name = firmware_options[selected_index].split(' (')[0]
                
                # Use the correct URL structure for MicroPython firmware
                if self.device_model == 'esp32c3':
                    firmware_url = f"https://micropython.org/resources/firmware/{firmware_name}"
                elif self.device_model == 'esp32s3':
                    firmware_url = f"https://micropython.org/resources/firmware/{firmware_name}"
                elif self.device_model == 'esp32c6':
                    firmware_url = f"https://micropython.org/resources/firmware/{firmware_name}"
                else:  # esp32
                    firmware_url = f"https://micropython.org/resources/firmware/{firmware_name}"
                
                print(f"📥 Downloading {firmware_name}...")
                print(f"🔗 URL: {firmware_url}")
                
                try:
                    response = requests.get(firmware_url, timeout=30)
                    response.raise_for_status()
                    
                    self.firmware_file = firmware_name
                    with open(self.firmware_file, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ Downloaded: {firmware_name}")
                    
                except requests.RequestException as e:
                    print(f"❌ Error downloading firmware: {e}")
                    print("Trying alternative download method...")
                    
                    # Try alternative URL structure
                    alt_url = f"https://github.com/micropython/micropython/releases/download/v1.26.1/{firmware_name}"
                    try:
                        response = requests.get(alt_url, timeout=30)
                        response.raise_for_status()
                        
                        self.firmware_file = firmware_name
                        with open(self.firmware_file, 'wb') as f:
                            f.write(response.content)
                        
                        print(f"✅ Downloaded from alternative URL: {firmware_name}")
                        
                    except requests.RequestException as e2:
                        print(f"❌ Alternative download also failed: {e2}")
                        print("Please download firmware manually or use local file option.")
                        return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching firmware versions: {e}")
            print("Using local firmware file if available...")
            
            # Check for existing local firmware
            local_files = list(Path('.').glob(f"{self.device_model}*.bin"))
            if local_files:
                self.firmware_file = str(local_files[0])
                print(f"✅ Using existing local firmware: {self.firmware_file}")
                return True
            else:
                print("❌ No local firmware files found!")
                return False
    
    def flash_micropython(self):
        """Flash MicroPython to ESP32"""
        print(f"\n⚡ Flashing MicroPython to {self.device_port}...")
        
        try:
            # Erase flash first
            print("🧹 Erasing flash memory...")
            erase_cmd = [
                'esptool', '--chip', self.device_model,
                '--port', self.device_port,
                'erase-flash'
            ]
            
            result = subprocess.run(erase_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"❌ Error erasing flash: {result.stderr}")
                return False
            
            print("✅ Flash erased successfully")
            
            # Flash MicroPython
            print("📤 Flashing MicroPython firmware...")
            flash_cmd = [
                'esptool', '--chip', self.device_model,
                '--port', self.device_port,
                '--baud', '460800',
                'write-flash', '-z', '0x0', self.firmware_file
            ]
            
            result = subprocess.run(flash_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                print(f"❌ Error flashing firmware: {result.stderr}")
                print("Trying with slower baud rate...")
                
                # Try with slower baud rate
                flash_cmd[4] = '115200'  # Change baud rate
                result = subprocess.run(flash_cmd, capture_output=True, text=True, timeout=120)
                if result.returncode != 0:
                    print(f"❌ Error flashing firmware: {result.stderr}")
                    return False
            
            print("✅ MicroPython flashed successfully!")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Flashing timed out. Try again.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during flashing: {e}")
            return False
    
    def test_connection(self):
        """Test MicroPython connection"""
        print(f"\n🧪 Testing MicroPython connection on {self.device_port}...")
        
        try:
            # Try to connect with Python serial
            test_cmd = [
                'python', '-c', f'''
import serial
import time
try:
    ser = serial.Serial("{self.device_port}", 115200, timeout=2)
    time.sleep(1)
    ser.write(b"print(\\"Hello MicroPython!\\")\\r\\n")
    time.sleep(1)
    response = ser.read_all().decode("utf-8", errors="ignore")
    ser.close()
    if "Hello MicroPython!" in response:
        print("✅ MicroPython connection successful!")
        print("Response:", response.strip())
    else:
        print("❌ No response from MicroPython")
        print("Response:", response.strip())
except Exception as e:
    print(f"❌ Connection test failed: {{e}}")
'''
            ]
            
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False
    
    def run(self):
        """Main execution flow"""
        print("🚀 ESP32 MicroPython Flashing Tool")
        print("=" * 50)
        
        # Check dependencies
        check_dependencies()
        
        # Ensure working directory
        self.ensure_working_directory()
        
        # Step 1: Check conda environment
        if not self.check_conda_environment():
            return False
        
        # Step 2: Detect ESP32 devices
        if not self.detect_esp32_devices():
            return False
        
        # Step 3: Detect current firmware
        firmware_info = self.detect_current_firmware()
        
        # Step 4: Confirm firmware overwrite if needed
        if not self.confirm_firmware_overwrite(firmware_info):
            return False
        
        # Step 5: Select firmware
        if not self.get_firmware_versions():
            return False
        
        # Step 6: Flash MicroPython
        if not self.flash_micropython():
            return False
        
        # Step 7: Test connection
        self.test_connection()
        
        print("\n🎉 MicroPython installation completed successfully!")
        print(f"📁 Working directory: {self.working_dir}")
        print(f"📱 Device: {self.device_port} ({self.device_model})")
        print(f"💾 Firmware: {self.firmware_file}")
        
        print("\n🔗 To connect to MicroPython:")
        print(f"   screen {self.device_port} 115200")
        print(f"   # Or use Thonny IDE with port: {self.device_port}")
        
        return True

def main():
    """Main entry point"""
    try:
        manager = ESPToolManager()
        success = manager.run()
        
        if success:
            print("\n✅ All done! Your ESP32 is ready for MicroPython development.")
        else:
            print("\n❌ Installation failed. Check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()