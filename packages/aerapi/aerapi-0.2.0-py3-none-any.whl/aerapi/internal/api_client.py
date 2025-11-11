# from common.auth import make_authenticated_request
from ..common.base_api import BaseAPIClient


class InternalAPIClient(BaseAPIClient):
    def __init__(self,  BaseAPI):
        """
        Initialize APIClient with a BaseAPI instance.
        """
        # Initialize the BaseAPI using the provided instance
        super().__init__(BaseAPI.env, BaseAPI.client)
        self.config = BaseAPI.config  # Inherit configuration from BaseAPI

    def __dir__(self):
        # Dynamically filter out attributes from Parent
        parent_attrs = set(dir(BaseAPIClient))  # Get all attributes from Parent
        all_attrs = set(super().__dir__())  # Get all attributes inherited by Child
        child_specific_attrs = all_attrs - parent_attrs  # Exclude Parent attributes
        return sorted(child_specific_attrs)

    def create_assembly(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new assembly.
        
        Parameters:

        - data (dict): The payload to create the assembly.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created assembly details (JSON response).
        """

        url = "/kb_api/assemblies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_assembly(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update an assembly.
        
        Parameters:
        - env (str): The environment (e.g., 'preprod').
        - client (str): The specific client (e.g., 'api-api-preprod-amergin').
        - data (dict): The payload to update the assembly.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated assembly details (JSON response).
        """

        url = "/kb_api/assemblies"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def delete_assembly(self, externalId, debug=False):
        """
        DELETE: Delete a specific assembly.
        
        Parameters:
        - env (str): The environment (e.g., 'preprod').
        - client (str): The specific client (e.g., 'api-api-preprod-amergin').
        - externalId (str): The external ID of the assembly to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The response of the delete operation (JSON response).
        """

        url = f"/kb_api/assembly/{externalId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_assembly(self, externalId, debug=False):
        """
        GET: Get details of a specific assembly.
        
        Parameters:
        - env (str): The environment (e.g., 'preprod').
        - client (str): The specific client (e.g., 'api-api-preprod-amergin').
        - externalId (str): The external ID of the assembly to fetch.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The assembly data (JSON response).
        """

        url = f"/kb_api/assembly/{externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_all_assemblies(self, limit, offset, debug=False):
        """
        GET: Get all assemblies with pagination.
        
        Parameters:
        - env (str): The environment (e.g., 'preprod').
        - client (str): The specific client (e.g., 'api-api-preprod-amergin').
        - limit (int): The number of results per page.
        - offset (int): The pagination offset.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The list of all assemblies (JSON response).
        """
        url = f"/kb_api/assemblies/{limit}/{offset}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_assembly_snapshots(self, externalId, debug=False):
        """
        GET: Get snapshots of a specific assembly.
        
        Parameters:
        - env (str): The environment (e.g., 'preprod').
        - client (str): The specific client (e.g., 'api-api-preprod-amergin').
        - externalId (str): The external ID of the assembly to get snapshots for.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The snapshots of the assembly (JSON response).
        """

        url = f"/kb_api/assembly/{externalId}/snapshots"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_assembly_snapshot(self, externalId, as_of, debug=False):
        """
        GET: Get a specific snapshot of an assembly.
        
        Parameters:
        - env (str): The environment (e.g., 'preprod').
        - client (str): The specific client (e.g., 'api-api-preprod-amergin').
        - externalId (str): The external ID of the assembly.
        - as_of (str): The snapshot timestamp or identifier.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The details of the specific snapshot (JSON response).
        """

        url = f"/kb_api/assembly/{externalId}/snapshot/{as_of}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_aircraft(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create a new aircraft.
        
        Parameters:
        - data (dict): A dictionary containing the details of the aircraft to be created.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created aircraft details in JSON format, including its unique identifier and metadata.
        """

        url = "/kb_api/aircraft"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update the details of an existing aircraft.
        
        Parameters:
        - env (str): The environment where the API is hosted (e.g., 'preprod').
        - client (str): The client identifier for the API.
        - data (dict): A dictionary containing the updated aircraft details. This should
                       include the aircraft's unique identifier and the fields to be updated.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft details in JSON format, including the updated fields.
        """

        url = "/kb_api/aircraft"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def delete_aircraft(self, aircraft_model_externalId, msn, debug=False):
        """
        DELETE: Delete a specific aircraft by its model external ID and MSN.
        
        Parameters:
        - aircraft_model_externalId (str): The unique external ID of the aircraft model.
        - msn (str): The manufacturer's serial number (MSN) of the aircraft to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The response of the delete operation in JSON format, confirming the deletion.
                If the aircraft is not found or the deletion fails, the response will include an error message.
        """

        url = f"/kb_api/aircraft/{aircraft_model_externalId}/{msn}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_aircraft(self, aircraft_model_externalId, msn, debug=False):
        """
        GET: Retrieve details of a specific aircraft by its model external ID and MSN.
        
        Parameters:
        - aircraft_model_externalId (str): The unique external ID of the aircraft model.
        - msn (str): The manufacturer's serial number (MSN) of the aircraft to fetch.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The aircraft data in JSON format, including all metadata and relevant fields.
                If the aircraft is not found, an appropriate error message will be returned.
        """

        url = f"/kb_api/aircraft/{aircraft_model_externalId}/{msn}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_all_assemblies_for_aircraft(self, aircraft_model_externalId, msn, debug=False):
        """
        GET: Retrieve all assemblies for a specific aircraft.
        
        Parameters:
        - aircraft_model_externalId (str): The unique external ID of the aircraft model.
        - msn (str): The manufacturer's serial number (MSN) of the aircraft for which assemblies are to be fetched.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of assemblies for the specific aircraft in JSON format. The response will include
                metadata about the assemblies.
        """

        url = f"/kb_api/aircraft/{aircraft_model_externalId}/{msn}/assemblies"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_all_aircraft(self, limit, offset, debug=False):
        """
        GET: Retrieve all aircraft in a paginated format.
        
        Parameters:
        - limit (int): The number of aircraft to return per page (pagination).
        - offset (int): The starting point for pagination (e.g., 0 for the first page).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A paginated list of aircraft in JSON format. The response will contain
                the list of aircraft and any pagination metadata (e.g., next page, total count).
        """

        url = f"/kb_api/all_aircraft/{limit}/{offset}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_part_type(self, externalId, debug=False):
        """
        GET: Retrieve details of a specific aircraft part type by its external ID.
        
        Parameters:
        - externalId (str): The unique external ID of the aircraft part type to fetch.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The aircraft part type data in JSON format, including all relevant fields.
                If the part type is not found, an appropriate error message will be returned.
        """

        url = f"/kb_api/aircraft_part_type/{externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_aircraft_part_types(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new aircraft part types in the system.
        
        Parameters:
        - data (dict): A dictionary containing the details of the aircraft part types to be created.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created aircraft part types in JSON format. The response will contain
                the details of the newly created part types, including their unique identifiers.
        """

        url = "/kb_api/aircraft_part_types"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_part_types(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing aircraft part types.
        
        Parameters:
        - data (dict): A dictionary containing the updated aircraft part types details. This should
                       include the part types' unique identifiers and the fields to be updated.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft part types details in JSON format, including the updated fields.
        """

        url = "/kb_api/aircraft_part_types"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_aircraft_models(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new aircraft models in the system.
        
        Parameters:
        - data (dict): A dictionary containing the details of the aircraft models to be created.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created aircraft models in JSON format. The response will contain
                the details of the newly created models, including their unique identifiers.
        """

        url = "/kb_api/aircraft_models"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_models(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing aircraft models.
        
        Parameters:
        - data (dict): A dictionary containing the updated aircraft model details. This should
                       include the models' unique identifiers and the fields to be updated.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft model details in JSON format, including the updated fields.
        """

        url = "/kb_api/aircraft_models"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def get_all_aircraft_models(self, limit, offset, debug=False):
        """
        GET: Retrieve all aircraft models in a paginated format.
        
        Parameters:
        - limit (int): The number of aircraft models to return per page (pagination).
        - offset (int): The starting point for pagination (e.g., 0 for the first page).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A paginated list of aircraft models in JSON format. The response will contain
                the list of models and any pagination metadata (e.g., next page, total count).
        """

        url = f"/kb_api/aircraft_models/{limit}/{offset}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_model(self, aircraft_model_externalId, debug=False):
        """
        GET: Retrieve details of a specific aircraft model by its external ID.
        
        Parameters:
        - aircraft_model_externalId (str): The unique external ID of the aircraft model to fetch.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The aircraft model data in JSON format, including all relevant fields.
                If the model is not found, an appropriate error message will be returned.
        """

        url = f"/kb_api/aircraft_model/{aircraft_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_engine_models(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new engine models in the system.
        
        Parameters:
        - data (dict): A dictionary containing the details of the engine models to be created.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created engine models in JSON format. The response will contain
                the details of the newly created models, including their unique identifiers.
        """

        url = "/kb_api/engine_models"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_models(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing engine models.
        
        Parameters:
        - data (dict): A dictionary containing the updated engine model details. This should
                       include the models' unique identifiers and the fields to be updated.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated engine model details in JSON format, including the updated fields.
        """

        url = "/kb_api/engine_models"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def get_engine_model(self, engine_model_externalId, debug=False):
        """
        GET: Retrieve details of a specific engine model by its external ID.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model to fetch.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The engine model data in JSON format, including all relevant fields.
                If the model is not found, an appropriate error message will be returned.
        """

        url = f"/kb_api/engine_model/{engine_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def add_optional_llps_to_engine_models(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Add optional LLPs (Life-Limited Parts) to engine models.
        
        Parameters:
        - data (dict): A dictionary containing the details of the optional LLPs to add to the engine models.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated engine models with the new LLPs added in JSON format.
        """

        url = "/kb_api_engine_models/add_optional_llps"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_model_llp_stack(self, engine_model_externalId, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update the LLP stack of a specific engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model to update.
        - data (dict): A dictionary containing the updated LLP stack details for the engine model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated LLP stack of the engine model in JSON format.
        """

        url = f"/kb_api/engine_model/{engine_model_externalId}/llp_stack"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_model_llp_stack_optionality(self, engine_model_externalId, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update the LLP stack optionality of a specific engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model to update.
        - data (dict): A dictionary containing the updated optionality details for the LLP stack.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated LLP stack optionality in JSON format.
        """

        url = f"/kb_api/engine_model/{engine_model_externalId}/llp_stack_optionality"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_model_llp_stack_scope(self, engine_model_externalId, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update the LLP stack scope of a specific engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model to update.
        - data (dict): A dictionary containing the updated scope of the LLP stack.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated LLP stack scope in JSON format.
        """

        url = f"/kb_api/engine_model/{engine_model_externalId}/llp_stack_scope"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_model_module_names(self, engine_model_externalId, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update the module names of a specific engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model to update.
        - data (dict): A dictionary containing the updated module names for the engine model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated engine model with the new module names in JSON format.
        """

        url = f"/kb_api/engine_model/{engine_model_externalId}/module_names"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def get_all_engine_models(self, limit, offset, debug=False):
        """
        GET: Retrieve all engine models in a paginated format.
        
        Parameters:
        - limit (int): The number of engine models to return per page (pagination).
        - offset (int): The starting point for pagination (e.g., 0 for the first page).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A paginated list of engine models in JSON format. The response will contain
                the list of engine models and any pagination metadata (e.g., next page, total count).
        """

        url = f"/kb_api/engine_models/{limit}/{offset}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_part_maintenance_policy_type(self, externalId, debug=False):
        """
        GET: Retrieve details of a specific aircraft part maintenance policy type by its external ID.
        
        Parameters:
        - externalId (str): The unique external ID of the aircraft part maintenance policy type to fetch.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The maintenance policy type data in JSON format, including all relevant fields.
                If the policy type is not found, an appropriate error message will be returned.
        """

        url = f"/kb_api/aircraft_part_maintenance_policy_type/{externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_part_maintenance_policy_types(self, aircraft_part_type_externalId, debug=False):
        """
        GET: Retrieve all maintenance policy types for a given aircraft part type.
        
        Parameters:
        - aircraft_part_type_externalId (str): The unique external ID of the aircraft part type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of maintenance policy types in JSON format, including the details of each policy type.
        """

        url = f"/kb_api/aircraft_part_maintenance_policy_types/{aircraft_part_type_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_aircraft_part_maintenance_policy_types(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new aircraft part maintenance policy types.
        
        Parameters:
        - data (dict): A dictionary containing the details of the maintenance policy types to be created.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created maintenance policy types in JSON format, including their unique identifiers.
        """

        url = "/kb_api/aircraft_part_maintenance_policy_types"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_part_maintenance_policy_types(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing aircraft part maintenance policy types.
        
        Parameters:
        - data (dict): A dictionary containing the updated maintenance policy types details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated maintenance policy types in JSON format, including the updated fields.
        """

        url = "/kb_api/aircraft_part_maintenance_policy_types"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def delete_aircraft_part_maintenance_policy_type(self, aircraft_part_maintenance_policy_type_externalId, debug=False):
        """
        DELETE: Delete a specific aircraft part maintenance policy type by its external ID.
        
        Parameters:
        - aircraft_part_maintenance_policy_type_externalId (str): The unique external ID of the policy type to delete.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The response of the delete operation in JSON format, confirming the deletion.
                If the policy type is not found or deletion fails, the response will include an error message.
        """

        url = f"/kb_api/aircraft_part_maintenance_policy_type/{aircraft_part_maintenance_policy_type_externalId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_template_lease_snapshot(self, lease_externalId, debug=False):
        """
        GET: Retrieve the template lease snapshot for a specific lease.
        
        Parameters:
        - lease_externalId (str): The unique external ID of the lease to fetch the template snapshot.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The lease snapshot in JSON format, containing metadata about the lease's
                terms, structure, and conditions as of the specified time.
        """

        url = f"/kb_api/lease_snapshot/template/{lease_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_aircraft_appraisals(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new aircraft appraisals in the system.
        
        Parameters:
        - data (dict): A dictionary containing the appraisal details for the aircraft.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created aircraft appraisal in JSON format. The response will include
                the appraisal details, its unique identifier, and relevant metadata.
        """

        url = "/kb_api/appraisals"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_appraisals(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing aircraft appraisals.
        
        Parameters:
        - data (dict): A dictionary containing the updated appraisal details for the aircraft.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft appraisal in JSON format, including the updated fields and metadata.
        """

        url = "/kb_api/appraisals"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_appraisers(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Add new appraisers to the system.
        
        Parameters:
        - data (dict): A dictionary containing the appraiser's details (e.g., name, credentials).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created appraiser information in JSON format, including their unique identifier.
        """

        url = "/kb_api/appraisers"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_appraisers(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update details of existing appraisers.
        
        Parameters:
        - data (dict): A dictionary containing the updated appraiser details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated appraiser details in JSON format, including the updated fields.
        """

        url = "/kb_api/appraisers"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_technical_snapshots(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new technical snapshots for an aircraft.
        
        Parameters:
        - data (dict): A dictionary containing the details of the technical snapshot (e.g., current technical status, configurations).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created technical snapshot in JSON format, including metadata and the snapshot's unique identifier.
        """

        url = "/kb_api/technical_snapshots"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_technical_snapshots(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing technical snapshots.
        
        Parameters:
        - data (dict): A dictionary containing the updated technical snapshot details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated technical snapshot in JSON format, including updated metadata.
        """

        url = "/kb_api/technical_snapshots"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_leases(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new lease records in the system.
        
        Parameters:
        - data (dict): A dictionary containing the lease details (e.g., lessee, term, conditions).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created lease in JSON format, including metadata and the unique lease identifier.
        """

        url = "/kb_api/leases"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_leases(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing lease records.
        
        Parameters:
        - data (dict): A dictionary containing the updated lease details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated lease in JSON format, including updated metadata and terms.
        """

        url = "/kb_api/leases"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_lease_snapshots(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create snapshots of lease records.
        
        Parameters:
        - data (dict): A dictionary containing the details of the lease to snapshot (e.g., terms, status at the time).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created lease snapshot in JSON format, including metadata.
        """

        url = "/kb_api/lease_snapshots"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_lease_snapshots(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing lease snapshots.
        
        Parameters:
        - data (dict): A dictionary containing the updated lease snapshot details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated lease snapshot in JSON format.
        """

        url = "/kb_api/lease_snapshots"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def get_aircraft_part_maintenance_policy(self, aircraft_part_type_externalId, aircraft_part_maintenance_policy_type_externalId, as_of, debug=False):
        """
        GET: Retrieve a specific maintenance policy for an aircraft part.
        
        Parameters:
        - aircraft_part_type_externalId (str): The unique external ID of the aircraft part type.
        - aircraft_part_maintenance_policy_type_externalId (str): The unique external ID of the maintenance policy type.
        - as_of (str): The timestamp or identifier for the specific policy snapshot.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The maintenance policy data in JSON format, including relevant terms and conditions.
        """

        url = f"/kb_api/aircraft_part_maintenance_policy/{aircraft_part_type_externalId}/{aircraft_part_maintenance_policy_type_externalId}/{as_of}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_part_maintenance_policies(self, aircraft_part_maintenance_policy_type_externalId, debug=False):
        """
        GET: Retrieve all maintenance policies for a specific aircraft part type.
        
        Parameters:
        - aircraft_part_maintenance_policy_type_externalId (str): The unique external ID of the maintenance policy type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of maintenance policies in JSON format, including their terms and relevant metadata.
        """

        url = f"/kb_api/aircraft_part_maintenance_policies/{aircraft_part_maintenance_policy_type_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_aircraft_part_maintenance_policies(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new maintenance policies for aircraft parts.
        
        Parameters:
        - data (dict): A dictionary containing the maintenance policy details (e.g., terms, conditions, applicability).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created maintenance policy in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/aircraft_part_maintenance_policies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_part_maintenance_policies(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing aircraft part maintenance policies.
        
        Parameters:
        - data (dict): A dictionary containing the updated policy details (e.g., terms, conditions).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated policy details in JSON format.
        """

        url = "/kb_api/aircraft_part_maintenance_policies"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_part_maintenance_policy_date(self, aircraft_part_type_externalId, aircraft_part_maintenance_policy_type_externalId, debug=False):
        """
        PUT: Update the effective date of a maintenance policy for an aircraft part.
        
        Parameters:
        - aircraft_part_type_externalId (str): The unique external ID of the aircraft part type.
        - aircraft_part_maintenance_policy_type_externalId (str): The unique external ID of the maintenance policy type.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated policy date in JSON format.
        """

        url = f"/kb_api/aircraft_part_maintenance_policy_date/{aircraft_part_type_externalId}/{aircraft_part_maintenance_policy_type_externalId}"

        return self.make_authenticated_request(self.config, url, method='PUT', debug=debug)

    def create_default_utilizations(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create default utilization values for aircraft or engine components.
        
        Parameters:

        - data (dict): A dictionary containing the details of the default utilizations (e.g., flight hours, cycles).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created default utilizations in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/default_utilizations"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_default_utilizations(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing default utilizations.
        
        Parameters:
        - data (dict): A dictionary containing the updated default utilization values.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated default utilizations in JSON format, including the updated metadata and values.
        """

        url = "/kb_api/default_utilizations"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_engine_pr_maintenance_policies(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new engine Performance Restoration (PR) maintenance policies.
        
        Parameters:
        - data (dict): A dictionary containing the PR maintenance policy details for engines.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created PR maintenance policy in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/engine_pr_maintenance_policies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_pr_maintenance_policies(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing engine Performance Restoration (PR) maintenance policies.
        
        Parameters:
        - data (dict): A dictionary containing the updated PR maintenance policy details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated PR maintenance policy in JSON format.
        """

        url = "/kb_api/engine_pr_maintenance_policies"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_pr_maintenance_policy_date(self, engine_model_externalId, debug=False):
        """
        PUT: Update the effective date of an engine PR maintenance policy.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated PR maintenance policy date in JSON format.
        """

        url = f"/kb_api/engine_pr_maintenance_policy_date/{engine_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='PUT', debug=debug)

    def get_engine_pr_maintenance_policy(self, engine_model_externalId, as_of, debug=False):
        """
        GET: Retrieve a specific PR maintenance policy for an engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model.
        - as_of (str): The timestamp or identifier for the policy snapshot to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The PR maintenance policy data in JSON format.
        """

        url = f"/kb_api/engine_pr_maintenance_policy/{engine_model_externalId}/{as_of}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_pr_maintenance_policies(self, engine_model_externalId, debug=False):
        """
        GET: Retrieve all PR maintenance policies for a specific engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of PR maintenance policies in JSON format, including relevant metadata and terms.
        """

        url = f"/kb_api/engine_pr_maintenance_policies/{engine_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_engine_llp_maintenance_policies(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new LLP (Life-Limited Parts) maintenance policies for engine models.
        
        Parameters:
        - data (dict): A dictionary containing the LLP maintenance policy details (e.g., replacement intervals).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created LLP maintenance policy in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/engine_llp_maintenance_policies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_llp_maintenance_policies(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing LLP (Life-Limited Parts) maintenance policies for engines.
        
        Parameters:
        - data (dict): A dictionary containing the updated LLP maintenance policy details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated LLP maintenance policy in JSON format.
        """

        url = "/kb_api/engine_llp_maintenance_policies"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_llp_maintenance_policy_date(self, engine_model_externalId, debug=False):
        """
        PUT: Update the effective date for an LLP maintenance policy on a specific engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated LLP maintenance policy date in JSON format.
        """

        url = f"/kb_api/engine_llp_maintenance_policy_date/{engine_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='PUT', debug=debug)

    def get_engine_llp_maintenance_policy(self, engine_model_externalId, as_of, debug=False):
        """
        GET: Retrieve a specific LLP maintenance policy for an engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model.
        - as_of (str): The timestamp or identifier for the policy snapshot to retrieve.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The LLP maintenance policy data in JSON format.
        """

        url = f"/kb_api/engine_llp_maintenance_policy/{engine_model_externalId}/{as_of}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_llp_maintenance_policies(self, engine_model_externalId, debug=False):
        """
        GET: Retrieve all LLP maintenance policies for a specific engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of LLP maintenance policies in JSON format, including relevant metadata and terms.
        """

        url = f"/kb_api/engine_llp_maintenance_policies/{engine_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_shop_visit_category_downtime(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new shop visit category downtime records for engines or aircraft components.
        
        Parameters:
        - data (dict): A dictionary containing the shop visit category downtime details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created shop visit category downtime in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/shop_visit_category_downtime"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_shop_visit_category_downtime(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing shop visit category downtime records.
        
        Parameters:
        - data (dict): A dictionary containing the updated shop visit category downtime details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated shop visit category downtime in JSON format.
        """

        url = "/kb_api/shop_visit_category_downtime"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_severity_defaults(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new severity defaults for maintenance or operational purposes.
        
        Parameters:
        - data (dict): A dictionary containing the severity default details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created severity defaults in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/severity_defaults"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_severity_defaults(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing severity defaults for maintenance or operational records.
        
        Parameters:
        - data (dict): A dictionary containing the updated severity default values.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated severity defaults in JSON format.
        """

        url = "/kb_api/severity_defaults"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_countries(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new country records in the system.
        
        Parameters:
        - data (dict): A dictionary containing the country details (e.g., name, code).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created country record in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/countries"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_countries(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing country records.
        
        Parameters:
        - data (dict): A dictionary containing the updated country details (e.g., name, code).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated country record in JSON format.
        """

        url = "/kb_api/countries"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_regions(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new region records in the system.
        
        Parameters:
        - data (dict): A dictionary containing the region details (e.g., name, code).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created region record in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/regions"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_regions(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing region records.
        
        Parameters:
        - data (dict): A dictionary containing the updated region details (e.g., name, code).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated region record in JSON format.
        """

        url = "/kb_api/regions"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_manufacturers(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new manufacturer records in the system.
        
        Parameters:
        - data (dict): A dictionary containing the manufacturer details (e.g., name, country, aircraft types produced).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created manufacturer record in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/manufacturers"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_manufacturers(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing manufacturer records.
        
        Parameters:
        - data (dict): A dictionary containing the updated manufacturer details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated manufacturer record in JSON format.
        """

        url = "/kb_api/manufacturers"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_companies(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new company records in the system.
        
        Parameters:
        - data (dict): A dictionary containing the company details (e.g., name, registration number, address).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created company record in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/companies"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_companies(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing company records.
        
        Parameters:
        - data (dict): A dictionary containing the updated company details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated company record in JSON format, including metadata.
        """

        url = "/kb_api/companies"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def get_contracted_lease(self, assembly_externalId, debug=False):
        """
        GET: Retrieve contracted lease information for a specific assembly.
        
        Parameters:
        - assembly_externalId (str): The unique external ID of the assembly to retrieve contracted lease information.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The contracted lease data in JSON format, including terms and conditions related to the assembly.
        """

        url = f"/kb_api/contracted_lease/{assembly_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_fee_structures(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new fee structures for leasing or maintenance agreements.
        
        Parameters:
        - data (dict): A dictionary containing the fee structure details (e.g., rates, terms).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created fee structure in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/fee_structure"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_fee_structures(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing fee structures for leasing or maintenance agreements.
        
        Parameters:
        - data (dict): A dictionary containing the updated fee structure details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated fee structure in JSON format, including updated terms and rates.
        """

        url = "/kb_api/fee_structure"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_build_standards(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new build standards for aircraft or engines.
        
        Parameters:
        - data (dict): A dictionary containing the build standard details (e.g., technical specifications).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created build standard in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/build_standards"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_build_standards(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing build standards.
        
        Parameters:
        - data (dict): A dictionary containing the updated build standard details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated build standard in JSON format.
        """

        url = "/kb_api/build_standards"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def add_actuals_payments_batch(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Add a batch of actuals payments for a specific client.
        
        Parameters:
        - data (dict): A dictionary containing details of the batch of actuals payments.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created actuals payments batch in JSON format, including metadata and the batch ID.
        """

        url = "/kb_api/actuals_payments/batch"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def delete_actuals_payments_batch(self, actuals_payments_batch_externalId, debug=False):
        """
        DELETE: Delete a batch of actuals payments using the batch external ID.
        
        Parameters:
        - actuals_payments_batch_externalId (str): The unique external ID of the batch to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The response of the delete operation in JSON format, confirming the deletion or providing error information.
        """

        url = f"/kb_api/actuals_payments/batch/{actuals_payments_batch_externalId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_actuals_payments(self, aircraft_model_externalId, msn, debug=False):
        """
        GET: Retrieve actuals payments for a specific aircraft model and serial number.
        
        Parameters:
        - aircraft_model_externalId (str): The unique external ID of the aircraft model.
        - msn (str): The manufacturer's serial number (MSN) of the aircraft.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The actuals payments data in JSON format, including payment details related to the aircraft.
        """

        url = f"/kb_api/actuals_payments/aircraft/{aircraft_model_externalId}/{msn}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_actuals_payment(self, paymentId, debug=False):
        """
        GET: Retrieve details of a specific actuals payment by its payment ID.
        
        Parameters:
        - paymentId (str): The unique ID of the actuals payment to fetch.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The actuals payment details in JSON format, including metadata and payment-specific information.
        """

        url = f"/kb_api/actuals_payments/{paymentId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def delete_actuals_payment(self, paymentId, debug=False):
        """
        DELETE: Delete a specific actuals payment using its payment ID.
        
        Parameters:
        - paymentId (str): The unique ID of the actuals payment to be deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The response of the delete operation in JSON format, confirming the deletion or providing error information.
        """

        url = f"/kb_api/actuals_payments/{paymentId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def update_actuals_payment(self, paymentId, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update a specific actuals payment using its payment ID.
        
        Parameters:
        - paymentId (str): The unique ID of the actuals payment to be updated.
        - data (dict): A dictionary containing the updated actuals payment details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated actuals payment in JSON format, including updated payment details and metadata.
        """

        url = f"/kb_api/actuals_payments/{paymentId}"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def create_maintenance_escalations(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new maintenance escalation records for engines or aircraft.
        
        Parameters:
        - data (dict): A dictionary containing the maintenance escalation details (e.g., escalated cost rates).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created maintenance escalation record in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/maintenance_escalations"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_maintenance_escalations(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing maintenance escalation records.
        
        Parameters:
        - data (dict): A dictionary containing the updated maintenance escalation details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated maintenance escalation record in JSON format.
        """

        url = "/kb_api/maintenance_escalations"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def get_engine_maintenance_escalations(self, debug=False):
        """
        GET: Retrieve all engine maintenance escalations.
        
        Parameters:
        - env (str): The environment where the API is hosted (e.g., 'preprod').
        - client (str): The client identifier for the API (e.g., 'api-api-preprod-amergin').
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of engine maintenance escalations in JSON format, including details like escalated cost rates, 
                applicable engine models, and relevant metadata.
        """

        url = "/kb_api/engine_maintenance_escalations"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_engine_maintenance_escalation(self, engine_model_externalId, debug=False):
        """
        GET: Retrieve details of a specific engine maintenance escalation by engine model.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model whose maintenance escalation is being fetched.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The maintenance escalation details for the specific engine model, in JSON format, including escalated rates, 
                applicable time periods, and any other relevant data.
        """

        url = f"/kb_api/engine_maintenance_escalation/{engine_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_engine_maintenance_escalations(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new engine maintenance escalation records for an engine model.
        
        Parameters:
        - data (dict): A dictionary containing the escalation details (e.g., cost escalation rates, applicable engine models).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created engine maintenance escalation record in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/engine_maintenance_escalations"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_engine_maintenance_escalations(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing engine maintenance escalation records.
        
        Parameters:
        - data (dict): A dictionary containing the updated escalation details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated engine maintenance escalation record in JSON format.
        """

        url = "/kb_api/engine_maintenance_escalations"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def delete_engine_maintenance_escalation(self, engine_model_externalId, debug=False):
        """
        DELETE: Delete a specific engine maintenance escalation by engine model external ID.
        
        Parameters:
        - engine_model_externalId (str): The unique external ID of the engine model whose maintenance escalation is being deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the escalation is not found.
        """

        url = f"/kb_api/engine_maintenance_escalation/{engine_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)

    def get_aircraft_maintenance_escalations(self, debug=False):
        """
        GET: Retrieve all aircraft maintenance escalations.
        
        Parameters:
        - env (str): The environment where the API is hosted (e.g., 'preprod').
        - client (str): The client identifier for the API (e.g., 'api-api-preprod-amergin').
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A list of aircraft maintenance escalations in JSON format, including details like escalated cost rates, 
                applicable aircraft models, and relevant metadata.
        """

        url = "/kb_api/aircraft_maintenance_escalations"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def get_aircraft_maintenance_escalation(self, aircraft_model_externalId, debug=False):
        """
        GET: Retrieve details of a specific aircraft maintenance escalation by aircraft model.
        
        Parameters:
        - aircraft_model_externalId (str): The unique external ID of the aircraft model whose maintenance escalation is being fetched.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The maintenance escalation details for the specific aircraft model, in JSON format, including escalated rates, 
                applicable time periods, and any other relevant data.
        """

        url = f"/kb_api/aircraft_maintenance_escalation/{aircraft_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='GET', debug=debug)

    def create_aircraft_maintenance_escalations(self, data, multiSend=False, sendSize=20, debug=False):
        """
        POST: Create new aircraft maintenance escalation records for an aircraft model.
        
        Parameters:
        - data (dict): A dictionary containing the escalation details (e.g., cost escalation rates, applicable aircraft models).
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The created aircraft maintenance escalation record in JSON format, including metadata and the unique identifier.
        """

        url = "/kb_api/aircraft_maintenance_escalations"

        return self.make_authenticated_request(self.config, url, method='POST', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def update_aircraft_maintenance_escalations(self, data, multiSend=False, sendSize=20, debug=False):
        """
        PUT: Update existing aircraft maintenance escalation records.
        
        Parameters:
        - data (dict): A dictionary containing the updated escalation details.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: The updated aircraft maintenance escalation record in JSON format.
        """

        url = "/kb_api/aircraft_maintenance_escalations"

        return self.make_authenticated_request(self.config, url, method='PUT', data=data, debug=debug, multiSend=multiSend, sendSize=sendSize)

    def delete_aircraft_maintenance_escalation(self, aircraft_model_externalId, debug=False):
        """
        DELETE: Delete a specific aircraft maintenance escalation by aircraft model external ID.
        
        Parameters:
        - aircraft_model_externalId (str): The unique external ID of the aircraft model whose maintenance escalation is being deleted.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Returns:
        - dict: A confirmation of the delete operation in JSON format, or an error message if the escalation is not found.
        """

        url = f"/kb_api/aircraft_maintenance_escalation/{aircraft_model_externalId}"

        return self.make_authenticated_request(self.config, url, method='DELETE', debug=debug)
