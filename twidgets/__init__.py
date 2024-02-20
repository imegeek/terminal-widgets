from time import time
from io import StringIO
from threading import Thread
from rich.console import Console
from  datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor
import os, re, sys, json, random, argparse, platform, requests, subprocess

pyversion = sys.version.split()[0]  # Get the Python version
window_rows, window_columns = os.get_terminal_size()  # Get the size of the terminal window
window_size = f"{window_rows}×{window_columns}"

HOME = os.path.expanduser("~")  # Get the path to the user's home directory
# Construct the path to the configuration file within the user's home directory
CONFIG_PATH = os.path.join(HOME, ".twidgets.json")

# Check if the configuration file exists
if not os.path.isfile(CONFIG_PATH):
    # If the configuration file does not exist, create it
    with open(CONFIG_PATH, "w") as f:
        # Open the configuration file in write mode and write an empty string to it
        f.write("")

color_mode = ["normal", "vivid", "random", "custom"]

parser = argparse.ArgumentParser(
    epilog="See full documentation at: https://github.com/imegeek/terminal-widgets"
)

parser.add_argument(
    "--configs",
    action='store_true',
    help="Show the configuration file."
)

parser.add_argument(
    "--widgets",
    action='store_true',
    help="Show build-in widgets and it's values."
)

parser.add_argument(
    "--stdout",
    action='store_true',
    help="Turn of all colors and disable any ASCII, printing only texts."
)

parser.add_argument(
    "--json",
    action='store_true',
    help="Shows widgets output as JSON object."
)

parser.add_argument(
    "--show",
    choices=["logo", "widgets"],
    metavar=["logo", "widgets"],
    default=["logo", "widgets"],
    help="Specify what to show: 'logo' or 'widgets'."
)

parser.add_argument(
    "--color",
    choices=color_mode,
    default=color_mode[0],
    metavar=color_mode,
    help="Choose an color mode for terminal widgets."
)

parser.add_argument(
    "--weather",
    dest="location",
    metavar="location",
    help="Set weather location to show in widgets."
)

parser.add_argument(
    "-c", "--config",
    metavar="file",
    help="Specify the JSON configuration file to load."
)

parser.add_argument(
    "--column",
    type=int,
    default=5,
    metavar="length",
    help="Specify the number of columns that will be displayed for each row."
)

parser.add_argument(
    "--whitespace",
    type=lambda x: min(int(x), 10),
    default=0,
    metavar="length",
    help="Specify the number of whitespaces that will be displayed before and after execute."
)

args = parser.parse_args()  # Parse the command-line arguments

if args.column < 3:
    print("Ensure that the length of the column is more than two.")
    sys.exit(1)

# Check if a custom configuration file path is provided as a command-line argument
if args.config:
    # Assign the provided file path to the 'file' variable
    file = args.config

    # Check if the provided file exists
    if os.path.isfile(file):
        # If the file exists, update the CONFIG_PATH variable with the provided file path
        CONFIG_PATH = file
    else:
        # If the file does not exist, print an error message and exit the program
        print(f"'{file}' does not exist.\nPlease provide a valid file path.")
        sys.exit(1)

t = datetime.now()  # Get the current time
__time__ = f"{t.hour}:{t.minute}"  # Format the current time as hours:minutes

# Get today's date and format it as "Day of the week, Month Day"
today = date.today().strftime("%a, %b %d")

console = Console()  # Create a Console object for rich console output

def generate_random_color(colors, min_distance=100):
    while True:
        # Generate minimal light random colors
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        # Ensure minimal light values
        while r + g + b < 384:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
        
        new_color = (r, g, b)
        
        # Check dissimilarity with existing colors
        dissimilar = all(color_distance(new_color, existing_color) >= min_distance for existing_color in colors)
        if dissimilar:
            return new_color

def color_distance(color1, color2):
    # Calculate Euclidean distance in RGB space
    return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5

