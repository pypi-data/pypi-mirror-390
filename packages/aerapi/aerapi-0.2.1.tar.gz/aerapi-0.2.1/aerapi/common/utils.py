import requests
import time
import os
import json
import numpy as np
import re
from collections import defaultdict
import pandas as pd
from typing import List, Dict, Any
from jsonschema import validate
import jsonschema.exceptions
# import urllib
# import datetime as dt
from .config import (
    # get_api_config,
    get_ts_files_info,
    extract_urls_from_file,
    find_new_apis,
)


def list_one_item_checker(mylist, string, broken):
    """
    Checks if the provided list is empty, contains multiple items, or a single item,
    and logs critical errors accordingly. If the list is valid, returns the single item.

    Parameters:
    ----------
    mylist : list
        A list of items to be checked.
    string : str
        A string used in the following errors: f"No items found for {string}"
                                               f"Multiple Items found for {string}"
    broken : bool
        A boolean flag indicating if a previous step was already marked as broken
    """
    if len(mylist) < 1:
        # print(f"No items found for {string} in {SN}-{variant_name}")
        # print([x for x in aerlytix_ass['parts'] if 'MAIN' in x['aircraftPartTypeExternalId']])

        print(f"No items found for {string}")


    elif len(mylist) > 1:
        print(f"Multiple items found for {string}")

    elif type(mylist) == list:
        mylist = mylist[0]

    return mylist, broken

def identify_missing_external_apis(base_directory, python_client_path):
    """
    Wrapper function to extract, compare, and identify missing API implementations.

    Parameters:
    - base_directory (str): The base directory where the TypeScript paths files are located.
    - python_client_path (str): The path to the Python client file containing the implemented URLs.

    Returns:
    - list: A list of new APIs that need to be implemented.
    
    Eaxmple:
        base_directory = "C:\\Users\\SeanNicholson\\GitHub\\core2\\backend\\src\\modules\\external_api"
        python_client_path = ./external/api_client.py
        
    """
    # Extract TypeScript path info
    extracted_info = get_ts_files_info(base_directory)

    # Extract URLs from the existing Python client
    existing_urls = extract_urls_from_file(python_client_path)

    # Find new APIs that are not yet implemented
    new_apis = find_new_apis(extracted_info, existing_urls)

    print(f"Found {len(new_apis)} unimplemented endpoints")

    # Print the new APIs for clarity
    for api in new_apis:
        print(f"API Name: {api['name']}, Method: {api['method']}, Path: {api['path']}, Pagination: {api['pagination']}")

    return new_apis

# def export_addin_functions_to_excel(env, client, analysis=True, path=os.getcwd()):
#     """
#     Exports Excel Add-in functions (either analysis or risk) from an API endpoint to an Excel file.

#     This function retrieves the list of Excel Add-in functions (either for "analysis" or "risk") from a specified 
#     environment's API. The functions are extracted, transformed into a DataFrame, and exported to an Excel file. 
#     The resulting Excel file contains two columns: the function ID and its description.

#     Parameters:
#     - env (str): The environment in which the API is hosted (e.g., 'prod', 'qa').
#     - client (str): The client identifier for the API.
#     - analysis (bool): Determines whether to fetch "analysis" functions (True) or "risk" functions (False). Defaults to True.
#     - path (str): The directory path where the resulting Excel file will be saved. Defaults to the current working directory.

#     Returns:
#     - data (dict): The JSON data retrieved from the API, containing all functions and their descriptions.
#     """
#     config = get_api_config(env, client)
#     base_url = config['base_url'].rstrip('/')

#     base_url = base_url.replace('/api/v1', '')

#     addin_type = "analysis" if analysis else "risk"
#     url = f"{base_url}/excel-addin/{addin_type}/functions.json"
#     print(f"Request URL: {url}")
#     request = urllib.request.urlopen(url)
#     data = json.load(request)

#     dict_functions = {i['id']: i['description'] for i in data['functions']}

#     df_functions = pd.DataFrame(list(dict_functions.items()), columns=['Function', 'Description'])

