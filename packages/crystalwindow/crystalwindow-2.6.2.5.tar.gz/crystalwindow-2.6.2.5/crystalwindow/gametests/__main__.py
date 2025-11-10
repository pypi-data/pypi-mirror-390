# crystalWindow/examples/__main__.py
import importlib

DEMO_SCRIPTS = {
    "guitesting": "GUI widgets & layout demo",
    "gravitytest": "Gravity + physics test",
    "windowtesting": "Basic window and draw test",
    "sandbox": "Free experiment playground",
}

def list_demos():
    print("CrystalWindow Example Demos 🧊")
    print("--------------------------------")
    for name, desc in DEMO_SCRIPTS.items():
        print(f"{name:<15} - {desc}")
    print("\nRun one with:")
    print("  python -m cystalWindow.examples.<demo_name>\n")

def main():
    list_demos()

if __name__ == "__main__":
    main()
