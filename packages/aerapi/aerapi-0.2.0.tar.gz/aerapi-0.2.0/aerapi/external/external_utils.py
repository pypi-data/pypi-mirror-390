import requests
import json
import pandas as pd
import time
import logging
from pathlib import Path
import copy
from deepdiff import DeepDiff #REPLACE THIS
import copy
import json
from . import ExternalAPIClient
from ..common import *

class ExternalUtilsClient(ExternalAPIClient):
    def __init__(self, ExternalAPI):
        """
        Initialize InternalUtils with a BaseAPI instance.
        """
        super().__init__(ExternalAPI)  # Initialize the parent class (APIClient)

    def __dir__(self):
        # Dynamically filter out attributes from Parent
        parent_attrs = set(dir(ExternalAPIClient))  # Get all attributes from Parent
        all_attrs = set(super().__dir__())  # Get all attributes inherited by Child
        child_specific_attrs = all_attrs - parent_attrs  # Exclude Parent attributes
        return sorted(child_specific_attrs)

    def fetch_all_assemblies(self, aircraftId=None, batch_size=100, max_retries=5, backoff_factor=2, log_interval=1000, debug=False):
        """
        Fetch all assemblies from the external API using pagination with retries, backoff, and logging.

        Parameters:
        - aircraftId (str, optional): Optional aircraft ID to filter assemblies by a specific aircraft.
        - batch_size (int): The number of assemblies to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 assemblies.

        Returns:
        - list: A list of all fetched assemblies.
        """
        all_assemblies = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Assembly Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch assemblies using the external API
                response = self.get_assemblies(aircraftId=aircraftId, limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_assemblies.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval assemblies
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} assemblies so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} assemblies.")
        return all_assemblies

    

    def fetch_all_engines(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=5000, debug=False):
        """
        Fetch all engines from the external API using pagination with retries, backoff, and logging.

        Parameters:
        - batch_size (int): The number of engines to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 engines.

        Returns:
        - list: A list of all fetched engines.
        """

        all_engines = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Engine Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch engines using the external API
                response = self.get_engine_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_engines.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval engines
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} engines so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} engines.")
        return all_engines

    def fetch_all_aircraft_details(self, batch_size=200, max_retries=5, backoff_factor=2, log_interval=100, debug=False):
        """
        Fetch all aircraft details from the external API using pagination with retries, backoff, and logging.

        Parameters:
        - batch_size (int): The number of aircraft details to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 aircraft details.

        Returns:
        - list: A list of all fetched aircraft details.
        """
        all_aircraft_details = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Aircraft Details Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch aircraft details using the external API
                response = self.search_aircraft(limit=batch_size, offset=offset, debug=debug)
                # Check if we have valid items in the response
                if response and  response['items']:
                    all_aircraft_details.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval aircraft details
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} aircraft details so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                # Exponential backoff before retrying
                wait_time = backoff_factor ** retry_count
                print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} aircraft details.")
        return all_aircraft_details

    def fetch_all_aircraft_appraisals(self, aircraftId=None, batch_size=100, max_retries=5, backoff_factor=2, log_interval=500, debug=False):
        """
        Fetch all aircraft part maintenance appraisals from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - aircraftId (str, optional): Optional aircraft ID to filter appraisals.
        - batch_size (int): The number of appraisals to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 appraisals.

        Returns:
        - list: A list of all fetched appraisals.
        """
        all_appraisals = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Aircraft Maintenance appraisal Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch appraisals using the external API
                response = self.get_aircraft_appraisal_list(limit=batch_size, offset=offset, aircraftId=aircraftId, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:

                    # print(response['items'])
                    
                    all_appraisals.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval appraisals
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} appraisals so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
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

        print(f"Finished fetching a total of {total_count} appraisals.")
        return all_appraisals


    def fetch_all_aircraft_part_maintenance_policy_types(self, aircraftPartTypeId=None, batch_size=20, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all aircraft part maintenance policy types from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - aircraftPartTypeId (str, optional): Optional aircraft part type ID to filter policy types.
        - batch_size (int): The number of policy types to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 policy types.

        Returns:
        - list: A list of all fetched policy types.
        """
        all_policy_types = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Aircraft Part Maintenance Policy Type Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch policy types using the external API
                response = self.get_all_aircraft_part_maintenance_policy_types(limit=batch_size, offset=offset, aircraftPartTypeId=aircraftPartTypeId, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_policy_types.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval policy types
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} policy types so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
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

        print(f"Finished fetching a total of {total_count} policy types.")
        return all_policy_types

    def fetch_all_aircraft_part_maintenance_policies(self, batch_size=200, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all aircraft part maintenance policies from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of policy types to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 policy types.

        Returns:
        - list: A list of all fetched policies.
        """
        all_policies = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Aircraft Part Maintenance Policies Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch policies using the external API
                response = self.get_aircraft_part_maintenance_policies(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_policies.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval policy types
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} policies so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
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

        print(f"Finished fetching a total of {total_count} policies.")
        return all_policies

    def fetch_all_companies(self, filter=None, batch_size=200, max_retries=5, backoff_factor=2, log_interval=1000, debug=False):
        """
        Fetch all companies from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - filter (str, optional): A filter string based on company roles.
        - batch_size (int): The number of companies to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 companies.

        Returns:
        - list: A list of all fetched companies.
        """
        all_companies = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Companies Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch companies using the external API
                response = self.get_all_companies(limit=batch_size, offset=offset, filter=filter, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_companies.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval companies
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} companies so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
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

        print(f"Finished fetching a total of {total_count} companies.")
        return all_companies

    def fetch_all_sovereign_ratings(self, debug=False):
        """
        Fetch all sovereign_ratings from the external API using pagination with retries, backoff, and logging.
        
        Returns:
        - list: A list of all fetched sovereign_ratings.
        """
        all_sovereign_ratings = {}
        no_rating = []
        count = 0
    
        all_countries = self.fetch_all_countries()
    
        for country in all_countries:
            response = self.get_sovereign_ratings(countryId = country['id'],debug=debug)
            if response['totalItemCount'] !=0:
                all_sovereign_ratings[country['name']] = response['items']
                count+=1
                if count%10==0:
                    print(f"{count} Countries Ratings Obtained")
            else:
                no_rating.append(country['name'])
    
    
        print(f"\nFinished fetching sovereign ratings for {len(all_sovereign_ratings)} countries.")
        print(f"\nThe following countries have no sovereign ratings:\n{no_rating}")

        return all_sovereign_ratings

    def fetch_all_ihi_ratings(self, countryId=None, ratingAgencyId=None, batch_size=20, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all ihi_ratings from the external API using pagination with retries, backoff, and logging.
        
        Parameters:
        
        - filter (str, optional): A filter string based on ihi_rating roles.
        - batch_size (int): The number of ihi_ratings to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 ihi_ratings.
        
        Returns:
        - list: A list of all fetched ihi_ratings.
        """
        all_ihi_ratings = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting ihi_rating Extract from External API')
        
        if batch_size > log_interval:
            log_interval = batch_size
        
        while run:
            try:
                # Fetch ihi_ratings using the external API
                response = self.get_all_ihi_ratings(limit=batch_size, offset=offset, countryId=countryId, ratingAgencyId=ratingAgencyId, debug=debug)
        
                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_ihi_ratings.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])
        
                    # Log progress after every log_interval ihi_ratings
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} ihi_ratings so far...")
        
                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False
        
                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
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
    
        print(f"Finished fetching a total of {total_count} ihi_ratings.")
        return all_ihi_ratings

    def fetch_all_wari_ratings(self, countryId=None, ratingAgencyId=None, batch_size=20, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all wari_ratings from the external API using pagination with retries, backoff, and logging.
        
        Parameters:
        
        - filter (str, optional): A filter string based on wari_rating roles.
        - batch_size (int): The number of wari_ratings to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 wari_ratings.
        
        Returns:
        - list: A list of all fetched wari_ratings.
        """
        all_wari_ratings = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting wari_rating Extract from External API')
        
        if batch_size > log_interval:
            log_interval = batch_size
        
        while run:
            try:
                # Fetch wari_ratings using the external API
                response = self.get_all_wari_ratings(limit=batch_size, offset=offset, countryId=countryId, ratingAgencyId=ratingAgencyId, debug=debug)
        
                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_wari_ratings.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])
        
                    # Log progress after every log_interval wari_ratings
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} wari_ratings so far...")
        
                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False
        
                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
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
    
        print(f"Finished fetching a total of {total_count} wari_ratings.")
        return all_wari_ratings

    def fetch_all_gari_ratings(self, countryId=None, ratingAgencyId=None, batch_size=20, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all gari_ratings from the external API using pagination with retries, backoff, and logging.
        
        Parameters:
        
        - filter (str, optional): A filter string based on gari_rating roles.
        - batch_size (int): The number of gari_ratings to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 gari_ratings.
        
        Returns:
        - list: A list of all fetched gari_ratings.
        """
        all_gari_ratings = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting gari_rating Extract from External API')
        
        if batch_size > log_interval:
            log_interval = batch_size
        
        while run:
            try:
                # Fetch gari_ratings using the external API
                response = self.get_all_gari_ratings(limit=batch_size, offset=offset, countryId=countryId, ratingAgencyId=ratingAgencyId, debug=debug)
        
                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_gari_ratings.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])
        
                    # Log progress after every log_interval gari_ratings
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} gari_ratings so far...")
        
                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False
        
                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
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
    
        print(f"Finished fetching a total of {total_count} gari_ratings.")
        return all_gari_ratings

    def fetch_all_operating_severity_defaults(self, filter=None, batch_size=200, max_retries=5, backoff_factor=2, log_interval=1000, debug=False):
        """
        Fetch all operating_severity_defaults from the external API using pagination with retries, backoff, and logging.
        
        Parameters:
        
        - filter (str, optional): A filter string based on operating_severity_default roles.
        - batch_size (int): The number of operating_severity_defaults to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 operating_severity_defaults.
        
        Returns:
        - list: A list of all fetched operating_severity_defaults.
        """
        all_operating_severity_defaults = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Severity Defaults Extract from External API')
        
        if batch_size > log_interval:
            log_interval = batch_size
        
        while run:
            try:
                # Fetch operating_severity_defaults using the external API
                response = self.get_all_operating_severity_defaults(limit=batch_size, offset=offset, query=filter, debug=debug)
        
                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_operating_severity_defaults.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])
        
                    # Log progress after every log_interval operating_severity_defaults
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} operating_severity_defaults so far...")
        
                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False
        
                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
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
    
        print(f"Finished fetching a total of {total_count} operating_severity_defaults.")
        return all_operating_severity_defaults

    def fetch_all_balance_sheets_per_company(self, companyId, batch_size=20, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all balance sheets for a specific company from the external API using pagination, with retries,
        backoff, and logging.

        Parameters:

        - companyId (str): UUID of the company for which balance sheets are fetched.
        - batch_size (int): The number of balance sheets to fetch per request. Default is 20.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 100 sheets.

        Returns:
        - list: A list of all fetched balance sheets.
        """
        all_balance_sheets = []
        offset = 0
        total_count = 0
        retry_count = 0
        log_count = 0
        run = True
        print(f"Starting Balance Sheets Extract for Company {companyId} from External API")

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch balance sheets for the specified company
                response = self.get_balance_sheet_list_per_company(
                    companyId, limit=batch_size, offset=offset, debug=debug
                )

                # Validate response
                if response and 'items' in response and response['items']:
                    all_balance_sheets.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress at intervals
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} balance sheets so far...")

                    # Stop loop if fewer items than batch_size are returned
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print("Max retries reached. Stopping the fetch.")
                    break
                else:
                    # Exponential backoff
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} balance sheets for Company {companyId}.")
        return all_balance_sheets

    def fetch_all_income_statements_per_company(self, companyId, batch_size=20, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all income statements for a specific company from the external API using pagination, with retries,
        backoff, and logging.

        Parameters:

        - companyId (str): UUID of the company for which income statements are fetched.
        - batch_size (int): The number of income statements to fetch per request. Default is 20.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 100 statements.

        Returns:
        - list: A list of all fetched income statements.
        """
        all_income_statements = []
        offset = 0
        total_count = 0
        retry_count = 0
        log_count = 0
        run = True
        print(f"Starting Income Statements Extract for Company {companyId} from External API")

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch income statements for the specified company
                response = self.get_income_statement_list_per_company(
                    companyId, limit=batch_size, offset=offset, debug=debug
                )

                # Validate response
                if response and 'items' in response and response['items']:
                    all_income_statements.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress at intervals
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} income statements so far...")

                    # Stop loop if fewer items than batch_size are returned
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print("Max retries reached. Stopping the fetch.")
                    break
                else:
                    # Exponential backoff
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} income statements for Company {companyId}.")
        return all_income_statements

    def fetch_all_engine_models(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=100, debug=False):
        """
        Fetch all engine models from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of engine models to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 100 engine models.

        Returns:
        - list: A list of all fetched engine models.
        """
        all_engine_models = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Engine Models Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch engine models using the external API
                response = self.get_engine_model_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_engine_models.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval engine models
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} engine models so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                # Exponential backoff before retrying
                wait_time = backoff_factor ** retry_count
                print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} engine models.")
        return all_engine_models

    def fetch_all_engine_llp_mx_policies(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=100, debug=False):
        """
        Fetch all engine llps from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of engine llps to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 100 engine llps.

        Returns:
        - list: A list of all fetched engine llps.
        """
        all_engine_llps = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Engine LLP Policy Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch engine llp policies using the external API
                response = self.get_engine_llp_mx_policies_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_engine_llps.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # check = [i for i in response['items'] if i['engineModelId'] == 'c67d1394-cd85-45b3-a0ed-36a498c59bf0']
                    # if check:
                    #     print(response)

                    # Log progress after every log_interval engine llps
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} engine llps so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                # Exponential backoff before retrying
                wait_time = backoff_factor ** retry_count
                print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} engine llps.")
        return all_engine_llps

    def fetch_all_engine_pr_mx_policies(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=100, debug=False):
        """
        Fetch all engine prs from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of engine prs to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 100 engine prs.

        Returns:
        - list: A list of all fetched engine prs.
        """
        all_engine_prs = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Engine PR Policy Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch engine pr policies using the external API
                response = self.get_engine_pr_mx_policies_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_engine_prs.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval engine prs
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} engine prs so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                # Exponential backoff before retrying
                wait_time = backoff_factor ** retry_count
                print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} engine prs.")
        return all_engine_prs

    def fetch_all_aircraft_models(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all aircraft models from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of aircraft models to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 100 aircraft models.

        Returns:
        - list: A list of all fetched aircraft models.
        """
        all_aircraft_models = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Aircraft Models Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch aircraft models using the external API
                response = self.get_aircraft_model_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_aircraft_models.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval aircraft models
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} aircraft models so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                # Exponential backoff before retrying
                wait_time = backoff_factor ** retry_count
                print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} aircraft models.")
        return all_aircraft_models

    def fetch_all_aircraft_part_types(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=20, debug=False):
        """
        Fetch all aircraft part types from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of aircraft models to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 100 aircraft models.

        Returns:
        - list: A list of all fetched aircraft part types.
        """
        all_aircraft_part_types = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Aircraft Part Types Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch aircraft models using the external API
                response = self.get_aircraft_part_types_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if (response and 'items' in response and response['items']):
                    all_aircraft_part_types.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval aircraft models
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} aircraft part types so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    break
                # Exponential backoff before retrying
                wait_time = backoff_factor ** retry_count
                print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} aircraft part types.")
        return all_aircraft_part_types

    def fetch_all_aircraft_parts(self, batch_size=200, max_retries=5, backoff_factor=2, log_interval=5000, debug=False):
        """
        Fetch all aircraft parts from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of aircraft parts to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 aircraft parts.

        Returns:
        - list: A list of all fetched parts.
        """
        all_aircraft_parts = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Aircraft Parts Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch parts using the external API
                response = self.get_aircraft_parts_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_aircraft_parts.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval parts
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} parts so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} aircraft parts.")
        return all_aircraft_parts

    def fetch_all_aircraft_part_snapshots(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=5000, debug=False):
        """
        Fetch all aircraft part snapshots from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of aircraft part snapshots to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 aircraft part snapshots.

        Returns:
        - list: A list of all fetched part snapshots.
        """
        all_aircraft_part_snapshots = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting aircraft part snapshots Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch part snapshots using the external API
                response = self.get_aircraft_part_snapshot_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_aircraft_part_snapshots.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval part snapshots
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} part snapshots so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} aircraft part snapshots.")
        return all_aircraft_part_snapshots

    def fetch_all_engine_snapshots(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=5000, debug=False):
        """
        Fetch all engine snapshots from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of engine snapshots to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 engine snapshots.

        Returns:
        - list: A list of all fetched engine snapshots.
        """
        all_engine_snapshots = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting engine snapshots Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch engine snapshots using the external API
                response = self.get_engine_snapshot_list(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_engine_snapshots.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval engine snapshots
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} engine snapshots so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} engine snapshots.")
        return all_engine_snapshots
    
    def fetch_all_countries(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=5000, debug=False):
        """
        Fetch all countries from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of countries to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 countries.

        Returns:
        - list: A list of all fetched countries.
        """
        all_countries = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting countries Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch countries using the external API
                response = self.get_all_countries(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_countries.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval countries
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} countries so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} countries.")
        return all_countries

    def fetch_all_regions(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=5000, debug=False):
        """
        Fetch all regions from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of regions to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 regions.

        Returns:
        - list: A list of all fetched regions.
        """
        all_regions = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting regions Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch regions using the external API
                response = self.get_all_regions(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_regions.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval regions
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} regions so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} regions.")
        return all_regions
    
    def fetch_all_engine_maintenance_inflation_defaults(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=5000, debug=False):
        """
        Fetch all engine maintenance inflation from the external API using pagination with retries, backoff, and logging.

        Parameters:

        - batch_size (int): The number of engine maintanence inflation defaults to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 regions.

        Returns:
        - list: A list of all fetched engine maintenance inflation defaults.
        """
        all_engine_maintenance_inflation_defaults = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Engine Maintenance Inflation Defaults Extractration from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch Engine Maintenance Inflation Defaults using the external API
                response = self.get_all_engine_maintenance_inflation_defaults(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_engine_maintenance_inflation_defaults.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval regions
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} Engine Maintenance Inflation Defaults so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} Engine Maintenance Inflation Defaults.")
        return all_engine_maintenance_inflation_defaults
    

    def check_assembly_dependencixes(self, assemblyId: str, debug: bool = False) -> list[tuple]:
        """
        Function to check if an assembly has any dependencies (leases, analyses, etc.) to determine
        if it can be safely deleted.

        Parameters:

        assemblyId (str): The identifier of the assembly.
        debug (bool): Optional flag to enable debug logging.

        Returns:
        list[tuple]: A list of tuples with the count of leases, analyses, and tech specs (dependencies).
        """

        # Get assembly details
        assembly_details = self.get_assembly_details(assemblyId=assemblyId, debug=debug)

        # Extract aircraftId from the assembly details, required for fetching analyses.
        aircraftId = assembly_details.get("aircraftId")
        engineId_list = [engine['engineId'] for engine in assembly_details.get("engines")]
        partId_list = [part['aircraftPartId'] for part in assembly_details.get("parts")]

        # Fetch leases associated with the assembly
        leases = self.get_lease_list(assemblyId=assemblyId, debug=debug).get("items", [])
        count_of_leases = len(leases)

        # Fetch analyses associated with the aircraft
        analyses = self.get_analysis_contexts_for_aircraft(aircraftId=aircraftId, limit=None, offset=None, debug=debug).get("items", [])
        count_of_analyses = len(analyses)

        # Fetch Engines tech specs
        all_engine_snaps = []
        for engineId in engineId_list:
            engine_snaps = self.get_engine_snapshot_list(debug=debug, engineId=engineId).get("items", [])
            if len(engine_snaps) > 0:
                all_engine_snaps.append(engine_snaps)
        count_of_engine_snaps = len(all_engine_snaps)

        # Fetch Part Snapshots
        all_part_snaps = []
        for partId in partId_list:
            part_snaps = self.get_aircraft_part_snapshot_list(debug=debug, aircraftPartId=partId).get("items", [])
            if len(part_snaps) > 0:
                all_part_snaps.append(part_snaps)
        count_of_part_snaps = len(all_part_snaps)

        # Return the results as a list of tuples
        return [("Leases", count_of_leases), ("Analyses", count_of_analyses), ("Engine Snaps", count_of_engine_snaps), ("Part Snaps", count_of_part_snaps)]

    def fetch_uuid_mapping_for_env(self,path = Path('.').resolve() / 'Database' / 'UUID_Mapping'):

        if not path.exists():
            path_resp = input(f'Path Defined does not exist!\nDo you want to create the path Y/N \n{path}')
            while path_resp.upper() not in ['Y', 'N']:
                print('Invalid Answer Y/N not selected, type N to abort')
                path_resp = input(f'Path Defined does not exist!\nDo you want to create the path Y/N \n{path}')
            if path_resp.upper() == 'Y':
                path.mkdir(parents=True)
                print(f"Path '{path}' created.")
            elif path_resp.upper() == 'N':
                return 'No Path Created, Aborting Export'

        mapping_json = {}
        aircraft_details = self.fetch_all_aircraft_details()
        assemblies = self.fetch_all_assemblies()
        companies = self.fetch_all_companies()
        aircraft_models = self.fetch_all_aircraft_models()
        aircraft_part_maintenance_policy_types = self.fetch_all_aircraft_part_maintenance_policy_types()
        aircraft_part_types = self.fetch_all_aircraft_part_types()
        engine_models = self.fetch_all_engine_models()

        for aircraft in aircraft_details:
            assembly = [x for x in assemblies if x['aircraftId'] == aircraft['id']]
            if len(assembly) == 1:
                assembly = assembly[0]
            elif len(assembly) == 0:
                print(f"No Assembly found for aircraft {aircraft['msn']}-{aircraft['aircraftModelSubSeries']}")
            else:
                print(f"More than one assembly found for {aircraft['msn']}-{aircraft['aircraftModelSubSeries']}")
            aircraft['aircraftModelId'] = assembly['aircraftModelId']

        aircraft_details_mapping = {x['id']: (x['msn'], x['aircraftModelId']) for x in aircraft_details}
        assemblies_mapping = {x['id']: x['externalAssemblyId'] for x in assemblies}
        companies_mapping = {x['id']: x['externalId'] for x in companies}
        aircraft_models_mapping = {x['id']: x['externalID'] for x in aircraft_models}
        aircraft_part_maintenance_policy_types_mapping = {x['id']: x['externalId'] for x in aircraft_part_maintenance_policy_types}
        aircraft_part_types_mapping = {x['id']: x['externalId'] for x in aircraft_part_types}
        engine_models_mapping = {x['id']: x['externalId'] for x in engine_models}

        mapping_json['aircraft_details'] = aircraft_details_mapping
        mapping_json['assemblies'] = assemblies_mapping
        mapping_json['companies'] = companies_mapping
        mapping_json['aircraft_models'] = aircraft_models_mapping
        mapping_json['aircraft_part_maintenance_policy_types'] = aircraft_part_maintenance_policy_types_mapping
        mapping_json['aircraft_part_types'] = aircraft_part_types_mapping
        mapping_json['engine_models'] = engine_models_mapping




        utils.dump_json(mapping_json, self.env, path)


    def fetch_all_users(self, batch_size=100, max_retries=5, backoff_factor=2, log_interval=5000, debug=False):
        """
        Fetch all users from the external API using pagination with retries, backoff, and logging.

        Parameters:
        - batch_size (int): The number of aircraft parts to fetch per request. Default is 100.
        - max_retries (int): Maximum number of retries in case of API failures. Default is 5.
        - backoff_factor (int): Factor by which to increase the wait time between retries. Default is 2.
        - log_interval (int): Interval for logging progress. Default is every 5000 aircraft parts.

        Returns:
        - list: A list of all fetched users.
        """

        all_users = []
        offset = 0
        total_count = 0
        retry_count = 0
        run = True
        log_count = 0
        print('Starting Users Extract from External API')

        if batch_size > log_interval:
            log_interval = batch_size

        while run:
            try:
                # Fetch users using the external API
                response = self.get_users(limit=batch_size, offset=offset, debug=debug)

                # Check if we have valid items in the response
                if response and 'items' in response and response['items']:
                    all_users.extend(response['items'])
                    offset += batch_size
                    total_count += len(response['items'])

                    # Log progress after every log_interval users
                    if total_count // log_interval > log_count:
                        log_count += 1
                        print(f"Fetched {total_count} users so far...")

                    # If fewer than batch_size items are returned, stop the loop
                    if len(response['items']) < batch_size:
                        run = False

                else:
                    # Stop if no items are returned in the current batch
                    print(f"Received empty or invalid response at offset {offset}. Stopping fetch.")
                    break

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries reached. Stopping the fetch.")
                    # Exponential backoff before retrying
                    wait_time = backoff_factor ** retry_count
                    print(f"Retrying in {wait_time} seconds due to error: {str(e)}")
                    time.sleep(wait_time)

        print(f"Finished fetching a total of {total_count} users.")
        return all_users

    def update_aircraft_model_name(self, data_to_change, aircraftModelId, debug=False):
        """
        Updates an aircraft model and its associated parts and maintenance policies based on the provided changes.
    
        This function performs the following operations:
        1. Retrieves the details of an aircraft model, its associated parts, and maintenance policy types.
        2. Modifies the aircraft model and its associated parts by replacing specified substrings in the data.
        3. Updates the modified aircraft model, parts, and maintenance policy types via PUT requests.
        4. Confirms user approval before proceeding with the changes.
        
        Parameters:
        - data_to_change (dict): A dictionary where the keys are substrings to be replaced and the values are the replacements.
        - aircraftModelId (str): The unique ID of the aircraft model to update.
        - debug (bool, optional): If True, enables debugging output. Defaults to False.
    
        Returns:
        - None: The function performs actions (e.g., updates the model, parts, and policies) based on user confirmation.
    
        Example:
        - data_to_change = {' (CS300)': '', '_CS300': ''} where {'string to change':'replacement'}
        - aircraftModelId = "f8d0e4b0-4881-4bbe-9fa4-697d39e60e4c"
        - update_aircraft_model_name(data_to_change, aircraftModelId)
        """
        
        def name_changes(data, changes):
            """
            Modifies the given data by replacing specified substrings according to the changes dictionary.
    
            Parameters:
            - data (dict): The data to modify.
            - changes (dict): A dictionary where the keys are substrings to be replaced and the values are the replacements.
    
            Returns:
            - dict: The modified data with the replacements applied.
            """
            json_str = json.dumps(data)
            
            for old_param, new_param in changes.items():
                json_str = json_str.replace(old_param, new_param)
            
            data = json.loads(json_str)
            return data
        
        ac_model = self.get_aircraft_model_info(aircraftModelId=aircraftModelId)
        all_part_types = self.fetch_all_aircraft_part_types()
        part_types = [i for i in all_part_types if ac_model['externalId'] in i['externalId']]
        print(f'\nAircraft parts fetched')
        
        print(f'\nModifying {ac_model["externalId"]} and associated parts')
        
        # Modifying the aircraft model
        modified_ac_model = name_changes(ac_model, data_to_change)
        print(f'\n ----Modified ac_model----\n{json.dumps(modified_ac_model, indent=4)}')
        
        modified_part_types = []
        modified_policy_types = []
        
        for part in part_types:
            ac_part_id = part['id']
            part['trueAircraftPartTypeTEMPId'] = ac_part_id  # Field needed for PUT request
            modified_part_type = name_changes(part, data_to_change)
            modified_part_types.append(modified_part_type)
        
            policy_type = self.get_all_aircraft_part_maintenance_policy_types(aircraftPartTypeId=ac_part_id)['items'][0]
            modified_policy_type = name_changes(policy_type, data_to_change)
            
            modified_policy_types.append(modified_policy_type)
        
        print(f'\n ---- Modified modified_part_types----\n{json.dumps(modified_part_types, indent=4)}')
        print(f'\n---- Modified modified_policy_types----\n{json.dumps(modified_policy_types, indent=4)}')
    
        def confirm_changes(decision, modified_ac_model, modified_part_types, modified_policy_types):
            if decision == "YES":
                print("\n✔️ Proceeding with updates...\n")
        
                response = self.update_aircraft_model(aircraftModelId=modified_ac_model['id'], data=modified_ac_model)
                if response.get('id') == modified_ac_model['id']:  # Checking if API request is a success
                    print(f'Success: The modified aircraft model {modified_ac_model["externalId"]} was successfully updated.\n')
                else:
                    print("Error: The request failed.")
                    print("Error details:", response)
        
                for part in modified_part_types:
                    response = self.update_aircraft_part_type(aircraftPartTypeId=part['id'], data=part)
                    if response.get('id') == part['id']:
                        print(f'Success: The modified part - {part["externalId"]} was successfully updated.\n')
                    else:
                        print("Error: The request failed.")
                        print("Error details:", response)
    
                for modified_policy in modified_policy_types:
                    response = self.update_aircraft_part_maintenance_policy_type(aircraftPartMaintenancePolicyTypeId=modified_policy['id'], data=modified_policy)
                    if response.get('id') == modified_policy['id']:
                        print(f'Success: The modified policy type - {modified_policy["externalId"]} was successfully updated.\n')
                    else:
                        print("Error: The request failed.")
                        print("Error details:", response)
        
            else:
                print("\n❌ Changes discarded. Exiting.\n")
        
        # Ask user for confirmation in the terminal
        def get_user_confirmation():
            while True:
                decision = input("\n-----REVIEW THE CHANGES!-----\nDo you want to proceed with the changes? (YES/NO): ").strip().upper()
                if decision in ["YES", "NO"]:
                    return decision
                else:
                    print("Invalid input. Please enter 'YES' or 'NO'.")
        
        # Get user confirmation
        user_decision = get_user_confirmation()
        
        # Call the function to confirm changes
        return confirm_changes(user_decision, modified_ac_model, modified_part_types, modified_policy_types)

    def create_contracted_lease_clones(self,base_assembly_id, target_assembly_ids):
        """
        Create 'Unapproved' cloned leases for target aircraft (MSNs) based on a base aircraft's CONTRACTED lease details.
    
        The function performs the following steps:
        1. Fetches the base aircraft's assembly and lease details.
        2. Validates engine and part compatibility between the base and target aircraft.
        3. Checks for technical specifications and maintenance policies.
        4. Clones the base lease, updates identifiers, and assigns it to the target aircraft.
        5. Posts and updates the cloned lease.
    
        Parameters:
        - base_assembly_id (str): Assembly ID of the base aircraft whose lease will be cloned.
        - target_assembly_ids (list): List of assembly IDs for target aircraft.
    
        Returns:
        - dict: A dictionary mapping target MSNs to their cloned lease IDs and details on tech spec
        """

    
        # Step 1: Fetch base assembly and lease details
        base_assembly = self.get_assembly_details(assemblyId=base_assembly_id)
        base_msn = base_assembly.get('msn')
        base_ac_model_id = base_assembly['aircraftModelId']
    
        # Determine required tech spec length (number of engines + number of parts)
        required_tech_spec_length = len(base_assembly['engines']) + len(base_assembly['parts'])
    
        # Extract relevant IDs from base assembly
        base_engine_ids = [i['engineId'] for i in base_assembly['engines']]
        base_eng_mod_id = [i['engineModelId'] for i in base_assembly['engines']][0]  # Extract engine model ID
        base_engine_model = self.get_engine_model_info(engineModelId=base_eng_mod_id)
    
        # Fetching base lease details
        response = self.get_lease_list(assemblyId=base_assembly_id)
        if 'items' not in response:
            return print(f'Warning {response}')
        else:
            approved_lease = [lease for lease in response['items'] if 'Approved' in lease['status']]
            if approved_lease:
                base_lease = approved_lease.pop()
                print(f"\nLease Found for base msn: {base_msn}, id: {base_lease['id']} \n")
            else:
                return print(f'Critical No contracted lease found for base msn')

        # Step 2: Initial target aircraft compatibility validation
        cloned_assemblies = []
        for clone_assembly_id in target_assembly_ids:
            assembly = self.get_assembly_details(assemblyId=clone_assembly_id)
            msn = assembly.get('msn')
    
            # Check if target aircraft model matches the base aircraft model
            if len(assembly['engines']) != len(base_assembly['engines']):
                print(
                    f'Critical: MSN {msn} (assembly id: {clone_assembly_id})\nDifferent number of engines detected on target msn\n')
                continue
    
            if len(assembly['parts']) != len(base_assembly['parts']):
                print(
                    f'Critical: MSN {msn} (assembly id: {clone_assembly_id})\nDifferent number of parts detected on target msn\n')
                continue
    
            # Check engine compatibility
            eng_mod_id = [i['engineModelId'] for i in assembly['engines']][0]
            engine_model = self.get_engine_model_info(engineModelId=eng_mod_id)
    
            # Alternative engine compatability function compares both modules and llps:
            # eng_compatibility = utils.engine_compatibility(base_engine_model,engine_model)
    
            # Comparing just modular breakdown (sufficient)
            eng_compatibility = True
            base_modules = [i['moduleTypeId'] for i in base_engine_model['engineModuleTypes']]
            clone_modules = [i['moduleTypeId'] for i in engine_model['engineModuleTypes']]
    
            if set(base_modules) != set(clone_modules):
                eng_compatibility = False
    
            if not eng_compatibility:
                print(f'Critical: MSN {msn} (assembly id: {clone_assembly_id})\nHas an incompatible engine model\nIf rates are grouped can be done. Add code to function if desired\n')
                continue
    
            cloned_assemblies.append(assembly)
    
        # Step 3: Construct cloned leases
        cloned_lease_data = []
    
        for assembly in cloned_assemblies:
            print(f"\n ------------ Processing MSN: {assembly['msn']}  ------------ \n")
            copy_msn = assembly['msn']
            ac_model_id = assembly['aircraftModelId']
            engine_ids = [i['engineId'] for i in assembly['engines']]
    
             # Step 3a: ------------------- Checking Technical Specifications -------------------
    
            all_engine_snaps = []
            for eng_id in engine_ids:
                response = self.get_engine_snapshot_list(engineId=eng_id)
                if 'items' not in response:
                    print(f'Warning {response}')  # Missing engine snapshot for example
                else:
                    latest_snap = response['items']
                    if latest_snap:
                        all_engine_snaps.append(latest_snap.pop())
    
            all_part_snaps = []
            part_ids = [i['aircraftPartId'] for i in assembly['parts']]
            for part_id in part_ids:
                response = self.get_aircraft_part_snapshot_list(aircraftPartId=part_id)
                if 'items' not in response:
                    print(f'Warning on Part Snapshot Get: {response}')
                else:
                    latest_snap = response['items']
                    if latest_snap:
                        all_part_snaps.append(latest_snap.pop())
    
            tech_spec = all_engine_snaps + all_part_snaps
    
            # Validate tech spec
            tech_spec_required = 'No'
            if not tech_spec:
                print(f"Warning: MSN {assembly['msn']} has no tech spec.")
                tech_spec_required = 'Yes, Missing'
            elif len(tech_spec) != required_tech_spec_length:
                print(f"Warning: MSN {assembly['msn']} has an incomplete tech spec.")
                tech_spec_required = 'Yes, Incomplete'
            
            # Step 3b: ------------------- Cloning the Lease -------------------
            msn_lease = copy.deepcopy(base_lease)
            msn_lease['status'] = 'Unapproved'
            msn_lease['aircraftAssemblyId'] = assembly['id']
            msn_lease.pop('id')  # Remove original lease ID
            # print(msn_lease)
            # msn_lease.pop('creationTs')  # Remove timestamp
    
            # Update lease identifiers
            if base_msn in msn_lease['externalId']:
                msn_lease['externalId'] = msn_lease['externalId'].replace(base_msn, copy_msn)
            if base_msn in msn_lease['name']:
                msn_lease['name'] = msn_lease['name'].replace(base_msn, copy_msn)
    
            # Step 3c: Comparing maintenance policy types between those on lease and on the target MSN. If compatible continue, if not break
            
            assembly_parts_parameters = {}
            gear_categories = {'nose':0, 'wing':0, 'main':0}
            for part in assembly['parts']:
                response = self.get_aircraft_part_info(aircraftPartId=part['aircraftPartId'])
                if 'category' not in response:
                    print(f'MSN {copy_msn}: get API Error - {response}')
                    continue
                part_category = response["category"]
                part_id = response['id']
                part_type_id = response['aircraftPartTypeId']
                policy_type_id = response['aircraftPartMaintenancePolicyTypeId']
                
                if part_category in ('apu', 'airframe'):
                    assembly_parts_parameters[part_category] = {'policy_type_id':policy_type_id, 'part_type_id':part_type_id, 'part_ids':part_id}
                
                # Accounting for possible differences in landing gear policy structures
                for gear in gear_categories:
                    if gear in response['externalId'].lower():
                        key = f"{gear}_gear"
                        if key not in assembly_parts_parameters:
                            assembly_parts_parameters[key] = {
                                'policy_type_id': policy_type_id,
                                'part_type_id': part_type_id,
                                'part_ids': []
                            }
                        assembly_parts_parameters[key]['part_ids'].append(part_id)
                        
            
            skip = False
            for policy in msn_lease['policyTypes']:
                
                base_policy_type_id = policy['policyTypeId']
                policy_part_category = policy['partCategory']

                if 'landing_gear' in policy_part_category:
                    response = self.get_aircraft_part_info(aircraftPartId=policy['aircraftPartId'])
                    if 'category' not in response:
                        print(f'Base MSN {base_msn}: get API Error - {response}')
                        continue

                    for gear in gear_categories:
                        if gear in response['externalId'].lower():
                            gear_type = f"{gear}_gear"
                            part_index = gear_categories[gear]
                            gear_categories[gear] += 1
                            ac_part_type_id = assembly_parts_parameters[gear_type]['part_type_id']
                            ac_policyType_id = assembly_parts_parameters[gear_type]['policy_type_id']
                            ac_part_id = assembly_parts_parameters[gear_type]['part_ids'][part_index]
                
                else:
                    ac_part_type_id = assembly_parts_parameters[policy_part_category]['part_type_id']
                    ac_policyType_id = assembly_parts_parameters[policy_part_category]['policy_type_id']
                    ac_part_id = assembly_parts_parameters[policy_part_category]['part_ids']

                # Finding the part policy type if not specified
                if ac_policyType_id is None:
                    response = self.get_all_aircraft_part_maintenance_policy_types(aircraftPartTypeId=ac_part_type_id)
                    if 'items' not in response:
                        print(f'MSN {copy_msn}: get API Error - {response}')
                    else:
                        ac_policy_types = response['items']
                        ac_policyType_id = [i['id'] for i in ac_policy_types if i['default'] is True]
    
                        if len(ac_policyType_id) == 1:
                            ac_policyType_id = ac_policyType_id.pop()
                        else:
                            if len(ac_policyType_id) > 1:
                                print(
                                    f"MSN {copy_msn}: Multiple default policies on aircraft {policy['partCategory']} part type")
                            else:
                                print(f"MSN {copy_msn}: No default policy on aircraft {policy['partCategory']} part type")
    
                            if base_ac_model_id == ac_model_id:  # Select specified policy type
                                ac_policyType_id = [i['id'] for i in ac_policy_types if i['id'] == policy[
                                    'policyTypeId']].pop()  # this will only work if ac model is the same
                            else:
                                print(
                                    f"Critical: MSN {copy_msn} has an unclear {policy['partCategory']} maintenance policy type")
                                skip = True
                                break

                ac_part_policy_type = self.get_aircraft_part_maintenance_policy_type_info(aircraftPartMaintenancePolicyTypeId=ac_policyType_id)
                base_part_policy_type = self.get_aircraft_part_maintenance_policy_type_info(aircraftPartMaintenancePolicyTypeId=base_policy_type_id)

                # Comparing the types here not the policies
                clone_check_policy = ac_part_policy_type["checkPolicies"]
                base_check_policy = base_part_policy_type["checkPolicies"]
    
                check_diff = DeepDiff(base_check_policy, clone_check_policy, ignore_order=True)
    
                # Could probably be more precise by comparing the actual intervals with an overwrite option. Add if desired.
                if check_diff:
                    # print(clone_check_policy)
                    # print(base_check_policy)
                    print(f"Critical: MSN {copy_msn} has an incompatible {policy['partCategory']} maintenance policy. Difference in check policies:")
                    # print(f"\nDifference in maintenance check policies")
                    print(check_diff)
                    skip = True
                    break

                # Step 3d: Update aircraft part ids
                msn_lease = json.loads(
                    json.dumps(msn_lease).replace(policy['aircraftPartId'], ac_part_id))

                # Step 3e: Update aircraft part policy type ids
                msn_lease = json.loads(
                    json.dumps(msn_lease).replace(policy['policyTypeId'], ac_policyType_id))
    
            if skip:
                continue
    
            # Step 3f: Update engine IDs
            for i, base_engid in enumerate(base_engine_ids):
                msn_lease = json.loads(json.dumps(msn_lease).replace(base_engid, engine_ids[i]))
            
            # Step 4a: ------------------- Creating the Cloned Lease -------------------
            lease = copy.deepcopy(msn_lease)
    
            post_data = {
                "externalId": lease['externalId'],
                "assemblyId": lease['aircraftAssemblyId'],
                "entityGroup": lease['entityGroup'],
                "status": lease['status']
            }
    
            post_response = self.create_contracted_lease(data=post_data)
            # lease['creationTs'] = post_response['creationTs']
            lease['lease_id'] = post_response['id']
    
        
            # Step 4b ------------------- Updating the Cloned Lease -------------------
            put_response = self.update_lease(leaseId=lease['lease_id'], data=lease)
            if "aircraftAssemblyId" in put_response:
                print(f'Lease for MSN {copy_msn} successfully cloned')
                cloned_lease_data.append({
                    "Msn": copy_msn,
                    "LeaseId": lease['lease_id'],
                    "TechSpecRequired": tech_spec_required
                })
            else:
                print(f'Lease PUT for MSN {copy_msn} unsuccessful. Error {put_response}')
    
                # Delete failed lease entry
                del_resp = self.delete_lease(leaseId=lease['lease_id'])
                if "aircraftAssemblyId" in del_resp:
                    print(f'Lease for MSN {copy_msn} deleted following unsuccessful PUT')
                # print(del_resp)
    
        return cloned_lease_data

    def create_base_lease_clones(self, base_lease_id, target_assembly_ids, desired_status):
        """
        Create cloned leases for target MSNs based on a base lease details.
    
        The function performs the following steps:
        1. Fetches the base lease details and the associated aircraft's assembly.
        2. Validates engine and part compatibility between the base and target aircraft.
        3. Checks for technical specifications and maintenance policies.
        4. Clones the base lease, updates identifiers, and assigns it to the target aircraft.
        5. Posts and updates the cloned lease.
    
        Parameters:
        - base_assembly_id (str): Assembly ID of the base aircraft whose lease will be cloned.
        - target_assembly_ids (list): List of assembly IDs for target aircraft.
        - desired_status (str): The status to be assigned to the cloned leases. #CAREFUL NOT TO OVERWRITE APPROVED LEASES (Additional code perhaps?)
    
        Returns:
        - dict: A dictionary mapping target MSNs to their cloned lease IDs and details on tech spec
        """
    
        # Step 1: Fetch base assembly and lease details
        response = self.get_lease_details(leaseId=base_lease_id)
        if "aircraftAssemblyId" in response:
            base_lease = response
            status = base_lease['status']
            print(f"\nLease Found with status of {status} \n")
        else:
            return print(f'Critical: No lease found for this id {response}')
    
        base_assembly_id = base_lease["aircraftAssemblyId"]
        base_assembly = self.get_assembly_details(assemblyId=base_assembly_id)
        base_msn = base_assembly.get('msn')
        base_ac_model_id = base_assembly['aircraftModelId']
    
        # Determine required tech spec length (number of engines + number of parts)
        required_tech_spec_length = len(base_assembly['engines']) + len(base_assembly['parts'])
    
        # Extract relevant IDs from base assembly
        base_engine_ids = [i['engineId'] for i in base_assembly['engines']]
        base_eng_mod_id = [i['engineModelId'] for i in base_assembly['engines']][0]  # Extract engine model ID
        base_engine_model = self.get_engine_model_info(engineModelId=base_eng_mod_id)
    
    
        # Step 2: Initial target aircraft compatibility validation
        cloned_assemblies = []
        for clone_assembly_id in target_assembly_ids:
            assembly = self.get_assembly_details(assemblyId=clone_assembly_id)
            msn = assembly.get('msn')
    
            # Check if target aircraft model matches the base aircraft model
            if len(assembly['engines']) != len(base_assembly['engines']):
                print(
                    f'Critical: MSN {msn} (assembly id: {clone_assembly_id})\nDifferent number of engines detected on target msn\n')
                continue
    
            if len(assembly['parts']) != len(base_assembly['parts']):
                print(
                    f'Critical: MSN {msn} (assembly id: {clone_assembly_id})\nDifferent number of parts detected on target msn\n')
                continue
    
            # Check engine compatibility
            eng_mod_id = [i['engineModelId'] for i in assembly['engines']][0]
            engine_model = self.get_engine_model_info(engineModelId=eng_mod_id)
    
            # Alternative engine compatability function compares both modules and llps:
            # eng_compatibility = utils.engine_compatibility(base_engine_model,engine_model)
    
            # Comparing just modular breakdown (sufficient)
            eng_compatibility = True
            base_modules = [i['moduleTypeId'] for i in base_engine_model['engineModuleTypes']]
            clone_modules = [i['moduleTypeId'] for i in engine_model['engineModuleTypes']]
    
            if set(base_modules) != set(clone_modules):
                eng_compatibility = False
    
            if not eng_compatibility:
                print(
                    f'Critical: MSN {msn} (assembly id: {clone_assembly_id})\nHas an incompatible engine model\nIf rates are grouped can be done. Add code to function if desired\n')
                continue
    
            cloned_assemblies.append(assembly)
    
        # Step 3: Construct cloned leases
        cloned_lease_data = []
    
        for assembly in cloned_assemblies:
            print(f"\n ------------ Processing MSN: {assembly['msn']}  ------------ \n")
            copy_msn = assembly['msn']
            copy_msn_id = assembly['id']
            ac_model_id = assembly['aircraftModelId']
            engine_ids = [i['engineId'] for i in assembly['engines']]
    
            # Step 3a: ------------------- Checking Technical Specifications -------------------
    
            all_engine_snaps = []
            for eng_id in engine_ids:
                response = self.get_engine_snapshot_list(engineId=eng_id)
                if 'items' not in response:
                    print(f'Warning {response}')  # Missing engine snapshot for example
                else:
                    latest_snap = response['items']
                    if latest_snap:
                        all_engine_snaps.append(latest_snap.pop())
    
            all_part_snaps = []
            part_ids = [i['aircraftPartId'] for i in assembly['parts']]
            for part_id in part_ids:
                response = self.get_aircraft_part_snapshot_list(aircraftPartId=part_id)
                if 'items' not in response:
                    print(f'Warning on Part Snapshot Get: {response}')
                else:
                    latest_snap = response['items']
                    if latest_snap:
                        all_part_snaps.append(latest_snap.pop())
    
            tech_spec = all_engine_snaps + all_part_snaps
    
            tech_spec_required = 'No'
            # Validate tech spec
            if not tech_spec:
                print(f"Warning: MSN {assembly['msn']} has no tech spec.")
                tech_spec_required = 'Yes, Missing'
            elif len(tech_spec) != required_tech_spec_length:
                print(f"Warning: MSN {assembly['msn']} has an incomplete tech spec.")
                tech_spec_required = 'Yes, Incomplete'
    
            # Step 3b: ------------------- Cloning the Lease -------------------
            msn_lease = copy.deepcopy(base_lease)
            msn_lease['status'] = desired_status
            msn_lease['aircraftAssemblyId'] = assembly['id']
            msn_lease.pop('id')  # Remove original lease ID
            msn_lease.pop('creationTs')  # Remove timestamp
    
            # Update lease identifiers
            if base_msn in msn_lease['externalId']:
                msn_lease['externalId'] = msn_lease['externalId'].replace(base_msn, copy_msn)
            if base_msn in msn_lease['name']:
                msn_lease['name'] = msn_lease['name'].replace(base_msn, copy_msn)
    
            # Step 3c: Comparing maintenance policy types between those on lease and on the target MSN. If compatible continue, if not break

            # Finding the parts and part policy types on target msn
            assembly_parts_parameters = {}
            gear_categories = {'nose':0, 'wing':0, 'main':0}
            for part in assembly['parts']:
                response = self.get_aircraft_part_info(aircraftPartId=part['aircraftPartId'])
                if 'category' not in response:
                    print(f'MSN {copy_msn}: get API Error - {response}')
                    continue
                part_category = response["category"]
                part_id = response['id']
                part_type_id = response['aircraftPartTypeId']
                policy_type_id = response['aircraftPartMaintenancePolicyTypeId']
                
                if part_category in ('apu', 'airframe'):
                    assembly_parts_parameters[part_category] = {'policy_type_id':policy_type_id, 'part_type_id':part_type_id, 'part_ids':part_id}
                
                # Accounting for possible differences in landing gear policy structures
                for gear in gear_categories:
                    if gear in response['externalId'].lower():
                        key = f"{gear}_gear"
                        if key not in assembly_parts_parameters:
                            assembly_parts_parameters[key] = {
                                'policy_type_id': policy_type_id,
                                'part_type_id': part_type_id,
                                'part_ids': []
                            }
                        assembly_parts_parameters[key]['part_ids'].append(part_id)

            # Starting comparison with base assembly policy types
            skip = False
            for policy in msn_lease['policyTypes']: 
    
                base_policy_type_id = policy['policyTypeId']
                policy_part_category = policy['partCategory']

                if 'landing_gear' in policy_part_category:
                    response = self.get_aircraft_part_info(aircraftPartId=policy['aircraftPartId'])
                    if 'category' not in response:
                        print(f'Base MSN {base_msn}: get API Error - {response}')
                        continue

                    for gear in gear_categories:
                        if gear in response['externalId'].lower():
                            gear_type = f"{gear}_gear"
                            part_index = gear_categories[gear]
                            gear_categories[gear] += 1
                            ac_part_type_id = assembly_parts_parameters[gear_type]['part_type_id']
                            ac_policyType_id = assembly_parts_parameters[gear_type]['policy_type_id']
                            ac_part_id = assembly_parts_parameters[gear_type]['part_ids'][part_index]
                else:
                    ac_part_type_id = assembly_parts_parameters[policy_part_category]['part_type_id']
                    ac_policyType_id = assembly_parts_parameters[policy_part_category]['policy_type_id']
                    ac_part_id = assembly_parts_parameters[policy_part_category]['part_ids']
    
                # If the policy type id is not specified, logic below to find
                if ac_policyType_id is None:
                    response = self.get_all_aircraft_part_maintenance_policy_types(aircraftPartTypeId=ac_part_type_id)
                    if 'items' not in response:
                        print(f'MSN {copy_msn}: get API Error - {response}')
                    else:
                        ac_policy_types = response['items']
                        ac_policyType_id = [i['id'] for i in ac_policy_types if i['default'] is True]
    
                        if len(ac_policyType_id) == 1:
                            ac_policyType_id = ac_policyType_id.pop()
                        else:
                            if len(ac_policyType_id) > 1:
                                print(
                                    f"MSN {copy_msn}: Multiple default policies on aircraft {policy['partCategory']} part type")
                            else:
                                print(f"MSN {copy_msn}: No default policy on aircraft {policy['partCategory']} part type")
    
                            if base_ac_model_id == ac_model_id:  # Select specified policy type
                                ac_policyType_id = [i['id'] for i in ac_policy_types if i['id'] == policy[
                                    'policyTypeId']].pop()  # this will only work if ac model is the same
                            else:
                                print(
                                    f"Critical: MSN {copy_msn} has an unclear {policy['partCategory']} maintenance policy type")
                                skip = True
                                break
    
                ac_part_policy_type = self.get_aircraft_part_maintenance_policy_type_info(ac_policyType_id)
                base_part_policy_type = self.get_aircraft_part_maintenance_policy_type_info(base_policy_type_id)
    
                # Comparing the types here not the policies
                clone_check_policy = ac_part_policy_type["checkPolicies"]
                base_check_policy = base_part_policy_type["checkPolicies"]
    
                check_diff = DeepDiff(base_check_policy, clone_check_policy, ignore_order=True)
    
                # Could probably be more precise by comparing the actual intervals with an overwrite option. Add if desired.
                if check_diff:
                    # print(clone_check_policy)
                    # print(base_check_policy)
                    print(f"Critical: MSN {copy_msn} has an incompatible {policy['partCategory']} maintenance policy. Difference in check policies:")
                    # print(f"\nDifference in maintenance check policies")
                    print(check_diff)
                    skip = True
                    break

                # Step 3d: Update aircraft part ids
                msn_lease = json.loads(
                    json.dumps(msn_lease).replace(policy['aircraftPartId'], ac_part_id))

                # Step 3e: Update aircraft part policy type ids
                msn_lease = json.loads(
                    json.dumps(msn_lease).replace(policy['policyTypeId'], ac_policyType_id))
    
            if skip:
                continue
    
            # Step 3f: Update engine IDs
            for i, base_engid in enumerate(base_engine_ids):
                msn_lease = json.loads(json.dumps(msn_lease).replace(base_engid, engine_ids[i]))
    
            # Step 4a: ------------------- Creating the Cloned Lease -------------------
            lease = copy.deepcopy(msn_lease)
    
            post_data = {
                "externalId": lease['externalId'],
                "assemblyId": lease['aircraftAssemblyId'],
                "entityGroup": lease['entityGroup'],
                "status": lease['status']
            }
    
            if 'Structuring' in lease['status']:
                post_response = self.create_structuring_lease(data=post_data)
            else:
                post_response = self.create_contracted_lease(data=post_data)
    
            lease['creationTs'] = post_response['creationTs']
            lease['lease_id'] = post_response['id']
    
            # Step 4b ------------------- Updating the Cloned Lease -------------------
            put_response = self.update_lease(leaseId=lease['lease_id'], data=lease)
            if "aircraftAssemblyId" in put_response:
                print(f'Lease for MSN {copy_msn} successfully cloned')
                # Save Lease ID
                cloned_lease_data.append({
                    "Msn": copy_msn,
                    "LeaseId": lease['lease_id'],
                    "TechSpecRequired": tech_spec_required
                })
            else:
                print(f'Lease PUT for MSN {copy_msn} unsuccessful. Error {put_response}')
    
                # Delete failed lease entry
                del_resp = self.delete_lease(leaseId=lease['lease_id'])
                if "aircraftAssemblyId" in del_resp:
                    print(f'Lease for MSN {copy_msn} deleted following unsuccessful PUT')
                # print(del_resp)
    
        return cloned_lease_data

    def escalate_engine_llp_maintenance_policies(self, defined_engine_llp_policies, escalation_percentage: float, target_year: int, mode='deescalate', take_dates=False):
        """
        Escalate or deescalate the LLP maintenance costs for each module of the engine model in the supplied policies.
        Fills in missing years by escalating/deescalating from the latest policy year to the target using the given escalation percentage.
        
        Parameters:
        - defined_engine_llp_policies (list): List of LLP maintenance policies for an engine model.
        - escalation_percentage (float): Annual percentage to escalate/deescalate the maintenance costs (e.g., 0.05 for 5%).
        - target_year (int): The furthest year to project to (past for deescalation, future for escalation).
        - mode (str): 'escalate' to project into the future, 'deescalate' to backfill past. Default = 'deescalate'.
        - take_dates (bool): If True, retain the day and month from the latest policy for new years.
        
        Returns:
        - list: List of newly created policies with escalated or deescalated LLP costs.
        """
        # Validate escalation mode
        mode = mode.lower()

        if mode not in ['escalate', 'deescalate']:
            raise ValueError("mode must be either 'escalate' or 'deescalate'")

        # Validate single engine model
        engine_model_ids = set(policy['engineModelId'] for policy in defined_engine_llp_policies)
        
        if not engine_model_ids:
            raise ValueError("No engineModelIds found in the provided policies.")
        
        engine_model_externalIds = []
        missing_ids = []
        
        for i in engine_model_ids:
            try:
                response = self.get_engine_model_info(engineModelId=i, debug=False)
                engine_exid = response['externalId']
                engine_model_externalIds.append(engine_exid)
            except Exception as e:
                print(response)
                missing_ids.append(i)
        
        if missing_ids:
            raise ValueError(f"Could not retrieve engine model info for the following IDs: {missing_ids}")
        
        if len(engine_model_externalIds) > 1:
            raise ValueError(f"Expected policies for a single engine model, but found multiple: {engine_model_externalIds}")
        
        # Safe assignment
        engine_model_exid = engine_model_externalIds[0]

        # Identify the most recent policy date and use it as the base
        max_policy_date = max([pd.to_datetime(i['asOf']) for i in defined_engine_llp_policies])
        max_year = max_policy_date.year
        base_policy = [i for i in defined_engine_llp_policies if i['asOf'] == max_policy_date.strftime('%Y-%m-%d')][0]
        
        # Validate target year based on mode
        if mode == 'deescalate' and target_year >= max_year:
            raise ValueError(f"Engine {engine_model_exid}: When deescalating, target_year must be LESS than {max_year}")
        if mode == 'escalate' and target_year <= max_year:
            raise ValueError(f"Engine {engine_model_exid}: When escalating, target_year must be GREATER than {max_year}")
        
        # Collect all years that already exist
        all_policy_years = [pd.to_datetime(i['asOf']).year for i in defined_engine_llp_policies]
        
        # Determine which years are missing
        if mode == 'deescalate':
            year_range = range(max_year, target_year - 1, -1)
        else:  # 'escalate'
            year_range = range(max_year + 1, target_year + 1)
        
        years_required = sorted(set(year_range) - set(all_policy_years), reverse=(mode == 'deescalate'))
        
        if not years_required:
            print(f"For engine model {engine_model_exid}, LLP policies already cover up to {target_year}.\n")
            return []
        
        new_policies = []
        
        for year in years_required:
            new_policy = copy.deepcopy(base_policy)
        
            # Compound the escalation or deescalation factor
            power = (1 + escalation_percentage) ** abs(max_year - year)
        
            # Assign the new policy date
            if take_dates:
                new_policy['asOf'] = pd.to_datetime(f'{year}-{max_policy_date.month}-{max_policy_date.day}').strftime('%Y-%m-%d')
            else:
                new_policy['asOf'] = f'{year}-01-01'
        
            # Apply cost escalation to each module
            for module in new_policy['modules']:
                if len(module['llpPolicies']) == 0:
                    continue
                for llp in module['llpPolicies']:
                    original_cost = llp['replacementCostUsd']
                    escalated_cost = original_cost * power if mode == 'escalate' else original_cost / power
                    llp['replacementCostUsd'] = int(escalated_cost)
        
            new_policies.append(new_policy)
            print(f"{mode.capitalize()}d LLP stack for engine model {engine_model_exid} to {new_policy['asOf']}")
        
        return new_policies

    def escalate_all_engine_llp_maintenance_policies(self, escalation_percentage: float, target_year: int, mode='deescalate', exclude_engine_model_ids=None, take_dates=False, debug=False, cut_off=None):
        """
        Escalate or deescalate LLP maintenance policies for all engine models, applying a percentage-based adjustment
        of interval costs for each module in the supplied LLP maintenance policies.
    
        Parameters:
        - escalation_percentage (float): The annual percentage to escalate or escalate LLP costs (e.g., 0.05 for 5%).
        - target_year (int): The furthest year to project to (past for escalation, future for escalation).
        - mode (str): 'escalate' or 'deescalate' (default: 'deescalate').
        - exclude_engine_model_ids (list): Optional. List of engine model IDs to exclude from processing.
        - take_dates (bool): Optional. If True, retain the month/day from the base policy's date.
        - debug (bool): Optional. If True, prints extra debug output.
        - cut_off (int): Optional. Limit the number of engine models processed. If None, process all.
    
        Returns:
        - list: A list of all new LLP maintenance policies generated by escalation or deescalation.
        """

        # Validate escalation mode
        mode = mode.lower()

        if mode not in ['escalate', 'deescalate']:
            raise ValueError("mode must be either 'escalate' or 'deescalate'")
    
        exclude_engine_model_ids = exclude_engine_model_ids or []
        engine_models = self.fetch_all_engine_models()
        engine_llp_policies = self.fetch_all_engine_llp_mx_policies()
        all_escalated_policies = []

        for engine in engine_models[:cut_off]:
            engine_id = engine['id']

            try:
                response = self.get_engine_model_info(engineModelId=engine_id, debug=False)
                engine_exid = response['externalId']
            except Exception as e:
                print(response)
                continue

            print(f'\n-------- {engine_exid} --------\n')
    
            if engine_id in exclude_engine_model_ids:
                print(f"Skipping excluded engine model: {engine_exid}")
                continue
    
            llp_policies = [i for i in engine_llp_policies if engine_id in i['engineModelId']]
    
            if not llp_policies:
                print(f"Couldn't find policies for engine model {engine_exid}")
                continue
    
            # Validate direction for this engine model
            latest_year = max([pd.to_datetime(i['asOf']).year for i in llp_policies])
            if mode == 'deescalate' and target_year >= latest_year:
                print(f"Skipping {engine_exid}: Cannot deescalate to {target_year}, target year must be LESS than {latest_year}")
                continue
            if mode == 'escalate' and target_year <= latest_year:
                print(f"Skipping {engine_exid}: Cannot escalate to {target_year}, target year must be GREATER than {latest_year}")
                continue
    
            # Call the escalate/deescalate method
            escalated_policies = self.escalate_engine_llp_maintenance_policies(
                llp_policies,
                escalation_percentage,
                target_year,
                mode,
                take_dates
            )

    
            all_escalated_policies.extend(escalated_policies)

        return all_escalated_policies

    def escalate_engine_pr_maintenance_policies(self, defined_engine_pr_policies, escalation_percentage: float, target_year: int, mode='deescalate', take_dates=False):
        """
        Escalate or deescalate the PR (Performance Restoration) interval costs for each module in the supplied policies.
        Fills in missing years by escalating/deescalating from the latest policy year to the target using the given escalation percentage.
    
        Parameters:
        - defined_engine_pr_policies (list): List of policy dictionaries, each with modules and associated cost data.
        - escalation_percentage (float): The percentage to escalate or deescalate the PR interval costs per year (e.g., 0.05 for 5%).
        - target_year (int): The furthest year to project to (past or future depending on mode).
        - mode (str): Either 'escalate' or 'deescalate' (default is 'deescalate').
        - take_dates (bool): Optional. If True, retain the month and day from the base policy's date; else use Jan 1st.
    
        Returns:
        - list: List of new PR maintenance policies generated by escalation/deescalation.
        """
    
        # Validate escalation mode
        mode = mode.lower()

        if mode not in ['escalate', 'deescalate']:
            raise ValueError("mode must be either 'escalate' or 'deescalate'")

        # Validate single engine model
        engine_model_ids = set(policy['engineModelId'] for policy in defined_engine_pr_policies)
        
        if not engine_model_ids:
            raise ValueError("No engine model Ids found in the provided policies.")
        
        engine_model_externalIds = []
        missing_ids = []
        for i in engine_model_ids:
            try:
                response = self.get_engine_model_info(engineModelId=i, debug=False)
                engine_exid = response['externalId']
                engine_model_externalIds.append(engine_exid)
            except Exception as e:
                print(response)
                missing_ids.append(i)
        
        if missing_ids:
            raise ValueError(f"Could not retrieve engine model info for the following IDs: {missing_ids}")
        
        if len(engine_model_externalIds) > 1:
            raise ValueError(f"Expected policies for a single engine model, but found multiple: {engine_model_externalIds}")
        
        engine_model_exid = engine_model_externalIds[0]

        # Identify the most recent policy date and use it as the base
        max_policy_date = max([pd.to_datetime(i['asOf']) for i in defined_engine_pr_policies])
        max_year = max_policy_date.year
        base_policy = [i for i in defined_engine_pr_policies if i['asOf'] == max_policy_date.strftime('%Y-%m-%d')][0]
        
        # Validate target year based on mode
        if mode == 'deescalate' and target_year >= max_year:
            raise ValueError(f"Engine {engine_model_exid}: When deescalating, target_year must be LESS than {max_year}")
        if mode == 'escalate' and target_year <= max_year:
            raise ValueError(f"Engine {engine_model_exid}: When escalating, target_year must be GREATER than {max_year}")
        
        # Collect all years that already exist
        all_policy_years = [pd.to_datetime(i['asOf']).year for i in defined_engine_pr_policies]
        
        # Determine which years are missing
        if mode == 'deescalate':
            year_range = range(max_year, target_year - 1, -1)
        else:  # 'escalate'
            year_range = range(max_year + 1, target_year + 1)
        
        years_required = sorted(set(year_range) - set(all_policy_years), reverse=(mode == 'deescalate'))
        
        if not years_required:
            print(f"For engine model {engine_model_exid}, LLP policies already cover up to {target_year}.\n")
            return []
        
        new_policies = []
        for year in years_required:
            new_policy = copy.deepcopy(base_policy)
            
            # Compound the escalation or deescalation factor
            power = (1 + escalation_percentage) ** abs(max_year - year)

            # Set the new date: preserve month/day if take_dates=True, otherwise just use Jan 1

            if take_dates:
                new_policy['asOf'] = pd.to_datetime(f'{year}-{max_policy_date.month}-{max_policy_date.day}').strftime('%Y-%m-%d')
            else:
                new_policy['asOf'] = f'{year}-01-01'
    
            for module in new_policy['modules']:
                for interval_cost in ['firstRunCostUsd', 'subsequentRunCostUsd']:
                    original_cost = module[interval_cost]
                    escalated_cost = original_cost * power if mode == 'escalate' else original_cost / power
                    module[interval_cost] = int(escalated_cost)
    
            new_policies.append(new_policy)
    
            print(f"{mode.capitalize()}d PR Policies for engine model {engine_model_exid} to {new_policy['asOf']}")
    
        return new_policies

    def escalate_all_engine_pr_maintenance_policies(self, escalation_percentage: float, target_year: int, mode='deescalate', exclude_engine_model_ids=None, take_dates=False, debug=False, cut_off=None):
        """
        Escalate or deescalate PR maintenance policies for all engine models, applying a percentage-based adjustment
        of costs for each module in the supplied PR maintenance policies.
        
        Parameters:
        - escalation_percentage (float): The annual percentage to escalate or escalate PR costs (e.g., 0.05 for 5%).
        - target_year (int): The furthest year to project to (past for deescalation, future for escalation).
        - mode (str): 'escalate' or 'deescalate' (default: 'deescalate').
        - exclude_engine_model_ids (list): Optional. List of engine model IDs to exclude from processing.
        - take_dates (bool): Optional. If True, retain the month/day from the base policy's date.
        - debug (bool): Optional. If True, prints extra debug output.
        - cut_off (int): Optional. Limit the number of engine models processed. If None, process all.
        
        Returns:
        - list: A list of all new PR maintenance policies generated by escalation or deescalation.
        """
        
        # Validate escalation mode
        mode = mode.lower()
        
        if mode not in ['escalate', 'deescalate']:
            raise ValueError("mode must be either 'escalate' or 'deescalate'")
        
        exclude_engine_model_ids = exclude_engine_model_ids or []
        engine_models = self.fetch_all_engine_models()
        engine_pr_policies = self.fetch_all_engine_pr_mx_policies()
        all_escalated_policies = []
        
        for engine in engine_models[:cut_off]:
            engine_id = engine['id']
            try:
                response = self.get_engine_model_info(engineModelId=engine_id, debug=False)
                engine_exid = response['externalId']
            except Exception as e:
                print(response)
                continue
        
            print(f'\n-------- {engine_exid} --------\n')
        
            if engine_id in exclude_engine_model_ids:
                print(f"Skipping excluded engine model: {engine_exid}")
                continue
        
            pr_policies = [i for i in engine_pr_policies if engine_id in i['engineModelId']]
        
            if not pr_policies:
                print(f"Couldn't find policies for engine model {engine_exid}")
                continue
        
            # Validate direction for this engine model
            latest_year = max([pd.to_datetime(i['asOf']).year for i in pr_policies])
            if mode == 'deescalate' and target_year >= latest_year:
                print(f"Skipping {engine_exid}: Cannot deescalate to {target_year}, target year must be LESS {latest_year}")
                continue
            if mode == 'escalate' and target_year <= latest_year:
                print(f"Skipping {engine_exid}: Cannot escalate to {target_year}, target year must be GREATER {latest_year}")
                continue
        
            # Call the escalate/deescalate method
            escalated_policies = self.escalate_engine_pr_maintenance_policies(
                pr_policies,
                escalation_percentage,
                target_year,
                mode,
                take_dates
            )
        
        
            all_escalated_policies.extend(escalated_policies)
        
        return all_escalated_policies

    def escalate_part_maintenance_policies(self, defined_part_policies, escalation_percentage: float, target_year:int, mode='deescalate', take_dates=False):
        """
        Escalate or deescalate the maintenance policies for an aircraft part policy in the supplied policies. 
        Fills in missing years by escalating/deescalating from the latest policy year to the target using the given escalation percentage.
        
        Parameters:
        - policy (dict): The policy data containing aircraft part intervals and costs.
        - escalation_percentage (float): The percentage to escalate the check costs (e.g., 0.05 for 5%).
        - target_year (int): The furthest year to project to (past or future depending on mode).
        - mode (str): Either 'escalate' or 'deescalate' (default is 'deescalate').
        - take_dates (Bool): Optional. If True, retain the month and day from the base policy's date; else use Jan 1st.
        
        Returns:
        - list: List of new part maintenance policies generated by escalation/deescalation.
        """
    
        # Validate escalation mode
        mode = mode.lower()

        if mode not in ['escalate', 'deescalate']:
            raise ValueError("mode must be either 'escalate' or 'deescalate'")

        # Validate single policy type
        policy_type_ids = set(policy['policyTypeId'] for policy in defined_part_policies)
        
        if not policy_type_ids:
            raise ValueError("No policy type Ids found in the provided policies.")
        
        policy_type_externalIds = []
        missing_ids = []
        for i in policy_type_ids:
            try:
                response = self.get_aircraft_part_maintenance_policy_type_info(aircraftPartMaintenancePolicyTypeId=i, debug=False)
                policy_type_exid = response['externalId']
                policy_type_externalIds.append(policy_type_exid)
            except Exception as e:
                print(response)
                missing_ids.append(i)
        
        if missing_ids:
            raise ValueError(f"Could not retrieve policy type info for the following IDs: {missing_ids}")
        
        if len(policy_type_externalIds) > 1:
            raise ValueError(f"Expected policies for a single aircraft part policy type, but found multiple: {policy_type_externalIds}")
        
        policy_type_exid = policy_type_externalIds[0]

        # Identify the most recent policy date and use it as the base
        max_policy_date = max([pd.to_datetime(i['asOf']) for i in defined_part_policies])
        max_year = max_policy_date.year
        base_policy = [i for i in defined_part_policies if i['asOf'] == max_policy_date.strftime('%Y-%m-%d')][0]

        # Validate target year based on mode
        if mode == 'deescalate' and target_year >= max_year:
            raise ValueError(f"Policy {policy_type_exid}: When deescalating, target_year must be LESS than {max_year}")
        if mode == 'escalate' and target_year <= max_year:
            raise ValueError(f"Policy {policy_type_exid}: When escalating, target_year must be GREATER than {max_year}")
        
        # Collect all years that already exist
        all_policy_years = [pd.to_datetime(i['asOf']).year for i in defined_part_policies]
        
        # Determine which years are missing
        if mode == 'deescalate':
            year_range = range(max_year, target_year - 1, -1)
        else:  # 'escalate'
            year_range = range(max_year + 1, target_year + 1)
        
        years_required = sorted(set(year_range) - set(all_policy_years), reverse=(mode == 'deescalate'))
    
        if not years_required:
            print(f"For policy type {policy_type_exid}, part policies present back to {target_year}\n")
            return []
    
        new_policies = []
    
        for year in years_required:
            new_policy = copy.deepcopy(base_policy)
            power = (1 + escalation_percentage) ** abs(max_year - year)
    
            # Set the new date: preserve month/day if take_dates=True, otherwise just use Jan 1
            if take_dates:
                new_policy['asOf'] = pd.to_datetime(f'{year}-{max_policy_date.month}-{max_policy_date.day}').strftime('%Y-%m-%d')
            else:
                new_policy['asOf'] = f'{year}-01-01'
    
            # Adjust cost for each check and run using the de-escalated factor
            for check in new_policy['checkPolicies']:
                for run in check['maintenanceRuns']:
                    original_cost = run['costUsd']
                    escalated_cost = original_cost * power if mode == 'escalate' else original_cost / power
                    run['costUsd'] = int(escalated_cost)
    
            # Append the new de-escalated policy to the output list
            new_policies.append(new_policy)
    
            print(f"{mode.capitalize()}d Policies for policy type {policy_type_exid} to {new_policy['asOf']}")
    
        return new_policies

    def escalate_all_part_maintenance_policies(self, escalation_percentage_dictionary, target_year: int, mode='deescalate', take_dates=False, debug=False, cut_off=None):
        """
        Escalate or deescalate the maintenance policies for all aircraft part maintenance policy types, applying a percentage-based escalation of interval costs
        for each check in the supplied part maintenance policies.
        
        Parameters:
        - escalation_percentage_dictionary (float): A dictionary specifying the escalation percentage for each part type. 
                Example: {'airframe': 0.01, 'landing_gear': 0.02,  'apu': 0.03, 'propeller_hub':0.04,'propeller_blades':0.05}
        - target_year (int): The earliest year to de-escalate to, going backward from the max policy year. For example, from 2022 to 2015.
        - mode (str): 'escalate' or 'deescalate' (default: 'deescalate').
        - take_dates (bool): Optional. Default is False. If True, retain the month and day from the base policy's date while de-escalating.
                             If False, set the date to January 1st of each year.
        - cut_off (int): Optional. Limit the number of policy types to process. If None, all are included.
        
        Returns:
        - list: A list of esclataed aircraft part maintenance policies for all aircraft part policy types.
        """
    
        # Validate escalation mode
        mode = mode.lower()
        
        if mode not in ['escalate', 'deescalate']:
            raise ValueError("mode must be either 'escalate' or 'deescalate'")

        # Fetch reference data
        all_part_policy_types = self.fetch_all_aircraft_part_maintenance_policy_types()
        all_part_policies = self.fetch_all_aircraft_part_maintenance_policies()
        all_escalated_policies = []
    
        # Process each policy type up to the cut-off
        for policy_type in all_part_policy_types[:cut_off]:

            part_category = policy_type['category']
            # Check if this part category has a escalation rate defined
            if part_category in escalation_percentage_dictionary:
                escalation_percentage = escalation_percentage_dictionary[part_category]
            else:
                print(f"\n#### WARNING: Esclation rate for {part_category} not specified, policies not escalated ####")
                continue  # Skip if no escalation rate is defined

            
            pol_type_id = policy_type['id']

            try:
                response = self.get_aircraft_part_maintenance_policy_type_info(aircraftPartMaintenancePolicyTypeId=pol_type_id, debug=False)
                policy_type_exid = response['externalId']
            except Exception as e:
                print(response)
                continue
        
            print(f'\n-------- {policy_type_exid} --------\n')
            
    
            # Get all policies that belong to the current policy type
            type_policies = [i for i in all_part_policies if i['policyTypeId'] in pol_type_id]

            if not type_policies:
                print(f"Couldn't find policies for policy type {policy_type_exid}")
                continue

            # Validate direction for this policy type
            latest_year = max([pd.to_datetime(i['asOf']).year for i in type_policies])
            if mode == 'deescalate' and target_year >= latest_year:
                print(f"Skipping {policy_type_exid}: Cannot deescalate to {target_year}, target year must be LESS than {latest_year}")
                continue
            if mode == 'escalate' and target_year <= latest_year:
                print(f"Skipping {policy_type_exid}: Cannot escalate to {target_year}, target year must be GREATER than {latest_year}")
                continue
    
            # Call the escalate/deescalate method
            escalated_policies = self.escalate_part_maintenance_policies(
                type_policies,
                escalation_percentage,
                target_year,
                mode,
                take_dates
            )

            all_escalated_policies.extend(escalated_policies)
        
        return all_escalated_policies

    def update_engine_module_name_and_poll_for_response(self, engineModelId: str, data: dict, poll_interval: float = 1.0, debug: bool = False):
        """
        PUT: Update an existing engine model by its ID.

        Parameters:
        - engineModelId (str): The unique ID of the engine model to update.
        - data (dict): A dictionary containing the updated details of the engine module.
        - poll_interval (float): Seconds to wait between polling requests.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Data Format:
        - {
          "oldId": "",
          "newId": "",
          "newName": ""
        }


        Returns:
        - dict: The updated engine model details in JSON format.
        """
        
        response = self.async_update_engine_module_name(engineModelId=engineModelId, data=data, debug=debug)
        try:
            jobId = response['jobId']
            while True:
                poll_response = self.get_async_job_status(jobId=jobId, debug=debug)
                print(f"Progress: {poll_response['progress']}%")
                if poll_response['status'] == "completed":
                    print(f"Successfully Renamed Module from '{data['oldId']}' to '{data['newId']}' with name '{data['newName']}'")
                    return f"Successfully Renamed Module from '{data['oldId']}' to '{data['newId']}' with name '{data['newName']}'"
                else:
                    time.sleep(poll_interval)

        except:
            print(f"Error during PUT on/external-api/engine-models/module-name/{engineModelId}\nNo jobId to poll. Check the data structure.\nAPI responded: {response}")
            return response
    
    def update_engine_llp_name_and_poll_for_response(self, engineModelId: str, data: dict, poll_interval: float = 1.0, debug: bool = False):
        """
        PUT: Update an existing engine model by its ID.

        Parameters:
        - engineModelId (str): The unique ID of the engine model to update.
        - data (dict): A dictionary containing the updated details of the llp.
        - poll_interval (float): Seconds to wait between polling requests.
        - debug (bool): Optional. If True, prints the URL for debugging purposes.

        Data Format:
        - {
          "oldId": "",
          "newId": "",
          "newName": ""
        }


        Returns:
        - dict: The updated engine model details in JSON format.
        """
        
        response = self.async_update_engine_llp_name(engineModelId=engineModelId, data=data, debug=debug)
        try:
            jobId = response['jobId']
            while True:
                poll_response = self.get_async_job_status(jobId=jobId, debug=debug)
                print(f"Progress: {poll_response['progress']}%")
                if poll_response['status'] == "completed":
                    print(f"Successfully Renamed llp from '{data['oldId']}' to '{data['newId']}' with name '{data['newName']}'")
                    return f"Successfully Renamed llp from '{data['oldId']}' to '{data['newId']}' with name '{data['newName']}'"
                else:
                    time.sleep(poll_interval)

        except:
            print(f"Error during PUT on/external-api/engine-models/llp-stack/{engineModelId}\nNo jobId to poll. Check the data structure.\nAPI responded: {response}")
            return response

    def log(self, message, extra=None, level=logging.CRITICAL):
        """
        Internal logging helper. Uses provided logger if available,
        otherwise falls back to print().

        Args:
            message (str): Log message.
            extra (dict, optional): Extra context fields that match your
                configured logging formatter (e.g., {"Assembly": "ENG-123"}).
            level (int, optional): Logging level, default is CRITICAL.
        """
        if self.error_logger:
            self.error_logger.log(level, message, extra=extra or {})
        else:
            print(message, extra or {})

    def single_post(self, supplied_data, api_end, successes, id_to_externalId_dict):
        """
        Attempt to POST snapshot data to the API.

        Args:
            supplied_data (list[dict]): List of {componentId: payload}.
            api_end (str): API endpoint (e.g., "aircraft-part-snapshots").
            successes (list[str]): Accumulates successful snapshot IDs.
            id_to_externalId_dict (dict): Map of componentId → external metadata.

        Returns:
            tuple:
                - "No errors" or dict of {externalAssemblyId: error_details}.
                - Updated list of successes.
        """
        errors = {}
        no_error = True
        for my_dict in supplied_data:
            componentId, data = next(iter(my_dict.items()))
            url = f"{self.key_row['URL']}/v1/external-api/{api_end}/{componentId}"
            response = requests.post(url, headers=self.headers, json=data)
            r_json = response.json()

            if "id" in r_json:
                successes.append(r_json["id"])
            else:
                no_error = False
                errors[id_to_externalId_dict[componentId]["externalAssemblyId"]] = {
                    "response_code": response,
                    "response_json": r_json,
                    "post_json": data,
                    "componentId": componentId,
                }
        return ("No errors" if no_error else errors), successes

    def single_put(self, supplied_data, api_end, successes, id_to_externalId_dict):
        """
        Attempt to PUT (update) snapshot data after a failed POST.

        Args:
            supplied_data (list[dict]): Dicts with {"json", "componentId"}.
            api_end (str): API endpoint (e.g., "engine-snapshots").
            successes (list[str]): Accumulates successful snapshot IDs.
            id_to_externalId_dict (dict): Map of componentId → external metadata.

        Returns:
            tuple:
                - "No errors" or dict of {externalAssemblyId: error_details}.
                - Updated list of successes.
        """
        errors = {}
        no_error = True
        for my_dict in supplied_data:
            if "json" not in my_dict:
                continue
            data = my_dict["json"]
            componentId = my_dict["componentId"]

            # First GET to find snapshot by asOf date
            url1 = f"{self.key_row['URL']}/v1/external-api/{api_end}"
            params = {"aircraftPartId": componentId, "engineId": componentId}
            response1 = requests.get(url1, headers=self.headers, params=params)
            r1_json = response1.json()

            snap_id = None
            if "items" in r1_json:
                snap_list = [x for x in r1_json["items"] if x["asOf"] == data["asOf"]]
                if len(snap_list) == 1:
                    snap_id = snap_list[0]["id"]
                else:
                    continue
            if not snap_id:
                continue

            # PUT update
            url2 = f"{self.key_row['URL']}/v1/external-api/{api_end}/{snap_id}"
            response2 = requests.put(url2, headers=self.headers, json=data)
            r2_json = response2.json()

            if "id" in r2_json:
                successes.append(r2_json["id"])
            else:
                no_error = False
                errors[id_to_externalId_dict[componentId]["externalAssemblyId"]] = {
                    "response_code": response2,
                    "response_json": r2_json,
                    "post_json": data,
                    "componentId": componentId,
                }
        return ("No errors" if no_error else errors), successes

    def delete_snapshots(self, deletes, api_end):
        """
        Cleanup helper. Deletes snapshots from API if failures occur.

        Args:
            successes (list[str]): Successful snapshot IDs to delete.
            api_end (str): API endpoint to delete from.
        """
        for delete in deletes:
            url = f"{self.key_row['URL']}/api/v1/external-api/{api_end}/{success}"
            requests.delete(url, headers=self.headers)

    def integration_posting(
            self,
            part_snaps=None,
            engine_snaps=None,
            id_to_externalId_dict=None,
            assembly=None,
            extra=None,
    ):
        """
        Orchestrates posting part & engine snapshots to the external API.

        Handles POST, retries with PUT on conflicts, and cleans up on failure.

        Args:
            part_snaps (list[dict], optional): Part snapshot payloads.
            engine_snaps (list[dict], optional): Engine snapshot payloads.
            id_to_externalId_dict (dict, optional): Map of componentId → external metadata.
            assembly (dict, optional): Assembly object for part/engine counts.
            extra (dict, optional): Passed to logger; keys must match
                formatter fields (e.g., {"Assembly": "ASM-001"}).

        Returns:
            dict: Summary of results with:
                - total_success (int)
                - part_failure_count (int)
                - eng_failure_count (int)
                - successes (list[str])
        """
        part_snaps = part_snaps or []
        engine_snaps = engine_snaps or []
        id_to_externalId_dict = id_to_externalId_dict or {}
        total_success = 0
        part_failure_count, eng_failure_count = 0, 0
        successes = []

        # === PART SNAPSHOTS ===
        if assembly is None or len(part_snaps) == len(assembly.get("parts", [])):
            ass_errors, successes = self.single_post(
                part_snaps, "aircraft-part-snapshots", successes, id_to_externalId_dict)
            ass_puts = []

            if ass_errors != "No errors":
                for error, details in ass_errors.items():
                    if "409" in str(details["response_code"]):
                        ass_puts.append({"json": details["post_json"], "componentId": details["componentId"]})
                    else:
                        msg = (", ".join(details["response_json"]["errorMessages"])
                            if "errorMessages" in details["response_json"]
                            else details["response_json"].get("message", "Unknown error key from api, raise with Aerlytix"))
                        part_failure_count += 1
                        self.log(msg, extra=extra)

                put_errors, successes = self.single_put(
                    ass_puts, "aircraft-part-snapshots", successes, id_to_externalId_dict
                )
                if put_errors != "No errors":
                    for error, details in put_errors.items():
                        msg = (
                            ", ".join(details["response_json"]["errorMessages"])
                            if "errorMessages" in details["response_json"]
                            else details["response_json"].get("message", "Unknown error key from api, raise with Aerlytix")
                        )
                        part_failure_count += 1
                        self.log(msg, extra=extra)

        # === ENGINE SNAPSHOTS ===
        if assembly is None or len(engine_snaps) == len(assembly.get("engines", [])):
            ass_errors, successes = self.single_post(
                engine_snaps, "engine-snapshots", successes, id_to_externalId_dict
            )
            ass_puts = []

            if ass_errors != "No errors":
                for error, details in ass_errors.items():
                    if "409" in str(details["response_code"]):
                        ass_puts.append(
                            {"json": details["post_json"], "componentId": details["componentId"]}
                        )
                    else:
                        msg = (
                            " : ".join(details["response_json"]["errorMessages"])
                            if "errorMessages" in details["response_json"]
                            else details["response_json"].get("message", "Unknown error")
                        )
                        eng_failure_count += 1
                        self.log(msg, extra=extra)

                put_errors, successes = self.single_put(
                    ass_puts, "engine-snapshots", successes, id_to_externalId_dict
                )
                if put_errors != "No errors":
                    for error, details in put_errors.items():
                        msg = (
                            ", ".join(details["response_json"]["errorMessages"])
                            if "errorMessages" in details["response_json"]
                            else details["response_json"].get("message", "Unknown error")
                        )
                        eng_failure_count += 1
                        self.log(msg, extra=extra)

            # Cleanup if failures
            if eng_failure_count == 0 and part_failure_count == 0:
                total_success += 1
            else:
                if eng_failure_count > 1:
                    self.delete_snapshots(successes, "engine-snapshots")
                if part_failure_count > 1:
                    self.delete_snapshots(successes, "aircraft-part-snapshots")

        return {
            "total_success": total_success,
            "part_failure_count": part_failure_count,
            "eng_failure_count": eng_failure_count,
            "successes": successes,
        }
