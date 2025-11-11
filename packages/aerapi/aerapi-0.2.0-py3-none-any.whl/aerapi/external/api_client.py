from ..common.base_api import BaseAPIClient, APIConfig
from typing import Dict
from enum import Enum


class HttpMethod(str, Enum):
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    DELETE = 'DELETE'


class Endpoints(str, Enum):
    EXTERNAL_API = 'external-api'
    ENGINE_MX_OVERRIDES = 'engine-mx-overrides'
    UTILIZATION_SHOCK_TABLE_RELATION = 'utilization-shock-table-relation'


class ExternalAPIClient(BaseAPIClient):
    base_api: BaseAPIClient = None
    config: APIConfig = None

    def __init__(self, base_api: BaseAPIClient):
        """
        Initialize ExternalAPI using an existing BaseAPI instance.
        """
        if not isinstance(base_api, BaseAPIClient):
            raise TypeError("base_api must be an instance of BaseAPI")
        self.base_api = base_api
        self.config = self.base_api.config
        

    def __dir__(self):
        # Dynamically filter out attributes from Parent
        parent_attrs = set(dir(BaseAPIClient))  # Get all attributes from Parent
        all_attrs = set(super().__dir__())  # Get all attributes inherited by Child
        child_specific_attrs = all_attrs - parent_attrs  # Exclude Parent attributes
        return sorted(child_specific_attrs)

    def get_aircraft_details(self, aircraftId, debug=False):
        """
        GET: Retrieve details for a specific aircraft by its aircraft ID.

        Parameters:

        - aircraftId (str): The unique ID of the aircraft to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The aircraft details in JSON format, including specifications, configurations, and other relevant metadata.
        """
        url = f"/external-api/aircraft/{aircraftId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def update_aircraft(self, aircraftId, data, debug=False):
        """
        PUT: Update details for a specific aircraft by its aircraft ID.

        Parameters:

        - aircraftId (str): The unique ID of the aircraft to update details for.
        - data (dict): The body containing the updated details of the aircraft.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response from the API in JSON format, indicating success or failure.
        """
        url = f"/external-api/aircraft/{aircraftId}"

        # Validate data
        required_keys = [
            "buildYear", "certifiedMTOW", "deliveryDate", "engineModelId", "firstFlightDate",
            "inServiceDate", "managerId", "minorVariant", "modifiers", "operatingMTOW",
            "operatorId", "orderDate", "ownerId", "ownershipStatus", "registration",
            "status", "financierId"
        ]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required field in data: {key}")

        # Make the authenticated PUT request
        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug)
    
    def delete_aircraft(self, aircraftId: str, debug: bool=False) -> Dict:
        """
        DELETE: Delet aircraft by its Id.

        Parameters:

        - aircraftId (str): The unique ID of the aircraft to delete.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response from the API in JSON format, indicating success or failure.
        """
        url = f"/external-api/aircraft/{aircraftId}"

        # Make the authenticated PUT request
        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def create_aircraft(self, data, debug=False):
        """
        POST: Create an aircraft.

        Parameters:

        - data (dict): The body containing the updated details of the aircraft.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response from the API in JSON format, indicating success or failure.
        """
        url = f"/external-api/aircraft"

        # Validate data
        required_keys = [
            "buildYear", "certifiedMTOW", "deliveryDate", "engineModelId", "firstFlightDate",
            "inServiceDate", "managerId", "minorVariant", "modifiers", "operatingMTOW",
            "operatorId", "orderDate", "ownerId", "ownershipStatus", "registration",
            "status"
        ]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required field in data: {key}")

        # Make the authenticated POST request
        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)

    def get_assemblies(self, aircraftId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all assemblies, with optional filtering by aircraft ID, and pagination.

        Parameters:

        - aircraftId (str, optional): The ID of the aircraft to filter assemblies.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of all assemblies in JSON format, filtered by aircraft ID if provided.
        """
        url = "/external-api/assemblies"

        # Adding query parameters for aircraftId, limit, and offset if provided
        params = {}
        if aircraftId:
            params['aircraftId'] = aircraftId
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_assembly_details(self, assemblyId, debug=False):
        """
        GET: Retrieve detailed information for a specific assembly by its assembly ID.

        Parameters:

        - assemblyId (str): The unique ID of the assembly to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The assembly details in JSON format, including metadata like assembly configuration, parts, and other relevant information.
        """
        url = f"/external-api/assemblies/{assemblyId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)
    
    def update_assembly(self, assemblyId, data, debug=False):
        """
        PUT: Update an existing assembly.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - assemblyId (str): The unique ID of the assembly to update.
        - data (dict): A dictionary containing the updated assembly details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the updated country's details.
        """
        url = f"/external-api/assemblies/{assemblyId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)
    
    def delete_assembly(self, assemblyId, debug=False):
        """
        DELETE: Delete an existing assembly.

        Parameters:
        - assemblyId (str): The unique ID of the assembly to update.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the updated country's details.
        """
        url = f"/external-api/assemblies/{assemblyId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)
    
    def create_assembly(self, aircraftId: str, data: Dict, debug=False) -> Dict:
        """
        POST: Create an assembly.

        Parameters:
        - aircraftId (str)
        - data (dict): A dictionary containing the updated assembly details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the posted Assembly
        """
        url = f"/external-api/assemblies/{aircraftId}"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=False, sendSize=1)

    def search_aircraft(self, search_params=None, limit=None, offset=None, order_by=None, order=None, debug=False):
        """
        GET: Search for aircraft based on certain criteria with optional pagination and sorting.

        Parameters:

        - search_params (dict, optional): A dictionary of search parameters (e.g., model, year, manufacturer). Default is None.
        - limit (int, optional): The number of results to return per page. Default is None.
        - offset (int, optional): The starting point for pagination. Default is None.
        - order_by (str, optional): The field by which to sort the results (e.g., 'msn', 'registration', 'operator'). Default is None.
        - order (str, optional): The order of sorting, either 'ASC' or 'DESC'. Default is None.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The search results, including aircraft that match the given criteria.
        """
        url = "/external-api/aircraft/search"

        # Construct query parameters
        params = search_params or {}

        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if order_by:
            params['orderBy'] = order_by
        if order:
            if order.upper() not in ['ASC', 'DESC']:
                raise ValueError("Invalid order value. Must be 'ASC' or 'DESC'.")
            params['order'] = order.upper()

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_analysis_contexts_for_aircraft(self, aircraftId, limit=None, offset=None, debug=False):
        """
        GET: Retrieve all available analysis contexts for a specific aircraft with optional pagination.

        Parameters:
        - aircraftId (str): The unique ID of the aircraft to retrieve analysis contexts for.
        - limit (int, optional): The number of results to return per page. Default is None.
        - offset (int, optional): The starting point for pagination. Default is None.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of available analysis contexts for the aircraft in JSON format,
                each containing information about performance, maintenance, or other analysis contexts.
        """
        url = f"/external-api/aircraft/{aircraftId}/analysis-contexts"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_base_analysis_context_for_aircraft(self, aircraftId, debug=False):
        """
        GET: Retrieve the base analysis context for a specific aircraft.

        Parameters:
        - aircraftId (str): The unique ID of the aircraft to retrieve the base analysis context for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The base analysis context in JSON format, including core performance and operational metrics.
        """
        url = f"/external-api/aircraft/{aircraftId}/analysis-contexts/base"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_all_portfolios(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all portfolios with optional pagination.

        Parameters:

        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of portfolios in JSON format, including portfolio details like names, IDs, and metadata.
        """
        url = "/external-api/portfolios"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_portfolio_details(self, portfolioId, debug=False):
        """
        GET: Retrieve detailed information for a specific portfolio by its portfolio ID.

        Parameters:

        - portfolioId (str): The unique ID of the portfolio to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The portfolio details in JSON format, including information such as the assets within the portfolio, performance data, and other relevant details.
        """
        url = f"/external-api/portfolio/{portfolioId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_cashflows(self, analysis_contextId, debug=False):
        """
        GET: Retrieve cashflow data for a specific analysis context.

        Parameters:

        - analysis_contextId (str): The unique ID of the analysis context for which to retrieve cashflows.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The cashflow data in JSON format, including detailed financial metrics, timelines, and other relevant data.
        """
        url = f"/external-api/calculation/{analysis_contextId}/cashflows"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_maintenance_summary(self, analysis_contextId, debug=False):
        """
        GET: Retrieve maintenance summary data for a specific analysis context.

        Parameters:

        - analysis_contextId (str): The unique ID of the analysis context for which to retrieve the maintenance summary.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The maintenance summary data in JSON format, including maintenance schedules, costs, and other relevant details.
        """
        url = f"/external-api/calculation/{analysis_contextId}/maintenance-summary"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_all_companies(self, limit=None, offset=None, filter=None, debug=False):
        """
        GET: Retrieve a list of all companies with optional pagination and filtering.

        Parameters:

        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - filter (str, optional): A filter string based on company roles.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of companies in JSON format, including company details like names, IDs, and metadata.
        """
        url = "/external-api/companies"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if filter is not None:
            params['filter'] = filter

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_company_details(self, companyId, debug=False):
        """
        GET: Retrieve detailed information for a specific company by its company ID.

        Parameters:
        - companyId (str): The unique ID of the company to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The company details in JSON format, including name, address, industry, and other relevant information.
        """
        url = f"/external-api/companies/{companyId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_company(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new company.

        Parameters:
        - data (dict): A dictionary containing the new company details (e.g., name, address, industry).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created company details in JSON format, including its unique ID and metadata.
        """
        url = "/external-api/companies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_company(self, companyId, data, debug=False):
        """
        PUT: Update an existing company's details.

        Parameters:
        - companyId (str): The unique ID of the company to be updated.
        - data (dict): A dictionary containing the updated company details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated company details in JSON format, including the updated metadata.
        """
        url = f"/external-api/companies/{companyId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_company(self, companyId, debug=False):
        """
        DELETE: Delete a specific company by its company ID.

        Parameters:
        - companyId (str): The unique ID of the company to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/companies/{companyId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_manufacturers(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all manufacturers with optional pagination and filtering.

        Parameters:

        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of manufacturers in JSON format, including manufacturer details like names, IDs, and metadata.
        """
        url = "/external-api/manufacturers"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_manufacturer_details(self, manufacturerId, debug=False):
        """
        GET: Retrieve detailed information for a specific manufacturer by its manufacturer ID.

        Parameters:
        - manufacturerId (str): The unique ID of the manufacturer to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The manufacturer details in JSON format, including name, description and other relevant information.
        """
        url = f"/external-api/manufacturers/{manufacturerId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_manufacturer(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new manufacturer.

        Parameters:
        - data (dict): A dictionary containing the new manufacturer details (e.g., id, externalId, name, description).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created manufacturer details in JSON format, including its unique ID and metadata.
        """
        url = "/external-api/manufacturers"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_manufacturer(self, manufacturerId, data, debug=False):
        """
        PUT: Update an existing manufacturer's details.

        Parameters:
        - manufacturerId (str): The unique ID of the manufacturer to be updated.
        - data (dict): A dictionary containing the updated manufacturer details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated manufacturer details in JSON format, including the updated metadata.
        """
        url = f"/external-api/manufacturers/{manufacturerId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_manufacturer(self, manufacturerId, debug=False):
        """
        DELETE: Delete a specific manufacturer by its manufacturer ID.

        Parameters:
        - manufacturerId (str): The unique ID of the manufacturer to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/manufacturers/{manufacturerId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_operator_alliances(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all operator alliances with optional pagination and filtering.

        Parameters:

        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of operator alliances in JSON format, including operator alliance details like names, IDs, and metadata.
        """
        url = "/external-api/operator-alliances"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_operator_alliance_details(self, operatorAllianceId, debug=False):
        """
        GET: Retrieve detailed information for a specific operator alliance by its operator_alliance ID.

        Parameters:
        - operatorAllianceId (str): The unique ID of the operator alliance to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The operator_alliance details in JSON format, including name, airlines and other relevant information.
        """
        url = f"/external-api/operator-alliances/{operatorAllianceId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_operator_alliance(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new operator_alliance.

        Parameters:
        - data (dict): A dictionary containing the new operator alliance details (e.g., name, id, airlines).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created operator_alliance details in JSON format, including its unique ID and metadata.
        """
        url = "/external-api/operator-alliances"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_operator_alliance(self, operatorAllianceId, data, debug=False):
        """
        PUT: Update an existing operator_alliance's details.

        Parameters:
        - operatorAllianceId (str): The unique ID of the operator alliance to be updated.
        - data (dict): A dictionary containing the updated operator_alliance details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated operator_alliance details in JSON format, including the updated metadata.
        """
        url = f"/external-api/operator-alliances/{operatorAllianceId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_operator_alliance(self, operatorAllianceId, debug=False):
        """
        DELETE: Delete a specific operator alliance by its operator alliance ID.

        Parameters:
        - operatorAllianceId (str): The unique ID of the operator alliance to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/operator-alliances/{operatorAllianceId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_countries(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all countries with optional pagination.

        Parameters:

        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of countries in JSON format, including country details like name, code, and metadata.
        """
        url = "/external-api/countries"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_country_details(self, countryId, debug=False):
        """
        GET: Retrieve detailed information for a specific country by its country ID.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - countryId (str): The unique ID of the country for which details are to be retrieved.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing detailed information about the country,
                such as the country name, country code, geographic information, and other attributes.
        """
        url = f"/external-api/countries/{countryId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_country(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new country record in the system.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - data (dict): A dictionary containing the new country details such as country name, country code, and other relevant attributes.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the newly created country's details, including the unique country ID and other metadata.
        """
        url = "/external-api/countries"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_country(self, countryId, data, debug=False):
        """
        PUT: Update an existing country's details.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - countryId (str): The unique ID of the country to update.
        - data (dict): A dictionary containing the updated country details, such as updated country name, country code, and other attributes.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the updated country's details.
        """
        url = f"/external-api/countries/{countryId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_country(self, countryId, debug=False):
        """
        DELETE: Delete a specific country by its country ID.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - countryId (str): The unique ID of the country to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response confirming the deletion or providing error information if the operation fails.
        """
        url = f"/external-api/countries/{countryId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_lease_list(self, assemblyId, debug=False):
        """
        GET: Retrieve a list of leases for a specific assembly.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - assemblyId (str): The unique ID of the assembly for which to retrieve the list of leases.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing a list of leases for the given assembly, including lease details like start date, end date, and lessee information.
        """
        url = f"/external-api/leases/assembly/{assemblyId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_lease_details(self, leaseId, debug=False):
        """
        GET: Retrieve detailed information for a specific lease by its lease ID.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - leaseId (str): The unique ID of the lease to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing details about the lease, such as lease start and end dates, lessee information, financial terms, and maintenance agreements.
        """
        url = f"/external-api/leases/{leaseId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_contracted_lease(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new contracted lease in the system.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - data (dict): A dictionary containing the details of the new contracted lease, such as start date, end date, terms, and lessee details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the newly created contracted lease details, including the unique lease ID and metadata.
        """
        url = "/external-api/leases/contracted"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_structuring_lease(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new structuring lease in the system.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - data (dict): A dictionary containing the details of the new structuring lease, such as terms and structuring specifics.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the newly created structuring lease details, including the unique lease ID and metadata.
        """
        url = "/external-api/leases/structuring"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_lease(self, leaseId, data, debug=False):
        """
        PUT: Update an existing lease by its lease ID.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - leaseId (str): The unique ID of the lease to update.
        - data (dict): A dictionary containing the updated lease details, such as updated terms, lessee information, and financial agreements.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the updated lease details.
        """
        url = f"/external-api/leases/{leaseId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_lease(self, leaseId, debug=False):
        """
        DELETE: Delete a specific lease by its lease ID.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - leaseId (str): The unique ID of the lease to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response confirming the deletion or providing error information if the operation fails.
        """
        url = f"/external-api/leases/{leaseId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_engine_snapshot_info(self, engineSnapshotId, debug=False):
        """
        GET: Retrieve detailed information for a specific engine snapshot.

        Parameters:
        - engineSnapshotId (str): The unique ID of the engine snapshot to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The engine snapshot details in JSON format.
        """
        url = f"/external-api/engine-snapshots/{engineSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_snapshot_list(self, limit=None, offset=None, engineId=None, debug=False):
        """
        GET: Retrieve a list of all engine snapshots.

        Parameters:
        - engineId (str): Optional. If included, only snapshots related to that engine Id are returned.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of engine snapshots in JSON format.
        """
        url = "/external-api/engine-snapshots/"
        params={}
        if engineId:
            url = url + f"?engineId={engineId}"
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_engine_snapshot(self, engineId, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new engine snapshot.

        Parameters:
        - engineId (str): The unique ID of the engine for which the snapshot is being created.
        - data (dict): A dictionary containing the engine snapshot details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created engine snapshot details in JSON format.
        """
        url = f"/external-api/engine-snapshots/{engineId}"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_snapshot(self, engineSnapshotId, data, debug=False):
        """
        PUT: Update an existing engine snapshot by its ID.

        Parameters:
        - engineSnapshotId (str): The unique ID of the engine snapshot to update.
        - data (dict): A dictionary containing the updated engine snapshot details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated engine snapshot details in JSON format.
        """
        url = f"/external-api/engine-snapshots/{engineSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_engine_snapshot(self, engineSnapshotId, debug=False):
        """
        DELETE: Delete a specific engine snapshot by its ID.

        Parameters:
        - engineSnapshotId (str): The unique ID of the engine snapshot to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response confirming the deletion.
        """
        url = f"/external-api/engine-snapshots/{engineSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_lease_snapshot_list(self, leaseId, debug=False):
        """
        GET: Retrieve a list of lease snapshots for a specific lease.

        Parameters:
        - leaseId (str): The unique ID of the lease to retrieve snapshots for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of lease snapshots for the given lease in JSON format.
        """
        url = f"/external-api/leaseSnapshots/lease/{leaseId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_lease_snapshot_details(self, leaseSnapshotId, debug=False):
        """
        GET: Retrieve detailed information for a specific lease snapshot.

        Parameters:
        - leaseSnapshotId (str): The unique ID of the lease snapshot to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The lease snapshot details in JSON format.
        """
        url = f"/external-api/leaseSnapshots/{leaseSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_lease_snapshot(self, leaseId, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new lease snapshot for a specific lease.

        Parameters:
        - leaseId (str): The unique ID of the lease for which the snapshot is being created.
        - data (dict): A dictionary containing the lease snapshot details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created lease snapshot details in JSON format.
        """
        url = f"/external-api/leaseSnapshots/{leaseId}"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_lease_snapshot(self, leaseSnapshotId, data, debug=False):
        """
        PUT: Update an existing lease snapshot by its ID.

        Parameters:
        - leaseSnapshotId (str): The unique ID of the lease snapshot to update.
        - data (dict): A dictionary containing the updated lease snapshot details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated lease snapshot details in JSON format.
        """
        url = f"/external-api/leaseSnapshots/{leaseSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_lease_snapshot(self, leaseSnapshotId, debug=False):
        """
        DELETE: Delete a specific lease snapshot by its ID.

        Parameters:
        - leaseSnapshotId (str): The unique ID of the lease snapshot to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response confirming the deletion.
        """
        url = f"/external-api/leaseSnapshots/{leaseSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def add_aircraft_to_portfolio(self, portfolioId, aircraftId, debug=False):
        """
        POST: Add an aircraft to a specific portfolio.

        Parameters:
        - portfolioId (str): The unique ID of the portfolio to add the aircraft to.
        - aircraftId (str): The unique ID of the aircraft to be added to the portfolio.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the operation in JSON format.
        """
        url = f"/external-api/portfolios/addAircraftToPortfolio/{portfolioId}/{aircraftId}"

        return self.make_authenticated_request(self.config, url, method='PUT', debug=debug)

    def remove_aircraft_from_portfolio(self, portfolioId, aircraftId, debug=False):
        """
        DELETE: Remove an aircraft from a specific portfolio.

        Parameters:
        - portfolioId (str): The unique ID of the portfolio from which the aircraft is to be removed.
        - aircraftId (str): The unique ID of the aircraft to be removed from the portfolio.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the operation in JSON format.
        """
        url = f"/external-api/portfolios/removeAircraftFromPortfolio/{portfolioId}/{aircraftId}"

        return self.make_authenticated_request(self.config, url, method='PUT', debug=debug)

    def get_sovereign_ratings(self, countryId, debug=False):
        """
        GET: Retrieve all sovereign ratings for a specific country.

        Parameters:
        - countryId (str): The unique ID of the country for which to retrieve sovereign ratings.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of sovereign ratings in JSON format.
        """
        url = f"/external-api/countries/{countryId}/sovereign-ratings"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_one_sovereign_rating(self, sovereignRatingId, debug=False):
        """
        GET: Retrieve a specific sovereign rating by its ID.

        Parameters:
        - sovereignRatingId (str): The unique ID of the sovereign rating to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The sovereign rating details in JSON format.
        """
        url = f"/external-api/sovereign-ratings/{sovereignRatingId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_sovereign_rating(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new sovereign rating.

        Parameters:
        - data (dict): A dictionary containing the details of the new sovereign rating.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created sovereign rating details in JSON format.
        """
        url = "/external-api/sovereign-ratings"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_sovereign_rating(self, sovereignRatingId, data, debug=False):
        """
        PUT: Update an existing sovereign rating.

        Parameters:
        - sovereignRatingId (str): The unique ID of the sovereign rating to update.
        - data (dict): A dictionary containing the updated sovereign rating details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated sovereign rating details in JSON format.
        """
        url = f"/external-api/sovereign-ratings/{sovereignRatingId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_sovereign_rating(self, sovereignRatingId, debug=False):
        """
        DELETE: Delete a specific sovereign rating by its ID.

        Parameters:
        - sovereignRatingId (str): The unique ID of the sovereign rating to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the deletion in JSON format.
        """
        url = f"/external-api/sovereign-ratings/{sovereignRatingId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_aircraft_part_maintenance_policy_type_info(self, aircraftPartMaintenancePolicyTypeId, debug=False):
        """
        GET: Retrieve detailed information for a specific aircraft part maintenance policy type.

        Parameters:
        - aircraftPartMaintenancePolicyTypeId (str): The unique ID of the aircraft part maintenance policy type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The detailed information about the aircraft part maintenance policy type in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policy-types/{aircraftPartMaintenancePolicyTypeId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_all_aircraft_part_maintenance_policy_types(self, limit=50, offset=0, aircraftPartTypeId=None, debug=False):
        """
        GET: Retrieve a list of all aircraft part maintenance policy types with optional pagination and filtering by aircraft part type.

        Parameters:

        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - aircraftPartTypeId (str, optional): The ID of the aircraft part type to filter maintenance policies.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of maintenance policy types in JSON format.
        """
        url = "/external-api/aircraft-part-maintenance-policy-types"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if aircraftPartTypeId:
            params['aircraftPartTypeId'] = aircraftPartTypeId

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_aircraft_part_maintenance_policy_type(self, aircraftPartTypeId, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft part maintenance policy type for a specific aircraft part type.

        Parameters:
        - aircraftPartTypeId (str): The unique ID of the aircraft part type.
        - data (dict): The details of the new aircraft part maintenance policy type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created aircraft part maintenance policy type in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policy-types/{aircraftPartTypeId}"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_part_maintenance_policy_type(self, aircraftPartMaintenancePolicyTypeId, data, debug=False):
        """
        PUT: Update an existing aircraft part maintenance policy type.

        Parameters:
        - aircraftPartMaintenancePolicyTypeId (str): The unique ID of the aircraft part maintenance policy type.
        - data (dict): The updated details of the aircraft part maintenance policy type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft part maintenance policy type in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policy-types/{aircraftPartMaintenancePolicyTypeId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_aircraft_part_maintenance_policy_type(self, aircraftPartMaintenancePolicyTypeId, debug=False):
        """
        DELETE: Delete a specific aircraft part maintenance policy type.

        Parameters:
        - aircraftPartMaintenancePolicyTypeId (str): The unique ID of the aircraft part maintenance policy type to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the deletion in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policy-types/{aircraftPartMaintenancePolicyTypeId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_aircraft_part_snapshot_info(self, aircraftPartSnapshotId, debug=False):
        """
        GET: Retrieve detailed information for a specific aircraft part snapshot.

        Parameters:
        - aircraftPartSnapshotId (str): The unique ID of the aircraft part snapshot.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The detailed information about the aircraft part snapshot in JSON format.
        """
        url = f"/external-api/aircraft-part-snapshots/{aircraftPartSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_part_snapshot_list(self,aircraftPartId=None, limit=300, offset=0, debug=False):
        """
        GET: Retrieve a list of all aircraft part snapshots.

        Parameters:
        - aircraftPartId (str): Optional. If included, only snapshots related to that part Id are returned.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of all available aircraft part snapshots in JSON format.
        """
        url = "/external-api/aircraft-part-snapshots"
        if aircraftPartId:
            url = url + f"?aircraftPartId={aircraftPartId}"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_aircraft_part_snapshot(self, aircraftPartId, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft part snapshot for a specific aircraft part.

        Parameters:
        - aircraftPartId (str): The unique ID of the aircraft part.
        - data (dict): The details of the new aircraft part snapshot.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created aircraft part snapshot in JSON format.
        """
        url = f"/external-api/aircraft-part-snapshots/{aircraftPartId}"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_part_snapshot(self, aircraftPartSnapshotId, data, debug=False):
        """
        PUT: Update an existing aircraft part snapshot.

        Parameters:
        - aircraftPartSnapshotId (str): The unique ID of the aircraft part snapshot.
        - data (dict): The updated details of the aircraft part snapshot.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft part snapshot in JSON format.
        """
        url = f"/external-api/aircraft-part-snapshots/{aircraftPartSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_aircraft_part_snapshot(self, aircraftPartSnapshotId, debug=False):
        """
        DELETE: Delete a specific aircraft part snapshot.

        Parameters:
        - aircraftPartSnapshotId (str): The unique ID of the aircraft part snapshot to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the deletion in JSON format.
        """
        url = f"/external-api/aircraft-part-snapshots/{aircraftPartSnapshotId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_aircraft_appraisal_info(self, aircraftAppraisalId, debug=False):
        """
        GET: Retrieve detailed information for a specific aircraft appraisal by its ID.

        Parameters:
        - aircraftAppraisalId (str): The unique ID of the aircraft appraisal to retrieve.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Detailed information about the aircraft appraisal in JSON format.
        """
        url = f"/external-api/aircraft-appraisals/{aircraftAppraisalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_appraisal_list(self, limit=None, offset=None, aircraftId=None, debug=False):
        """
        GET: Retrieve a list of all aircraft appraisals, with optional pagination and filtering by aircraft ID.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - aircraftId (str, optional): Filter results by aircraft ID.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of aircraft appraisals in JSON format.
        """
        url = "/external-api/aircraft-appraisals"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if aircraftId:
            params['aircraftId'] = aircraftId

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_aircraft_appraisal(self, aircraftId, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft appraisal for a specific aircraft.

        Parameters:
        - aircraftId (str): The unique ID of the aircraft to appraise.
        - data (dict): The details of the new aircraft appraisal.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created aircraft appraisal in JSON format.
        """
        url = f"/external-api/aircraft-appraisals/{aircraftId}"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_appraisal(self, aircraftAppraisalId, data, debug=False):
        """
        PUT: Update an existing aircraft appraisal.

        Parameters:
        - aircraftAppraisalId (str): The unique ID of the aircraft appraisal.
        - data (dict): The updated details of the aircraft appraisal.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft appraisal in JSON format.
        """
        url = f"/external-api/aircraft-appraisals/{aircraftAppraisalId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_aircraft_appraisal(self, aircraftAppraisalId, debug=False):
        """
        DELETE: Delete a specific aircraft appraisal by its ID.

        Parameters:
        - aircraftAppraisalId (str): The unique ID of the aircraft appraisal to be deleted.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the deletion in JSON format.
        """
        url = f"/external-api/aircraft-appraisals/{aircraftAppraisalId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_appraiser_info(self, appraiserId, debug=False):
        """
        GET: Retrieve detailed information for a specific appraiser by its ID.

        Parameters:
        - appraiserId (str): The unique ID of the appraiser to retrieve.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Detailed information about the appraiser in JSON format.
        """
        url = f"/external-api/appraisers/{appraiserId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_appraiser_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all appraisers, with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of appraisers in JSON format.
        """
        url = "/external-api/appraisers"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_appraiser(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new appraiser.

        Parameters:
        - data (dict): The details of the new appraiser.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The newly created appraiser in JSON format.
        """
        url = "/external-api/appraisers"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_appraiser(self, appraiserId, data, debug=False):
        """
        PUT: Update an existing appraiser by its ID.

        Parameters:
        - appraiserId (str): The unique ID of the appraiser to update.
        - data (dict): The updated details of the appraiser.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated appraiser details in JSON format.
        """
        url = f"/external-api/appraisers/{appraiserId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_appraiser(self, appraiserId, debug=False):
        """
        DELETE: Delete a specific appraiser by its ID.

        Parameters:
        - appraiserId (str): The unique ID of the appraiser to be deleted.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the deletion in JSON format.
        """
        url = f"/external-api/appraisers/{appraiserId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_aircraft_model_info(self, aircraftModelId, debug=False):
        """
        GET: Retrieve details for a specific aircraft model by its ID.

        Parameters:
        - aircraftModelId (str): The unique ID of the aircraft model to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The aircraft model details in JSON format.
        """
        url = f"/external-api/aircraft-models/{aircraftModelId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_model_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of aircraft models with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of aircraft models in JSON format.
        """
        url = "/external-api/aircraft-models"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_aircraft_model(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft model.

        Parameters:
        - data (dict): A dictionary containing the details of the aircraft model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The details of the newly created aircraft model in JSON format.
        """
        url = "/external-api/aircraft-models"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_model(self, aircraftModelId, data, debug=False):
        """
        PUT: Update an existing aircraft model by its ID.

        Parameters:
        - aircraftModelId (str): The unique ID of the aircraft model to update.
        - data (dict): A dictionary containing the updated details of the aircraft model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft model details in JSON format.
        """
        url = f"/external-api/aircraft-models/{aircraftModelId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def get_engine_model_info(self, engineModelId, debug=False):
        """
        GET: Retrieve details for a specific engine model by its ID.

        Parameters:
        - engineModelId (str): The unique ID of the engine model to retrieve details for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The engine model details in JSON format.
        """
        url = f"/external-api/engine-models/{engineModelId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_model_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of engine models with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of engine models in JSON format.
        """
        url = "/external-api/engine-models"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_engine_model(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new engine model.

        Parameters:
        - data (dict): A dictionary containing the details of the engine model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The details of the newly created engine model in JSON format.
        """
        url = "/external-api/engine-models"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_model(self, engineModelId, data, debug=False):
        """
        PUT: Update an existing engine model by its ID.

        Parameters:
        - engineModelId (str): The unique ID of the engine model to update.
        - data (dict): A dictionary containing the updated details of the engine model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated engine model details in JSON format.
        """
        url = f"/external-api/engine-models/{engineModelId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def async_update_engine_llp_name(self, engineModelId, data, debug=False):
        """
        PUT: Update an existing engine model llp ID & name.

        ** This is an asynchronous call and should not be called directly without a specific reason. 
        ** Use the ExternalUtils function instead.

        Parameters:
        - engineModelId (str): The unique ID of the engine model to update.
        - data (dict): A dictionary containing the updated details of the engine model.     
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Data Format:
        - {
          "oldId": "",
          "newId": "",
          "newName": ""
        }

        Returns:
        - dict containing an asynchronous JobId
        """

        url = f"/external-api/engine-models/llp-stack/{engineModelId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)
    
    def async_update_engine_module_name(self, engineModelId, data, debug=False):
        """
        PUT: Update an existing engine model module Id & name.

        ** This is an asynchronous call and should not be called directly without a specific reason. 
        ** Use the ExternalUtils function instead.

        Parameters:
        - engineModelId (str): The unique Id of the engine model to update.
        - data (dict): A dictionary containing the updated details of the engine model.     
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Data Format:
        - {
          "oldId": "",
          "newId": "",
          "newName": ""
        }

        Returns:
        - dict containing an asynchronous JobId
        """
        
        url = f"/external-api/engine-models/module-name/{engineModelId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)
    
    def get_async_job_status(self, jobId, debug=False):
        """
        GET: Get the status an existing asynchronous Job.

        Parameters:
        - jobId (str): The unique Id of the Job returned from the asynchronous request.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.


        Returns:
        - dict: status of the asynchronous Job.
        """
        url = f"/external-api/asynchronous-jobs/{jobId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug, multiSend=False, sendSize=1)
    
        
    def get_income_statement_list_per_company(self, companyId, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of income statements with optional pagination.

        Parameters:
        - companyId (str): Company UUID for which income statements will be returned.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of income statements in JSON format.
        """
        url = "/external-api/financial-statements/income-statements"

        params = {
            "companyId": companyId
        }
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_income_statement_info(self, incomeStatementId, debug=False):
        """
        GET: Retrieve details for a specific income statement by its ID.

        Parameters:
        - incomeStatementId (str): The unique ID of the income statement to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The income statement details in JSON format.
        """
        url = f"/external-api/financial-statements/income-statements/{incomeStatementId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def delete_income_statement(self, incomeStatementId, debug=False):
        """
        DELETE: Delete a specific income statement by its ID.

        Parameters:
        - incomeStatementId (str): The unique ID of the income statement to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the deletion.
        """
        url = f"/external-api/financial-statements/income-statements/{incomeStatementId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_balance_sheet_list_per_company(self, companyId, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of balance sheets with optional pagination.

        Parameters:
        - companyId (str): Company UUID for which balance sheets will be returned.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of balance sheets in JSON format.
        """
        url = "/external-api/financial-statements/balance-sheets"

        params = {
            "companyId": companyId
        }

        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_balance_sheet_info(self, balanceSheetId, debug=False):
        """
        GET: Retrieve details for a specific balance sheet by its ID.

        Parameters:
        - balanceSheetId (str): The unique ID of the balance sheet to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The balance sheet details in JSON format.
        """
        url = f"/external-api/financial-statements/balance-sheets/{balanceSheetId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def delete_balance_sheet(self, balanceSheetId, debug=False):
        """
        DELETE: Delete a specific balance sheet by its ID.

        Parameters:
        - balanceSheetId (str): The unique ID of the balance sheet to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the deletion.
        """
        url = f"/external-api/financial-statements/balance-sheets/{balanceSheetId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)


    def get_all_fee_structures(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all fee structure with optional filters and pagination.

        Parameters:
        - limit (int, optional): The maximum number of results to return per request.
        - offset (int, optional): The starting index for paginated results.
        - debug (bool, optional): If True, prints the request URL and parameters for debugging.

        Returns:
        - dict: A JSON response containing the list of fee structures, including metadata such as total count and pagination details if applicable.
        """
        url = "/external-api/fee-structure"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_fee_structure(self, feeStructureId, debug=False):
        """
        GET: Retrieve details for a specific fee structure by its ID.

        Parameters:
        - feeStructureId (str): The unique ID of the fee structure to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The fee structure details in JSON format.
        """
        url = f"/external-api/fee-structure/{feeStructureId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_fee_structure(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new fee structure.

        Parameters:
        - data (dict): Data for the new fee structure.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/fee-structure"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_fee_structure(self, feeStructureId, data, multiSend=False, debug=False):
        """
        PUT: Update an existing fee structure by its ID.

        Parameters:
        - feeStructureId (str): The unique ID of the fee structure to retrieve.
        - data (dict): Updated data for the fee structure.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/fee-structure/{feeStructureId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_fee_structure(self, feeStructureId, debug=False):
        """
        DELETE: Delete a specific fee structure by its ID.

        Parameters:
        - feeStructureId (str): The unique ID of the fee structure to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/fee-structure/{feeStructureId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)


    def get_user_info(self, userId, debug=False):
        """
        GET: Retrieve detailed information for a specific user by its ID.

        Parameters:
        - userId (str): The unique ID of the user to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: Detailed information about the user in JSON format.
        """
        url = f"/external-api/users/{userId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_user_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all users with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of users in JSON format.
        """
        url = "/external-api/users"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_role_info(self, roleId, debug=False):
        """
        GET: Retrieve detailed information for a specific role by its ID.

        Parameters:
        - roleId (str): The unique ID of the role to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: Detailed information about the role in JSON format.
        """
        url = f"/external-api/roles/{roleId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_role_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all roles with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of roles in JSON format.
        """
        url = "/external-api/roles"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_aircraft_part_type_info(self, aircraftPartTypeId, debug=False):
        """
        GET: Retrieve information for a specific aircraft part type by its ID.

        Parameters:
        - aircraftPartTypeId (str): The unique ID of the aircraft part type to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The aircraft part type details in JSON format.
        """
        url = f"/external-api/aircraft-part-types/{aircraftPartTypeId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_part_types_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all aircraft part types with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A paginated list of aircraft part types in JSON format.
        """
        url = "/external-api/aircraft-part-types"

        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_aircraft_part_type(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft part type.

        Parameters:
        - data (dict): Data for the new aircraft part type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/aircraft-part-types"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_part_type(self, aircraftPartTypeId, data, debug=False):
        """
        PUT: Update an existing aircraft part type by its ID.

        Parameters:
        - aircraftPartTypeId (str): The unique ID of the aircraft part type to update.
        - data (dict): Updated data for the aircraft part type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/aircraft-part-types/{aircraftPartTypeId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def get_credit_model_list(self, limit=None, offset=None, name=None, debug=False):
        """
        Retrieve a list of credit models with optional pagination and filtering by name.

        Args:
            limit (int, optional): The number of results to return per page.
            offset (int, optional): The starting point for pagination.
            name (str, optional): Name filter for credit models.
            debug (bool): Optional flag to enable debugging information.

        Returns:
            dict: A paginated list of credit models in JSON format.
        """
        url = "/external-api/risk/credit-models"
        params = {k: v for k, v in {'limit': limit, 'offset': offset, 'name': name}.items() if v is not None}

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_credit_model_info(self, creditModelId, debug=False):
        """
        Retrieve details for a specific credit model by its ID.

        Args:
            creditModelId (str): The unique ID of the credit model to retrieve.
            debug (bool): Optional flag to enable debugging information.

        Returns:
            dict: Details of the specified credit model in JSON format.
        """
        url = f"/external-api/risk/credit-models/{creditModelId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def generate_company_rating(self, companyId, creditModelId, balanceSheetId=None, incomeStatementId=None, debug=False):
        """
        Generate a company rating for a specific company by its ID, using optional financial statement references.

        Args:
            companyId (str): The unique ID of the company to generate the rating for.
            creditModelId (str): The ID of the credit model to use.
            balanceSheetId (str, optional): The ID of the balance sheet to use in rating generation.
            incomeStatementId (str, optional): The ID of the income statement to use in rating generation.
            debug (bool): Optional flag to enable debugging information.

        Returns:
            dict: The generated company rating in JSON format.
        """
        url = f"/external-api/risk/company-ratings/generate/{companyId}"
        params = {k: v for k, v in {
            'creditModelId': creditModelId,
            'balanceSheetId': balanceSheetId,
            'incomeStatementId': incomeStatementId
        }.items() if v is not None}

        return self.make_authenticated_request(self.config, url, method='POST', params=params, debug=debug)

    def create_company_rating(self, companyId, creditModelId, effectiveDate, companyRating, debug=False):
        """
        Create a company rating for a specific company by its ID.

        Args:
            companyId (str): The unique ID of the company to create the rating for.
            creditModelId (str): The ID of the credit model to associate with the rating.
            effectiveDate (str): The effective date of the rating.
            companyRating (float): The rating score for the company.
            debug (bool): Optional flag to enable debugging information.

        Returns:
            dict: Confirmation of the rating creation in JSON format.
        """
        url = f"/external-api/risk/company-ratings/create/{companyId}"
        data = {
            'creditModelId': creditModelId,
            'effectiveDate': effectiveDate,
            'companyRating': companyRating
        }

        return self.make_authenticated_request(self.config, url, method='POST', json=data, debug=debug)

    def get_all_wari_ratings(self, countryId=None, ratingAgencyId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all WARI ratings for a country with optional countryId, ratingAgencyId, and pagination.

        Parameters:
        - countryId (str, optional): Country UUID from which the WARI ratings will be returned.
        - ratingAgencyId (str, optional): Rating agency UUID from which the WARI ratings will be returned.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of WARI ratings in JSON format.
        """
        url = "/external-api/country-ratings/wari-ratings"

        params = {
            'countryId': countryId,
            'ratingAgencyId': ratingAgencyId
        }
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_wari_rating_info(self, wariRatingId, debug=False):
        """
        GET: Retrieve details for a specific WARI rating by its ID.

        Parameters:
        - wariRatingId (str): The unique ID of the WARI rating to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The WARI rating details in JSON format.
        """
        url = f"/external-api/country-ratings/wari-ratings/{wariRatingId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_wari_rating(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new WARI rating.

        Parameters:
        - data (dict): Data for the new WARI rating.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/country-ratings/wari-ratings"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_wari_rating(self, wariRatingId, data, debug=False):
        """
        PUT: Update an existing WARI rating by its ID.

        Parameters:
        - wariRatingId (str): The unique ID of the WARI rating to update.
        - data (dict): Updated data for the WARI rating.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/country-ratings/wari-ratings/{wariRatingId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_wari_rating(self, wariRatingId, debug=False):
        """
        DELETE: Delete a specific WARI rating by its ID.

        Parameters:
        - wariRatingId: The unique ID of the WARI rating to be deleted.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/country-ratings/wari-ratings/{wariRatingId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_ihi_ratings(self, countryId=None, ratingAgencyId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all IHI ratings for a country with optional countryId, ratingAgencyId, and pagination.

        Parameters:
        - countryId (str, optional): Country UUID from which the IHI ratings will be returned.
        - ratingAgencyId (str, optional): Rating agency UUID from which the IHI ratings will be returned.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of IHI ratings in JSON format.
        """
        url = "/external-api/country-ratings/ihi-ratings"

        params = {
            'countryId': countryId,
            'ratingAgencyId': ratingAgencyId
        }
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_ihi_rating_info(self, ihiRatingId, debug=False):
        """
        GET: Retrieve details for a specific ihi rating by its ID.

        Parameters:
        - ihiRatingId (str): The unique ID of the IHI rating to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The IHI rating details in JSON format.
        """
        url = f"/external-api/country-ratings/ihi-ratings/{ihiRatingId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_ihi_rating(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new IHI rating.

        Parameters:
        - data (dict): Data for the new IHI rating.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/country-ratings/ihi-ratings"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_ihi_rating(self, ihiRatingId, data, debug=False):
        """
        PUT: Update an existing IHI rating by its ID.

        Parameters:
        - ihiRatingId (str): The unique ID of the IHI rating to update.
        - data (dict): Updated data for the IHI rating.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/country-ratings/ihi-ratings/{ihiRatingId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_ihi_rating(self, ihiRatingId, debug=False):
        """
        DELETE: Delete a specific IHI rating by its ID.

        Parameters:
        - wariRatingId: The unique ID of the IHI rating to be deleted.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/country-ratings/ihi-ratings/{ihiRatingId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_gari_ratings(self, countryId=None, ratingAgencyId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all GARI ratings for a country with optional countryId, ratingAgencyId, and pagination.

        Parameters:
        - countryId (str, optional): Country UUID from which the GARI ratings will be returned.
        - ratingAgencyId (str, optional): Rating agency UUID from which the GARI ratings will be returned.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of GARI ratings in JSON format.
        """
        url = "/external-api/country-ratings/gari-ratings"

        params = {
            'countryId': countryId,
            'ratingAgencyId': ratingAgencyId
        }
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_gari_rating_info(self, gariRatingId, debug=False):
        """
        GET: Retrieve details for a specific GARI rating by its ID.

        Parameters:
        - gariRatingId (str): The unique ID of the GARI rating to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The GARI rating details in JSON format.
        """
        url = f"/external-api/country-ratings/gari-ratings/{gariRatingId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_gari_rating(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new GARI rating.

        Parameters:
        - data (dict): Data for the new GARI rating.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/country-ratings/gari-ratings"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_gari_rating(self, gariRatingId, data, debug=False):
        """
        PUT: Update an existing GARI rating by its ID.

        Parameters:
        - gariRatingId (str): The unique ID of the GARI rating to update.
        - data (dict): Updated data for the GARI rating.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/country-ratings/gari-ratings/{gariRatingId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_gari_rating(self, gariRatingId, debug=False):
        """
        DELETE: Delete a specific GARI rating by its ID.

        Parameters:
        - gariRatingId: The unique ID of the GARI rating to be deleted.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/country-ratings/gari-ratings/{gariRatingId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_utilization_defaults(self, limit=None, offset=None, aircraftModelId=None, operatorCompanyId=None, regionId=None, debug=False):
        """
        GET: Retrieve a list of all utilization defaults with optional filters and pagination.

        Parameters:
        - limit (int, optional): The maximum number of results to return per request.
        - offset (int, optional): The starting index for paginated results.
        - aircraftModelId (str, optional): Filter results by a specific aircraft model ID.
        - operatorCompanyId (str, optional): Filter results by a specific operator company ID.
        - regionId (str, optional): Filter results by a specific region ID.
        - debug (bool, optional): If True, prints the request URL and parameters for debugging.

        Returns:
        - dict: A JSON response containing the list of utilization defaults, including metadata such as total count and pagination details if applicable.
        """
        url = "/external-api/default-utilizations"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if aircraftModelId:
            params['aircraftModelId'] = aircraftModelId
        if operatorCompanyId:
            params['operatorCompanyId'] = operatorCompanyId
        if regionId:
            params['regionId'] = regionId

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_utilization_default(self, defaultUtilizationId, debug=False):
        """
        GET: Retrieve details for a specific utilization default by its ID.

        Parameters:
        - defaultUtilizationId (str): The unique ID of the utilization default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The utilization default details in JSON format.
        """
        url = f"/external-api/default-utilizations/{defaultUtilizationId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_utilization_default(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new utilization default.

        Parameters:
        - data (dict): Data for the new utilization default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/default-utilizations"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_utilization_default(self, defaultUtilizationId, data, multiSend=False, debug=False):
        """
        PUT: Update an existing utilization default by its ID.

        Parameters:
        - defaultUtilizationId (str): The unique ID of the utilization default to retrieve.
        - data (dict): Updated data for the utilization default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/default-utilizations/{defaultUtilizationId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_utilization_default(self, defaultUtilizationId, debug=False):
        """
        DELETE: Delete a specific utilization default by its ID.

        Parameters:
        - defaultUtilizationId (str): The unique ID of the utilization default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/default-utilizations/{defaultUtilizationId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_operating_severity_defaults(self, limit=None, offset=None, mode=None, query=None, debug=False):
        """
        GET: Retrieve a list of all severity defaults with optional filters and pagination.

        Parameters:
        - limit (int, optional): The maximum number of results to return per request.
        - offset (int, optional): The starting index for paginated results.
        - mode (str, optional): Filter results by default mode. 
            - OperatorAndEngineModel
            - Operator
            - CountryAndEngineModel
            - Country
            - RegionAndEngineModel
            - Region
            - Generic
        - query (str, optional): Filter results by engine model, operator company, country or region.
        - debug (bool, optional): If True, prints the request URL and parameters for debugging.

        Returns:
        - dict: A JSON response containing the list of severity defaults, including metadata such as total count and pagination details if applicable.
        """
        url = "/external-api/severity-defaults"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if mode:
            params['mode'] = mode
        if query:
            params['query'] = query

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_operating_severity_default(self, severityDefaultId, debug=False):
        """
        GET: Retrieve details for a specific severity default by its ID.

        Parameters:
        - severityDefaultId (str): The unique ID of the severity default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The severity default details in JSON format.
        """
        url = f"/external-api/severity-defaults/{severityDefaultId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_operating_severity_default(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new severity default.

        Parameters:
        - data (dict): Data for the new severity default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/severity-defaults"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_operating_severity_default(self, severityDefaultId, data, multiSend=False, debug=False):
        """
        PUT: Update an existing severity default by its ID.

        Parameters:
        - severityDefaultId (str): The unique ID of the severity default to retrieve.
        - data (dict): Updated data for the severity default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/severity-defaults/{severityDefaultId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_operating_severity_default(self, severityDefaultId, debug=False):
        """
        DELETE: Delete a specific severity default by its ID.

        Parameters:
        - severityDefaultId (str): The unique ID of the severity default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/severity-defaults/{severityDefaultId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_shop_visit_downtime_defaults(self, limit=None, offset=None, shopVisitDowntimeType=None, category=None, query=None, debug=False):
        """
        GET: Retrieve a list of all shop visit downtime with optional filters and pagination.

        Parameters:
        - limit (int, optional): The maximum number of results to return per request.
        - offset (int, optional): The starting index for paginated results.
        - shopVisitDowntimeType (str, optional): Filter results by shopVisitDowntimeType. 
            - generic
            - engine
            - aircraft
        - category (str, optional): Filter results by shop visit category.
            - engine_check
            - airframe_check
            - airframe_multi_check
        - query (str, optional): Filter results by engine model or aircraft model.
        - debug (bool, optional): If True, prints the request URL and parameters for debugging.

        Returns:
        - dict: A JSON response containing the list of shop visit downtime defaults, including metadata such as total count and pagination details if applicable.
        """
        url = "/external-api/shop-visit-downtime-defaults"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if shopVisitDowntimeType:
            params['shopVisitDowntimeType'] = shopVisitDowntimeType
        if category:
            params['category'] = category
        if query:
            params['query'] = query

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_shop_visit_downtime_default(self, shopVisitDowntimeDefaultId, debug=False):
        """
        GET: Retrieve details for a specific shop visit downtime default by its ID.

        Parameters:
        - shopVisitDowntimeDefaultId (str): The unique ID of the shop visit downtime default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The shop visit downtime default details in JSON format.
        """
        url = f"/external-api/shop-visit-downtime-defaults/{shopVisitDowntimeDefaultId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_shop_visit_downtime_default(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new shop visit downtime default.

        Parameters:
        - data (dict): Data for the new shop visit downtime default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/shop-visit-downtime-defaults"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_shop_visit_downtime_default(self, shopVisitDowntimeDefaultId, data, multiSend=False, debug=False):
        """
        PUT: Update an existing shop visit downtime default by its ID.

        Parameters:
        - shopVisitDowntimeDefaultId (str): The unique ID of the shop visit downtime default to retrieve.
        - data (dict): Updated data for the shop visit downtime default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/shop-visit-downtime-defaults/{shopVisitDowntimeDefaultId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_shop_visit_downtime_default(self, shopVisitDowntimeDefaultId, debug=False):
        """
        DELETE: Delete a specific shop visit downtime default by its ID.

        Parameters:
        - shopVisitDowntimeDefaultId (str): The unique ID of the shop visit downtime default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/shop-visit-downtime-defaults/{shopVisitDowntimeDefaultId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)



    def get_aircraft_part_info(self, aircraftPartId, debug=False):
        """
        GET: Retrieve information for a specific aircraft part by its ID.

        Parameters:
        - aircraftPartId (str): The unique ID of the aircraft part to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The aircraft part details in JSON format.
        """
        url = f"/external-api/aircraft-part/{aircraftPartId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_parts_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all aircraft parts with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A paginated list of aircraft part in JSON format.
        """
        url = "/external-api/aircraft-part"

        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_aircraft_part(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft part.

        Parameters:
        - data (dict): Data for the new aircraft part.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/aircraft-part"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_part(self, aircraftPartId, data, debug=False):
        """
        PUT: Update an existing aircraft part by its ID.

        Parameters:
        - aircraftPartId (str): The unique ID of the aircraft part to update.
        - data (dict): Updated data for the aircraft part.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/aircraft-part/{aircraftPartId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)
    
    def delete_aircraft_part(self, aircraftPartId: str, debug: bool=False):
        """
        DELETE: Delete an existing aircraft part.

        Parameters:
        - aircraftPartId (str): The UUID of the aircraft part to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The deleted aircraft part object
        """
        url = f"/external-api/aircraft-part/{aircraftPartId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def update_aircraft_part_maintenance_policy_type_checks(self, aircraftPartMaintenancePolicyTypeId, data, debug=False):
        """
        GET: Retrieve checks for a specific aircraft part maintenance policy type.

        Parameters:

        - aircraftPartMaintenancePolicyTypeId (str): The unique ID of the aircraft part maintenance policy type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The details of the checks for the given maintenance policy type in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policy-types/checks/{aircraftPartMaintenancePolicyTypeId}"

        return self.make_authenticated_request(self.config,  url, method='PUT', data =data, debug=debug)


    def get_aircraft_part_maintenance_policies(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve aircraft part maintenance policies.

        Parameters:

        - limit (int): Optional. The maximum number of items to fetch.
        - offset (int): Optional. The number of items to skip when fetching.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The details of the aircraft part maintenance policies in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policies"

        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)


    def get_aircraft_part_maintenance_policy_info(self, aircraftPartMxPolicyId, debug=False):
        """
        GET: Retrieve the info of an aircraft part maintenance policy

        Parameters:

        - aircraftPartMxPolicyId (str): Required. The uuid of the aircraft Part Maintenance Policy to get.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The details of an aircraft part maintenance policy in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policies/{aircraftPartMxPolicyId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)


    def create_aircraft_part_maintenance_policy(self, data, debug=False):
        """
        GET: Create an aircraft part maintenance policy

        Parameters:

        - data (dict): Required. The data (dictionary/json) to post.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The details of the created aircraft part maintenance policy in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)


    def update_aircraft_part_maintenance_policy(self, aircraftPartMxPolicyId, data, debug=False):
        """
        GET: Create an aircraft part maintenance policy

        Parameters:

        - aircraftPartMxPolicyId (str): Required. The uuid of the aircraft Part Maintenance Policy to get.
        - data (dict): Required. The data (dictionary/json) to post.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The details of the created aircraft part maintenance policy in JSON format.
        """
        url = f"/external-api/aircraft-part-maintenance-policies/{aircraftPartMxPolicyId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug)


    def get_airframe_build_standard_info(self, airframeBuildStandardId, debug=False):
        """
        GET: Retrieve information about a specific airframe build standard.

        Parameters:
        - airframeBuildStandardId (str): The unique ID of the airframe build standard.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The airframe build standard information in JSON format.
        """
        url = f"/external-api/airframe-build-standards/{airframeBuildStandardId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_airframe_build_standards_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a paginated list of airframe build standards.

        Parameters:
        - limit (int, optional): The number of results to return per page. Default is None.
        - offset (int, optional): The starting point for pagination. Default is None.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The paginated list of airframe build standards in JSON format.
        """
        url = "/external-api/airframe-build-standards"
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_airframe_build_standard(self, data, debug=False):
        """
        POST: Create a new airframe build standard.

        Parameters:
        - data (dict): The payload for the airframe build standard creation.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after creating the airframe build standard in JSON format.
        """
        url = "/external-api/airframe-build-standards"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)

    def update_airframe_build_standard(self, airframeBuildStandardId, data, debug=False):
        """
        PUT: Update an existing airframe build standard.

        Parameters:
        - airframeBuildStandardId (str): The unique ID of the airframe build standard to update.
        - data (dict): The payload for the airframe build standard update.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after updating the airframe build standard in JSON format.
        """
        url = f"/external-api/airframe-build-standards/{airframeBuildStandardId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug)

    def get_engine_build_standard_info(self, engineBuildStandardId, debug=False):
        """
        GET: Retrieve information about a specific engine build standard.

        Parameters:
        - engineBuildStandardId (str): The unique ID of the engine build standard.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The engine build standard information in JSON format.
        """
        url = f"/external-api/engine-build-standards/{engineBuildStandardId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_build_standards_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a paginated list of engine build standards.

        Parameters:
        - limit (int, optional): The number of results to return per page. Default is None.
        - offset (int, optional): The starting point for pagination. Default is None.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The paginated list of engine build standards in JSON format.
        """
        url = "/external-api/engine-build-standards"
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_engine_build_standard(self, data, debug=False):
        """
        POST: Create a new engine build standard.

        Parameters:
        - data (dict): The payload for the engine build standard creation.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after creating the engine build standard in JSON format.
        """
        url = "/external-api/engine-build-standards"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)

    def update_engine_build_standard(self, engineBuildStandardId, data, debug=False):
        """
        PUT: Update an existing engine build standard.

        Parameters:
        - engineBuildStandardId (str): The unique ID of the engine build standard to update.
        - data (dict): The payload for the engine build standard update.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after updating the engine build standard in JSON format.
        """
        url = f"/external-api/engine-build-standards/{engineBuildStandardId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug)

    def get_engine_llp_mx_policy_info(self, engineLlpMxPolicyId, debug=False):
        """
        GET: Retrieve information about a specific engine LLP maintenance policy.

        Parameters:
        - engineLlpMxPolicyId (str): The unique ID of the engine LLP maintenance policy.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The engine LLP maintenance policy information in JSON format.
        """
        url = f"/external-api/engine-llp-mx-policies/{engineLlpMxPolicyId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_llp_mx_policies_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a paginated list of engine LLP maintenance policies.

        Parameters:
        - limit (int, optional): The number of results to return per page. Default is None.
        - offset (int, optional): The starting point for pagination. Default is None.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The paginated list of engine LLP maintenance policies in JSON format.
        """
        url = "/external-api/engine-llp-mx-policies"
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_engine_llp_mx_policy(self, data, debug=False):
        """
        POST: Create a new engine LLP maintenance policy.

        Parameters:
        - data (dict): The payload for the engine LLP maintenance policy creation.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after creating the engine LLP maintenance policy in JSON format.
        """
        url = "/external-api/engine-llp-mx-policies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)

    def update_engine_llp_mx_policy(self, engineLlpMxPolicyId, data, debug=False):
        """
        PUT: Update an existing engine LLP maintenance policy.

        Parameters:
        - engineLlpMxPolicyId (str): The unique ID of the engine LLP maintenance policy to update.
        - data (dict): The payload for the engine LLP maintenance policy update.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after updating the engine LLP maintenance policy in JSON format.
        """
        url = f"/external-api/engine-llp-mx-policies/{engineLlpMxPolicyId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug)

    def get_engine_pr_mx_policy_info(self, enginePrMxPolicyId, debug=False):
        """
        GET: Retrieve information about a specific engine PR maintenance policy.

        Parameters:
        - enginePrMxPolicyId (str): The unique ID of the engine PR maintenance policy.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The engine PR maintenance policy information in JSON format.
        """
        url = f"/external-api/engine-pr-mx-policies/{enginePrMxPolicyId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_pr_mx_policies_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a paginated list of engine PR maintenance policies.

        Parameters:
        - limit (int, optional): The number of results to return per page. Default is None.
        - offset (int, optional): The starting point for pagination. Default is None.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The paginated list of engine PR maintenance policies in JSON format.
        """
        url = "/external-api/engine-pr-mx-policies"
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_engine_pr_mx_policy(self, data, debug=False):
        """
        POST: Create a new engine PR maintenance policy.

        Parameters:
        - data (dict): The payload for the engine PR maintenance policy creation.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after creating the engine PR maintenance policy in JSON format.
        """
        url = "/external-api/engine-pr-mx-policies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)

    def update_engine_pr_mx_policy(self, enginePrMxPolicyId, data, debug=False):
        """
        PUT: Update an existing engine PR maintenance policy.

        Parameters:
        - enginePrMxPolicyId (str): The unique ID of the engine PR maintenance policy to update.
        - data (dict): The payload for the engine PR maintenance policy update.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after updating the engine PR maintenance policy in JSON format.
        """
        url = f"/external-api/engine-pr-mx-policies/{enginePrMxPolicyId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug)
    
    def delete_engine_pr_mx_policy(self, enginePrMxPolicyId, debug=False):
        """
        DELETE: Delete an engine PR maintenance policy.

        Parameters:
        - enginePrMxPolicyId (str): The unique ID of the engine PR maintenance policy to update.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response of deleting the engine PR maintenance policy.
        """
        url = f"/external-api/engine-pr-mx-policies/{enginePrMxPolicyId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_engine_info(self, engineId, debug=False):
        """
        GET: Retrieve details for a specific engine by its ID.

        Parameters:
        - engineId (str): The unique ID of the engine.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The engine details in JSON format.
        """
        url = f"/external-api/engines/{engineId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a paginated list of engines.

        Parameters:
        - limit (int, optional): The number of results to return per page. Default is None.
        - offset (int, optional): The starting point for pagination. Default is None.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The paginated list of engines in JSON format.
        """
        url = "/external-api/engines"
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def create_engine(self, engineModelId, data, debug=False):
        """
        POST: Create a new engine for a specific engine model.

        Parameters:
        - engineModelId (str): The ID of the engine model for which the engine is being created.
        - data (dict): The payload for the engine creation.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after creating the engine in JSON format.
        """
        url = f"/external-api/engines/{engineModelId}"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)

    def update_engine(self, engineId, data, debug=False):
        """
        PUT: Update an existing engine by its ID.

        Parameters:
        - engineId (str): The unique ID of the engine to update.
        - data (dict): The payload for the engine update.
        - debug (bool): Optional. If True, prints the URL and payload for debugging purposes.

        Returns:
        - dict: The response after updating the engine in JSON format.
        """
        url = f"/external-api/engines/{engineId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug)

    def delete_engine(self, engineId, debug=False):
        """
        DELETE: Delete an existing engine by its ID.

        Parameters:
        - engineId (str): The unique ID of the engine to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The response after deleting the engine in JSON format.
        """
        url = f"/external-api/engines/{engineId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_company_rating_list(self, companyId, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a paginated list of company ratings.

        Parameters:
        - limit (int, optional): The number of results to return per page. Default is None.
        - offset (int, optional): The starting point for pagination. Default is None.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The paginated list of company ratings in JSON format.
        """
        url = "/external-api/risk/company-ratings"
        params = {
            "companyId": companyId
        }
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_company_rating_details(self, companyRatingId, debug=False):
        """
        GET: Retrieve details of a specific company rating.

        Parameters:
        - companyRatingId (str): The unique ID of the company rating.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The company rating details in JSON format.
        """
        url = f"/external-api/risk/company-ratings/{companyRatingId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def delete_company_rating(self, companyRatingId, debug=False):
        """
        DELETE: Delete a specific company rating by its ID.

        Parameters:
        - companyRatingId (str): The unique ID of the company rating to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The response after deleting the company rating in JSON format.
        """
        url = f"/external-api/risk/company-ratings/{companyRatingId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_aircraft_maintenance_inflation_defaults(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all aircraft maintenance inflation defaults with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of aircraft maintenance inflation defaults in JSON format.
        """
        url = "/external-api/aircraft-maintenance-inflation-defaults"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_aircraft_maintenance_inflation_default(self, aircraftMxInflationDefaultId, debug=False):
        """
        GET: Retrieve details for a specific aircraft maintenance inflation default by its ID.

        Parameters:
        - aircraftMxInflationDefaultId (str): The unique ID of the aircraft maintenance inflation default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The aircraft maintenance inflation default details in JSON format.
        """
        url = f"/external-api/aircraft-maintenance-inflation-defaults/{aircraftMxInflationDefaultId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_aircraft_maintenance_inflation_default(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft maintenance inflation default.

        Parameters:
        - data (dict): Data for the new aircraft mx inflation default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/aircraft-maintenance-inflation-defaults"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_maintenance_inflation_default(self, aircraftMxInflationDefaultId, data, multiSend=False, debug=False):
        """
        PUT: Update an existing aircraft maintenance inflation default by its ID.

        Parameters:
        - aircraftMxInflationDefaultId (str): The unique ID of the aircraft maintenance inflation default to retrieve.
        - data (dict): Updated data for the aircraft mx inflation default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/aircraft-maintenance-inflation-defaults/{aircraftMxInflationDefaultId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_aircraft_maintenance_inflation_default(self, aircraftMxInflationDefaultId, debug=False):
        """
        DELETE: Delete a specific aircraft maintenance inflation default by its ID.

        Parameters:
        - aircraftMxInflationDefaultId (str): The unique ID of the aircraft maintenance inflation default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/aircraft-maintenance-inflation-defaults/{aircraftMxInflationDefaultId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_engine_maintenance_inflation_defaults(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all engine maintenance inflation defaults with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of engine maintenance inflation defaults in JSON format.
        """
        url = "/external-api/engine-maintenance-inflation-defaults"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)

    def get_engine_maintenance_inflation_default(self, engineMxInflationDefaultId, debug=False):
        """
        GET: Retrieve details for a specific engine maintenance inflation default by its ID.

        Parameters:
        - engineMxInflationDefaultId (str): The unique ID of the engine maintenance inflation default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The engine maintenance inflation default details in JSON format.
        """
        url = f"/external-api/engine-maintenance-inflation-defaults/{engineMxInflationDefaultId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_engine_maintenance_inflation_default(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new engine maintenance inflation default.

        Parameters:
        - data (dict): Data for the new engine mx inflation default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/engine-maintenance-inflation-defaults"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_maintenance_inflation_default(self, engineMxInflationDefaultId, data, multiSend=False, debug=False):
        """
        PUT: Update an existing engine maintenance inflation default by its ID.

        Parameters:
        - engineMxInflationDefaultId (str): The unique ID of the engine maintenance inflation default to retrieve.
        - data (dict): Updated data for the engine mx inflation default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/engine-maintenance-inflation-defaults/{engineMxInflationDefaultId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=1)

    def delete_engine_maintenance_inflation_default(self, engineMxInflationDefaultId, debug=False):
        """
        DELETE: Delete a specific engine maintenance inflation default by its ID.

        Parameters:
        - engineMxInflationDefaultId (str): The unique ID of the aircraft maintenance inflation default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the deletion failed.
        """
        url = f"/external-api/engine-maintenance-inflation-defaults/{engineMxInflationDefaultId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_all_generic_maintenance_inflation_defaults(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all generic maintenance inflation defaults with optional pagination.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of generic maintenance inflation defaults in JSON format.
        """
        url = "/external-api/generic-maintenance-inflation-defaults"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)


    def get_generic_maintenance_inflation_default(self, genericMxInflationDefaultId, debug=False):
        """
        GET: Retrieve details for a specific generic maintenance inflation default by its ID.

        Parameters:
        - genericMxInflationDefaultId (str): The unique ID of the generic maintenance inflation default to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The generic maintenance inflation default details in JSON format.
        """
        url = f"/external-api/generic-maintenance-inflation-defaults/{genericMxInflationDefaultId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)


    def create_generic_maintenance_inflation_default(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new generic maintenance inflation default.

        Parameters:
        - data (dict): Data for the new generic mx inflation default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the creation in JSON format.
        """
        url = "/external-api/generic-maintenance-inflation-defaults"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_generic_maintenance_inflation_default(self, genericMxInflationDefaultId, data, multiSend=False, debug=False):
        """
        PUT: Update an existing generic maintenance inflation default by its ID.

        Parameters:
        - genericMxInflationDefaultId (str): The unique ID of the generic maintenance inflation default to retrieve.
        - data (dict): Updated data for the generic mx inflation default.
        - multiSend (bool, optional): If True, allows for batch sending.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: Confirmation of the update in JSON format.
        """
        url = f"/external-api/generic-maintenance-inflation-defaults/{genericMxInflationDefaultId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=1)

    
    def get_users(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of users.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of users.
        """
        
        url = "/external-api/users"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)
    

    def get_user(self, user_id, debug=False):
        """
        GET: Retrieve details of a user.

        Parameters:
        - user_id (str): the uuid of the user to fetch information from.
        - debug (bool): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A dictionary of the user object.
        """

        url = f"/external-api/users/{user_id}"


        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)
    

    def get_severity_defaults_list(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of severity defaults.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of severity defaults.
        """
        
        url = "/external-api/severity-defaults"

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)
    
    
    def create_severity_default(self, data, debug=False):
        """
        POST: Create a severity default.

        Parameters:
        - data: The payload for the severity default creation.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created severity default object
        """
        
        url = "/external-api/severity-defaults"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)
    

    def get_severity_default(self, severityDefaultId, debug=False):
        """
        GET: Retrieve a severity default by unique id.

        Parameters:
        - severityDefaultId: The unique ID of the severity default to retrieve.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The requested severity default object
        """
        
        url = f"/external-api/severity-defaults/{severityDefaultId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)
    

    def delete_severity_default(self, severityDefaultId, debug=False):
        """
        DELETE: Deletes a severity default by unique id.

        Parameters:
        - severityDefaultId: The unique ID of the severity default to delete.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: 
        """
        
        url = f"/external-api/severity-defaults/{severityDefaultId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)
    

    def update_severity_default(severityDefaultId, data, self, limit=None, offset=None, debug=False):
        """
        PUT: Updates a severity default by unique id.

        Parameters:
        - severityDefaultId: The unique ID of the severity default to delete.
        - data: The payload for the severity default update.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated severity default object.
        """
        
        url = f"/external-api/severity-defaults/{severityDefaultId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, sendSize=1)

    def get_all_regions(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all regions with optional pagination.

        Parameters:

        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of regions in JSON format, including country details like name, code, and metadata.
        """
        url = "/external-api/regions"

        # Construct query parameters
        params = {}
        if limit is not None:
            params['limit'] = limit
        else:
            limit = 999
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method='GET', params=params, debug=debug)


    def get_region_details(self, regionId, debug=False):
        """
        GET: Retrieve detailed information for a specific region by its region ID.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - regionId (str): The unique ID of the region for which details are to be retrieved.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing detailed information about the region
        """
        url = f"/external-api/regions/{regionId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)


    def create_region(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new region record in the system.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - data (dict): A dictionary containing the new region details such as region name, region code, and other relevant attributes.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the newly created region's details.
        """
        url = "/external-api/regions"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)


    def update_region(self, regionId, data, debug=False):
        """
        PUT: Update an existing region's details.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - regionId (str): The unique ID of the region to update.
        - data (dict): A dictionary containing the updated region details, such as updated region name, region code, and other attributes.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the updated region's details.
        """
        url = f"/external-api/regions/{regionId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=False, sendSize=1)

    def delete_region(self, regionId, debug=False):
        """
        DELETE: Delete a specific region by its region ID.

        Parameters:
        - env (str): The environment in which the API is hosted.
        - client (str): The specific client identifier.
        - regionId (str): The unique ID of the region to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response confirming the deletion or providing error information if the operation fails.
        """
        url = f"/external-api/regions/{regionId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)
    
    

    def get_all_dashboards(self, debug: bool=False):
        """
        GET: Retrieve a list of all dashboards

        Parameters:

        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of dashboards in JSON format.
        """
        url = "/external-api/dashboards"
        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)
    


    def get_dashboard(self, dashboardId: str, debug: bool=False):
        """
        GET: Retrieve a dashboard by id

        Parameters:
        - dashboardId (str): Required. The Id of the dashboard to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the requested dashboard's details.
        """
        url = f"/external-api/dashboards/{dashboardId}"
        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)


    def update_dashboard(self, dashboardId:str, data:Dict, debug: bool=False):
        """
        PUT: Update a dashboard by id

        Parameters:
        - dashboardId (str): Required. The Id of the dashboard to update.
        - data (Dict): Required. The data structure to update the dashboard with.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the updated dashboard's details.
        """
        url = f"/external-api/dashboards/{dashboardId}"
        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)


    def create_dashboard(self, data:Dict, debug: bool=False):
        """
        POST: Create a new dashboard in the system.

        Parameters:
        - data (dict): Required. A dictionary containing the new dashboard details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response containing the newly created dashboard's details.
        """
        url = "/external-api/dashboards"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug)


    def delete_dashboard(self, dashboardId: str, debug:bool=False):
        """
        DELETE: Delete a dashboard by its Id.

        Parameters:
        - dashboardId (str): The id of the dashboard to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A JSON response confirming the deletion or providing error information if the operation fails.
        """
        url = f"/external-api/dashboards/{dashboardId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)


    def get_engine_mx_override(self, engineMxOverrideId, debug=False):
        """
        GET: Retrieve a single engine maintenance override by its id.

        Parameters:
        - engineMxOverrideId: The unique id of the engine maintenance override to retrieve.
        - debug (bool, optional): If True, prints the URL for debugging purposes.

        Returns:
        - dict: The requested severity default object
        """
        url = f"/external-api/engine-mx-overrides/{engineMxOverrideId}"
        
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)


    def get_all_engine_mx_overrides(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all engine maintenance overrides with optional pagination.

        Params:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of engine maintenance overrides in JSON format.
        """
        url = f"/external-api/engine-mx-overrides"
        
        params = {}
        
        if limit is not None: 
            params['limit'] = limit
        else:
            limit = 999
        
        if offset is not None:
            params['offset'] = offset

        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug) 
    

    def get_all_utilization_shock_table_relations(self, bodyType=None, limit=None, offset=None, operatorCompanyId=None, regionId=None, shockTableId=None, debug=False):
        """
        GET: Retrieve a list of all utilization shock table relations with optional parameters.

        Parameters:
        - bodyType(enum, optional): A filter value based on airframe body type.
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - operatorCompanyId (str, optional): A filter string for operator companies.
        - regionId (str, optional): A filter string for regions.
        - shockTableId (str, optional): A filter string for shock tables.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of utilization shock table relations.
        """

        url = "/external-api/utilization-shock-table-relation"

        params = {} # Construct optional parameter to send
        if bodyType is not None: params['bodyType'] = bodyType
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
        if operatorCompanyId is not None: params['operatorCompanyId'] = operatorCompanyId
        if regionId is not None: params['regionId'] = regionId
        if shockTableId is not None: params['shockTableId'] = shockTableId
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_utilization_shock_table_relation(self, utilizationShockTableRelationId, debug=False):
        """
        GET: Retrieve a single utilization shock table relation by id.

        Parameters:
        - utilizationShockTableRelationId (str): The unique id of the utilization shock table relation to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single utilization shock table relation.
        """

        url = f"/external-api/utilization-shock-table-relation/{utilizationShockTableRelationId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_utilization_shock_table_relation(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new utilization shock table relation.

        Parameters:
        - data (dict): A dictionary containing the new utilization shock table relation details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created utilization shock table relation.
        """

        url = f"/external-api/utilization-shock-table-relation"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_utilization_shock_table_relation(self, utilizationShockTableRelationId, data, debug=False):
        """
        PUT: Update an existing utilization shock table relation.

        Parameters:
        - utilizationShockTableRelationId (str): The unique id of the utilization shock table relation to retrieve.
        - data (dict): A dictionary containing the new utilization shock table relation details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated utilization shock table relation.
        """

        url = f"/external-api/utilization-shock-table-relation/{utilizationShockTableRelationId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_utilization_shock_table_relation(self, utilizationShockTableRelationId, debug=False):
        """
        DELETE: Delete an existing utilization shock table relation.

        - utilizationShockTableRelationId (str): The unique id of the utilization shock table relation to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted utilization shock table relation.
        """

        url = f"/external-api/utilization-shock-table-relation/{utilizationShockTableRelationId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    def get_all_abs_structures(self, absStructureId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all abs structures with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - absStructureId (str, optional): A filter string for abs structures.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of abs structures.
        """

        url = "/external-api/abs-structures"

        params = {} # Construct optional parameter to send
        if absStructureId is not None: params['absStructureId'] = absStructureId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_abs_structure(self, absStructureId, debug=False):
        """
        GET: Retrieve a single abs structure by id.

        Parameters:
        - absStructureId (str): The unique id of the abs structure to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single abs structure.
        """

        url = f"/external-api/abs-structures/{absStructureId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_abs_structure(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new abs structure.

        Parameters:
        - data (dict): A dictionary containing the new abs structure details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created abs structure.
        """

        url = f"/external-api/abs-structures"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_abs_structure(self, absStructureId, data, debug=False):
        """
        PUT: Update an existing abs structure.

        Parameters:
        - absStructureId (str): The unique id of the abs structure to retrieve.
        - data (dict): A dictionary containing the new abs structure details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated abs structure.
        """

        url = f"/external-api/abs-structures/{absStructureId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_abs_structure(self, absStructureId, debug=False):
        """
        DELETE: Delete an existing abs structure by id.

        - absStructureId (str): The unique id of the abs structure to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted abs structure.
        """

        url = f"/external-api/abs-structure/{absStructureId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    def get_all_average_aircraft_utilizations(self, aircraftId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all average aircraft utilizations with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - aircraftId (str, optional): A filter string.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of average aircraft utilizations.
        """

        url = "/external-api/average-aircraft-utilizations"

        params = {} # Construct optional parameter to send
        if aircraftId is not None: params['aircraftId'] = aircraftId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_average_aircraft_utilization(self, averageAircraftUtilizationId, debug=False):
        """
        GET: Retrieve a single average aircraft utilization by id.

        Parameters:
        - averageAircraftUtilizationId (str): The unique id of the average aircraft utilization to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single average aircraft utilization.
        """

        url = f"/external-api/average-aircraft-utilizations/{averageAircraftUtilizationId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_average_aircraft_utilization(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new average aircraft utilization.

        Parameters:
        - data (dict): A dictionary containing the new average aircraft utilization details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created average aircraft utilization.
        """

        url = f"/external-api/average-aircraft-utilizations"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_average_aircraft_utilization(self, averageAircraftUtilizationId, data, debug=False):
        """
        PUT: Update an existing average aircraft utilization.

        Parameters:
        - averageAircraftUtilizationId (str): The unique id of the average aircraft utilization to retrieve.
        - data (dict): A dictionary containing the new average aircraft utilization details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated average aircraft utilization.
        """

        url = f"/external-api/average-aircraft-utilizations/{averageAircraftUtilizationId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_average_aircraft_utilization(self, averageAircraftUtilizationId, debug=False):
        """
        DELETE: Delete an existing average aircraft utilization by id.

        - averageAircraftUtilizationId (str): The unique id of the average aircraft utilization to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted average aircraft utilization.
        """

        url = f"/external-api/average-aircraft-utilizations/{averageAircraftUtilizationId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    def get_all_utilization_analysis_settings(self, utilizationAnalysisSettingsId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all utilization analysis settings with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - utilizationAnalysisSettingsId (str, optional): A filter string.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of utilization analysis settings.
        """

        url = "/external-api/utilization-analysis-settings"

        params = {} # Construct optional parameter to send
        if utilizationAnalysisSettingsId is not None: params['utilizationAnalysisSettingsId'] = utilizationAnalysisSettingsId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_utilization_analysis_setting(self, utilizationAnalysisSettingsId, debug=False):
        """
        GET: Retrieve a single utilization analysis setting by id.

        Parameters:
        - utilizationAnalysisSettingsId (str): The unique id of the utilization analysis settings to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single utilization analysis settings.
        """

        url = f"/external-api/utilization-analysis-settings/{utilizationAnalysisSettingsId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_utilization_analysis_setting(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new utilization analysis settings.

        Parameters:
        - data (dict): A dictionary containing the new utilization analysis settings details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created utilization analysis settings.
        """

        url = "/external-api/utilization-analysis-settings"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_utilization_analysis_setting(self, utilizationAnalysisSettingsId, data, debug=False):
        """
        PUT: Update an existing utilization analysis settings.

        Parameters:
        - utilizationAnalysisSettingsId (str): The unique id of the utilization analysis settings to retrieve.
        - data (dict): A dictionary containing the new utilization analysis settings details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated utilization analysis settings.
        """

        url = f"/external-api/utilization-analysis-settings/{utilizationAnalysisSettingsId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_utilization_analysis_setting(self, utilizationAnalysisSettingsId, debug=False):
        """
        DELETE: Delete an existing utilization analysis settings by id.

        - utilizationAnalysisSettingsId (str): The unique id of the utilization analysis settings to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted utilization analysis settings.
        """

        url = f"/external-api/utilization-analysis-settings/{utilizationAnalysisSettingsId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    def get_all_aircraft_part_mx_overrides(self, aircraftPartId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all aircraft part maintenance overrides with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - aircraftPartId (str, optional): A filter string.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of aircraft part maintenance.
        """

        url = "/external-api/aircraft-part-mx-overrides"

        params = {} # Construct optional parameter to send
        if aircraftPartId is not None: params['aircraftPartId'] = aircraftPartId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_aircraft_part_mx_override(self, aircraftPartMxOverrideId, debug=False):
        """
        GET: Retrieve a single utilization analysis setting by id.

        Parameters:
        - aircraftPartMxOverrideId (str): The unique id of the aircraft part maintenance to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single aircraft part maintenance.
        """

        url = f"/external-api/aircraft-part-mx-overrides/{aircraftPartMxOverrideId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_aircraft_part_mx_override(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft part maintenance.

        Parameters:
        - data (dict): A dictionary containing the new aircraft part maintenance details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created aircraft part maintenance.
        """

        url = "/external-api/aircraft-part-mx-overrides"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_aircraft_part_mx_override(self, aircraftPartMxOverrideId, data, debug=False):
        """
        PUT: Update an existing aircraft part maintenance.

        Parameters:
        - aircraftPartMxOverrideId (str): The unique id of the aircraft part maintenance to retrieve.
        - data (dict): A dictionary containing the new aircraft part maintenance details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated aircraft part maintenance.
        """

        url = f"/external-api/aircraft-part-mx-overrides/{aircraftPartMxOverrideId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_aircraft_part_mx_override(self, aircraftPartMxOverrideId, debug=False):
        """
        DELETE: Delete an existing aircraft part maintenance by id.

        - aircraftPartMxOverrideId (str): The unique id of the aircraft part maintenance to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted aircraft part maintenance.
        """

        url = f"/external-api/aircraft-part-mx-overrides/{aircraftPartMxOverrideId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    def get_all_utilization_shock_tables(self, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all utilization shock tables with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of utilization shock tables.
        """

        url = "/external-api/utilization-shock-table"

        params = {} # Construct optional parameter to send
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_utilization_shock_table(self, utilizationShockTableId, debug=False):
        """
        GET: Retrieve a single utilization analysis setting by id.

        Parameters:
        - utilizationShockTableId (str): The unique id of the utilization shock table to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single utilization shock table.
        """

        url = f"/external-api/utilization-shock-table/{utilizationShockTableId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_utilization_shock_table(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new utilization shock table.

        Parameters:
        - data (dict): A dictionary containing the new utilization shock table details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created utilization shock table.
        """

        url = "/external-api/utilization-shock-table"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_utilization_shock_table(self, utilizationShockTableId, data, debug=False):
        """
        PUT: Update an existing utilization shock table.

        Parameters:
        - utilizationShockTableId (str): The unique id of the utilization shock table to retrieve.
        - data (dict): A dictionary containing the new utilization shock table details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated utilization shock table.
        """

        url = f"/external-api/utilization-shock-table/{utilizationShockTableId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_utilization_shock_table(self, utilizationShockTableId, debug=False):
        """
        DELETE: Delete an existing utilization shock table by id.

        - utilizationShockTableId (str): The unique id of the utilization shock table to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted utilization shock table.
        """

        url = f"/external-api/utilization-shock-table/{utilizationShockTableId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    


    def get_all_engine_appraisals(self, engineId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all engine appraisals with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - engineId (str, optional): A filter string.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of engine appraisals.
        """

        url = "/external-api/engine-appraisals"

        params = {} # Construct optional parameter to send
        if engineId is not None: params['engineId'] = engineId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_engine_appraisal(self, engineAppraisalId, debug=False):
        """
        GET: Retrieve a single engine appraisal by id.

        Parameters:
        - engineAppraisalId (str): The unique id of the engine appraisal to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single engine appraisal.
        """

        url = f"/external-api/engine-appraisals/{engineAppraisalId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_engine_appraisal(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new engine appraisal.

        Parameters:
        - data (dict): A dictionary containing the new engine appraisal details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created engine appraisal.
        """

        url = "/external-api/engine-appraisals"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_engine_appraisal(self, engineAppraisalId, data, debug=False):
        """
        PUT: Update an existing engine appraisal.

        Parameters:
        - engineAppraisalId (str): The unique id of the engine appraisal to retrieve.
        - data (dict): A dictionary containing the new engine appraisal details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated engine appraisal.
        """

        url = f"/external-api/engine-appraisals/{engineAppraisalId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_engine_appraisal(self, engineAppraisalId, debug=False):
        """
        DELETE: Delete an existing engine appraisal by id.

        - engineAppraisalId (str): The unique id of the engine appraisal to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted engine appraisal.
        """

        url = f"/external-api/engine-appraisals/{engineAppraisalId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    def get_all_aircraft_part_appraisals(self, aircraftPartId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all aircraft part appraisals with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - aircraftPartId (str, optional): A filter string.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of aircraft part appraisals.
        """

        url = "/external-api/aircraft-part-appraisals"

        params = {} # Construct optional parameter to send
        if aircraftPartId is not None: params['aircraftPartId'] = aircraftPartId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_aircraft_part_appraisal(self, aircraftPartAppraisalId, debug=False):
        """
        GET: Retrieve a single aircraft part appraisal by id.

        Parameters:
        - aircraftPartAppraisalId (str): The unique id of the aircraft part appraisal to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single aircraft part appraisal.
        """

        url = f"/external-api/aircraft-part-appraisals/{aircraftPartAppraisalId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_aircraft_part_appraisal(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft part appraisal.

        Parameters:
        - data (dict): A dictionary containing the new aircraft part appraisal details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created aircraft part appraisal.
        """

        url = "/external-api/aircraft-part-appraisals"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_aircraft_part_appraisal(self, aircraftPartAppraisalId, data, debug=False):
        """
        PUT: Update an existing aircraft part appraisal.

        Parameters:
        - aircraftPartAppraisalId (str): The unique id of the aircraft part appraisal to retrieve.
        - data (dict): A dictionary containing the new aircraft part appraisal details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated aircraft part appraisal.
        """

        url = f"/external-api/aircraft-part-appraisals/{aircraftPartAppraisalId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_aircraft_part_appraisal(self, aircraftPartAppraisalId, debug=False):
        """
        DELETE: Delete an existing aircraft part appraisal by id.

        - aircraftPartAppraisalId (str): The unique id of the aircraft part appraisal to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted aircraft part appraisal.
        """

        url = f"/external-api/aircraft-part-appraisals/{aircraftPartAppraisalId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    def get_all_abs_calculation_input_sets(self, absStructureId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all abs calculation input sets with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - absStructureId (str, optional): A filter string.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of abs calculation input sets.
        """

        url = "/external-api/abs-calculation-input-sets"

        params = {} # Construct optional parameter to send
        if absStructureId is not None: params['absStructureId'] = absStructureId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_abs_calculation_input_set(self, absCalculationInputSetId, debug=False):
        """
        GET: Retrieve a single abs calculation input set by id.

        Parameters:
        - absCalculationInputSetId (str): The unique id of the abs calculation input set to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single abs calculation input set.
        """

        url = f"/external-api/abs-calculation-input-sets/{absCalculationInputSetId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_abs_calculation_input_set(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new abs calculation input set.

        Parameters:
        - data (dict): A dictionary containing the new abs calculation input set details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created abs calculation input set.
        """

        url = "/external-api/abs-calculation-input-sets"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_abs_calculation_input_set(self, absCalculationInputSetId, data, debug=False):
        """
        PUT: Update an existing abs calculation input set.

        Parameters:
        - absCalculationInputSetId (str): The unique id of the abs calculation input set to retrieve.
        - data (dict): A dictionary containing the new abs calculation input set details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated abs calculation input set.
        """

        url = f"/external-api/abs-calculation-input-sets/{absCalculationInputSetId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_abs_calculation_input_set(self, absCalculationInputSetId, debug=False):
        """
        DELETE: Delete an existing abs calculation input set by id.

        - absCalculationInputSetId (str): The unique id of the abs calculation input set to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted abs calculation input set.
        """

        url = f"/external-api/abs-calculation-input-sets/{absCalculationInputSetId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    def get_all_abs_snapshots(self, absSnapshotId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all abs snapshots with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - absSnapshotId (str, optional): A filter string.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of abs snapshots.
        """

        url = "/external-api/abs-snapshots"

        params = {} # Construct optional parameter to send
        if absSnapshotId is not None: params['absSnapshotId'] = absSnapshotId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_abs_snapshot(self, absSnapshotId, debug=False):
        """
        GET: Retrieve a single abs snapshot by id.

        Parameters:
        - absSnapshotId (str): The unique id of the abs snapshot to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single abs snapshot.
        """

        url = f"/external-api/abs-snapshots/{absSnapshotId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_abs_snapshot(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new abs snapshot.

        Parameters:
        - data (dict): A dictionary containing the new abs snapshot details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created abs snapshot.
        """

        url = "/external-api/abs-snapshots"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_abs_snapshot(self, absSnapshotId, data, debug=False):
        """
        PUT: Update an existing abs snapshot.

        Parameters:
        - absSnapshotId (str): The unique id of the abs snapshot to retrieve.
        - data (dict): A dictionary containing the new abs snapshot details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated abs snapshot.
        """

        url = f"/external-api/abs-snapshots/{absSnapshotId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_abs_snapshot(self, absSnapshotId, debug=False):
        """
        DELETE: Delete an existing abs snapshot by id.

        - absSnapshotId (str): The unique id of the abs snapshot to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted abs snapshot.
        """

        url = f"/external-api/abs-snapshots/{absSnapshotId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
    

    ## Agency Rating System

    def get_all_agency_rating_systems(self, ratingAgencyId=None, limit=None, offset=None, debug=False):
        """
        GET: Retrieve a list of all agency rating systems with optional parameters.

        Parameters:
        - limit (int, optional): The number of results to return per page.
        - offset (int, optional): The starting point for pagination.
        - ratingAgencyId (str, optional): A filter string.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A list of agency rating systems.
        """

        url = "/external-api/agency-rating-systems"

        params = {} # Construct optional parameter to send
        if ratingAgencyId is not None: params['ratingAgencyId'] = ratingAgencyId
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, params=params, debug=debug)
    

    def get_agency_rating_system(self, agencyRatingSystemId, debug=False):
        """
        GET: Retrieve a single agency rating system by id.

        Parameters:
        - agencyRatingSystemId (str): The unique id of the agency rating system to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: A single agency rating system.
        """

        url = f"/external-api/agency-rating-systems/{agencyRatingSystemId}"
   
        return self.make_authenticated_request(self.config, url, method=HttpMethod.GET, debug=debug)
    

    def create_agency_rating_system(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new agency rating system.

        Parameters:
        - data (dict): A dictionary containing the new agency rating system details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The created agency rating system.
        """

        url = "/external-api/agency-rating-systems"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.POST, data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)
    

    def update_agency_rating_system(self, agencyRatingSystemId, data, debug=False):
        """
        PUT: Update an existing agency rating system.

        Parameters:
        - agencyRatingSystemId (str): The unique id of the agency rating system to retrieve.
        - data (dict): A dictionary containing the new agency rating system details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The updated agency rating system.
        """

        url = f"/external-api/agency-rating-systems/{agencyRatingSystemId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.PUT, data=data, debug=debug, multiSend=False, sendSize=1)


    def delete_agency_rating_system(self, agencyRatingSystemId, debug=False):
        """
        DELETE: Delete an existing agency rating system by id.

        - agencyRatingSystemId (str): The unique id of the agency rating system to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.
        
        Returns:
        - dict: The deleted agency rating system.
        """

        url = f"/external-api/agency-rating-systems/{agencyRatingSystemId}"

        return self.make_authenticated_request(self.config, url, method=HttpMethod.DELETE, debug=debug)
