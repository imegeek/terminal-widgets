import cpuinfo
from io import StringIO
from rich.text import Text
from time import time, sleep
from itertools import zip_longest
from .system import system, hostname, arch, release
from concurrent.futures import ThreadPoolExecutor
import os, re, sys, json, ctypes, requests, subprocess
from .config import (
    CONFIG_PATH,
    color_codes,
    window_rows,
    window_size,
    pyversion,
    console,
    cftime,
    today,
    color,
    align,
    logo,
    args
)

if not system == "android":
    import psutil

def contains_escape_code(text):
    # Extended pattern for ANSI and ASCII escape codes, including cursor movements and other control codes
    ansi_ascii_pattern = r'\x1B\[[0-9;?]*[A-Za-z]|\x1B[EF]'

    # Check if the text contains ANSI or ASCII escape codes
    if re.search(ansi_ascii_pattern, text):
        return True
    else:
        return False
    
def cleaned_string(text):
    is_contains_escape_code = contains_escape_code(text)

    if is_contains_escape_code:
        # Remove all matched ANSI escape codes and other escape sequences
        cleaned_text = re.sub(r'\x1B\[[0-?9;]*[mK]|\\n|\\t|\\r|\\b|\\f|\\v|\\0', '', text)
    else:
        # Remove all occurrences of text within square brackets (inclusive)
        cleaned_text = re.sub(r'\[.*?\]', '', text)

    return cleaned_text

