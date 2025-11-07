import numpy as np 
import pandas as pd 
import requests
import re

# These are the core utils functions for interacting with the eikon APIs
# ----------------------------------------



# general utility functions
# ----------------------------------------


# function to get an API key from user credentials
# -----
def get_api_key_from_credentials(email, password):
    """
    This is a function to get an API key from user credentials (email and password).
    This function requires an email address and password in string format.
    The function returns a string API key if successful, otherwise it returns None.
    
    Example usage: 
    
    my_api = get_api_key_from_credentials(my_email, my_password)

    Exmaple response:

    "my_random_api_key_12345"
    
    """
    
    # send the user email to the backend to check if the user already has an account
    base_api_address = f"https://slugai.pagekite.me/"
    endpoint = "eikon_get_api_key_for_user"
    payload = {"email_address": email,
              "password":password
              }
    r = requests.post(base_api_address + endpoint, json=payload, timeout=120)
    if r.ok:
        api_key = r.json()["api_key"]
        return api_key
    else:
        return None
    
# function to check credits balance
# -----

def check_users_current_credit_balance(api_key):
    """
    This is a function to check a user's current API credit balance.
    This function requires an api_key in string format.
    The function returns an continuous float value of the user's current API credit balance in GBP if successful, otherwise it returns None.
    
    Example usage:
    current_credits = check_users_current_credit_balance(my_api_key)

    Example response:
    42 # this is equivalent to £42 or 42 GBP.


    """
    base_api_address = f"https://slugai.pagekite.me/"
    endpoint = "check_eikon_api_credits"
    payload = {"api_key": api_key}
    r = requests.post(base_api_address+endpoint, json=payload, timeout=120)
    print(r)
    if r.ok:
        current_api_balance = r.json()["current_api_credit_balance"]
        return current_api_balance
    else:
        return None
    
# function to get payments link to add credits to user accounts
# -----
def get_payments_link_to_add_credits():

    """
    This is a function to get a payments link to add credits to user accounts.
    
    """

    base_api_address = f"https://slugai.pagekite.me/"
    endpoint = "get_payments_link_to_top_credit_balance"
    payload = {"prompt": "_",
              }
    r = requests.post(base_api_address + endpoint, json=payload, timeout=120)
    if r.ok:
        valid_payment_link_url = r.json()["payment_link"]
        return valid_payment_link_url
    else:
        return None
    
# function to get link to the eikon datastore to purchase flat files
# -----

def get_link_to_eikon_datastore():
    """
    This is a function to get a link to the eikon datastore to purchase flat files.
    
    """
    base_api_address = f"https://slugai.pagekite.me/"
    endpoint = "get_link_to_eikon_datastore"
    payload = {"prompt": "_"}
    r = requests.post(base_api_address + endpoint, json=payload, timeout=120)
    if r.ok:
        valid_datastore_link_url = r.json()["datastore_link"]
        return valid_datastore_link_url
    else:
        return None
    
# this function is to get access to your previous eikon search api results
# -------

def get_previous_search_api_results(api_key,
                                    num_requested_results):
    """
    This is a function that retrieves your previous N results.

    Note: The number of previous search results you have access to is capped at 5.

    Your num_requested_results value must be an integer or a float

    """
    base_api_address = f"https://slugai.pagekite.me/"
    endpoint = "get_latest_results_for_eikon_search_agent_api_job_web_many"
    payload = {"api_key": api_key,
               "num_searches": int(num_requested_results)}
    r = requests.post(base_api_address + endpoint, json=payload, timeout=360)
    if r.ok:
        search_results_retrieved_str = r.json()["latest_search_results"]
        search_results_requested_list = search_results_retrieved_str.split("|")
        return search_results_requested_list
    else:
        return None

def list_of_supported_areas():
    """
    
    This is a function that returns a list of all the areas in Eikon that can be used to filter for the search API.
    
    """

    # Ping the server side for the latest catalogue that lists the areas that are currently supported by Eikon

    base_api_address = f"https://slugai.pagekite.me/"
    endpoint = "get_valid_locations_for_eikon_filtering"
    payload = {"placeholder": ""
               }
    r = requests.post(base_api_address + endpoint, json=payload, timeout=360)
    if r.ok:
        valid_location_names = r.json()["supported_area_names"]
        valid_location_names_list = valid_location_names.split("|")
        return valid_location_names_list
    else:
        return None