import os
import platform, subprocess

arch = platform.machine().lower()   # Get the lowercase machine architecture of the system

try:
    # Try to access the ANDROID_ROOT environment variable
    android = os.environ["ANDROID_ROOT"]
    getprop = "/system/bin/getprop"

    # Check if "/system" is in the value of the ANDROID_ROOT environment variable
    if "/system" in android:
        system = "android"
        hostname = subprocess.run([getprop, "ro.product.model"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()
        release = subprocess.run([getprop, "ro.build.version.release"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout.strip()
except Exception:
    # If there's an exception (e.g., the ANDROID_ROOT environment variable doesn't exist),
    # use psutil and platform to determine the system
    system = platform.system().lower()  # Get the lowercase platform name
    hostname = platform.node().lower()  # Get the lowercase hostname of the system
    release = platform.release()

    if system == "darwin":
        # If the platform is macOS (Darwin), set the system variable to "macos"
        system = "macos"