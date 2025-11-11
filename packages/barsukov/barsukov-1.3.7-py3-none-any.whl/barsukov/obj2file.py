### BEGIN Dependencies ###
import dill
import os
from barsukov.logger import debug
### END Dependencies ###


def save_object(obj, file_name, update=False, full_folder_path=None, script=None):
    """
    Saves a class object to a file using the '.pickle' format.

    Args:
        obj (object): An instance of a class to be saved. (Required)
        file_name (str): Name of the file (must end with '.pickle'). (required)
        update (bool, optional): if 'True', overwrites an existing file. Defaults to 'False'.
        full_folder_path (str, optional): absolute path to the directory (e.g., "C://Users//John//Documents").
            Defaults to the current working directory if not provided.
        script (Script, optional): Script object providing directory information. 
            Defaults to 'None'.

    Returns:
        str: Confirmation message upon successful save.

    Raises:
        FileExistsError: If the file already exists and 'update=False'.

    Example:
        >>> equipment = mwHP(...)
        >>> save_object(obj=equipment, file_name="mwHP.pickle")
        'equipment successfully saved in mwHP.pickle.'
    """
    # Check if full_folder_path is provided and is an absolute path:
    if full_folder_path and not os.path.isabs(full_folder_path):
        return debug(f"Please provide an absolute path (e.g., 'C://Users//John//Documents').")

    #Set folder_path based on the provided or default to current directory
    full_folder_path = full_folder_path or (script.full_folder_path if script else os.getcwd())
    full_file_path = os.path.join(full_folder_path, file_name)

    if update:
        # If update is True, overwrite the file
        with open(full_file_path, 'wb') as file:
            dill.dump(obj, file)
            return debug(f"{obj} object successfully saved.")
    else:
        try:
            # Try to create the file and save the object
            with open(full_file_path, 'xb') as file:
                dill.dump(obj, file)
                return debug(f"{obj} successfully saved in {file_name}.")
        except FileExistsError:
            # If the file already exists, provide a message
            raise FileExistsError(f"File '{file_name}' already exists. Use 'update=True' to overwrite.")


def load_object(file_name, full_folder_path=None, script=None):
    """
    Loads a class object stored in a '.pickle' formatted file.

    Args:
        file_name (str): Class object file (must end in '.pickle'). (Required)
        full_folder_path (str, optional): absolute path to the directory where file exists (excluding the file name).
            Defaults to the current working directory.
        script (Script, optional): Script object providing directory information. 
            Defaults to 'None'.

    Returns:
        object: The loaded class object.

    Raises:
        FileNotFoundError: If the file doesn't exist in the specified location.

    Example:
        >>> new_equipment = load_object(file_name="mw.pickle")
        'Object successfully loaded from mw.pickle.'
    """
    # Check if the provided full_folder_path is absolute
    if full_folder_path and not os.path.isabs(full_folder_path):
        return debug(f"Please provide an absolute path (e.g., 'C://Users//John//Documents').")

    # Set full_folder_path based on provided or default to current directory
    full_folder_path = full_folder_path or (script.full_folder_path if script else os.getcwd())
    full_file_path = os.path.join(full_folder_path, file_name)

    # Check if the file exists at the specified path
    if not os.path.isabs(full_file_path):
        raise FileNotFoundError(f"The object file {file_name} does not exist at the specified directory.")

    # load the object from the file
    with open(full_file_path, 'rb') as file:
        instance = dill.load(file)
        print(debug(f'Object successfully loaded from {file_name}.'))
    return instance
