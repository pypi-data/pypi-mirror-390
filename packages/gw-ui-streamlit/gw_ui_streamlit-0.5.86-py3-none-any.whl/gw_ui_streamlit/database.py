import json
from dbm import dumb

from pydantic import InstanceOf

import gw_ui_streamlit.core as gws
import requests
from gw_settings_management.setting_management import get_endpoint
from gw_ui_streamlit.constants import LOCAL_DBM_LOCATION
from gw_ui_streamlit.utils import update_session


def local_dbm_database(*, db_name: str, location: str = None) -> str:
    """
    Constructs a file path for a local database file.

    Args:
        db_name (str): The name of the database file.
        location (str, optional): The directory path where the database file is located.
            If not provided, the default `LOCAL_DBM_LOCATION` is used.

    Returns:
        str: The full file path to the database file.
    """
    if location is None:
        local_dbm = f"{LOCAL_DBM_LOCATION}/{db_name}"
    else:
        local_dbm = f"{location}/{db_name}"
    return local_dbm


def save_dbm_database(*, db_name: str, record_key: str):
    """
    Save a serialized state to a DBM database.

    This function stores a JSON-serialized state in a DBM database under the specified record key.
    It ensures that both the database name and record key are provided before proceeding.

    Args:
        db_name (str): The name of the DBM database to save the record to.
        record_key (str): The key under which the serialized state will be stored.

    Returns:
        None: The function does not return any value.

    Notes:
        - If either `db_name` or `record_key` is `None`, the function exits without performing any operation.
        - The database is opened in "c" mode, which creates the database if it does not exist.
        - The serialized state is generated using `gws.create_saved_state(short_key=True)`.

    Raises:
        Any exceptions related to file handling or DBM operations are not explicitly handled within this function.
    """
    if record_key is None or db_name is None:
        return
    dbm_dict = dumb.open(local_dbm_database(db_name=db_name), "c")
    saved_state = json.dumps(gws.create_saved_state(short_key=True))
    dbm_dict[record_key] = saved_state
    dbm_dict.close()


def load_from_dbm_database(
    *, db_name: str, selection: str = None, record_key: str = None
):
    """
    Load data from a DBM database and update the session.

    Args:
        db_name (str): The name of the database to load data from.
        selection (str, optional): The selection key used to fetch a value. Defaults to None.
        record_key (str, optional): The record key to directly access the database. Defaults to None.

    Returns:
        None: This function does not return a value. It updates the session with the retrieved data.

    Notes:
        - If `selection` is provided, the function fetches a value using `gws.fetch_value_reset`
          and extracts the key from the fetched value.
        - If `selection` is not provided, the `record_key` is used directly as the key.
        - The retrieved value is read from the database using `read_from_dbm_database` and
          then passed to `update_session` for session update.
    """
    if selection is None:
        key = record_key
    else:
        selected_value = gws.fetch_value_reset(name=selection)
        key = selected_value.split("-")[0].replace(" ", "")
    value = read_from_dbm_database(db_name=db_name, key=key)
    update_session(value, using_code=True)


def read_from_dbm_database(*, db_name: str, key: str, returns: str = "dict"):
    """
    Reads a record from a DBM database and returns it in the specified format.

    Args:
        db_name (str): The name of the DBM database to read from.
        key (str): The key of the record to retrieve from the database.
        returns (str, optional): The format in which to return the record.
            Defaults to "dict". If "dict", the record is decoded,
            NaN values are replaced with null, and the result is returned as a dictionary.
            Otherwise, the raw record is returned.

    Returns:
        Union[dict, bytes]: The record from the database. If `returns` is "dict",
        the record is returned as a dictionary. Otherwise, the raw record is returned as bytes.

    Raises:
        json.JSONDecodeError: If the record cannot be decoded into a dictionary
        when `returns` is "dict".
    """
    dbm = dumb.open(local_dbm_database(db_name=db_name), "c")
    dbm_record = dbm.get(str(key))
    dbm.close()
    if returns == "dict":
        return_dict = dbm_record.decode().replace("NaN", "null")
        return json.loads(return_dict)
    else:
        return dbm_record


def list_from_dbm_database(*, db_name: str, key_structure: list = []) -> list:
    """
    Retrieve a list of formatted strings from a DBM database.

    Args:
        db_name (str): The name of the DBM database to access.
        key_structure (list, optional): A list of keys to extract from the
            database values for inclusion in the formatted output. Defaults to an empty list.

    Returns:
        list: A list of strings, where each string represents a key from the
        database and optionally includes additional information from the value
        based on the provided key_structure.
    """
    dbm_dict = dumb.open(local_dbm_database(db_name=db_name), "c")
    list_applications = []
    for key in dbm_dict.keys():
        value_key = key.decode()
        value_dict = json.loads(dbm_dict[key].decode("utf8"))
        display = f"{value_key}"
        for structure_key in key_structure:
            display = display + f" - {value_dict[structure_key]}"
        list_applications.append(display)
    dbm_dict.close()
    return list_applications


