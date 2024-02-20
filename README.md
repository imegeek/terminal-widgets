<div align="center">
<kbd>
  <img src="https://github.com/imegeek/terminal-widgets/assets/63346676/30780c81-38f5-4083-98b6-caef644a2563" alt="Preview" />
</kbd>
</div><br>

Terminal Widgets is a versatile CLI program designed to enhance your terminal experience by providing various widgets and customizable features. Below is a list of features offered by Terminal Widgets:

<div align="center">
<img src="https://img.shields.io/static/v1?label=build with&message=♡&color=ff7751&labelColor=1e2528&style=for-the-badge">
<br>
<img src="https://img.shields.io/github/stars/imegeek/terminal-widgets?color=F2CD80&labelColor=1e2528&style=for-the-badge">
<img src="https://img.shields.io/static/v1?label=license&message=MIT&color=8ccf7e&labelColor=1e2528&style=for-the-badge">
<img src="https://img.shields.io/github/forks/imegeek/terminal-widgets?color=8EC8D8&labelColor=1e2528&style=for-the-badge">
</div>

## Features:

- **System Information Widgets:**
   - Displays system-related information such as battery status, weather, shell, storage details, hostname, date, RAM usage and many more.

- **Customizable build-in Widgets:**
   - Users can customize widgets according to their preferences, including text, color, icon, index and state.

- **Addons Widgets:**
   - Supports addon widgets with customizable text, color, script execution, icon display, and position settings.

- **Dynamic Content Configuration:**
   - Offers a dynamic way to set content inside text, script, or program files without explicitly defining color or icon keys.

- **Configuration Options:**
   - Provides a configuration file (`~/.twidgets.json`) for users to modify settings like custom color codes, addon widgets, and built-in widget configurations.

- **Easy Installation:**
   - Available for installation via pip or as a local install for convenient setup.

- **Color Formatting Support:**
   - Supports color formatting using both named colors (e.g., `[red]`) and hexadecimal color codes.

- **Icon Integration:**
    - Allows integration of icons into text content using Unicode characters, enhancing visual representation within widgets.