def print_align(string, source=console.width, align=align, end=""):
    is_contains_escape_code = contains_escape_code(string)
    cleaned_lines = cleaned_string(string).splitlines()
    lines = string.splitlines()
    width = source

    if isinstance(source, str):
        width = len(max(cleaned_lines))

    # Calculate the maximum length of the lines
    max_length = max(len(line) for line in cleaned_lines)

    # Determine padding based on alignment
    if align == "left":
        padding = ""
    else:  # center alignment
        # Calculate the total padding needed to center the logo in the terminal
        padding = " " * int(((width - max_length) // 2) + 2)

    aligned_lines = []
    
    for line in lines:
        # Add the aligned line to the list
        aligned_lines.append(padding + line)
        
    aligned_text = "\n".join(aligned_lines)
    if is_contains_escape_code:
        console.print(Text.from_ansi(aligned_text), end=end)
    else:
        console.print(aligned_text, end=end)
    if end == "\r":
        return end + " " * int(len(line) + len(padding))
    # console.print(*aligned_lines, end=end)

def is_superuser():
    """
    Returns True if the script is running with superuser (admin) privileges,
    otherwise False.
    """
    
    # Check for superuser on Unix-based systems
    if os.name == 'posix':
        return os.geteuid() == 0

    # Check for superuser on Windows
    elif os.name == 'nt':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    return False

def convert_size(size_in_bytes):
    """
    Convert the size in bytes to a more human-readable format with appropriate units.

    Args:
    size_in_bytes (int): The size in bytes to be converted.

    Returns:
    tuple: A tuple containing the converted size and its corresponding unit.

    Example:
    >>> convert_size(2048)
    (2.0, 'K')
    """

    # Define the units for conversion
    units = ['B', 'K', 'M', 'G', 'T', 'P']

    # Initialize unit index
    unit_index = 0

    # Loop until the size is smaller than 1024 or until the last unit is reached
    while size_in_bytes >= 1024 and unit_index < len(units) - 1:
        size_in_bytes /= 1024  # Divide size by 1024 for conversion
        unit_index += 1  # Increment unit index

    # Select the appropriate unit based on the unit index
    selected_unit = units[unit_index]

    # If the selected unit is 'K', further divide the size by 1024
    if selected_unit == units[1]:
        size_in_bytes /= 1024  # Further divide size by 1024 for 'K' unit

    # Return the converted size and its corresponding unit
    return size_in_bytes, selected_unit

margin = "\n"*args.margin

try:
    logo = logo.select(args.logo).format(**color_codes)
except Exception:
    logo = logo.select(args.logo)
    
if args.direction == "row":
    cleaned_logo = cleaned_string(logo)
    logo_len = len(cleaned_logo.splitlines())

    max_logo_width_len = len(max(cleaned_logo.splitlines()))
    alongside_width = max_logo_width_len + 2

def truncate_text(text):
    """
    Truncates the text if it exceeds the available window width, adding an ellipsis if truncated.

    Parameters:
    - text (str): The text to display.
    - alongside_width (int): The width occupied by elements alongside the text.
    - window_rows (int): The total available width of the window in characters.

    Returns:
    - str: The original or truncated text with an ellipsis if necessary.
    """

    try:
        # Calculate the total width by adding alongside width and the text length
        total_width = alongside_width + len(cleaned_string(text)) + 5        
    except Exception:
        total_width = len(cleaned_string(text)) + 5
    
    # Determine the remaining width by subtracting total width from available window rows
    remaining_width = window_rows - total_width
    
    # If the remaining width is negative, truncate the text and add an ellipsis
    if total_width > window_rows:
        text = text[:remaining_width] + "\u2026"  # "\u2026" is the unicode for ellipsis (…)
    
    return text

def getCols(data):
    cols = [line.strip().split() for line in data]
    return cols

def findStr(data, find):
    fstr = [i for i in data if any(find in j for j in i)]

    # Use a set to remove duplicates, then check if the length is 1
    if len(set(tuple(sublist) for sublist in fstr)) == 1:
    # Print the first sublist (index 0)
        return fstr[0]

    if len(fstr) > 1:
        return fstr
    else:
        return fstr[0]
    
def insert_dict(dictionary, index, key, value):
    try:
        dictionary.pop(key)  # Remove the dictionary item with the specified key.
    except Exception:
        pass

    # insert new key and value using keys() and values() methods
    keys = list(dictionary.keys())
    values = list(dictionary.values())

    # insert new key and value at the desired index
    keys.insert(index, key)
    values.insert(index, value)

    # create a new dictionary using keys and values list
    return dict(zip(keys, values))

class Icon():
    net: str
    user    = ""
    host    = "󰇄"
    shell   = ""
    python  = "󰌠"
    online  = ""
    offline = ""
    package = "󰏗"
    window  = ""
    arch    = "󰘚"
    cpu     = ""
    ram     = ""
    storage = "󰋊"
    volume  = "󰕾"
    signal  = ""
    uptime  = "󰔚"
    time    = ""
    date    = "󰃭"
    mute    = "󰖁"

    circle = [
    "", ""
    ]

    status = [
    "󰗠", "", ""
    ]

    battery_list = [
    "󰁺","󰁻","󰁼","󰁽","󰁾","󰁿","󰂀","󰂁","󰂂","󰁹","󰂄"
    ]

    battery = dict(enumerate(battery_list))
    battery[-1] = battery.pop(len(battery) - 1)

    weather = {
    "Clear":"",
    "Clouds":"󰖐",
    "Haze":"󰼰",
    "Snow":"󰼶",
    "Rain":"",
    "Fog":"󰖑",
    "Mist":"",
    "Ash":"",
    "Squall":"󰖝",
    "Dust":"",
    "Smoke":"",
    "Tornado":"󰼸",
    "Drizzle":"󰖗",
    "Thunderstorm":""
    }

    os = {
    "windows":"",
    "linux":"󰻀",
    "macos":"",
    "android":"󰀲"
    }

    # Get the icon corresponding to the current system
    # If the current system is not found in the dictionary, default to an status icon.
    os = os.get(system, status[2])

    def __init__(self):
        self.color = color

    def badge(self, text:str, color:str = None, icon:str = None, no_badge:str = args.no_badge):
        """
        Generate a badge with specified color, icon, and text.

        Args:
        color (str): The color of the badge.
        icon (str): The icon string containing the icon and possibly a number.
        text (str): The text to display alongside the badge.

        Returns:
        str: The generated badge.
        """

        text = truncate_text(text)

        if no_badge:
            badge = {
                "left": "",
                "right": ""
            }
        else:
            badge = {
                "left": f"[{self.color.black}]{self.circle[0]}[on {self.color.black}]",
                "right": f"[/][{self.color.black}]{self.circle[1]}"
            }

        if icon and color and text:
            return f"{badge["left"]}[{color}]{icon}[/] [b white]{text}[/]{badge["right"]}"
        elif not icon and not color and text:
            return f"{badge["left"]}[b white]{text}[/]{badge["right"]}"
        elif not icon and text:
            return f"{badge["left"]}[b white][{color}]{text}[/][/]{badge["right"]}"
        else:
            # If conditions are not met, return an empty string
            return ''

class System():
    @staticmethod
    def getInternet():
        try:
            global reqStatus
            # sending equest to get network status code
            req = requests.get(f"https://1.1.1.1", timeout=3)
            status = req.status_code

            # capture request status code and set boolean with ternary operator
            reqStatus = True if status == 200 else None
            
        except Exception:
            reqStatus = False

    @staticmethod
    def getPackage():
        """
        Determines the package manager and counts the number of installed packages
        based on the current operating system.

        Returns:
            str: A string representing the count of installed packages and the package manager used.
            Returns None if an error occurs.
        """
        if system == "windows":
            # For Windows, use PowerShell to count installed programs
            pkg = "exe"
            command = r"(Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | ? { $_.DisplayName -and $_.DisplayName -notmatch '^KB[0-9]' }).Count"
            command = f"powershell -c \"{command}\""

        elif system == "android":
            # For Android, use apt to count installed packages
            pkg = "apt"
            command = "dpkg -l | wc -l"

        elif system == "linux":
            # For Linux, determine the package manager based on the distribution
            def get_distro():
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().lower()

            distro = get_distro()

            def is_apt_supported():
                return os.path.isfile("/etc/apt/sources.list")
            
            def is_pacman_supported():
                return os.path.isfile("/etc/pacman.conf")

            if is_apt_supported():
                pkg = "apt"
                command = "dpkg -l | grep '^ii' | wc -l"

            elif is_pacman_supported():
                pkg = "pacman"
                command = "pacman -Q | wc -l"

            elif any(d in distro for d in ["centos", "rhel", "fedora"]):
                pkg = "rpm"
                command = "yum list installed | wc -l"

            elif "alpine" in distro:
                pkg = "apk"
                command = "apk info | wc -l"

            elif "void" in distro:
                pkg = "xbps"
                command = "xbps-query -l | wc -l"

            elif "opensuse" in distro:
                pkg = "rpm"
                command = "zypper packages --installed-only | wc -l"

            elif "freebsd" in distro:
                pkg = "pkg"
                command = "pkg info | wc -l"

            elif any(d in distro for d in ["openbsd", "netbsd"]):
                pkg = "pkg"
                command = "pkg_info | wc -l"
            else:
                return None

        elif system == "darwin":
            # For macOS, use Homebrew to count installed packages
            pkg = "brew"
            command = "brew list | wc -l"

        try:
            # Run the command and capture the output
            output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()
        except Exception:
            # Return None if an error occurs
            return None
        
        # Return the count of installed packages and the package manager used
        return output + f" {pkg}"
    
    @staticmethod
    def getCPU():
        """
        Retrieves the CPU info of the system.

        Returns:
            str: A string representing the CPU info with its appropriate unit (GHz or MHz).
        """
        freqs, unit = cpu_info["hz_advertised_friendly"].split()
        freqs = round(float(freqs), 1)
        if args.text == "detailed":
            if system == "android":
                cpu = f"{cpu_info["hardware_raw"]} {freqs} {unit}"
            else:
                cpu = f"{cpu_info["brand_raw"]}"
        else:
            cpu = f"{freqs} {unit}"  # Concatenate frequency and unit to form CPU information string
        
        return cpu

    @staticmethod
    def getRAM():
        """
        Retrieves the system RAM usage.

        Returns:
            str or None: A string representing the used and total RAM, in GB (Gigabytes), if successful; None otherwise.
        """
        if system == "android":
            try:
                # For Android systems, read RAM information from /proc/meminfo
                mem_path = "/proc/meminfo"
                with open(mem_path) as f:
                    mem_info = f.readlines()

                # Extract relevant columns from the memory info
                mem = getCols(mem_info)
                total_ram_bits = int(findStr(mem, "MemTotal")[1]) * 1024
                avail_ram_bits = int(findStr(mem, "MemAvailable")[1]) * 1024
                total_ram, unitT = convert_size(total_ram_bits)

                # Calculate used RAM by subtracting available RAM from total RAM
                used_ram, unitU = convert_size(total_ram_bits - avail_ram_bits)
            except Exception:
                # Return None if an exception occurs
                return None
        else:
            try:
                # For non-Android systems, use psutil to retrieve virtual memory information
                svmem = psutil.virtual_memory()

                # Convert total and used RAM sizes to human-readable format
                total_ram, unitT = convert_size(svmem.total)
                used_ram, unitU = convert_size(svmem.used)
            except Exception:
                # Return None if an exception occurs
                return None

        if args.text == "detailed":
            # Format RAM usage as "used/total" and percent with appropriate units
            ram = f"{used_ram:.1f}{unitU}B/{total_ram:.0f}{unitT}B ({int((used_ram/total_ram) * 100)}%)"
        else:
            # Format RAM usage as "used/total" with appropriate units
            ram = f"{used_ram:.1f}{unitU}/{total_ram:.0f}{unitT}"
        return ram

    @staticmethod
    def getSHELL():
        """
        Determines the current shell being used by the user.

        Returns:
            str: The name of the current shell if determined, otherwise None.
        """
        if not system == "windows":
            # Get the value of the SHELL environment variable
            current_shell = os.environ.get('SHELL')

            if current_shell:
                # Extract the name of the shell from its path
                shell = current_shell.split("/")[-1]
            else:
                # Return None if the SHELL environment variable is not set
                None
        else:
            # If the system is Windows, determine the shell based on running processes
            for process in psutil.process_iter(attrs=['pid', 'name']):
                try:
                    process_info = process.info
                    process_name = process_info['name']
                    
                    # Check for common terminal emulators
                    if "cmd.exe" in process_name:
                        shell = "cmd"
                    elif "powershell.exe" in process_name:
                        shell = "powershell"
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Return None if there are specific psutil exceptions
                    return None
                
        # Return the determined shell
        return shell
    
    @staticmethod
    def getBATTERY():
        """
        Retrieves the battery status and percentage.

        Returns:
            tuple or None: A tuple containing the battery level index (0-9) and the battery percentage,
            or None if battery information cannot be obtained.
        """
        try:
            if system == "android":
                # For Android systems, retrieve battery status using termux-battery-status command
                battery_info = subprocess.run("termux-battery-status", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()
                battery = json.loads(battery_info)
                percent = battery["percentage"]
                power = True if battery["status"] == "CHARGING" else False
            else:
                # For other systems, use psutil to retrieve battery information
                battery = psutil.sensors_battery()
                percent = int(battery.percent)
                power = battery.power_plugged
                
            if power:
                # if Charging, sets index to -1
                index = -1
            else:
                # else Discharging, sets index to ranges from 0 to 9
                index = (percent // 10) -1

            if args.text == "detailed":
                if index == -1:
                    status = f"{percent}% (charging)"
                else:
                    status = f"{percent}% (unplugged)"
            else:
                status = f"{percent}%"
            return index, status  # Return battery status and icon index and percentage
        except Exception:
            # Return None if an exception occurs while retrieving battery information
            return None, None

    @staticmethod
    def getDISK():
        """
        Retrieves disk usage information.

        Returns:
            tuple or None: A tuple containing available disk space and its unit,
            or None if disk information cannot be obtained.
        """
        try:
            if system == "android":
                # For Android systems, retrieve disk usage information using 'df' command
                df_path = "/system/bin/df"
                df_info = subprocess.run(df_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip().split("\n")

                # Extract relevant columns from the disk usage information
                disk = getCols(df_info)

                avail_bits = int(findStr(disk, "emulated")[3])*1024
                used_bits = int(findStr(disk, "emulated")[2])*1024

                # Convert available space to human-readable format
                avail_space = convert_size(avail_bits)
                total_space = convert_size(used_bits+avail_bits)
            else:
                # Get disk usage information for the root directory
                disk_usage = psutil.disk_usage('/')
                total_space = convert_size(disk_usage.total)

                # Convert available space to human-readable format
                avail_space = convert_size(disk_usage.free)

            if system == "windows":
                # For Windows systems, print which volume label is in use
                volume_label = os.getcwd().split("\\")[0]  # Extract volume label from current directory
                if args.text == "detailed":
                    return f"{avail_space[0]:.1f} {avail_space[-1]}B free of {total_space[0]:.0f} {total_space[-1]}B ({volume_label})"  # Return available disk space with volume label
                else:
                    return f"{avail_space[0]:.1f}{avail_space[-1]} ({volume_label})"  # Return available disk space with volume label
            else:
                if args.text == "detailed":
                    return f"{avail_space[0]:.1f} {avail_space[-1]}B free of {total_space[0]:.0f} {total_space[-1]}B"  # Return available disk space with volume label
                else:
                    return f"{avail_space[0]:.1f}{avail_space[-1]}"  # Return available disk space
        except Exception:
            # Return None if an exception occurs while retrieving disk information
            return None

    @staticmethod
    def getUPTIME():
        """
        Retrieves the system uptime, i.e., the time since the system was last booted.

        Returns:
            str: A formatted string representing the system uptime.
            Returns None if the uptime cannot be determined.
        """
        # Check if the system is Android
        if system == "android":
            # Use ctypes to access system information on Android
            import ctypes, struct
            libc = ctypes.CDLL("libc.so")
            buf = ctypes.create_string_buffer(128)

            # Call sysinfo to get system information
            if libc.sysinfo(buf) < 0:
                return None
            uptime_seconds = struct.unpack_from("@l", buf.raw)[0]
        else:
            # Get system boot time using psutil
            boot_time_timestamp = psutil.boot_time()
            
            # Calculate the uptime in seconds
            uptime_seconds = int(time()) - boot_time_timestamp
        
        # Calculate days, hours, and minutes
        uptime_days = uptime_seconds // (24 * 3600)
        uptime_hours = (uptime_seconds % (24 * 3600)) // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        uptime_seconds = uptime_seconds % 60  # Remaining seconds

        # Format the output
        days_str = "day" if uptime_days == 1 else "days"
        if args.text == "detailed":
            hours_str = "hour" if uptime_hours < 1 else "hours"
            mins_str = "min" if uptime_minutes < 2 else "mins"
        else:
            hours_str = "hr" if uptime_hours < 1 else "hrs"

        if uptime_days == 0:
            uptime_days = ""
        else:
            uptime_days = f"{int(uptime_days)} {days_str} "

        if args.text == "detailed":
            uptime = f"{uptime_days}{int(uptime_hours)} {hours_str} {int(uptime_minutes)} {mins_str}"
        else:
            uptime = f"{uptime_days}{int(uptime_hours)}.{int(uptime_minutes)//10} {hours_str}"

        return uptime

    @staticmethod
    def getWeather():
        """
        Retrieves weather information for a specified location using the OpenWeatherMap API.

        Returns:
            tuple: A tuple containing weather type and temperature in Celsius if successful,
            otherwise (None, None) if an error occurs.
        """

        # Check if a location argument is provided
        if args.location:
            # Replace spaces in the location string with URL encoding
            area = args.location.replace(" ", "%20")
            open_weather_api = args.weather_api
            try:
                # Send a GET request to OpenWeatherMap API
                req = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={area}&appid={open_weather_api}&units=metric", timeout=3)
            except Exception:
                # If an exception occurs during the request, return None values
                return None, None
            
            # Parse the JSON response
            jq = req.json()
            # print(json.dumps(jq, indent=4))

            # Check if the request was successful (status code 200)
            if req.status_code == 200:
                # Extract weather type and temperature from the JSON response
                weather_type = jq["weather"][0]["main"]
                weather_temp = str(int(jq["main"]["temp"])) + "°C"

                if args.text == "detailed":
                    weather_feel = jq["main"].get("feels_like", "")
                    feels_like = f"feels like {int(weather_feel)}" + "°C" if weather_feel else ""
                    weather_temp = f"{weather_temp} {feels_like}"
                # Return weather type and temperature
                return weather_type, weather_temp
            else:
                # If the request was not successful, print the error message and exit
                print_align(req.text, align=align)
                sys.exit(1)
        # If no location argument is provided, return None values
        return None, None

icon = Icon()
badge = icon.badge

def main():
    global arch, cpu_info, color

    try:
        if not any(var for var in [args.stdout, args.json]):
            if "logo" in args.show:
                logo_ = "\n" * args.margin + logo
                print_align(logo_, end="\n")

                if args.direction == "row":
                    for _ in range(logo_len):
                        sys.stdout.write("\033[F")  # Move cursor up one line

        if "logo" == args.show:
            if args.direction == "row":
                for _ in range(logo_len):
                    print()
            sys.exit(0)
        
        if not any(var for var in [args.stdout, args.json]):
            # Construct the badge string
            if args.direction == "row":
                sys.stdout.write(f"\033[{alongside_width}C")  # Move right the cursor
            
            loading_info = badge(color=color.green, icon=icon.signal, text="getting info, wait")
            
            if args.direction == "row":
                loading_info_len = print_align(loading_info, align="left", end="\r")
            
            else:
                loading_info_len = print_align(loading_info, end="\r")

        if system == "android":
            istermux = subprocess.run("pwd", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()
            if not args.bypass_system_api and "com.termux" in istermux:
                command = "am startservice -n com.termux.api/.KeepAliveService"
                try:
                    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stderr.strip()
                except Exception:
                    output = None

                if output:
                    console.print(badge(color=color.red, icon=icon.status[1], text="Termux:API not found, install to continue."))
                    console.print("https://f-droid.org/en/packages/com.termux.api")
                    sys.exit(1)

                command = "dpkg -l"

                try:
                    package = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip().split("\n")
                    if any(pkg for pkg in package if "termux-api" in pkg):
                        package = True
                    else:
                        package = False
                except Exception:
                    package = None

                if not package:
                    console.print(badge(color=color.red, icon=icon.status[1], text="termux-api package not found, install to continue."))
                    sys.exit(1)

        # Get detailed CPU info
        cpu_info = cpuinfo.get_cpu_info()

        try:
            # Try to get the lowercase username of the current user
            username = os.getlogin().lower()
        except Exception:
            # If unable to get the login name, fallback to the lowercase username from environment variables
            username = os.environ.get('USER')

        if is_superuser():
            username = "admin"

        if args.text == "detailed":
            arch = f"{arch} {cpu_info["bits"]} bits ({cpu_info["count"]})"

        # package = System.getPackage()
        # cpu = System.getCPU()
        # ram = System.getRAM()
        # shell = System.getSHELL()
        # battery = System.getBATTERY()
        # disk = System.getDISK()
        # weather = System.getWeather()

        sysinfo = {
            "internet": System.getInternet,
            "package": System.getPackage,
            "cpu": System.getCPU,
            "ram": System.getRAM,
            "shell": System.getSHELL,
            "battery": System.getBATTERY,
            "disk": System.getDISK,
            "uptime": System.getUPTIME,
            "weather": System.getWeather
        }

        # Create a dummy object to store results using dot notation
        class InfoObject:
            pass

        info = InfoObject()  # Create an instance of the InfoObject class

        with ThreadPoolExecutor(max_workers=len(sysinfo)) as executor:
            # Submit each function to the executor using a loop
            futures = {name: executor.submit(func) for name, func in sysinfo.items()}

            # Retrieve results and store them in the sysinfo dictionary
            for name, future in futures.items():
                # sysinfo[name] = future.result()
                setattr(info, name, future.result())

        # setting network status using ternary operator
        network = "online" if reqStatus else "offline"

        # setting network icon to the Class which depends on network status using ternary operator
        icon.net = icon.online if reqStatus else icon.offline
        
        widgets_set = {
            "username": {
                "text": username,
                "color": color.red if is_superuser() else color.green,
                "icon": icon.user
            },

            "hostname": {
                "text": hostname,
                "color": color.green,
                "icon": icon.host
            },

            "platform": {
                "text": system + " " + release if args.text == "detailed" else system,
                "color": color.cyan,
                "icon": icon.os
            },

            "shell": {
                "text": info.shell,
                "color": color.red,
                "icon": icon.shell
            },

            "python": {
                "text": pyversion,
                "color": color.sky,
                "icon": icon.python
            },

            "internet": {
                "text": network,
                "color": color.cyan,
                "icon": icon.net
            },

            "package": {
                "text": info.package,
                "color": color.purple,
                "icon": icon.package
            },

            "window": {
                "text": window_size,
                "color": color.cyan,
                "icon": icon.window
            },

            "arch": {
                "text": arch,
                "color": color.green,
                "icon": icon.arch
            },

            "cpu": {
                "text": info.cpu,
                "color": color.yellow,
                "icon": icon.cpu
            },

            "memory": {
                "text": info.ram,
                "color": color.cyan,
                "icon": icon.ram
            },

            "storage": {
                "text": info.disk,
                "color": color.green,
                "icon": icon.storage
            },
            
            "battery": {
                "text": info.battery[1],
                "color": color.sky,
                "icon": icon.battery.get(info.battery[0], None)
            },

            "uptime": {
                "text": info.uptime,
                "color": color.yellow,
                "icon": icon.uptime
            },

            "weather": {
                "text": info.weather[1],
                "color": color.yellow,
                "icon": icon.weather.get(info.weather[0], None)
            },

            "time": {
                "text": cftime,
                "color": color.cyan,
                "icon": icon.time
            },

            "date": {
                "text": today,
                "color": color.green,
                "icon": icon.date
            }
        }

        if args.stdout:
            # Iterate over the widgets set
            for name, widget in widgets_set.items():
                # Check if the widget has text
                if widget["text"]:
                    # Print the widget name and text
                    print(f"{name.capitalize()}: {widget['text']}")
            # Exit the program with a success status code
            sys.exit(0)

        try:
            # Initialize widget_config variable
            widget_config = None
            
            # Try to open the configuration file
            with open(CONFIG_PATH) as f:
                if f.read():
                    # If the file is not empty, load the JSON content
                    widget_config = json.load(open(CONFIG_PATH))["widgets"]
        except Exception as err:
            # Handle exceptions
            if not "widgets" in str(err):
                # Check if the error is not related to "widgets" property
                # If so, print an error message
                console.print(f"Expecting property name enclosed in double quotes at: {CONFIG_PATH}")
                sys.exit(0)

        if widget_config:
            try:
                # Iterate over each widget in the configuration
                for name, widget in widget_config.items():
                    try:
                        # Attempt to retrieve the state of the widget
                        state = widget["state"]
                    except Exception:
                        # If state is not provided, default to "active"
                        state = "active"

                    try:
                        # Retrieve the key 'index' of widget dict.
                        index = widget["index"]

                        # Retrieve the value associated with the specified name from the widgets_set
                        value = widgets_set[name]

                        widgets_set = insert_dict(widgets_set, index, name, value)
                        index = None
                    except Exception:
                        pass
                        # index = list(widgets_set.keys()).index(name)

                    # Check if the widget is disabled
                    if state == "disabled":
                        # If disabled, remove the widget from the widgets_set
                        widgets_set.pop(name)
                        state = None  # Reset state to None
                    else:
                        # If not disabled, update widget properties
                        # Get text, color, and icon from the widget configuration or use existing values if not provided
                        text = widget.get("text", widgets_set[name]["text"])
                        color = widget.get("color", widgets_set[name]["color"])
                        addon_icon = widget.get("icon", widgets_set[name]["icon"])

                        # Update the widget in the widgets_set if text, color, and icon are provided
                        if text and color and addon_icon:
                            widgets_set[name] = {
                                "text": text,
                                "color": color,
                                "icon": addon_icon
                            }
            except Exception:
                # Handle any unexpected errors during iteration
                console.print(f"widgets not configured properly at: {CONFIG_PATH}")
                sys.exit(0)

        # Initialize an empty dictionary to store valid widgets
        widgets = {}
        # Iterate over the items in the widgets_set dictionary
        for name, widget in widgets_set.items():
            try:
                # Attempt to extract the necessary properties from the widget
                text = widget["text"]
                color = widget["color"]
                addon_icon = widget["icon"]

                # Check if all required properties are present and not empty
                if text and icon and color:
                    # Store the provided values in the widgets dictionary, associated with the specific widget name.
                    widgets[name] = badge(color=color, icon=addon_icon, text=text)
                    
            except Exception:
                # If any error occurs during extraction, continue to the next widget
                pass

        try:
            # Attempt to load the widget addons configuration from the specified path
            widget_addons = json.load(open(CONFIG_PATH))["addons"]
        except Exception:
            # If an exception occurs (e.g., file not found, JSON parsing error), set widget_addons to None
            widget_addons = None

        if widget_addons:
            try:
                for name, widget in widget_addons.items():
                    # Retrieve widget properties from the widget configuration or set default values if not provided
                    text   = widget.get("text", None)
                    addon_exec  = widget.get("exec", None)
                    script = widget.get("script", None)
                    addon_color  = widget.get("color", "na")
                    addon_icon  = widget.get("icon", "na")
                    index  = widget.get("index", len(widgets))

                    if addon_exec:
                        # Execute the command and capture the output
                        process = subprocess.run(addon_exec, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                        if process.stdout:
                            text = process.stdout.strip()
                        else:
                            # Print an error message indicating an invalid script
                            console.print(f"invalid script for '{name}' widget addon at: {CONFIG_PATH}")
                            sys.exit(1)
                        
                    elif script:
                        # Check if the script path is absolute and if the file exists
                        if os.path.isabs(script):
                            if os.path.isfile(script):
                                with open(script) as f:
                                    script = f.read()
                                    # Check if the script content is empty
                                    if not script.strip():
                                        # Print an error message and exit if the script file is empty
                                        console.print(f"script file is empty for {name} widget addon at: {CONFIG_PATH}")
                                        sys.exit(1)
                            else:
                                # Print an error message and exit if the script path is not found
                                console.print(f"script path not found for {name} widget addon at: {CONFIG_PATH}")
                                sys.exit(1)

                        try:
                            # Backup sys.stdout to preserve the original output stream
                            stdout_backup = sys.stdout
                            # Redirect sys.stdout to a StringIO object to capture script output
                            sys.stdout = StringIO()
                            # Execute the script
                            exec(script)
                            # Get the captured output and strip any leading/trailing whitespace
                            text = sys.stdout.getvalue().strip()
                            # Restore sys.stdout to its original value
                            sys.stdout = stdout_backup
                        except Exception:
                            # If an exception occurs during script execution or output capture
                            # Restore sys.stdout to its original value
                            sys.stdout = stdout_backup
                            # Print an error message indicating an invalid python code
                            console.print(f"invalid python code for '{name}' widget addon at: {CONFIG_PATH}")
                            # Exit the program with an error status code
                            sys.exit(1)

                    # Check if text is provided
                    if text:
                        # Check if icon is "na"
                        if addon_icon == "na":
                            # Construct the widget value with default icon
                            value = badge(color=addon_color, text=text)
                            # Insert the widget into the widgets dictionary at the specified index
                            widgets = insert_dict(widgets, index, name, value)

                        # Check if text, addon_color, and addon_icon are provided
                        elif not addon_color == "na" and not addon_icon == "na":
                            # Construct the widget value with provided icon
                            value = badge(color=addon_color, icon=addon_icon, text=text)
                            # Insert the widget into the widgets dictionary at the specified index
                            widgets = insert_dict(widgets, index, name, value)
                        else:
                            # Print an error message if the addon widget is not properly configured
                            console.print(f"'{name}' addon widget not configured properly at: {CONFIG_PATH}")
                            # Exit the program with an error status code
                            sys.exit(1)

                        # Insert the widget into the widgets_set dictionary with its properties
                        widgets_set = insert_dict(widgets_set, len(widgets_set), name, {"text": text, "color": addon_color, "icon": addon_icon})

            except Exception:
                # Handle any exceptions that occur during addon widget configuration
                console.print(f"addons not configured properly at: {CONFIG_PATH}")
                # Exit the program with an error status code
                sys.exit(1)

        if args.json:
            # Convert the widgets_set dictionary to JSON format with indentation for readability
            output = json.dumps(widgets, indent=2)
            # Print the JSON output
            print(output)
            # Exit the program with a success status code
            sys.exit(0)

        if args.color_bars:
            color_bars = "".join([f"[{color}]━━[/]" for color in color_codes])
            widgets["color_bars"] = badge(text=color_bars)

        # Extract the values (widget information) from the widgets dictionary and convert them into a list
        widget_values = list(widgets.values())
        # Divide the widget values into rows based on the specified number of columns
        widget_rows = [widget_values[i:i+args.column] for i in range(0, len(widget_values), args.column)]

        if args.direction == "column":
            print(loading_info_len, end="\r")
            if align == "center":
                sys.stdout.write("\033[F")  # Move cursor up one line

        # Iterate over each row of widgets
        for index, (widget, line) in enumerate(zip_longest(widget_rows, logo.splitlines(), fillvalue="")):
            sleep(0.005)
            if widget:
                row_gap = " " * args.row_gap
                widget = row_gap.join(widget)

                if args.direction == "row":
                    sys.stdout.write(f"\033[{alongside_width}C")  # Move right (40 columns) and print info
                    if index == 0:
                        spaces = " " * len(cleaned_string(loading_info))
                    else:
                        spaces = ""
                    print_align(widget + spaces, align="left")

                else:
                    # Print each widget in the row, with provided spaces padding on the left, following alignment, and provided newline after each row
                    print_align(widget, align=align)
                print(end="\n" * args.column_gap)

            else:
                if args.direction == "row":
                    sys.stdout.write(f"\033[{alongside_width}C\n")

        # Print additional whitespace as specified by the user (args.margin - 1) times
        print("\n"*(args.margin-1))

    except (EOFError, KeyboardInterrupt):
        print_align(badge(color=color.red, icon=icon.status[1], text="Program interrupted."), align=align, end="\n\n")

if __name__ == "__main__":
    main()