#     date_now = dt.datetime.now().strftime('%Y_%m_%d')
#     excel_filename = f'{env}_{addin_type}_addin_functions_{date_now}.xlsx'

#     excel_export(df_functions, excel_filename, path)

#     print(f"Exported {len(dict_functions)} {addin_type} functions to {os.path.join(path, excel_filename)}")

#     return 'Complete'  # data


def chunkIt(seq, num):
    """
    Divides a sequence into approximately equal-sized chunks.

    Parameters:
    - seq: The sequence (list, string, etc.) to be split into chunks.
    - num: The number of chunks to divide the sequence into.

    Returns:
    - A list of sublists, each representing a chunk of the original sequence.
      If the sequence length is not perfectly divisible by the number of chunks, 
      the last few chunks might be slightly larger or smaller than the others.
    
    Example:
    >>> chunkIt([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4, 5]]
    """
    avg = len(seq) / float(num)  # Calculate average size of each chunk
    out = []  # List to store the chunks
    last = 0.0  # Track the starting index for each chunk

    # Continue slicing the sequence until all elements are chunked
    while last < len(seq):
        # Slice the sequence from the current position (last) to the calculated end (last + avg)
        out.append(seq[int(last):int(last + avg)])
        last += avg  # Move the starting point for the next chunk

    return out

def engine_compatibility(engine_model1, engine_model2):
    """
    Determines whether two engine models are structurally compatible based on 
    their module types and Life-Limited Part (LLP) stacks.

    Parameters:
    - engine_model1: A dictionary representing the first engine model
    - engine_model2: A dictionary representing the second engine model

    Returns:
    - True if both engines have the same module structure and matching LLP stacks.
    - False if there is any mismatch in module types or LLP configurations.

    Example:
    >>> engine1 = {
    ...     "engineModuleTypes": [
    ...         {"moduleTypeId": "A", "engineLlpTypes": [{"llpTypeId": "X"}, {"llpTypeId": "Y"}]},
    ...         {"moduleTypeId": "B", "engineLlpTypes": [{"llpTypeId": "Z"}]}
    ...     ]
    ... }
    >>> engine2 = {
    ...     "engineModuleTypes": [
    ...         {"moduleTypeId": "A", "engineLlpTypes": [{"llpTypeId": "X"}, {"llpTypeId": "Y"}]},
    ...         {"moduleTypeId": "B", "engineLlpTypes": [{"llpTypeId": "Z"}]}
    ...     ]
    ... }
    >>> engine_compatibility(engine1, engine2)
    True

    >>> engine3 = {
    ...     "engineModuleTypes": [
    ...         {"moduleTypeId": "A", "engineLlpTypes": [{"llpTypeId": "X"}]},
    ...         {"moduleTypeId": "B", "engineLlpTypes": [{"llpTypeId": "Z"}]}
    ...     ]
    ... }
    >>> engine_compatibility(engine1, engine3)
    False
    """
    
    def engine_structure(engine_model):
        """
        Extracts the module structure and LLP stacks from an engine model.
        
        Parameters:
        - engine_model: A dictionary representing an engine with module and LLP information.
        
        Returns:
        - A dictionary where keys are module type IDs and values are lists of LLP type IDs.
        """
        structure_dict = {}
        for module in engine_model['engineModuleTypes']:
            mod_id = module['moduleTypeId']
            llp_stack = [i['llpTypeId'] for i in module['engineLlpTypes']]
            structure_dict[mod_id] = llp_stack
        return structure_dict

    structure_eng1 = engine_structure(engine_model1)
    structure_eng2 = engine_structure(engine_model2)

    if structure_eng1.keys() == structure_eng2.keys():
        # Check if LLP stacks are the same for each module
        for mod_id in structure_eng1:
            if set(structure_eng1[mod_id]) != set(structure_eng2[mod_id]):
                return False  # Mismatch in LLP stacks
        return True  # Structures and LLP stacks match
    
    return False  # Different module structures


