import os

def show_code(practical_name):
    """
    Displays the code of a specific practical file.
    Example:
        import myprac
        myprac.show_code("prac2")
    """
    filename = f"{practical_name}.py"
    path = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(path):
        print(f"\n📘 ==== {filename} ====\n")
        with open(path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("⚠️ Practical not found! Use myprac.list_practicals() to see available ones.")

def list_practicals():
    """Lists all available practical files in this library."""
    files = [f for f in os.listdir(os.path.dirname(__file__)) if f.startswith("prac") and f.endswith(".py")]
    print("\n📚 Available Practicals:")
    for f in sorted(files):
        print("  -", f.replace(".py", ""))

print("✅ myprac library imported successfully!")
print("Use myprac.show_code('pracX') to view a practical.")
print("Use myprac.list_practicals() to see all available ones.")