- **Supports Command Line Arguments**
  - Terminal-Widgets offers support for command line arguments, providing users with flexibility in configuring and managing the program directly from the terminal.
  - Refer to the [Argument Options](#argument) for more detailed information.

## Screenshots

<kbd>
<p align="center">Windows
<img src="https://github.com/imegeek/terminal-widgets/assets/63346676/0915b7ad-671d-4e37-b68d-cd3e292cb2ed">
</p>
</kbd>

<kbd>
<p align="center">Linux
<img src="https://github.com/imegeek/terminal-widgets/assets/63346676/64132f65-748e-4ee3-966b-7be73d5ce8b7">
</p>
</kbd>

<kbd>
<p align="center">macOS
<img src="https://github.com/imegeek/terminal-widgets/assets/63346676/5697d372-9855-4929-9935-641291ffe8cb">
</p>
</kbd>

<kbd>
<p align="center">Android
<img src="https://github.com/imegeek/terminal-widgets/assets/63346676/386088c8-5229-4899-bc1b-45f74aaeaa8d">
</p>
</kbd>

## Supported platforms
- Linux
- Windows
- Darwin (macOS)
- Android (Termux)
- WSL (Windows Subsystem for Linux)

## Getting Started

To start using Terminal Widgets, follow these steps:
1. Install the program via pip or perform a local install.
2. Ensure you have Nerd Font installed for optimal display.
3. Customize your widgets and addons using the configuration file (`~/.twidgets.json`).
4. Refer to the [Configuration](#configuration) for more detailed information on configuration options and usage.

## Prerequisites

Before using Terminal Widgets, please ensure that you have the following prerequisites installed:

1. **Python 3.x**: Terminal Widgets is written in Python and requires Python 3.x to be installed on your system.

2. **Nerd Font**: Terminal Widgets requires Nerd Font for display glyphs. If not installed, download one from [here](https://www.nerdfonts.com/).

3. **For Android users using Termux**:
   - **Termux**: Terminal Widgets can be used on Android devices via Termux. Ensure that you have [Termux](https://f-droid.org/en/packages/com.termux/) installed on your Android device from the Google Play Store or F-Droid.

   - **Termux-API**: Terminal Widgets requires the Termux-API app for certain functionalities. Install the [Termux-API](https://f-droid.org/en/packages/com.termux.api/) app from the Google Play Store or F-Droid.

   - **termux-api**: Terminal Widgets requires the termux-api package for certain functionalities. Install termux-api by running the following command in your Termux terminal:

     ```
     pkg install termux-api
     ```

## Installation

You can install Terminal Widgets using pip, or you can clone the repository and install it locally.

### Install via pip

To install Terminal Widgets via pip, simply run the following command:

```
pip install terminal-widgets
```
or
```
pip3 install terminal-widgets
```

This will download and install the latest version of Terminal Widgets from the Python Package Index (PyPI) along with its dependencies.

### Manual Installation

To install Terminal Widgets locally, follow these steps:

1. Clone this repository to your local machine.
`git clone https://github.com/imegeek/terminal-widgets`

2. Navigate to the cloned directory.
`cd terminal-widgets`

3. Install the package using pip:
`pip install .`
or
`pip3 install .`

This will install Terminal Widgets along with its dependencies from the local source files.

## Usage

Simply run the **`twidgets`** in your terminal to get an overview of your system status.
try these command if not working:
```shell
python -m twidgets
```
or
```shell
python3 -m twidgets
```

<a name="argument"></a>
## Argument Options:

Terminal-Widgets supports the following command line options for customization and control:

- **-h, --help**: Show this help message and exit.
- **--configs**: Show the configuration file.
- **--widgets**: Show built-in widgets and their values.
- **--stdout**: Turn off all colors and disable any ASCII, printing only texts.
- **--json**: Show widgets output as a JSON object.
- **--show ['logo', 'widgets']**: Specify what to show: 'logo' or 'widgets'.
- **--color ['normal', 'vivid', 'random', 'custom']**: Choose a color mode for terminal widgets.
- **--weather location**: Set the weather location to show in widgets.
- **-c file, --config file**: Specify the JSON configuration file to load.
- **--column length**: Specify the number of columns that will be displayed for each row.
- **--whitespace length**: Specify the number of whitespaces that will be displayed before and after execution.

These options allow users to customize the behavior and appearance of Terminal-Widgets according to their preferences.

<a name="configuration"></a>
## Configuration

Terminal Widgets supports configuration options, allowing users to customize their widgets or add new ones.

To configure Terminal Widgets:

1. Open the configuration file located at `~/.twidgets.json`.

2. Modify the following key-value pairs according to your preferences:
  - **colors**: Define custom color codes for widgets and addons. This option requires all color names (`red`, `cyan`, etc.) to be specified, to show custom colors pass `--color custom` argument to the program.

   - **addons**: Customize addon widgets. Use properties like `text`, `color`, `script`, `exec`, `icon`, and `index`.
     - **text**: The text content to display for the addon.
     - **color**: The color code for the addon text or icon.
     - **script**: The Python script file or code to execute for dynamic text content.
     - **exec**: The terminal command to execute for dynamic text content.
     - **icon**: The UTF-8 code of the icon or glyph to display for the addon.
     - **index**: The position of the addon in the widget layout.
   - **widgets**: Configure built-in widgets like `username`, `hostname`, `platform`, `shell`, `package`, etc. Use properties like `text`, `color`, `icon`, `index`, and `state`.
     - **text**: The text content to display for the widget.
     - **color**: The color code for the widget icon.
     - **icon**: The UTF-8 code of the icon or glyph to display for the widget.
     - **index**: The position of the widget in the widget layout.
     - **state**: Use "disabled" value to hide specific widget.

3. Dynamic Method for Defining **widget-addon** without Specifying 'color' or 'icon'.
  - **Add Text**:
    - Simply input the desired text.

  - **Add Color**:
    - "[color_name or hex_code]" marks the beginning of the color for the content.
    - "[/]" signifies the end of color formatting.

  - **Add Icon**:
    - Incorporate icons into text content using Unicode characters. For instance, utilize "\uf255" to depict a custom Unicode character as an icon within the text.

  - Refer to Example 11 for further clarification.


4. Save the changes and restart Terminal Widgets to apply the new configuration.


## Configuration Examples
- **Example 1:**
  - This example defines custom **colors** code for terminal-widgets.
```json
{
    "colors": {
        "red": "#FF0000",
        "cyan": "#00FFFF",
        "purple": "#a06efc",
        "green": "#9ACB73",
        "yellow": "#f8d255",
        "sky": "#6AA1DA"
    }
}
```

- **Example 2:**
  - Configures the **build-in** widget `username` to change set custom color of icon.

```json
{
    "widgets": {
        "username": {
            "color": "#d0ff1f"
        }
    }
}
```

- **Example 3:**
  - Configures the **build-in** widget `hostname` to display the text "macbook pro" at index 2 in the layout.

```json
{
    "widgets": {
        "hostname": {
            "text": "macbook pro",
            "index": 2
        }
    }
}
```

- **Example 4:**
  - Configures the **build-in** widget `platform` to display the text "macos" with the custom icon.

```json
{
    "widgets": {
        "platform": {
          "text": "macos",
          "icon": "\uf179"
        }
    }
}
```

- **Example 5:**
  - Configures the **build-in** widget `shell` to display the text "zsh".

```json
{
    "widgets": {
          "shell": {
            "text": "zsh"
        }
    }
}
```

- **Example 6:**
  - Disables the **build-in** widget `storage`, preventing it from being displayed.

```json
{
    "widgets": {
        "storage": {
            "state": "disabled"
        }
    }
}
```

- **Example 7:**
  - Adds a welcome message **addon** with custom text, color, and position in the layout.

```json
{
    "addons": {
        "welcome": {
            "text": "Welcome to Terminal Widgets",
            "color": "#afdaaf",
            "index": 2
        }
    }
}
```

- **Example 8:**
  - Configures the `cputemp` **addon** to execute a Python script that prints a random temperature between 30°C and 60°C, with custom color and icon.

```json
{
    "addons": {
      "cputemp": {
          "script": "import random\nprint(random.randint(30, 60), '\u00B0C')",
          "color": "#ff8522",
          "icon": "\udb84\udcc3"
      }
    }
}
```

- **Example 9:**
  - Configures the `process` **addon** to execute a Python script located at "/path/to/the/file/script.py".

```json
{
    "addons": {
        "process": {
            "script": "/path/to/the/file/script.py"
        }
    }
}
```

- **Example 10:**
  - Configures the `pwd` addon to execute the "pwd" command in the terminal, displaying the current directory path with custom color and icon.

```json
{
    "addons": {
        "pwd": {
          "exec": "pwd",
          "color": "#ffa0f4",
          "icon": "\uf07b"
        }
    }
}
```

- **Example 11:**
  - Configures the `hi` addon to display custom formatted text with colors.
    - **text**: Sets the text content to "[#ff0000]\uf255[/] [#eeff00]Hi, there[/]", where:
      - "[#ff0000]" specifies the start of red color for the text.
      - "\uf255" represents a custom Unicode character.
      - "[#eeff00]" specifies the start of yellow-green color for the text "Hi, there".
      - "[/]" specifies the end of the color formatting.
      - "Hi, there" is the content to be displayed in yellow-green color and icon displayed in red color.

```json
{
    "addons": {
        "hi": {
          "text": "[#ff0000]\uf255[/] [#eeff00]Hi, there[/]"
        }
    }
}
```

- **Example 12:**
  - Configures the `color` addon to display custom color palette widget.
    - Uses a Python script to generate colored blocks representing each color in the palette.
    - Each color block is enclosed in color formatting tags, providing a visual representation of the color.
    - The color key specifies the color of the palette widget.
    - The icon key sets an icon for the palette widget.

```json
{
  "addons": {
    "color": {
        "script": "print(' '.join([f'[{color}]\ueabc[/]' for color in ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']]))",
        "color": "#6aafff",
        "icon": "\ue22b"
    }
  }
}
```

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/imegeek/terminal-widgets/blob/master/LICENSE) file for details.