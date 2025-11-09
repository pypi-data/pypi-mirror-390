import os

def show_stats(filename: str = None):
    """
    Displays code from the scipyy package.
    - If filename is given (without .py), shows that file's code.
    - If no filename is given, shows all .py files.
    """
    base_path = os.path.dirname(__file__)
    files = [f for f in os.listdir(base_path) if f.endswith(".py") and f != "__init__.py"]

    if filename:
        file_path = os.path.join(base_path, f"{filename}.py")
        if os.path.exists(file_path):
            print(f"\n=== Showing {filename}.py ===\n")
            with open(file_path, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print(f"\n❌ File '{filename}.py' not found in scipyy.\n")
            print("Available files:")
            for f in files:
                print("•", f.replace(".py", ""))
    else:
        print("\nAll practical codes in scipyy:\n")
        for f in files:
            print(f"\n=== {f} ===\n")
            with open(os.path.join(base_path, f), "r", encoding="utf-8") as file:
                print(file.read())
