# -----------------------------------------------------------
# Project: 
# Purpose Details: Handles reading and writing text files
# Course: CMPSC 488
# Author: Kamila Anarkulova
# Date Developed: October 21, 2025
# Last Date Changed: October 21, 2025
# Revision: 1.0 - Initial version, created file read/write functions
# -----------------------------------------------------------

def read_file(file_path):
    # Read and return text content from file
    try:
        # Open file in read mode with UTF-8 encoding to handle all characters
        with open(file_path, "r", encoding = "utf-8") as file:
            data = file.read()       # Read the entire content of the file
        return data
        
    except FileNotFoundError:
        # File not found – print an error message
        print(f"Error: file {file_path} not found")
        return None
        
    except Exception as e:
        # Handle any other unexpected error
        print(f"Error reading file: {e}")
        return None


def write_file(file_path, data):
    # Write(save) text content to a file.
    try:
        # Open file in write mode with UTF-8 encoding
        with open(file_path, "w", encoding = "utf-8") as file:
            file.write(data)             # Write the provided data to the file
        print(f"File saved successfully as '{file_path}'")

    except Exception as e:
        # Handle unexpected write errors
        print(f"Error writing file:{e}")