def hex_to_rgb_ansi(val, layout):
    if not val == 0:
        # Convert hex color to RGB
        val = val.lstrip('#')
        rgb_color = tuple(int(val[i:i+2], 16) for i in (0, 2, 4))

        # Create ANSI escape sequence for the RGB color
        return f'\033[{layout};2;{rgb_color[0]};{rgb_color[1]};{rgb_color[2]}m'
    else:
        return f"\033[{val}m"

custom_colors = {
    "red": None,
    "green": None,
    "yellow": None,
    "sky": None,
    "purple": None,
    "cyan": None
}

black   = "#505050"
white  = "#d6d6d6"

if args.color == "normal":
    # sets the normal colors
    red    = "#df6b78"
    green  = "#9ACB73"
    yellow = "#F2CD80"
    sky    = "#8AAED2"
    purple = "#b790ff"
    cyan   = "#8EC8D8"

# Check if the color argument is set to "vivid"
elif args.color == "vivid":
    # sets the vivid colors
    red    = "#D8425C"
    green  = "#8BC455"
    yellow = "#f8d255"
    sky    = "#6AA1DA"
    purple = "#a06efc"
    cyan   = "#6EBEDF"

elif args.color == "random":
    # Generate random colors ensuring at least 100 distance between each color
    num_colors = 6
    random_colors = []
    while len(random_colors) < num_colors:
        new_color = generate_random_color(random_colors, min_distance=100)
        random_colors.append(new_color)

    # Sets random colors as hexadecimal values
    for name, color in zip(custom_colors, random_colors):
        r, g, b = color
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        globals()[name] = hex_color

# Check if the color argument is set to "custom"
elif args.color == "custom":
    try:
        # Load custom colors from the configuration file
        ncolors = json.load(open(CONFIG_PATH))["colors"]

        # Update custom_colors and global variables with the loaded custom colors
        for name in ncolors:
            custom_colors[name] = ncolors[name]
            globals()[name] = ncolors[name]

        # Check if any custom colors are not configured
        nt_colors = [name for name, color in custom_colors.items() if not color]

        # If there are unconfigured custom colors, print an error message and exit
        if nt_colors:
            print(f"Color {nt_colors} is not configured at: {CONFIG_PATH}")
            sys.exit(0)
    except Exception:
        # If an exception occurs during loading or processing custom colors, print an error message and exit
        print(f"colors not configured properly at: {CONFIG_PATH}")
        sys.exit(0)

# Check if the 'configs' argument is provided
if args.configs:
    # Open the configuration file and read its contents
    with open(CONFIG_PATH) as f:
        config = f.read().strip()

        # Check if the configuration exists
        if config:

            # Print the configuration using the 'console' object if it's not empty
            console.print(config, f"\n~{CONFIG_PATH}")
        else:
            # Print a message if no configuration is found
            print("No configuration found.")
    sys.exit(0)

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

logo = "\n"*args.whitespace

logo += f"""[b]
[{yellow}]  ▄███████▄  [{green}]   ▄██████▄   [{sky}]   ▄██████▄   [{red}]   ▄██████▄   [{cyan}]   ▄██████▄   
[{yellow}]  ▄█████████▀▀ [{green}] ▄[{white}]█▀█[{green}]██[{white}]█▀█[{green}]██▄ [{sky}] ▄[{white}]█▀█[{sky}]██[{white}]█▀█[{sky}]██▄ [{red}] ▄[{white}]█▀█[{red}]██[{white}]█▀█[{red}]██▄ [{cyan}] ▄[{white}]█▀█[{cyan}]██[{white}]█▀█[{cyan}]██▄   
[{yellow}] ████████▀     [{green}] █[{white}]▄▄█[{green}]██[{white}]▄▄█[{green}]███ [{sky}] █[{white}]▄▄█[{sky}]██[{white}]▄▄█[{sky}]███ [{red}] █[{white}]▄▄█[{red}]██[{white}]▄▄█[{red}]███ [{cyan}] █[{white}]▄▄█[{cyan}]██[{white}]▄▄█[{cyan}]███   
[{yellow}] ████████▄     [{green}] ████████████ [{sky}] ████████████ [{red}] ████████████ [{cyan}] ████████████   
[{yellow}]  ▀█████████▄▄ [{green}] ██▀██▀▀██▀██ [{sky}] ██▀██▀▀██▀██ [{red}] ██▀██▀▀██▀██ [{cyan}] ██▀██▀▀██▀██   
[{yellow}]    ▀███████▀  [{green}] ▀   ▀  ▀   ▀ [{sky}] ▀   ▀  ▀   ▀ [{red}] ▀   ▀  ▀   ▀ [{cyan}] ▀   ▀  ▀   ▀   
[/]"""

