from .logo import Logo
from .system import system
from rich import print_json
from .path import CONFIG_PATH
from rich.console import Console
from  datetime import datetime, date
from rich_argparse import RichHelpFormatter
import argparse, os, sys, json, random, shlex, subprocess

logo = Logo()
console = Console()  # Create a Console object for rich console output
pyversion = sys.version.split()[0]  # Get the Python version
window_rows, window_columns = os.get_terminal_size()  # Get the size of the terminal window
window_size = f"{window_rows}×{window_columns}"

# Define custom color using hex code
RichHelpFormatter.styles = {
    "argparse.args": "#60bfff bold",
    "argparse.help": "#d2ddff",
    "argparse.metavar": "#9e9e9e",
    "argparse.text": "underline"
}

# Check if the configuration file exists
if not os.path.isfile(CONFIG_PATH):
    # If the configuration file does not exist, create it
    with open(CONFIG_PATH, "w") as f:
        # Open the configuration file in write mode and write an empty string to it
        f.write("")

try:
    weather_api = json.load(open(CONFIG_PATH))["weather_api"]
except Exception:
    weather_api = None

text_mode = {
    "detailed": "includes extended information",
    "compact": "short, less detailed"
}

color_mode = ["normal", "vivid", "random", "custom"]
align_mode = ["left", "center"]
direction_mode = ["row", "column"]

parser = argparse.ArgumentParser(
    description="A fully functional program for Terminal to show information about system, display, shell, package and many more.",
    epilog="See full documentation at: https://github.com/imegeek/terminal-widgets",
    formatter_class=RichHelpFormatter
)

parser.add_argument(
    "-v", "--version",
    action='version',
    version="1.25",
    help="Show the program version."
)

parser.add_argument(
    "-u", "--update",
    action="store_true",
    help="Update the program to the latest version."
)

parser.add_argument(
    "-c", "--config",
    metavar="file",
    help="Specify the JSON configuration file to load."
)

parser.add_argument(
    "--json",
    action='store_true',
    help="Shows widgets output as JSON object."
)

parser.add_argument(
    "--stdout",
    action='store_true',
    help="Turn of all colors and disable any ASCII, printing only texts."
)

parser.add_argument(
    "--configs",
    action='store_true',
    help="Show the configuration file."
)

parser.add_argument(
    "--no-badge",
    action='store_true',
    help="Show widgets without badge style."
)

parser.add_argument(
    "--color-bars",
    action='store_true',
    help="Show color bars in terminal widgets."
)

parser.add_argument(
    "--logo",
    choices=logo.list(),
    default=system,
    metavar=logo.list(),
    help="Choose an logo art that appear before widgets. ( default: auto (system default logo) )"
)

parser.add_argument(
    "--show",
    choices=["logo", "widgets"],
    metavar=["logo", "widgets"],
    default=["logo", "widgets"],
    help="Specify what to show: 'logo' or 'widgets'."
)

parser.add_argument(
    "--text",
    choices=[key for key in text_mode],
    default=list(text_mode.keys())[-1],
    metavar=text_mode,
    help="Choose text mode for terminal widgets. (default: compact)"
)

parser.add_argument(
    "--color",
    choices=color_mode,
    default=color_mode[0],
    metavar=color_mode,
    help="Choose color mode for terminal widgets. (default: normal)"
)

parser.add_argument(
    "--align",
    choices=align_mode,
    metavar=align_mode,
    help="Choose align mode for terminal widgets. (default: center)"
)

parser.add_argument(
    "--direction",
    choices=direction_mode,
    default=direction_mode[-1],
    metavar=direction_mode,
    help="Choose direction mode for terminal widgets. (default: row)"
)

parser.add_argument(
    "--weather",
    dest="location",
    metavar="location",
    help="Set weather location to show in widgets."
)

parser.add_argument(
    "--weather-api",
    metavar="API_KEY",
    default=weather_api,
    help="Set Open Weather API KEY."
)

parser.add_argument(
    "--bypass-system-api",
    action='store_true',
    help="Turn off API checking for required system."
)

parser.add_argument(
    "--column",
    type=int,
    default=5,
    metavar="length",
    help="Specify the number of widget that will be displayed for each row."
)

parser.add_argument(
    "--column-gap",
    type=int,
    default=2,
    metavar="length",
    help="Specify the gap between widgets that will be displayed for each column."
)

parser.add_argument(
    "--row-gap",
    type=int,
    default=1,
    metavar="length",
    help="Specify the gap between widgets that will be displayed for each row."
)

