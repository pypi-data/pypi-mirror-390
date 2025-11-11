from importlib.metadata import version as get_version, PackageNotFoundError
from packaging import version as parse_version
import requests
import os
import json

def check_for_update(package_name="crystalwindow"):
    """
    Checks PyPI for updates.
    Warns every run if outdated.
    Skips warning if your version is newer than PyPI.
    """
    try:
        try:
            current_version = get_version(package_name)
        except PackageNotFoundError:
            print(f"(⚠️ Package '{package_name}' not found)")
            return

        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=3)
        if response.status_code != 200:
            print("(⚠️ PyPI request failed, skipping version check)")
            return

        latest_version = response.json()["info"]["version"]

        # compare versions properly
        if parse_version(current_version) < parse_version(latest_version):
            print(f"\n⚠️ Yo dev! '{package_name}' is outdated ({current_version})")
            print(f"👉 Newest is {latest_version}! Run:")
            print(f"   pip install --upgrade {package_name}")
            print(f"Or peep: https://pypi.org/project/{package_name}/{latest_version}/\n")
        elif parse_version(current_version) > parse_version(latest_version):
            print(f"🚀 Local version ({current_version}) is newer than PyPI ({latest_version}) — flex on 'em 😎")
        else:
            print(f"✅ Up to date! ver = {current_version}.")

    except Exception as e:
        print(f"(⚠️ Version check failed: {e})")