try:
    # Try to access the ANDROID_ROOT environment variable
    android = os.environ["ANDROID_ROOT"]

    # Check if "/system" is in the value of the ANDROID_ROOT environment variable
    if "/system" in android:
        system = "android"
except Exception:
    # If there's an exception (e.g., the ANDROID_ROOT environment variable doesn't exist),
    # use psutil and platform to determine the system
    import psutil
    system = platform.system().lower()  # Get the lowercase platform name
    if system == "darwin":
        # If the platform is macOS (Darwin), set the system variable to "macos"
        system = "macos"

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
    
def insert_dict(dict_, index, key, value):
    try:
        dict_.pop(key)  # Remove the widget with the specified name from the widgets_set
    except Exception:
        pass

    # insert new key and value using keys() and values() methods
    keys = list(dict_.keys())
    values = list(dict_.values())

    # insert new key and value at the desired index
    keys.insert(index, key)
    values.insert(index, value)

    # create a new dictionary using keys and values list
    return dict(zip(keys, values))
    
def lget(lst, index, default=None):
    """
    Custom implementation of list get method.

    Args:
        lst (list): The list to access.
        index (int): The index of the element to access in the list.
        default: The default value to return if the index is out of range (default is None).

    Returns:
        The element at the specified index in the list if it exists, else the default value.
    """
    try:
        return lst[index]
    except Exception:
        return default

class Icon():
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
    ram     = ""
    storage = "󰋊"
    volume  = "󰕾"
    signal  = ""
    uptime  = "󰔚"
    time    = ""
    date    = "󰃭"
    mute    = "󰖁"
    color   = ""

    circle = [
    "", ""
    ]

    status = [
    "󰗠", "", ""
    ]

    battery = [
    "󰁺","󰁻","󰁼","󰁽","󰁾","󰁿","󰂀","󰂁","󰂂","󰁹","󰂄"
    ]

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

