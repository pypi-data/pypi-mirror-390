from importlib.metadata import version as get_version, PackageNotFoundError
import requests
import os
import json

def check_for_update(package_name="crystalwindow"):
    """
    Checks PyPI for updates.
    Warns every run if outdated.
    Only skips check when version is already latest.
    """
    try:
        # get current version
        try:
            current_version = get_version(package_name)
        except PackageNotFoundError:
            print(f"(⚠️ Package '{package_name}' not found)")
            return

        cache_file = os.path.join(os.path.expanduser("~"), f".{package_name}_version_cache.json")

        # load cache
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cache = json.load(f)
        else:
            cache = {}

        # get newest version from PyPI
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=3)

        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]

            if latest_version == current_version:
                # only print once per version
                if cache.get("last_checked") != current_version:
                    print(f"✅ Up to date! ver = {current_version}.")
                    cache["last_checked"] = current_version
                    with open(cache_file, "w") as f:
                        json.dump(cache, f)
            else:
                # always warn until updated
                print(f"\n⚠️ Yo dev! '{package_name}' is outdated ({current_version})")
                print(f"👉 Newest is {latest_version}! Run:")
                print(f"   pip install --upgrade {package_name}")
                print(f"Or peep: https://pypi.org/project/{package_name}/{latest_version}/\n")

        else:
            print("(⚠️ PyPI request failed, skipping version check)")

    except Exception as e:
        print(f"(⚠️ Version check failed: {e})")
