import os

# Get the path to the user's home directory
HOME = os.path.expanduser("~")

# Construct the path to the configuration file within the user's home directory
CONFIG_PATH = os.path.join(HOME, ".twidgets.json")

