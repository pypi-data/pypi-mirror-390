from importlib.metadata import version as get_version, PackageNotFoundError
import requests
import os
import json

def check_for_update(package_name="crystalwindow"):
    """
    Checks PyPI for updates once per installed version.
    If up to date, prints it only once.
    If outdated, warns user every time until updated.
    """
    try:
        # get current version
        try:
            current_version = get_version(package_name)
        except PackageNotFoundError:
            print(f"(⚠️ Package '{package_name}' not found)")
            return

        # file to track last notified version
        cache_file = os.path.join(os.path.expanduser("~"), f".{package_name}_version_cache.json")

        # load cache
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cache = json.load(f)
        else:
            cache = {}

        # skip check if we already confirmed this version
        if cache.get("last_checked") == current_version:
            return

        # get newest version from PyPI
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=3)

        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]

            if latest_version == current_version:
                print(f"✅ Up to date! ver = {current_version}.")
                cache["last_checked"] = current_version
            else:
                print(f"\n⚠️ Hey Future Dev! You're using an old version of {package_name} ({current_version})")
                print(f"👉 The latest is {latest_version}! To update, run:")
                print(f"   pip install --upgrade {package_name}")
                print(f"Or visit: https://pypi.org/project/{package_name}/{latest_version}/\n")

            with open(cache_file, "w") as f:
                json.dump(cache, f)

    except Exception as e:
        print(f"(⚠️ Version check failed: {e})")