parser.add_argument(
    "--margin",
    type=lambda x: min(int(x), 10),
    default=0,
    metavar="length",
    help="Specify the number of whitespaces line that will be displayed before and after execute."
)

try:
    arg_data = json.load(open(CONFIG_PATH))["args"]
    arg_list = shlex.split(arg_data)
except Exception:
    arg_data = None

try:
    # Check if command-line args are provided
    if len(sys.argv) > 1 or not arg_data:
        args = parser.parse_args()  # Parse the command-line arguments
    else:
        raise ValueError()
except Exception:
    args = parser.parse_args(arg_list)  # Parse the command-line arguments from json

if args.update:
    try:
        console.print(f"[green b]Updating terminal-widgets...[/]")
        # Run pip install command to update the package
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "terminal-widgets"]
        )
        console.print(f"[#60bfff b]terminal-widgets[/] [b u]has been updated to the latest version.[/]")
    except subprocess.CalledProcessError as e:
        console.print(f"[yellow]Failed to update terminal-widgets.[/] Error: {e}")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred:[/] {e}")
    sys.exit(0)

if args.column < 1:
    print("Ensure that the length of the column is atleast one.")
    sys.exit(1)

if args.column_gap < 1:
    print("Ensure that the length of the column gap is atleast one.")
    sys.exit(1)

if args.align:
    align = args.align
else:
    align = "center"

if args.direction == "row":
    align = "left"
    if not args.align == "left" and args.align:
        print(f"The align: '{args.align}' setting is only compatible with a direction: 'column'.")
        sys.exit(1)

if args.location and not args.weather_api:
    console.print(f"Set Open Weather API_KEY through argument or config file to proceed.\n[b]argument[/]: --weather-api <API_KEY>\n[b]config file[/]: \"weather_api\": \"<API_KEY>\" at [b u]{CONFIG_PATH}[/]\n\nGet API_KEY at https://openweathermap.org/api")
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

current_time = datetime.now()  # Get the current time

if args.text == "detailed":
    # Format the current time to include AM/PM
    cftime = current_time.strftime("%I:%M %p")
    # Get today's date and format it as "Day of the week, Month Day"
    today = date.today().strftime("%a, %D")
else:
    cftime = f"{current_time.hour}:{current_time.minute}"  # Format the current time as hours:minutes
    # Get today's date and format it as "Day of the week, Month Day"
    today = date.today().strftime("%a, %b %d")

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

color_codes = {
    "red": None,
    "green": None,
    "yellow": None,
    "sky": None,
    "purple": None,
    "cyan": None,
    "white": "#d6d6d6",
    "black": "#505050"
}

if args.color == "normal":
    # sets the normal colors
    colors = ["#df6b78", "#9ACB73", "#F2CD80", "#8AAED2", "#b790ff", "#8EC8D8"]
    for index, color in enumerate(colors):
        color_codes[list(color_codes.keys())[index]] = color

# Check if the color argument is set to "vivid"
elif args.color == "vivid":
    # sets the vivid colors
    colors = ["#D8425C", "#8BC455" "#f8d255", "#6AA1DA" "#a06efc", "#6EBEDF"]
    for index, color in enumerate(colors):
        color_codes[list(color_codes.keys())[index]] = color

elif args.color == "random":
    num_colors = 6
    random_colors = []
    while len(random_colors) < num_colors:
        # Generate random colors ensuring at least 100 distance between each color
        new_color = generate_random_color(random_colors, min_distance=100)
        random_colors.append(new_color)

    # Sets random colors as hexadecimal values
    for name, color in zip(color_codes, random_colors):
        r, g, b = color
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        color_codes[name] = hex_color

# Check if the color argument is set to "custom"
elif args.color == "custom":
    try:
        # Load custom colors from the configuration file
        ncolors = json.load(open(CONFIG_PATH))["colors"]

        # Update custom_colors and global variables with the loaded custom colors
        for name in ncolors:
            color_codes[name] = ncolors[name]

        # Check if any custom colors are not configured
        nt_colors = [name for name, color in color_codes.items() if not color]

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
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = f.read().strip()

        # Check if the configuration exists
        if config:
            # Print the json configuration
            print_json(config)
            console.print(f"\n[b]file located at:[/] [yellow u]{CONFIG_PATH}[/]")
        else:
            # Print a message if no configuration is found
            print("No configuration found.")
    sys.exit(0)

class Color:
    red: str
    green: str
    yellow: str
    sky: str
    purple: str
    cyan: str
    white: str
    black: str

    def __init__(self):
        for name, color in color_codes.items():
            setattr(self, name, color)

color = Color()
