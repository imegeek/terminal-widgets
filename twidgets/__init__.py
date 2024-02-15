from rich.console import Console
from  datetime import datetime, date
import platform, os, sys, subprocess, requests, re, json, threading, argparse

pyversion = sys.version.split()[0]

HOME = os.path.expanduser("~")
CONFIG_PATH = os.path.join(HOME, ".twidgets.json")

if not os.path.isfile(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        f.write("")

color_mode = ["normal", "vivid", "custom"]

parser = argparse.ArgumentParser()

parser.add_argument(
    "--color",
    choices=color_mode,
    default=color_mode[0],
    metavar=color_mode,
    help="Choice an color mode for terminal widgets."
)

args = parser.parse_args()

t = datetime.now()
__time__ = f"{t.hour}:{t.minute}"

today = date.today().strftime("%a, %b %d")

console = Console()

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
    # normal colors
    red    = "#df6b78"
    green  = "#9ACB73"
    yellow = "#F2CD80"
    sky    = "#8AAED2"
    purple = "#b790ff"
    cyan   = "#8EC8D8"
elif args.color == "vivid":
    # vivid colors
    red    = "#D8425C"
    green  = "#8BC455"
    yellow = "#f8d255"
    sky    = "#6AA1DA"
    purple = "#a06efc"
    cyan   = "#6EBEDF"
elif args.color == "custom":
    try:
        ncolors = json.load(open(CONFIG_PATH))["colors"]
        for name in ncolors:
            custom_colors[name] = ncolors[name]
            globals()[name] = ncolors[name]

        nt_colors = [name for name, color in custom_colors.items() if not color]
        if nt_colors:
            print(f"Color {nt_colors} is not configured at: {CONFIG_PATH}")
            sys.exit(0)
    except Exception:
        print(f"Colors not configured properly at: {CONFIG_PATH}")
        sys.exit(0)

def convert_size(size_in_bytes):
    units = ['B', 'K', 'M', 'G', 'T', 'P']
    
    unit_index = 0
    while size_in_bytes >= 1024 and unit_index < len(units) - 1:
        size_in_bytes /= 1024
        unit_index += 1

    selected_unit = units[unit_index]
    if selected_unit == units[1]:
        size_in_bytes /= 1024
    return size_in_bytes, selected_unit

logo = f"""[b]
[{yellow}]  ▄███████▄  [{green}]   ▄██████▄   [{sky}]   ▄██████▄   [{red}]   ▄██████▄   [{cyan}]   ▄██████▄   
[{yellow}]  ▄█████████▀▀ [{green}] ▄[{white}]█▀█[{green}]██[{white}]█▀█[{green}]██▄ [{sky}] ▄[{white}]█▀█[{sky}]██[{white}]█▀█[{sky}]██▄ [{red}] ▄[{white}]█▀█[{red}]██[{white}]█▀█[{red}]██▄ [{cyan}] ▄[{white}]█▀█[{cyan}]██[{white}]█▀█[{cyan}]██▄   
[{yellow}] ████████▀     [{green}] █[{white}]▄▄█[{green}]██[{white}]▄▄█[{green}]███ [{sky}] █[{white}]▄▄█[{sky}]██[{white}]▄▄█[{sky}]███ [{red}] █[{white}]▄▄█[{red}]██[{white}]▄▄█[{red}]███ [{cyan}] █[{white}]▄▄█[{cyan}]██[{white}]▄▄█[{cyan}]███   
[{yellow}] ████████▄     [{green}] ████████████ [{sky}] ████████████ [{red}] ████████████ [{cyan}] ████████████   
[{yellow}]  ▀█████████▄▄ [{green}] ██▀██▀▀██▀██ [{sky}] ██▀██▀▀██▀██ [{red}] ██▀██▀▀██▀██ [{cyan}] ██▀██▀▀██▀██   
[{yellow}]    ▀███████▀  [{green}] ▀   ▀  ▀   ▀ [{sky}] ▀   ▀  ▀   ▀ [{red}] ▀   ▀  ▀   ▀ [{cyan}] ▀   ▀  ▀   ▀   
[/]"""

def main():
    try:
        android = os.environ["ANDROID_ROOT"]    
        if "/system" in android:
            system = "Android"
    except Exception:
        import psutil
        system = platform.system()
        
    console.print(logo, justify="center")

    class Icon:
        battery = ["󰁺","󰁻","󰁼","󰁽","󰁾","󰁿","󰂀","󰂁","󰂂","󰁹","󰂄"]
        status = ["󰗠", "", ""]
        left = ""
        cpu = ""
        user = ""
        time = ""
        online = ""
        offline = ""
        storage = "󰋊"
        package = "󰏗"
        volume = "󰕾"
        python = "󰌠"
        signal = ""
        shell = ""
        date = ""
        mute = "󰖁"
        ram = ""
        right = ""
        os = {"Windows":"", "Linux":"󰻀", "Darwin":"", "Android":"󰀲"}
        os = os.get(system, status[2])

        def badge(self,color,icon,name):
            number = ''.join(re.findall(r'-?\d+', icon))
            icon = re.sub(r'[^a-zA-Z]', '', icon)

            if number:
                if not getattr(self, icon)[int(number)] == None or not name == None:
                    return f"[{black}]{self.left}[on {black}][{color}]{getattr(self, icon)[int(number)]}[/] [b white]{name}[/][/][{black}]{self.right}"
                else:
                    return ''
            else:
                if not getattr(self, icon) == None or not name == None:
                    return f"[{black}]{self.left}[on {black}][{color}]{getattr(self, icon)}[/] [b white]{name}[/][/][{black}]{self.right}"
                else:
                    return ''
            
        @staticmethod
        def hex_to_ansi(val,layout):
            if not val == 0:
                # Convert hex color to RGB
                val = val.lstrip('#')
                rgb_color = tuple(int(val[i:i+2], 16) for i in (0, 2, 4))

                # Create ANSI escape sequence for the RGB color
                return f'\033[{layout};2;{rgb_color[0]};{rgb_color[1]};{rgb_color[2]}m'
            else:
                return f"\033[{val}m"

    icon = Icon
    badge = Icon().badge
    ansi = Icon.hex_to_ansi

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

    def printINFO(color, icon, text):
        # string = f"{ansi(black, 38)}{icon.left}{ansi(black, 48)}{ansi("9ACB73", 38)}{icon.signal}{ansi(0, 38)}{ansi(black, 48)} getting info, wait{ansi(0, 38)}{ansi(black, 38)}{icon.right}"

        string = badge(color, icon, text)

        # hide extra coloring character from string
        re_string = re.sub(r'\[[^\]]*\]', '[]', string).replace("[]", "")

        # center text within the console width
        padding = " " * int(((console.width - len(re_string)) // 2)+2)
        console.print(padding + string, end="\r")

    def getREQ():
        try:
            global reqStatus
            # sending equest to get network status code
            req = requests.get(f"https://1.1.1.1")
            status = req.status_code

            # capture request status code and set boolean with ternary operator
            reqStatus = True if status == 200 else None
            
        except Exception:
            reqStatus = False

    printINFO(green, "signal", "getting information, wait")

    getREQ_thread = threading.Thread(target=getREQ)
    getREQ_thread.start()

    if system == "Android":
        command = "am startservice -n com.termux.api/.KeepAliveService"
        output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stderr.strip()
        if output:
            console.print(badge(red, f"status[1]", "Termux:API not found, install to continue."), justify="center")
            console.print("https://f-droid.org/en/packages/com.termux.api", justify="center")
            sys.exit(1)

    hostname = platform.node().lower()

    class System(Icon):
        @staticmethod
        def getPackage():
            """
            Get Package count
            """
            if system == "Windows":
                command = r"(Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | ? { $_.DisplayName -and $_.DisplayName -notmatch '^KB[0-9]' }).Count"
                output = subprocess.run(f"powershell -c \"{command}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()+" exe"

            elif system in ["Android", "Linux"]:
                command = "dpkg -l | wc -l"
                output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()+" apt"

            elif system == "Darwin":
                command = "brew list | wc -l"
                output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()+" brew"

            return output

        @staticmethod
        def getRAM():
            """
            RAM (Memory) information
            """
            if system == "Android":
                mem_path = "/proc/meminfo"
                with open(mem_path) as f:
                    mem_info = f.readlines()

                mem = getCols(mem_info)
                total_ram = int(findStr(mem, "MemTotal")[1])
                avail_ram = int(findStr(mem, "MemAvailable")[1])
                used_ram = total_ram - avail_ram
                ram = f"{used_ram / 1024**2:.1f}/{total_ram / 1024**2:.0f} GB"

            else:
                svmem = psutil.virtual_memory()
                total_ram = f"{svmem.total / (1024 ** 2):.0f}"
                used_ram = f"{svmem.used / (1024 ** 2):.0f}"

                if int(total_ram) > 512:
                    avail_ram = f"{(int(total_ram) - int(used_ram)) / 1024:.0f}"
                    ram = f"{int(used_ram) / 1024:.1f}/{int(total_ram) / 1024:.0f} GB"
                else:
                    avail_ram = f"{(int(total_ram) - int(used_ram))}"
                    ram = f"{used_ram}/{total_ram} MB"

            return ram

        @staticmethod
        def getSHELL():
            """
            SHELL information
            """
            if not system == "Windows":
                # Get the value of the SHELL environment variable
                current_shell = os.environ.get('SHELL')

                if current_shell:
                    shell = current_shell.split("/")[-1]
                else:
                    None
            else:
                # List all running processes
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
                        pass
            return shell
        
        @staticmethod
        def getBATTERY():
            """
            Battery information
            """
            if system == "Android":
                battery_info = subprocess.run("termux-battery-status", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()
                battery = json.loads(battery_info)
                percent = battery["percentage"]
                power = True if battery["status"] == "CHARGING" else False
            else:
                battery = psutil.sensors_battery()
                percent = battery.percent
                power = battery.power_plugged

            if power:
                index = -1
            else:
                index = (percent // 10) -1

            return [index,f"{percent}%"]

        @staticmethod
        def getDISK():
            """
            DISK (Storage) information
            """
            if system == "Android":
                df_path = "/system/bin/df"
                df_info = subprocess.run(df_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip().split("\n")

                disk = getCols(df_info)

                avail_space, size_unit = convert_size(int(findStr(disk, "emulated")[3])*1024)
                # used_space = int(findStr(disk, "emulated")[2]) / 1024**2
                # avail_space = int(findStr(disk, "emulated")[3]) / 1024**2
                # total_space = avail_space + used_space
            else:
                # Get disk usage information for the root directory
                disk_usage = psutil.disk_usage('/')

                avail_space, size_unit = convert_size(disk_usage.free)
                # used_space = disk_usage.used / (1024 ** 3)
                # avail_space = disk_usage.free / (1024 ** 3)
                # total_space = avail_space + used_space

            if system == "Windows":
                # Print which volume label is using.
                volume_label = os.getcwd().split("\\")[0].removesuffix(":")
                return f"{avail_space:.1f}{size_unit} | {volume_label}"
            else:
                return f"{avail_space:.1f}{size_unit}"

    package = System.getPackage()
    ram = System.getRAM()
    shell = System.getSHELL()
    battery = System.getBATTERY()
    disk = System.getDISK()

    try:
        getREQ_thread.join()
    except KeyboardInterrupt:
        console.print(badge(green, f"status[1]", "KeyboardInterrupt Error found."), justify="center")

    # setting network status using ternary operator
    network = "online" if reqStatus else "offline"

    # setting network icon to the Class which depends on network status using ternary operator
    Icon.net = Icon.online if reqStatus else Icon.offline

    # badge(sky, "python", pyversion) # upcomming...
    console.print(" "*2, badge(green, "user", hostname), badge(cyan, "os", system.lower()), badge(red, "shell", shell), badge(cyan, "ram", ram), badge(sky, f"battery[{battery[0]}]", battery[1]), justify="center", end="\n\n")
    console.print(" "*2, badge(cyan, "net", network), badge(purple, "package", package), badge(green, "storage", disk), badge(cyan, "time", __time__), badge(green, "date", today), justify="center", end="\n\n\n")

if __name__ == "__main__":
    main()
