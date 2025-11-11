import pandas as pd
import time
import copy
from . import InternalAPIClient
from ..common import utils

class InternalUtilsClient(InternalAPIClient):
    def __init__(self,InternalAPI):
        """
        Initialize InternalUtils with a BaseAPI instance.
        """
        super().__init__(InternalAPI)  # Initialize the parent class (APIClient)

    def __dir__(self):
        # Dynamically filter out attributes from Parent
        parent_attrs = set(dir(InternalAPIClient))  # Get all attributes from Parent
        all_attrs = set(super().__dir__())  # Get all attributes inherited by Child
        child_specific_attrs = all_attrs - parent_attrs  # Exclude Parent attributes
        return sorted(child_specific_attrs)


    def fetch_all_assemblies(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=1000, debug=False):
        """
        Fetch all assemblies from the internal API using pagination with retries, backoff, and logging.

        Parameters:
        - batch_size (int): The number of assemblies to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 assemblies.

        Returns:
        - list: A list of all fetched assemblies.
        """
        all_assemblies = []
        assembly_indexer = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Assembly Extract')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch assemblies using the internal API
                response = self.get_all_assemblies(batch_size, assembly_indexer, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_assemblies.extend(response['items'])
                    assembly_indexer += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval assemblies
                    if int(total_count / log_interval) > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} assemblies so far...")

                else:
                    # Stop if no items are returned in the current batch, regardless of batch size
                    print(f"Received empty or invalid response at index {assembly_indexer}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                else:
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} assemblies.")
        return all_assemblies

    def fetch_all_aircraft(self, batch_size=200, max_retries=5, backoff_factor=2, log_interval=1000, debug=False):
        """
        Fetch all aircraft from the internal API using pagination with retries, backoff, and logging.

        Parameters:
        - batch_size (int): The number of aircraft to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 aircraft.

        Returns:
        - list: A list of all fetched aircraft.
        """
        all_aircraft = []
        aircraft_indexer = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0

        print('Starting Aircraft Extract')

        # Adjust log_interval if batch_size is larger than log_interval
        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch aircraft using the internal API
                response = self.get_all_aircraft(batch_size, aircraft_indexer, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_aircraft.extend(response['items'])
                    aircraft_indexer += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval aircraft
                    if int(total_count / log_interval) > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} aircraft so far...")

                else:
                    # Stop if no items are returned in the current batch, regardless of batch size
                    print(f"Received empty or invalid response at index {aircraft_indexer}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                else:
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} aircraft.")
        return all_aircraft

    def fetch_all_engine_models(self, batch_size=20, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all engine models from the internal API using pagination with retries, backoff, and logging.

        Parameters:
        - env (str): Client environment (e.g., 'preprod').
        - client (str): The client identifier.
        - batch_size (int): The number of engine models to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 engine models.

        Returns:
        - list: A list of all fetched engine models.
        """
        all_engine_models = []
        engine_model_indexer = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0

        print('Starting Engine Models Extract')

        # Adjust log_interval if batch_size is larger than log_interval
        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch engine models using the internal API
                response = self.get_all_engine_models(batch_size, engine_model_indexer, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_engine_models.extend(response['items'])
                    engine_model_indexer += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval engine models
                    if int(total_count / log_interval) > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} engine models so far...")

                else:
                    # Stop if no items are returned in the current batch, regardless of batch size
                    print(f"Received empty or invalid response at index {engine_model_indexer}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                else:
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} engine models.")
        return all_engine_models

    def fetch_all_aircraft_models(self, batch_size=20, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all aircraft models from the internal API using pagination with retries, backoff, and logging.

        Parameters:
        - env (str): Client environment (e.g., 'preprod').
        - client (str): The client identifier.
        - batch_size (int): The number of aircraft models to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 aircraft models.

        Returns:
        - list: A list of all fetched aircraft models.
        """
        all_aircraft_models = []
        aircraft_model_indexer = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0

        print('Starting Aircraft Models Extract')

        # Adjust log_interval if batch_size is larger than log_interval
        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch aircraft models using the internal API
                response = self.get_all_aircraft_models(batch_size, aircraft_model_indexer, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_aircraft_models.extend(response['items'])
                    aircraft_model_indexer += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval aircraft models
                    if int(total_count / log_interval) > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} aircraft models so far...")

                else:
                    # Stop if no items are returned in the current batch, regardless of batch size
                    print(f"Received empty or invalid response at index {aircraft_model_indexer}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                else:
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} aircraft models.")
        return all_aircraft_models

    def fetch_all_engine_pr_maintenance_policies(self, engine_model_externalId, debug=False):
        """
        Fetch all PR maintenance policies for a specific engine model, and retrieve detailed 
        information for each policy using the engine model external ID.

        Parameters:
        - env (str): The environment where the API is hosted.
        - client (str): The client identifier for the API.
        - engine_model_externalId (str): The unique external ID of the engine model.
        
        Returns:
        - list: A list of detailed PR maintenance policies in JSON format.
        """
        all_policies = []

        try:
            # Fetch all PR maintenance policies for the engine model
            response = self.get_engine_pr_maintenance_policies(engine_model_externalId, debug=debug)

            if response and 'items' in response:
                # Iterate through the policies and fetch detailed information for each
                for policy in response['items']:
                    as_of = policy.get('asOf')  # Assuming 'as_of' is in the policy data
                    if as_of:
                        detailed_policy = self.get_engine_pr_maintenance_policy(engine_model_externalId, as_of.get('date'), debug=debug)
                        all_policies.extend(detailed_policy['items'])
                    else:
                        print(f"No policies found for engine model {engine_model_externalId}")
            else:
                print(f"No policies found for engine model {engine_model_externalId}")

        except Exception as e:
            print(f"Error fetching PR maintenance policies: {str(e)}")

        return all_policies

    def de_escalate_engine_pr_maintenance_policies(self, all_pr_policies_defined, deescalation_percentage, target_year, take_dates=False):
        """
        De-escalate the prIntervals values for each module in the supplied policies, strictly not overriding existing years, but filling the gaps with predefined deescalation from the maximum year.
        
        Parameters:
        - policy (dict): The policy data containing modules with intervals and costs.
        - deescalation_percentage (float): The percentage to de-escalate the prIntervals (e.g., 0.05 for 5%).
        - target_year (int): The year to begin de-escalation from. If this year doesn't exist in prIntervals,
                             the maximum year will be used.
        - take_dates (Bool): Optional, default = False. Take the day and month of the mak policy as the standard for all years going back
                             e.g., 2023-08-01 will be applied back 2019-08-01 if take_dates = True. If False, takes xxxx-01-01.
        
        Returns:
        - dict: The policy with de-escalated intervals.
        """

        max_policy_date = max([pd.to_datetime(i['asOf']['date']) for i in all_pr_policies_defined])
        base_policy = [i for i in all_pr_policies_defined if i['asOf']['date'] == max_policy_date.strftime('%Y-%m-%d')][0]
        all_policy_years = [pd.to_datetime(i['asOf']['date']).year for i in all_pr_policies_defined]

        years_in_between = list(range(max_policy_date.year, pd.to_datetime(str(target_year)).year - 1, -1))
        years_required = sorted(set(years_in_between) - set(all_policy_years), reverse=True)

        new_policies = []

        for year in years_required:
            new_policy = copy.deepcopy(base_policy)
            power = (1 + deescalation_percentage) ** int(max_policy_date.year - year)
            if take_dates:
                new_policy['asOf']['date'] = pd.to_datetime(f'{year}-{max_policy_date.month}-{max_policy_date.day}').strftime('%Y-%d-%m')
            else:
                new_policy['asOf']['date'] = f'{year}-01-01'

            for module in new_policy['modules']:
                for interval_cost in ['firstRunCostUsd', 'subsequentRunCostUsd']:
                    module_cost = module[interval_cost]
                    deescalated_module_cost = module_cost / power
                    module[interval_cost] = int(deescalated_module_cost)

            new_policies.append(new_policy)

        return new_policies

    def de_escalate_all_engine_pr_maintenance_policies(self, deescalation_percentage, target_year, take_dates=False, debug=False, cut_off=None):
        """
        De-escalate PR maintenance policies for all engine models, applying a percentage-based de-escalation of interval costs
        for each module in the supplied PR maintenance policies.
        
        Parameters:
        - env (str): The environment where the internal API is hosted (e.g., 'preprod').
        - client (str): The client identifier for the internal API.
        - deescalation_percentage (float): The percentage by which to de-escalate the prIntervals for each engine model's PR maintenance policy.
                                            For example, 0.05 for 5% de-escalation.
        - target_year (int): The target year from which to begin de-escalation. If this year doesn't exist in prIntervals,
                             the latest year will be used as the reference.
        - take_dates (bool): Optional. Default is False. If True, retain the month and day from the base policy's date while de-escalating.
                             If False, set the date to January 1st of each year.
                             
        Returns:
        - list: A list of all engine PR maintenance policies with de-escalated intervals, including policies for each engine model.
        """

        engine_models = self.fetch_all_engine_models(debug=debug)

        de_escalated_policies = []

        for engine_model in engine_models[:cut_off]:
            engine_model_externalId = engine_model['externalId']

            engine_pr_policies = self.fetch_all_engine_pr_maintenance_policies(engine_model_externalId, debug=debug)

            de_escalated_pr_policies = self.de_escalate_engine_pr_maintenance_policies(
                engine_pr_policies,
                deescalation_percentage,
                target_year,
                take_dates
            )

            de_escalated_policies.extend(de_escalated_pr_policies)

        return de_escalated_policies

    

    def fetch_all_engine_llp_maintenance_policies(self, engine_model_externalId, debug=False):
        """
        Fetch all LLP maintenance policies for a specific engine model, and retrieve detailed
        information for each policy using the engine model external ID.

        Parameters:
        - env (str): The environment where the API is hosted.
        - client (str): The client identifier for the API.
        - engine_model_externalId (str): The unique external ID of the engine model.

        Returns:
        - list: A list of detailed LLP maintenance policies in JSON format.
        """
        all_policies = []

        try:
            # Fetch all LLP maintenance policies for the engine model
            response = self.get_engine_llp_maintenance_policies(engine_model_externalId, debug=debug)

            if response and 'items' in response:
                # Iterate through the policies and fetch detailed information for each
                for policy in response['items']:
                    as_of = policy.get('asOf')  # Assuming 'as_of' is in the policy data
                    if as_of:
                        detailed_policy = self.get_engine_llp_maintenance_policy(engine_model_externalId, as_of.get('date'), debug=debug)
                        all_policies.extend(detailed_policy['items'])
                    else:
                        print(f"No policies found for engine model {engine_model_externalId}")
            else:
                print(f"No policies found for engine model {engine_model_externalId}")

        except Exception as e:
            print(f"Error fetching LLP maintenance policies: {str(e)}")

        return all_policies

    def de_escalate_engine_llp_maintenance_policies(self, all_llp_policies_defined, deescalation_percentage, target_year, take_dates=False):
        """
        De-escalate the LLP maintenance costs for each module in the supplied policies, strictly not overriding existing years, 
        but filling the gaps with predefined deescalation from the maximum year.
        
        Parameters:
        - policy (dict): The policy data containing modules with LLP intervals and costs.
        - deescalation_percentage (float): The percentage to de-escalate the maintenance intervals (e.g., 0.05 for 5%).
        - target_year (int): The year to begin de-escalation from. If this year doesn't exist in the intervals,
                             the maximum year will be used.
        - take_dates (Bool): Optional, default = False. Take the day and month of the max policy as the standard for all years going back.
        
        Returns:
        - dict: The policy with de-escalated intervals.
        """

        max_policy_date = max([pd.to_datetime(i['asOf']['date']) for i in all_llp_policies_defined])
        base_policy = [i for i in all_llp_policies_defined if i['asOf']['date'] == max_policy_date.strftime('%Y-%m-%d')][0]
        all_policy_years = [pd.to_datetime(i['asOf']['date']).year for i in all_llp_policies_defined]

        years_in_between = list(range(max_policy_date.year, pd.to_datetime(str(target_year)).year - 1, -1))
        years_required = sorted(set(years_in_between) - set(all_policy_years), reverse=True)

        new_policies = []

        for year in years_required:
            new_policy = copy.deepcopy(base_policy)
            power = (1 + deescalation_percentage) ** int(max_policy_date.year - year)
            if take_dates:
                new_policy['asOf']['date'] = pd.to_datetime(f'{year}-{max_policy_date.month}-{max_policy_date.day}').strftime('%Y-%d-%m')
            else:
                new_policy['asOf']['date'] = f'{year}-01-01'

            # for module in new_policy['modules']:
            #     for interval_cost in ['firstRunCostUsd', 'subsequentRunCostUsd']:
            #         module_cost = module[interval_cost]
            #         deescalated_module_cost = module_cost / power
            #         module[interval_cost] = int(deescalated_module_cost)

            for module in new_policy['modules']:
                for interval_cost in module['llpPolicies']:
                    module_cost = interval_cost['replacementCostUsd']
                    deescalated_module_cost = module_cost / power
                    interval_cost['replacementCostUsd'] = int(deescalated_module_cost)

            new_policies.append(new_policy)

        return new_policies

    def de_escalate_all_engine_llp_maintenance_policies(self, deescalation_percentage, target_year, take_dates=False, debug=False, cut_off=None):
        """
        De-escalate LLP maintenance policies for all engine models, applying a percentage-based de-escalation of interval costs
        for each module in the supplied LLP maintenance policies.
        
        Parameters:
        - env (str): The environment where the internal API is hosted.
        - client (str): The client identifier for the internal API.
        - deescalation_percentage (float): The percentage by which to de-escalate the LLP intervals for each engine model's policy.
                                            For example, 0.05 for 5% de-escalation.
        - target_year (int): The target year from which to begin de-escalation. If this year doesn't exist in intervals,
                             the latest year will be used as the reference.
        - take_dates (bool): Optional. Default is False. If True, retain the month and day from the base policy's date while de-escalating.
                             If False, set the date to January 1st of each year.

        Returns:
        - list: A list of all engine LLP maintenance policies with de-escalated intervals, including policies for each engine model.
        """

        # Fetch all engine models
        engine_models = self.fetch_all_engine_models(debug=debug)

        # List to hold all de-escalated LLP maintenance policies
        de_escalated_policies = []

        for engine_model in engine_models[:cut_off]:
            engine_model_externalId = engine_model['externalId']

            # Fetch LLP maintenance policies for the current engine model
            engine_llp_policies = self.fetch_all_engine_llp_maintenance_policies(engine_model_externalId, debug=debug)

            # De-escalate the LLP maintenance policies
            de_escalated_llp_policies = self.de_escalate_engine_llp_maintenance_policies(
                engine_llp_policies,
                deescalation_percentage,
                target_year,
                take_dates
            )

            # Add de-escalated policies to the list
            de_escalated_policies.extend(de_escalated_llp_policies)

        return de_escalated_policies
        

    def update_engine_models_for_optional_llps(self, engine_models, llps_to_add, id_format=True, low_scope=False, debug=False):
        """
        Updates specified engine models by adding optional LLPs (Life-Limited Parts) based on given criteria.

        Parameters:
        - env: The environment in which the update is being performed (e.g., development, production).
        - client: The client or database instance required for connecting to the API.
        - engine_models (list): A list of engine model identifiers to be updated.
        - llps_to_add (dict): A dictionary where keys are LLP names and values are corresponding module types to match 
          in each engine model.
        - id_format (bool): If True, formats the LLP identifier before use. Defaults to True.
        - low_scope (bool): Indicates if the added LLPs should be marked with low scope. Defaults to False.

        Returns:
        - None

        Raises:
        - Prints error messages if specific modules cannot be found within the engine model.
        
        Example:
        update_engine_models_for_optional_llps('dev', api_client, ['engine_model1'], {'LLP1': 'moduleTypeA','LLP2': 'moduleTypeB'}, id_format=True)

        Notes:
        - If 'id_format' is True, the function applies formatting to LLP identifiers via a utility function.
        - This function uses an internal API to handle data retrieval and updating.
        """
        errors = {}
        for engine_model in engine_models:
            print(engine_model)
            engine_model_og = self.get_engine_model(engine_model, debug=debug)

            if 'error' in engine_model_og:
                print(engine_model_og)
                continue

            modules = [x['moduleTypeId'] for x in engine_model_og['items'][0]['engineModuleTypes']]
            for llp in llps_to_add:
                if llps_to_add[llp] not in modules:
                    print(f"Error: Can't find module {llps_to_add[llp]} in {engine_model}")
                    continue
                else:
                    module_idx = modules.index(llps_to_add[llp])
                    engine_external_id = llp

                    if id_format:
                        engine_external_id = utils.format_id(llp)

                    llp_object = {
                        "llpTypeId": engine_external_id,
                        "name": llp,
                        "position": engine_model_og['items'][0]['engineModuleTypes'][module_idx]['engineLlpTypes'][-1]['position'] + 1,
                        "isOptional": True,
                        "lowScope": low_scope,
                    }

                    engine_model_og['items'][0]['engineModuleTypes'][module_idx]['engineLlpTypes'].append(llp_object)
            # engine_model_og=json.dumps(engine_model_og)

            add_llp = self.add_optional_llps_to_engine_models(data=engine_model_og, debug=debug)
            if 'result' in add_llp:
                print(add_llp)

            else:
                print(add_llp)
                if engine_model not in errors:
                    errors.update({engine_model: [add_llp]})
                else:
                    errors[engine_model].append(add_llp)

    def fetch_all_part_type_dependencies(self, part_types_ids, debug=False):
        """
        Fetches all part type dependencies, including part types, maintenance policy types, 
        and maintenance policies, for a given list of part type IDs. The function utilizes 
        several internal API calls to retrieve data and handle potential errors.

        Parameters:
        - env: The environment in which the API is being called (e.g., development, production).
        - client: The client or session object used for making API calls.
        - part_types_ids (list): A list of part type IDs for which dependencies need to be fetched.
        - include_part_types (bool): Flag to include part types in the results. Defaults to True.
        - include_policy_types (bool): Flag to include maintenance policy types in the results. Defaults to True.
        - include_policies (bool): Flag to include maintenance policies in the results. Defaults to True.

        Returns:
        - part_types (list): A list of part types retrieved from the API.
        - aircraft_part_maintenance_policy_types (list): A list of maintenance policy types for the given part types.
        - aircraft_part_maintenance_policies (list): A list of maintenance policies associated with the part types

        Notes:
        - Handles error responses from the API by printing error messages to the console.
        - If a particular part type, policy type, or policy is missing, it continues processing other items.



        """
        # Initialize result lists for part types, policy types, and policies.
        part_types = []
        aircraft_part_maintenance_policy_types = []
        aircraft_part_maintenance_policies = []

        # Loop through each part type ID provided.
        for part_types_id in part_types_ids[:]:

            # Fetch the part type details using the internal API.
            response = self.get_aircraft_part_type(part_types_id, debug=debug)
            if 'items' in response:
                # Append the retrieved part type items to the list.
                part_types.extend(response['items'])
            else:
                # Log an error message if the API call fails.
                print('error: {}'.format(part_types_id), response)

            # Fetch the maintenance policy types associated with the part type.
            response = self.get_aircraft_part_maintenance_policy_types(part_types_id, debug=debug)
            if 'items' in response:
                # Process each policy type retrieved from the API.
                for policy_type in response['items']:
                    # Fetch detailed information about each maintenance policy type.
                    response = self.get_aircraft_part_maintenance_policy_type(policy_type, debug=debug)
                    if 'items' in response:
                        # Append the policy type items to the result list.
                        aircraft_part_maintenance_policy_types.extend(response['items'])
                    else:
                        # Log an error message if fetching the policy type fails.
                        print('policy type error: {}'.format(policy_type), response)

                    # Fetch maintenance policies associated with the current policy type.
                    response = self.get_aircraft_part_maintenance_policies(policy_type, debug=debug)
                    if 'items' in response:
                        for policy in response['items']:
                            # Extract the 'asOf' date to fetch the policy details.
                            policy_asOf = policy['asOf']['date']
                            response = self.get_aircraft_part_maintenance_policy(part_types_id, policy_type, policy_asOf, debug=debug)

                            if 'items' in response:
                                # Append the retrieved policy items to the result list.
                                aircraft_part_maintenance_policies.extend(response['items'])
                            else:
                                # Log an error message if fetching the policy fails.
                                print('policy error: {}'.format(policy), response)
                    else:
                        # Log an error message if fetching policies fails.
                        print('policies error: {}'.format(policy_type), response)
            else:
                # Log an error message if fetching policy types fails.
                print('error: {}'.format(part_types_id), response)

        # Return the collected part types, policy types, and policies.
        return part_types, aircraft_part_maintenance_policy_types, aircraft_part_maintenance_policies