def delete_from_dbm_database(*, db_name: str, record_key: str):
    """
    Deletes a record from a DBM database and updates the session accordingly.

    Args:
        db_name (str): The name of the DBM database.
        record_key (str): The key of the record to be deleted.

    Functionality:
        - Opens the specified DBM database in "c" mode (create if not exists).
        - Reads the value associated with the given record key.
        - Sets all keys in the retrieved value to None.
        - Updates the session using the modified value.
        - Removes the record from the DBM database.
        - Closes the database connection.

    Raises:
        KeyError: If the specified record_key does not exist in the database.
    """
    dbm_dict = dumb.open(local_dbm_database(db_name=db_name), "c")
    value = read_from_dbm_database(db_name=db_name, key=record_key)
    for key in value:
        value[key] = None
    update_session(value, using_code=True)
    dbm_dict.pop(record_key)
    dbm_dict.close()


def update_record():
    """
    Updates or creates a record in the database using REST API endpoints.

    This function interacts with a REST API to either create a new record or update an existing one
    based on the presence of an "_id" field in the `saved_state`. It handles both POST and PUT requests
    and provides feedback to the user via toast notifications and error messages.

    Steps:
    - If the "_id" field in `saved_state` is `None`, a POST request is made to create a new record.
    - If the "_id" field is present, a PUT request is made to update the existing record.
    - Error handling is implemented to catch exceptions and display appropriate error messages.

    Notifications:
    - Success messages are displayed using toast notifications.
    - Error messages are displayed using `gws.show_error` and `gws.get_streamlit().toast`.

    Dependencies:
    - `gws`: A custom module for managing application state and UI interactions.
    - `requests`: Used for making HTTP requests.
    - `json`: Used for serializing and deserializing data.

    Raises:
        Exception: If an error occurs during the HTTP request.

    Returns:
        None
    """
    rest_endpoint = gws.model().rest
    saved_state = gws.create_saved_state(short_key=True, fields=True)
    if saved_state["_id"] is None:
        try:
            request_result = requests.post(
                get_endpoint(f"/{rest_endpoint}/"), data=json.dumps(saved_state)
            )
            if request_result.status_code != 200:
                if type(request_result.text) is str:
                    message = request_result.text
                else:
                    message = json.loads(request_result.text)["detail"]
                gws.show_error(message)
                gws.get_streamlit().toast(message, icon=":material/error:")
                return
            document_list = json.loads(request_result.text)
            update_session(document_list, using_code=True)
            gws.get_streamlit().toast(
                f"**{saved_state[gws.get_primary(gws.model()).db_field]} created**"
            )
        except Exception as e:
            gws.show_error(e)
    else:
        try:
            request_result = requests.put(
                get_endpoint(f"/{rest_endpoint}/"), data=json.dumps(saved_state)
            )
            gws.get_streamlit().toast(
                f"**{saved_state[gws.get_primary(gws.model()).db_field]} saved**"
            )
        except Exception as e:
            gws.show_error(e)


def delete_record():
    """
    Deletes a record from the database.

    This function retrieves the REST endpoint and the saved state of the record
    to be deleted. If the record's revision (`_rev`) is `None`, the function
    exits without performing any action. Otherwise, it attempts to delete the
    record using an HTTP DELETE request to the appropriate endpoint.

    Upon successful deletion, a toast notification is displayed to the user
    indicating the record has been deleted, and the input fields are reset.
    If an error occurs during the deletion process, the error is displayed
    using the `show_error` method.

    Note:
        - The function assumes the existence of a global workspace object (`gws`)
          with methods for model retrieval, state creation, primary key access,
          and UI interactions.
        - The `requests` library is used for making HTTP requests.

    Raises:
        Exception: If an error occurs during the HTTP DELETE request.

    Returns:
        None
    """
    rest_endpoint = gws.model().rest
    saved_state = gws.create_saved_state(short_key=True, fields=True)
    try:
        requests.delete(
            get_endpoint(
                f"/{rest_endpoint}/{saved_state[gws.get_primary(gws.model()).db_field]}"
            )
        )
        gws.get_streamlit().toast(
            f"{saved_state[gws.get_primary(gws.model()).db_field]} deleted"
        )
        gws.reset_inputs()
    except Exception as e:
        gws.show_error(e)
