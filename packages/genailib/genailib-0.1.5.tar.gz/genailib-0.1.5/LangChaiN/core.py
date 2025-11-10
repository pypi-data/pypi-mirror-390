import importlib.resources

def show_code(filename):
    """
    Print the contents of filename from the installed package.
    """
    try:
        # Locate and open the file inside the LangChaiN package
        with importlib.resources.files("LangChaiN").joinpath(filename).open("r", encoding="utf-8") as f:
            print(f.read(), end='')
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found in LangChaiN package.")
    except Exception as e:
        print(f"An error occurred while reading '{filename}': {e}")
