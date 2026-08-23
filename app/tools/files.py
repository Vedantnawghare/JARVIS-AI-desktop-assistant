import os
import shutil
import subprocess


def _expand_path(path: str) -> str:
    return os.path.expandvars(
        os.path.expanduser(
            path.strip()
        )
    )


def open_file_explorer(path: str = "") -> str:
    path = _expand_path(path)

    if not path:
        path = os.path.expanduser("~")

    if path.lower() in {
        "this pc",
        "this_pc",
        "my computer",
        "computer",
    }:
        try:
            subprocess.Popen(
                [
                    "explorer.exe",
                    "shell:MyComputerFolder",
                ]
            )
            return "Opened This PC"
        except Exception as exc:
            return f"Could not open This PC: {exc}"

    if not os.path.exists(path):
        return f"Path does not exist: {path}"

    try:
        os.startfile(path)
        return f"Opened Explorer at: {path}"
    except Exception as exc:
        return f"Could not open Explorer: {exc}"


def open_file_or_folder(path: str) -> str:
    path = _expand_path(path)

    if not path:
        return "File or folder path is empty"

    if path.lower() in {
        "this pc",
        "this_pc",
        "my computer",
        "computer",
    }:
        return open_file_explorer("this_pc")

    if not os.path.exists(path):
        return f"Path does not exist: {path}"

    try:
        os.startfile(path)
        return f"Opened: {path}"
    except Exception as exc:
        return f"Could not open: {exc}"


def create_folder(path: str) -> str:
    path = _expand_path(path)

    if not path:
        return "Folder path is empty"

    if os.path.exists(path):
        if os.path.isdir(path):
            return f"Folder already exists: {path}"
        return f"A file already exists at: {path}"

    try:
        os.makedirs(path, exist_ok=False)
        return f"Created folder: {path}"
    except Exception as exc:
        return f"Could not create folder: {exc}"


def create_file(path: str, content: str = "") -> str:
    path = _expand_path(path)

    if not path:
        return "File path is empty"

    if os.path.exists(path):
        return f"File already exists: {path}"

    parent = os.path.dirname(path)

    if parent and not os.path.exists(parent):
        return f"Parent folder does not exist: {parent}"

    try:
        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(content)

        return f"Created file: {path}"
    except Exception as exc:
        return f"Could not create file: {exc}"


def copy_file_or_folder(
    source: str,
    destination: str,
) -> str:
    source = _expand_path(source)
    destination = _expand_path(destination)

    if not os.path.exists(source):
        return f"Source does not exist: {source}"

    if not destination:
        return "Destination is empty"

    try:
        if os.path.isdir(source):
            final_destination = destination

            if os.path.isdir(destination):
                final_destination = os.path.join(
                    destination,
                    os.path.basename(
                        os.path.normpath(source)
                    ),
                )

            shutil.copytree(
                source,
                final_destination,
                dirs_exist_ok=False,
            )
        else:
            shutil.copy2(
                source,
                destination,
            )

        return (
            f"Copied '{source}' to "
            f"'{destination}'"
        )

    except FileExistsError:
        return (
            f"Destination already exists: "
            f"{destination}"
        )

    except Exception as exc:
        return f"Could not copy: {exc}"


def move_file_or_folder(
    source: str,
    destination: str,
) -> str:
    source = _expand_path(source)
    destination = _expand_path(destination)

    if not os.path.exists(source):
        return f"Source does not exist: {source}"

    if not destination:
        return "Destination is empty"

    try:
        shutil.move(
            source,
            destination,
        )

        return (
            f"Moved '{source}' to "
            f"'{destination}'"
        )

    except Exception as exc:
        return f"Could not move: {exc}"


def delete_file_or_folder(
    path: str,
) -> str:
    path = _expand_path(path)

    if not path:
        return "Path is empty"

    if not os.path.exists(path):
        return f"Path does not exist: {path}"

    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

        return f"Deleted: {path}"

    except Exception as exc:
        return f"Could not delete: {exc}"