class System(Icon):
    def badge(self, color, icon, name):
        """
        Generate a badge with specified color, icon, and name.

        Args:
        self: The instance of the class (assuming it's a method within a class).
        color (str): The color of the badge.
        icon (str): The icon string containing the icon and possibly a number.
        name (str): The name to display alongside the badge.

        Returns:
        str: The generated badge.
        """
        # Extract the number from the icon string using regular expression
        number = ''.join(re.findall(r'-?\d+', icon))

        # Remove non-alphabetic characters from the icon string using regular expression
        icon = re.sub(r'[^a-zA-Z]', '', icon)

        # Check if a number is extracted from the icon string
        if number:
            # If a number exists, check if the specified index in the icon attribute is not None and if name is not None
            if not getattr(self, icon)[int(number)] == None or not name == None:
                # If conditions are met, return the badge with the specified color, icon, and name
                return f"[{black}]{self.circle[0]}[on {black}][{color}]{getattr(self, icon)[int(number)]}[/] [b white]{name}[/][/][{black}]{self.circle[1]}"
            else:
                # If conditions are not met, return an empty string
                return ''
        else:
            # If no number is extracted from the icon string, check if the icon attribute is not None and if name is not None
            if not getattr(self, icon) == None or not name == None:
                # If conditions are met, return the badge with the specified color, icon, and name
                return f"[{black}]{self.circle[0]}[on {black}][{color}]{getattr(self, icon)}[/] [b white]{name}[/][/][{black}]{self.circle[1]}"
            else:
                # If conditions are not met, return an empty string
                return ''
            
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
        Retrieves the CPU frequency of the system.

        Returns:
            str: A string representing the CPU frequency with its appropriate unit (GHz or MHz).
        """
        def detect_unit(frequency):
            """
            Detects the appropriate unit (GHz or MHz) for the given frequency.

            Args:
                frequency (int): The CPU frequency in MHz.

            Returns:
                str: The appropriate unit (GHz or MHz).
            """
            return "GHz" if frequency >= 1000 else "MHz"
        
        if system == "android":
            # For Android systems, read CPU frequency from a specific path
            cpu_path = "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
            freqs = int(open(cpu_path).read())/1000 
        else:
            # For other systems, use psutil to retrieve CPU frequency
            freq_current = psutil.cpu_freq().current
            freq_max = psutil.cpu_freq().max
            # Use max frequency if available, else current frequency
            freqs = freq_current if freq_max == 0 else freq_max

        unit = detect_unit(freqs)  # Determine appropriate frequency unit
        freqs_ = str(round(freqs / 1000, 1))
        cpu = f"{freqs_} {unit}"  # Concatenate frequency and unit to form CPU information string
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
                total_ram = int(findStr(mem, "MemTotal")[1])
                avail_ram = int(findStr(mem, "MemAvailable")[1])

                # Calculate used RAM by subtracting available RAM from total RAM
                used_ram = total_ram - avail_ram

                # Format RAM usage as "used/total" in GB (Gigabytes)
                ram = f"{used_ram / 1024**2:.1f}/{total_ram / 1024**2:.0f}G"
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

                # Format RAM usage as "used/total" with appropriate units
                ram = f"{used_ram:.1f}{unitU}/{total_ram:.0f}{unitT}"
            except Exception:
                # Return None if an exception occurs
                return None
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

            return index, f"{percent}%"  # Return battery level index and percentage
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

                # Convert available space to human-readable format
                avail_space, size_unit = convert_size(int(findStr(disk, "emulated")[3])*1024)
            else:
                # Get disk usage information for the root directory
                disk_usage = psutil.disk_usage('/')

                # Convert available space to human-readable format
                avail_space, size_unit = convert_size(disk_usage.free)

            if system == "windows":
                # For Windows systems, print which volume label is in use
                volume_label = os.getcwd().split("\\")[0].removesuffix(":")  # Extract volume label from current directory
                return f"{avail_space:.1f}{size_unit} 󰽜 {volume_label}"  # Return available disk space with volume label
            else:
                return f"{avail_space:.1f}{size_unit}"  # Return available disk space
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

        # Format the output
        days_str = "day" if uptime_days == 1 else "days"
        hours_str = "hr" if uptime_hours < 1 else "hrs"

        if uptime_days == 0:
            uptime_days = ""
        else:
            uptime_days = f"{int(uptime_days)} {days_str} "
    
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
            weather_api = "704d823ce51a9ee3083dcaaaee8d8404"
            try:
                # Send a GET request to OpenWeatherMap API
                req = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={area}&appid={weather_api}&units=metric", timeout=3)
            except Exception:
                # If an exception occurs during the request, return None values
                return None, None
            
            # Parse the JSON response
            jq = req.json()

            # Check if the request was successful (status code 200)
            if req.status_code == 200:
                # Extract weather type and temperature from the JSON response
                weather_type = jq["weather"][0]["main"]
                weather_temp = str(int(jq["main"]["temp"])) +" °C"

                # Return weather type and temperature
                return weather_type, weather_temp
            else:
                # If the request was not successful, print the error message and exit
                console.print(jq, justify="center")
                sys.exit(1)
        # If no location argument is provided, return None values
        return None, None


def main():
    try:
        if not any(var for var in [args.widgets, args.stdout, args.json]):
            if "logo" in args.show:
                console.print(logo, justify="center")

        if "logo" == args.show:
            sys.exit(0)

        icon = Icon()
        badge = System().badge

        def printINFO(color, icon, text):
            # string = f"{ansi(black, 38)}{icon.circle[0]}{ansi(black, 48)}{ansi("9ACB73", 38)}{icon.signal}{ansi(0, 38)}{ansi(black, 48)} getting info, wait{ansi(0, 38)}{ansi(black, 38)}{icon.circle[1]}"

            string = badge(color, icon, text)

            # hide extra coloring character from string
            re_string = re.sub(r'\[[^\]]*\]', '[]', string).replace("[]", "")

            # center text within the console width
            padding = " " * int(((console.width - len(re_string)) // 2)+2)
            console.print(padding + string, end="\r")
        
        if not any(var for var in [args.widgets, args.stdout, args.json]):
            printINFO(green, "signal", "getting information, wait")

        if system == "android":
            command = "am startservice -n com.termux.api/.KeepAliveService"
            output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stderr.strip()
            if output:
                console.print(badge(red, f"status[1]", "Termux:API not found, install to continue."), justify="center")
                console.print("https://f-droid.org/en/packages/com.termux.api", justify="center")
                sys.exit(1)

        hostname = platform.node().lower()  # Get the lowercase hostname of the system
        try:
            # Try to get the lowercase username of the current user
            username = os.getlogin().lower()
        except Exception:
            # If unable to get the login name, fallback to the lowercase username from environment variables
            username = os.environ.get('USER')

        # Get the lowercase machine architecture of the system
        arch = platform.machine().lower()

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

        # __time = __time__.split(":")
        # time1 = __time[0]
        # time2 = list(__time[1])
        # time2.insert(0, "0")
        # print(time1, time2)
        
        widgets_set = {
            "username": {
                "text": username,
                "color": green,
                "icon": icon.user
            },

            "hostname": {
                "text": hostname,
                "color": green,
                "icon": icon.host
            },

            "platform": {
                "text": system,
                "color": cyan,
                "icon": icon.os
            },

            "shell": {
                "text": info.shell,
                "color": red,
                "icon": icon.shell
            },

            "python": {
                "text": pyversion,
                "color": sky,
                "icon": icon.python
            },

            "internet": {
                "text": network,
                "color": cyan,
                "icon": icon.net
            },

            "package": {
                "text": info.package,
                "color": purple,
                "icon": icon.package
            },

            "window": {
                "text": window_size,
                "color": cyan,
                "icon": icon.window
            },

            "arch": {
                "text": arch,
                "color": green,
                "icon": icon.arch
            },

            "cpu": {
                "text": info.cpu,
                "color": yellow,
                "icon": icon.cpu
            },

            "memory": {
                "text": info.ram,
                "color": cyan,
                "icon": icon.ram
            },

            "storage": {
                "text": info.disk,
                "color": green,
                "icon": icon.storage
            },
            
            "battery": {
                "text": info.battery[1],
                "color": sky,
                "icon": lget(icon.battery, info.battery[0], None)
            },

            "uptime": {
                "text": info.uptime,
                "color": yellow,
                "icon": icon.uptime
            },

            "weather": {
                "text": info.weather[1],
                "color": yellow,
                "icon": icon.weather.get(info.weather[0], None)
            },

            "time": {
                "text": __time__,
                "color": cyan,
                "icon": icon.time
            },

            "date": {
                "text": today,
                "color": green,
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
                console.print(f"Expecting property name enclosed in double quotes at: {CONFIG_PATH}", justify="center")
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
                        icon_ = widget.get("icon", widgets_set[name]["icon"])

                        # Update the widget in the widgets_set if text, color, and icon are provided
                        if text and color and icon_:
                            widgets_set[name] = {
                                "text": text,
                                "color": color,
                                "icon": icon_
                            }
            except Exception:
                # Handle any unexpected errors during iteration
                console.print(f"widgets not configured properly at: {CONFIG_PATH}", justify="center")
                sys.exit(0)

        # Initialize an empty dictionary to store valid widgets
        widgets = {}
        # Iterate over the items in the widgets_set dictionary
        for name, widget in widgets_set.items():
            try:
                # Attempt to extract the necessary properties from the widget
                text = widget["text"]
                color = widget["color"]
                icon_ = widget["icon"]

                # Check if all required properties are present and not empty
                if text and icon and color:
                    # Store the provided values in the widgets dictionary, associated with the specific widget name.
                    widgets[name] = f"[{black}]{icon.circle[0]}[on {black}][{color}]{icon_}[/] [b white]{text}[/][/][{black}]{icon.circle[1]}"
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
                    exec_  = widget.get("exec", None)
                    script = widget.get("script", None)
                    color  = widget.get("color", "na")
                    icon_  = widget.get("icon", "na")
                    index  = widget.get("index", len(widgets))

                    if exec_:
                        # Execute the command and capture the output
                        text = subprocess.run(exec_, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()
                        # Reset the exec_ variable to None to prevent further execution
                        exec_ = None
                        
                    elif script:
                        # Check if the script path is absolute and if the file exists
                        if os.path.isabs(script):
                            if os.path.isfile(script):
                                with open(script) as f:
                                    script = f.read()
                                    # Check if the script content is empty
                                    if not script.strip():
                                        # Print an error message and exit if the script file is empty
                                        console.print(f"script file is empty for {name} widget addon at: {CONFIG_PATH}", justify="center")
                                        sys.exit(1)
                            else:
                                # Print an error message and exit if the script path is not found
                                console.print(f"script path not found for {name} widget addon at: {CONFIG_PATH}", justify="center")
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
                            # Print an error message indicating an invalid script
                            console.print(f"invalid script for {name} widget addon at: {CONFIG_PATH}", justify="center")
                            # Exit the program with an error status code
                            sys.exit(1)

                    # Check if text is provided and icon is "na"
                    if text and icon_ == "na":
                        # Construct the widget value with default icon
                        value = f"[{black}]{icon.circle[0]}[on {black}][b white][{color}]{text}[/][/][/][{black}]{icon.circle[1]}"
                        # Insert the widget into the widgets dictionary at the specified index
                        widgets = insert_dict(widgets, index, name, value)

                    # Check if text, color, and icon are provided
                    elif text and not color == "na" and not icon_ == "na":
                        # Construct the widget value with provided icon
                        value = f"[{black}]{icon.circle[0]}[on {black}][{color}]{icon_}[/] [b white]{text}[/][/][{black}]{icon.circle[1]}"
                        # Insert the widget into the widgets dictionary at the specified index
                        widgets = insert_dict(widgets, index, name, value)
                    else:
                        # Print an error message if the addon widget is not properly configured
                        console.print(f"'{name}' addon widget not configured properly at: {CONFIG_PATH}", justify="center")
                        # Exit the program with an error status code
                        sys.exit(1)

                    # Insert the widget into the widgets_set dictionary with its properties
                    widgets_set = insert_dict(widgets_set, len(widgets_set), name, {"text": text, "color": color, "icon": icon_})

            except Exception:
                # Handle any exceptions that occur during addon widget configuration
                console.print(f"addons not configured properly at: {CONFIG_PATH}", justify="center")
                # Exit the program with an error status code
                sys.exit(1)

        if args.widgets:
            # Convert the widgets_set dictionary to JSON format with indentation for readability
            output = json.dumps(widgets_set, indent=2)
            # Print the JSON output
            print(output)
            # Exit the program with a success status code
            sys.exit(0)

        if args.json:
            # Convert the widgets_set dictionary to JSON format with indentation for readability
            output = json.dumps(widgets, indent=2)
            # Print the JSON output
            print(output)
            # Exit the program with a success status code
            sys.exit(0)

        # Extract the values (widget information) from the widgets dictionary and convert them into a list
        widget_values = list(widgets.values())
        # Divide the widget values into rows based on the specified number of columns
        widget_rows = [widget_values[i:i+args.column] for i in range(0, len(widget_values), args.column)]

        # console.print(max(widget_rows))

        # Iterate over each row of widgets
        for widget in widget_rows:
            # Print each widget in the row, with two spaces padding on the left, centered alignment, and newline after each row
            console.print(" "*2, *widget, justify="center", end="\n\n")
        # Print additional whitespace as specified by the user (args.whitespace - 1) times
        print("\n"*(args.whitespace-1))

    except (EOFError, KeyboardInterrupt):
        console.print(badge(red, f"status[1]", "Program interrupted."), justify="center", end="\n\n")

if __name__ == "__main__":
    main()