import os
import subprocess
import sys

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip() + result.stderr.strip()
    except Exception as e:
        return f"Error: {e}"

def print_section(title):
    print(f"\n{'='*10} {title} {'='*10}")

def check_env_var(var):
    val = os.environ.get(var, "Not Set")
    print(f"{var}: {val}")
    return val

print_section("OPERATING SYSTEM")
print(run_cmd("cat /etc/os-release | grep PRETTY_NAME"))

print_section("JAVA ENVIRONMENT")
check_env_var("JAVA_HOME")
print(f"Java Version Output:\n{run_cmd('java -version')}")
print(f"Javac Version: {run_cmd('javac -version')}")

print_section("GRADLE ENVIRONMENT")
print(f"System Gradle Version:\n{run_cmd('gradle -version')}")

print_section("ANDROID SDK")
sdk_root = check_env_var("ANDROID_HOME")
if sdk_root == "Not Set":
    sdk_root = "/opt/android-sdk" # Fallback check
    print(f"Checking default path: {sdk_root}")

if os.path.exists(sdk_root):
    print(f"SDK Root Exists: Yes")
    
    # Check Build Tools
    build_tools = os.path.join(sdk_root, "build-tools")
    if os.path.exists(build_tools):
        print("\nInstalled Build-Tools:")
        print(run_cmd(f"ls {build_tools}"))
    else:
        print("\nBuild-Tools folder NOT found.")

    # Check Platforms
    platforms = os.path.join(sdk_root, "platforms")
    if os.path.exists(platforms):
        print("\nInstalled Platforms (API Levels):")
        print(run_cmd(f"ls {platforms}"))
    else:
        print("\nPlatforms folder NOT found.")
        
    # Check Cmdline Tools
    cmdline = os.path.join(sdk_root, "cmdline-tools")
    if os.path.exists(cmdline):
         print(f"\nCmdline-Tools found at: {cmdline}")
         # Try to list specific tools versions
         print(run_cmd(f"ls -R {cmdline} | grep 'bin' -B 5 | head -n 10"))
else:
    print("CRITICAL: Android SDK directory not found!")

print_section("PYTHON ENVIRONMENT")
print(f"Python Version: {sys.version.split()[0]}")
print(f"Pip Version: {run_cmd('pip --version')}")
try:
    import PIL
    print(f"Pillow (Image Lib) Version: {PIL.__version__}")
except ImportError:
    print("Pillow is NOT installed.")

print_section("PROCESS LIMITS")
print(run_cmd("ulimit -a"))

print("\n" + "="*30)
print("DIAGNOSIS COMPLETE")
print("Please copy the output above and paste it back.")
