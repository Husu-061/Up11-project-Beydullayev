import os

files_to_check = [
    "resources/picture.png",
    "resources/watch_1.png"
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    print(f"Файл {file_path} существует: {exists}")