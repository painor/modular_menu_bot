import functools
import inspect
import json
import os
from telethon import Button
from importlib import util

from config import JSON_PATH, BUTTONS_PER_ROW


def import_file(full_name, path):
    """
    Import a file and return the imported module
    :param full_name: The name of the file/directory (without .py)
    :param path: The full path to the file (with .py)
    :return: The imported module
    """
    spec = util.spec_from_file_location(full_name, path)
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dynamic_import(full_path: str) -> tuple:
    """
    Dynamically import a module from a path.
    This will look for the __init__.py file to get the name and description from
    This will then look for a func.py file to get the callback function and message function which will be called
    When a user clicks or sends a message to the relevant module.
    This will also return the description of the module to be used in the buttons text
    :param full_path: The path of the module to import
    :return: Tuple of ({module_name: {name, description, callback_func,message_func}}, description)
    """
    modules = {}

    for directory in os.listdir(full_path):
        directory_path = os.path.join(full_path, directory)
        # we don't want to include __pychache__ so we filter it out
        # this is also useful if we want to add some custom folders (for storage)
        if os.path.isdir(directory_path) and not directory.startswith("_"):
            module = import_file(directory, os.path.join(directory_path, "__init__.py"))
            # first look for the name and description in the __init__.py file
            modules[directory] = {
                "name": module.name,
                "description": module.description,
            }
            # if there are no func.py file that means there will be more nested folders
            if os.path.isfile(os.path.join(directory_path, "func.py")):
                # if we find a func.py file, we import it and get the callback function and message function
                func_file = import_file(directory, os.path.join(directory_path, "func.py"))
                modules[directory]["callback_func"] = func_file.callback_func
                modules[directory]["message_func"] = func_file.message_func
    # we also want the description of the module
    module = import_file(os.path.basename(full_path), os.path.join(full_path, "__init__.py"))
    return modules, module.description


def chunk_buttons(buttons: Button.inline) -> list:
    """
    Chunks a list of buttons into a list of lists of buttons.
    Useful for making buttons display nicely.
    :param buttons: a flat list of inline buttons
    :return: a chunked list of lists of buttons
    """
    return [buttons[i:i + BUTTONS_PER_ROW] for i in range(0, len(buttons), BUTTONS_PER_ROW)]


def load_buttons(modules, add_back=False, path=None):
    """
    Loads the buttons for the specific modules.
    :param modules: the result of dynamic_import, basically a dict of modules with a name property
    :param add_back: Whether we want to add the back button or not
    :param path: if passed, the path to the module which will be used in the data of the buttons
    :return:
    """
    path = path or []
    # sometimes an empty path "" is passed in so we want to filter those out to avoid more if checks
    path = list(filter(None, path))

    # we use the name value from __init__ as the name of the module
    # for the data we use the path of the module seperated by _
    buttons = [
        Button.inline(module_values["name"], data="_".join(path + [module]))
        for module, module_values in modules.items()
    ]
    buttons = chunk_buttons(buttons)

    if add_back:
        buttons.append([Button.inline("Back", data="_".join(path + ["back"]))])
    return buttons


async def load_more_buttons(event, data):
    """
    Used to load more buttons for the modules.
    Useful when a module has nested modules
    :param event: The callbackQuery event
    :param data: the data from the callbackQuery event
    :return:
    """
    # we split the data by _ to get the path of the module
    data = data.split("_")
    path = os.path.join(os.path.dirname(__file__), "modules", *data)
    # we then dynamically import the module (and it's description)
    modules, description = dynamic_import(path)
    # we want to check whether this module is a nested one or not to show the back button
    is_last_data = bool(list(filter(None, data)))
    buttons = load_buttons(modules, add_back=is_last_data, path=data)
    await event.edit(description, buttons=buttons)


def handle_back(event, original_data):
    """
    Handles the back button.
    :param event: The callbackQuery event
    :param original_data: the original data from the callbackQuery event
    :return:
    """
    # we remove the last two element of the data (back and the module name)
    data = original_data.split("_")[:-2]
    # we join it again with _
    data = "_".join(data)
    # we send the data to load_more_buttons
    return load_more_buttons(event, data)


def stacktrace(func):
    """
    A decorator to include where this function was called from in the stacktrace
    Useful for saving the state of a specific module
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        # small hack
        # we will also save the func_name to be able to call it later if needed
        func_filename = inspect.stack()[1][1]
        full_path = os.path.dirname(func_filename)
        folder_name = os.path.basename(full_path)
        unique_key = folder_name
        # the unique name is the relative path of the module seperated by _
        while folder_name != "modules":
            full_path = os.path.dirname(full_path)
            folder_name = os.path.basename(full_path)
            unique_key += "_" + folder_name
        return func(*args, **kwargs, unique_key=unique_key, caller_function=func_filename)

    return wrapped


def load_json():
    """
    Loads the json file with the state of the modules
    :return:
    """
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_current_func() -> dict:
    """
    Gets the current saved function name for the user (or None)
    :return: dict
    """
    return load_json().get("current_func", None)


def reset_current_func() -> None:
    """
    Reset the current function to None, also reset the state
    :return:
    """
    save_json({"current_func": None})


def save_json(state_dict: dict) -> None:
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(state_dict, f)


@stacktrace
def load_state(state_name: str, unique_key, **kwargs):
    """
    Loads a state from the json file
    :param state_name: the name of the state to load
    :param unique_key: the unique key of the module to look for the state in
    :param kwargs: optional arguments
    :return: None or the state found
    """
    state_dict = load_json()
    return state_dict.get(unique_key, {}).get(state_name, None)


@stacktrace
def set_state(state_name: str, state_value, unique_key, caller_function):
    """
    Saves a state value to the json file and updates the current_func,
    :param state_name: the name of the state to save
    :param state_value: the value of the state to save
    :param unique_key: the unique key of the module to look for the state in
    :param caller_function: The path of the function that called this function (to save)&
    :return:
    """
    state_dict = load_json()
    state_dict.setdefault(unique_key, {})[state_name] = state_value
    state_dict["current_func"] = caller_function
    save_json(state_dict)
