import os
import re


def extract_paths(file_content):
    """
    Extracts API paths from a TypeScript paths file, including paths with parameters,
    and derives the HTTP method from the key, with special handling for 'list'.

    Parameters:
    - file_content (str): The content of the TypeScript file containing the paths.

    Returns:
    - dict: A dictionary mapping path names to a tuple containing the HTTP method, API path, and additional parameters.
    """
    paths = {}
    # Match the pattern for API paths (e.g., assemblyList: "/external-api/assemblies" or "/external-api/assemblies/:assemblyId")
    matches = re.findall(r'(\w+):\s*"(/[\w/-]+(:\w+)?)"', file_content)

    for match in matches:
        path_name, api_path, _ = match
        
        # Derive the method from the path name
        method, requires_pagination = derive_http_method(path_name)
        
        # Store the derived method, the API path, and pagination info
        paths[path_name] = {
            'method': method,
            'path': api_path,
            'pagination': requires_pagination
        }
    
    return paths


def derive_http_method(path_name):
    """
    Derives the HTTP method from the path name based on common action keywords, 
    and determines if pagination is needed.

    Parameters:
    - path_name (str): The name of the path (e.g., 'create', 'update', 'list', 'info').

    Returns:
    - tuple: (HTTP method as a string, requires_pagination as a bool)
    """
    # Common action keywords mapped to HTTP methods
    action_method_map = {
        'create': 'POST',
        'update': 'PUT',
        'delete': 'DELETE',
        'remove': 'DELETE',
        'get': 'GET',
        'info': 'GET'
    }

    # Default to GET method
    method = 'GET'
    requires_pagination = False

    # Special case for 'list' indicating a paginated GET request
    if 'list' in path_name.lower():
        method = 'GET'
        requires_pagination = True

    # Check for other keywords to determine the method
    for keyword, mapped_method in action_method_map.items():
        if keyword.lower() in path_name.lower():
            method = mapped_method
            break
    
    return method, requires_pagination


def get_ts_files_info(base_dir):
    """
    Searches through the specified directory for paths files, extracts relevant information from them.

    Parameters:
    - base_dir (str): The base directory where the search will start.

    Returns:
    - list: A list of dictionaries containing extracted data from paths files.
    """
    extracted_data = []

    # Traverse the directory to find TypeScript files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith("paths.ts"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    paths_info = extract_paths(content)
                    extracted_data.append({
                        'file': file,
                        'type': 'paths',
                        'data': paths_info
                    })
    
    return extracted_data


def extract_urls_from_file(file_path):
    """
    Extract all URLs from the specified api_client.py file.

    Parameters:
    - file_path (str): The path to the api_client.py file.

    Returns:
    - list: A list of all extracted URLs in the form they appear in the file.
    """
    urls = []
    # Define a regex pattern to match URL strings in the format "/external-api/...".
    url_pattern = re.compile(r'url\s*=\s*f?"(/external-api/[^\s"]+)"')

    with open(file_path, 'r', encoding='utf-8') as file:
        # Read the entire content of the file.
        content = file.read()

        # Find all occurrences of the URL pattern.
        matches = url_pattern.findall(content)

        # Collect and clean the URLs.
        for match in matches:
            urls.append(match)

    return urls


def find_new_apis(extracted_info, existing_urls):
    """
    Identifies APIs from extracted TypeScript paths that are not yet implemented in the Python client.

    Parameters:
    - extracted_info (list): List of dictionaries containing data from paths files.
    - existing_urls (list): List of URLs extracted from the existing Python API client.

    Returns:
    - list: A list of new APIs that need to be created.
    """
    new_apis = []

    # Normalize the existing URLs to match the TypeScript format
    normalized_existing_urls = {url.replace('{',':').replace('}','').rstrip('/') for url in existing_urls}

    # Loop through each extracted TypeScript path
    for file in extracted_info:
        for path_name, path_data in file['data'].items():
            # Normalize the path to ensure consistent comparison
            normalized_path = path_data['path'].rstrip('/')

            # Check if the path exists in the Python client
            if normalized_path not in normalized_existing_urls:
                new_apis.append({
                    'name': path_name,
                    'path': normalized_path,
                    'method': path_data.get('method', 'GET'),
                    'pagination': path_data.get('pagination', False)
                })
    
    return new_apis

