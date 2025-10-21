def read_file(file_path):
    # Reading and return text content from file
    try:
        with open(file_path, "r", encoding = "utf-8") as file:
            data = file.read()
        return data
    except FileNotFoundError:
        print(f"Error: file {file_path} not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def write_file(file_path, data):
    # Write(save) text content to a file.
    try:
        with open(file_path, "w", encoding = "utf-8") as file:
            file.write(data)
        print(f"File saved successfully as '{file_path}'")

    except Exception as e:
        print(f"Error writing file:{e}")