def retry_request(request_func, retries=3, delay=2, backoff=2, *args, **kwargs):
    """
    Retry an API request in case of failure.
    (Same as the example provided before.)
    """
    attempt = 0
    while attempt < retries:
        try:
            response = request_func(*args, **kwargs)
            if response.status_code == 200:
                return response.json()  # Assuming API returns JSON
        except requests.RequestException as e:
            print(f"Request failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= backoff
            attempt += 1
    return None


def flatten_json(nested_json, delimiter='_'):
    """
    Flatten a nested JSON object into a single level.
    (Same as the example provided before.)
    """
    flat_dict = {}

    def flatten(x, name=''):
        if isinstance(x, dict):
            for key in x:
                flatten(x[key], name + key + delimiter)
        elif isinstance(x, list):
            for i, item in enumerate(x):
                flatten(item, name + str(i) + delimiter)
        else:
            flat_dict[name[:-1]] = x

    flatten(nested_json)
    return flat_dict


def build_url(base_url, endpoint):
    """
    Build a complete API URL from the base URL and endpoint.
    (Same as the example provided before.)
    """
    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"


# Function to export a DataFrame to Excel in the current working directory
def excel_export(df, name, path=os.getcwd()):
    """
    Exports a pandas DataFrame to an Excel file in the specified path.
    
    Parameters:
    - df (pd.DataFrame): The DataFrame to export.
    - name (str): The name for the output Excel file.
    - path (str): The directory path to save the file. Defaults to the current working directory.
    """
    file_path = os.path.join(path, f'{name}.xlsx')
    with pd.ExcelWriter(file_path, datetime_format='YYYY-MM-DD') as writer:
        df.to_excel(writer)


# Function to check and create directories for standard uploading format
def check_dir(output_directory_name='exp'):
    """
    Ensures that a set of directories exists, creating them if necessary.
    
    Parameters:
    - output_directory_name (str): The base directory for the folder structure.
    
    Returns:
    - str: Confirmation message after completion.
    """
    base_path = os.path.join(os.getcwd(), output_directory_name)

    sub_dirs = ['assumptions', 'fee_structures', 'reference', 'maintenance', 'assemblies', 'leases']

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    for sub_dir in sub_dirs:
        full_path = os.path.join(base_path, sub_dir)
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    return 'Finished'


# JSON encoder class for handling numpy data types in JSON
class NpEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle numpy data types.
    Converts numpy data types to native Python types for JSON serialization.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def dump_json(data, filename, path=os.getcwd(), indent=4):
    """
    Dumps JSON data to a file. If the data is a list, it wraps the list into a dictionary 
    with the key "items" before dumping.
    
    Parameters:
    - data (dict or list): The JSON data to be saved. If it's a list, it will be wrapped with {"items": [data]}.
    - filename (str): The name of the file (without extension).
    - path (str): The directory path where the file should be saved. Defaults to the current working directory.
    - indent (int): The indentation level for the JSON output. Default is 4.
    
    Returns:
    - str: Full path of the saved JSON file.
    """
    # Construct the full file path
    file_path = os.path.join(path, f'{filename}.json')

    try:
        # If the data is a list, wrap it in a dictionary under the key "items"
        if isinstance(data, list):
            data = {"items": data}

        # Dump the JSON data to the file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=indent, cls=NpEncoder)
        return(f"JSON data successfully dumped to:{file_path}")
    except Exception as e:
        return(f"Error dumping JSON data to file:{e}")




# Function to load JSON data from a file
def load_json(file_path):
    """
    Loads JSON data from a file.

    Parameters:
    - file_path (str): The path of the file to load JSON data from.

    Returns:
    - dict: The loaded JSON data.
    """
    with open(file_path, 'r') as f:
        return json.load(f)


# Function to load a JSON schema from a file
def get_schema(schema_file_path):
    """
    Loads a JSON schema from a file.

    Parameters:
    - schema_file_path (str): The path to the JSON schema file.

    Returns:
    - dict: The loaded schema.
    """
    with open(schema_file_path, 'r') as file:
        return json.load(file)


# Function to validate JSON data against a schema
def validate_schema(schema_path, json_data):
    """
    Validates JSON data against a schema.

    Parameters:
    - schema_path (str): The path to the schema.
    - json_data (dict): The JSON data to be validated.

    Returns:
    - tuple: (bool, str) indicating whether the validation passed, and a message.
    """
    schema_id = json_data['$schema']
    full_schema_path = os.path.join(schema_path, schema_id)
    schema = get_schema(full_schema_path)

    try:
        validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return False, f"Given JSON data is invalid: {err}"

    return True, "Given JSON data is valid"


# Function to validate JSON data against a schema and export if valid
def validate_export(schema_path, file_path, json_data):
    """
    Validates JSON data against a schema and exports it to a file if valid.

    Parameters:
    - schema_path (str): The path to the schema.
    - file_path (str): The path to save the validated JSON data.
    - json_data (dict): The JSON data to validate and export.
    """
    is_valid, message = validate_schema(schema_path, json_data)

    if is_valid:
        export_json_cwd(file_path, json_data)
        print(f"Successfully exported {json_data['$schema'].split('.')[0].replace('KBImport', '')} to output file after passing schema validation.")
    else:
        print(f"CRITICAL: JSON validation failed. Error: {message}")


def format_id(s):
    """
    Formats a given input by removing special characters and standardizing it to uppercase with underscores.

    This function takes an input , removes parentheses, and splits on various 
    delimiters including spaces, hyphens, underscores, commas, dots, slashes, and hashes. The resulting 
    segments are joined by underscores, converted to uppercase, and stripped of any leading or trailing underscores.

    Parameters:
    - s: The input value to be formatted, which can be any type convertible to a string.

    Returns:
    - str: The formatted identifier, consisting of uppercase letters and underscores only.

    Example:
    >>> format_id("(hello-world) #123")
    'HELLO_WORLD_123'
    """
    y = str(s)
    y = ''.join(re.split('[()]', y))
    y = '_'.join(re.split('[#/\-_.,\s]+', y)).upper().strip('_')
    return y


def deep_replace(data, target, replacement):
    """
    Recursively replaces all occurrences of a substring within a nested structure.

    This function traverses a given data structure, which can contain nested dictionaries,
    lists, and strings, and replaces all occurrences of substring `a` with substring `b`
    in any string it encounters. For dictionaries, it applies the replacement to each 
    value. For lists, it iterates through each item and performs the replacement as needed.

    Parameters:
    - data (str | dict | list): The data structure to process. Can be a string, dictionary,
      list, or a nested combination thereof.
    - target (str): The substring to be replaced.
    - replacement (str): The replacement substring.

    Returns:
    - str | dict | list: A new data structure with all instances of `a` replaced by `b`
      in any strings found.

    Example:
    replace_deep({"name": "example", "items": ["example1", "test"]}, "example", "sample")
    {'name': 'sample', 'items': ['sample1', 'test']}
    """

    if isinstance(data, str):
        return data.replace(target, replacement)
    elif isinstance(data, dict):
        return {k: deep_replace(v, target, replacement) for k, v in data.items()}
    elif isinstance(data, list):
        return [deep_replace(v, target, replacement) for v in data]
    else:
        # nothing to do?
        return data


def filter_list_of_dictionaries_by_list_of_strings(list_of_dicts, include_items=None, exclude_items=None, key_string=None, include_filter_type='ANY', exclude_filter_type='ALL'):
    """
    Filters a list of dictionaries based on inclusion and/or exclusion criteria determined by substrings 
    found in the value of a specified key in each dictionary.

    Parameters:
    ----------
    - include_items (list, optional): 
        A list of substrings to include. If specified, the function includes dictionaries where the value 
        of `key_string` contains the substrings, according to the logic defined by `include_filter_type`.

    - exclude_items (list, optional): 
        A list of substrings to exclude. If specified, the function excludes dictionaries where the value 
        of `key_string` contains the substrings, according to the logic defined by `exclude_filter_type`.

    - key_string (str): 
        The name of the key in each dictionary whose value will be examined for inclusion or exclusion.

    - include_filter_type (str, optional): 
        Determines how `include_items` is applied:
        - 'ANY' (default): Includes dictionaries where any of the substrings in `include_items` are found.
        - 'ALL': Includes dictionaries where all substrings in `include_items` are found.

    - exclude_filter_type (str, optional): 
        Determines how `exclude_items` is applied:
        - 'ANY' (default): Excludes dictionaries where any of the substrings in `exclude_items` are found.
        - 'ALL': Excludes dictionaries where all substrings in `exclude_items` are found.

    - include (bool, optional): 
        If `True` (default), applies the inclusion criteria. If `False`, skips inclusion filtering.

    Returns:
    -------
    - filtered_list (list): 
        A list of dictionaries from the input that satisfy the filtering criteria:
          - Includes dictionaries meeting the `include_items` and `include_filter_type` criteria, if specified.
          - Excludes dictionaries meeting the `exclude_items` and `exclude_filter_type` criteria, if specified.

    """
    # Validate key_string parameter
    if not key_string or key_string not in list_of_dicts[0]:
        raise ValueError("The 'key_string' parameter must be specified and must be in the dictionaries")

    # Start with the original list
    filtered_list = list_of_dicts  # [] if( include_items is None and exclude_items is None) else list_of_dicts
    # Apply inclusion filtering if enabled
    if include_items is not None:
        if include_filter_type.strip().upper() == 'ANY':
            filtered_list = [
                x for x in filtered_list
                if any(item in x.get(key_string, '') for item in include_items)
            ]
        elif include_filter_type.strip().upper() == 'ALL':
            filtered_list = [
                x for x in filtered_list
                if all(item in x.get(key_string, '') for item in include_items)
            ]
        else:
            print(f"Invalid 'include_filter_type': {include_filter_type}. Must be 'ANY' or 'ALL'. Returning unmodified list.")
            return filtered_list

    # Apply exclusion filtering if specified
    if exclude_items is not None:
        if exclude_filter_type.strip().upper() == 'ANY':
            filtered_list = [
                x for x in filtered_list
                if not any(item in x.get(key_string, '') for item in exclude_items)
            ]
        elif exclude_filter_type.strip().upper() == 'ALL':
            filtered_list = [
                x for x in filtered_list
                if not all(item in x.get(key_string, '') for item in exclude_items)
            ]
        else:
            print(f"Invalid 'exclude_filter_type': {exclude_filter_type}. Must be 'ANY' or 'ALL'. Returning unmodified list.")
            return filtered_list

    return filtered_list

def check_dictionary_path_exists(obj, path):
    try:
        for key in path:
            obj = obj[key] if isinstance(obj, (dict, list)) else obj[key]
        return True
    except (KeyError, IndexError, TypeError):
        return False


def interpolate_table(df: pd.DataFrame, x_target, y_target=None):
    """
    Interpolates values from a DataFrame using linear regression (TREND-style).
    Returns exact table value if an exact match for x_target and y_target exists.
    Clips targets to axis bounds to avoid extrapolation.

    Parameters:
    - df: pandas DataFrame with index as y-axis and columns as x_axis.
    - x_target: target x value.
    - y_target: optional target y value.

    Returns:
    - interpolated or exact value (float)
    """
    x_axis = df.columns.to_numpy(dtype=float)
    y_axis = df.index.to_numpy(dtype=float)
    table = df.to_numpy(dtype=float)

    def trend(x_vals, y_vals, x):
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
        return slope * x + intercept

    # Clip targets to axis bounds
    x_target_clipped = np.clip(x_target, x_axis.min(), x_axis.max())

    if y_target is not None:
        y_target_clipped = np.clip(y_target, y_axis.min(), y_axis.max())
    else:
        y_target_clipped = None

    # Check exact match for 1D case
    if y_target_clipped is None:
        if df.shape[0] != 1:
            raise ValueError("For 1D interpolation, DataFrame must have exactly one row.")
        if x_target_clipped in x_axis:
            col_idx = np.where(x_axis == x_target_clipped)[0][0]
            return table[0, col_idx]
        else:
            return trend(x_axis, table[0], x_target_clipped)

    # 2D case: check exact matches
    exact_x = x_target_clipped in x_axis
    exact_y = y_target_clipped in y_axis

    if exact_x and exact_y:
        row_idx = np.where(y_axis == y_target_clipped)[0][0]
        col_idx = np.where(x_axis == x_target_clipped)[0][0]
        return table[row_idx, col_idx]

    # Find bounding indices after clipping
    idx_below = np.searchsorted(y_axis, y_target_clipped) - 1
    idx_above = idx_below + 1

    # Handle edge cases after clipping (at bounds)
    if idx_below < 0:
        idx_below = idx_above = 0
    elif idx_above >= len(y_axis):
        idx_below = idx_above = len(y_axis) - 1

    y1, y2 = y_axis[idx_below], y_axis[idx_above]
    row1 = table[idx_below]
    row2 = table[idx_above]

    f1 = trend(x_axis, row1, x_target_clipped)
    f2 = trend(x_axis, row2, x_target_clipped)

    if idx_below == idx_above:
        # On boundary, no vertical interpolation
        return f1
    else:
        return trend([y1, y2], [f1, f2], y_target_clipped)




def engine_grouping(engine_models):
    def normalize_engine_module_types(engine_module_types: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize the engineModuleTypes list by removing the 'position' attribute and sorting the dictionaries within.
        """
        normalized = []
        for module in engine_module_types:
            normalized_module = {
                'engineLlpTypes': sorted([{'llpTypeId': item['llpTypeId']} for item in module['engineLlpTypes']],
                                         key=lambda x: (x['llpTypeId'])),
                'moduleTypeId': module['moduleTypeId']}
            normalized.append(normalized_module)
        return sorted(normalized, key=lambda x: (x['moduleTypeId']))

    def group_by_engine_module_types(json_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group JSON objects by their normalized engineModuleTypes.
        """
        buckets = defaultdict(list)
        for json_obj in json_list:
            normalized_module_types = normalize_engine_module_types(json_obj['engineModuleTypes'])
            key = json.dumps(normalized_module_types, sort_keys=True)  # Convert to string for dictionary key
            buckets[key].append(json_obj['externalId'])
        return dict(buckets)

    json_list = engine_models  # copy.deepcopy()
    # Grouping the JSON objects
    buckets = group_by_engine_module_types(json_list)

    grouping_2 = {}
    # Exporting the new json which has the module llp grouping in "structure" and the list of engines external IDs associatied
    for key, group in buckets.items():
        json_key = json.loads(key)
        grouping_2[group[0]] = {
            "engines": sorted(group),
            "structure": json_key}
    return grouping_2

def factor_table_to_applied_rate(run_rate_table, x_axis, sector_length):
    """
        Converts a flat rate table into a DataFrame and applies 2D interpolation
        to find the applied run rate for a given x_axis and sector length.

        Parameters:
        ----------
        run_rate_table : dict
            A dictionary containing:
                - 'prRates': list of float values (flat, row-major order).
                - 'x_axis': list of float values (used as row indices).
                - 'segmentLengths': list of float values (used as column headers).

        x_axis : float
            The x_axis value to interpolate (maps to DataFrame index).

        sector_length : float
            The segment length to interpolate (maps to DataFrame columns).

        Returns:
        -------
        float
            Interpolated applied run rate based on the input x_axis and sector length.
        """
    table_data = run_rate_table  # contracted_lease['firstRunRateTable']

    # Get the lists
    pr_rates = table_data['prRates']
    x_axis = table_data['x_axis']
    y_axis = table_data['segmentLengths']

    # Reshape prRates into a 2D array
    # The number of rows will be len(x_axis) and columns len(segmentLengths)
    # This assumes prRates are ordered by x_axis, then by segmentLength
    reshaped_pr_rates = np.array(pr_rates).reshape(len(x_axis), len(y_axis))

    # Create the DataFrame
    df = pd.DataFrame(data=reshaped_pr_rates, index=x_axis, columns=y_axis)

    # Optional: Name the index and columns for clarity
    df.index.name = 'x_axis'
    df.columns.name = 'segmentLength'
    rate = interpolate_table(df, sector_length, x_axis)
    return rate