import os, sys, json, requests

from cryptography.fernet import Fernet
from apsfuncs.Toolbox.ConfigHandlers import get_resource_path

# Class to hold authentication handling for updating requests
class TokenAuthenticator:
    # Init
    def __init__(self, server_auth_location):
        self.server_auth_location = server_auth_location
        self.token_confirmed = False
        self.token = self.load_token()

    # Function to return the stored PAT token
    def load_token(self, storage=""):
        # Switch based on the storage key
        match (storage):
            case "":
                # Open the json for the key and token from the local directory
                auth_components_loc = os.path.join(get_resource_path(), "auth_props.json")
                with open(auth_components_loc) as auth_file:
                    auth_components = json.load(auth_file)

                key = auth_components['Key']
                cipher = Fernet(key)
                encrypted_token = auth_components['EncryptedToken']

                try:
                    token = cipher.decrypt(encrypted_token).decode()
                    return token
                except:
                    # Bad token info
                    return ""
            
            case "server":
                # Open the json from the camserver location
                auth_components_loc = self.server_auth_location

                # Check the program has access to the file, if not then just return a bad tocken
                if not os.path.exists(auth_components_loc):
                    return ""
                
                with open(auth_components_loc) as auth_file:
                    auth_components = json.load(auth_file)

                key = auth_components['Key']
                cipher = Fernet(key)
                encrypted_token = auth_components['EncryptedToken']

                try:
                    token = cipher.decrypt(encrypted_token).decode()
                    return token
                except:
                    # Bad token info
                    return ""
            
            case "recovery":
                # Open the json from the executable directory (if a recovery token is placed in the working folder) location
                auth_components_loc = os.path.join(sys.executable, "auth_props.json")

                # Check the program has access to the file, if not then just return a bad tocken
                if not os.path.exists(auth_components_loc):
                    return ""
                
                with open(auth_components_loc) as auth_file:
                    auth_components = json.load(auth_file)

                key = auth_components['Key']
                cipher = Fernet(key)
                encrypted_token = auth_components['EncryptedToken']

                try:
                    token = cipher.decrypt(encrypted_token).decode()
                    return token
                except:
                    # Bad token info
                    return ""
            case _:
                return ""
            
    # Function to return the current releases
    def get_releases(self, url):
        # Try to make the request with the stored token
        headers = {
            "Authorization": "token {}".format(self.token), 
            "Accept": "application/vnd.github.v3+json"
        }
        # If the authenticator token has already been confirmed then just use it, otherwise test each option until one is set
        if self.token_confirmed:
            return requests.get(url=url, headers=headers)
        
        test_response = requests.get(url=url, headers=headers)
        if test_response.ok:
            self.token_confirmed = True
            return "base", test_response

        # If the response was bad then try using a server token instead
        self.token = self.load_token(storage="server")
        headers = {
            "Authorization": "token {}".format(self.token), 
            "Accept": "application/vnd.github.v3+json"
        }
        test_response = requests.get(url=url, headers=headers)
        if test_response.ok:
            self.token_confirmed = True
            return "server", test_response
        
        # If the response was still bad then try using a recovery token instead, if this is bad then let it fail
        self.token = self.load_token(storage="recovery")
        headers = {
            "Authorization": "token {}".format(self.token), 
            "Accept": "application/vnd.github.v3+json"
        }
        test_response = requests.get(url=url, headers=headers)
        if test_response.ok:
            self.token_confirmed = True
        return "recovery", test_response
    
    # Function to get a download
    def get_download(self, url):
        # if a token is confirmed from previous use then just use it an continue
        if self.token_confirmed:
            headers = {
                "Authorization": "token {}".format(self.token), 
                "Accept": "application/octet-stream"
            }
            return requests.get(url=url, headers=headers)
        
        # If a token is not yet confirmed then test each option in turn 
        # Try to make the request with the stored token
        headers = {
            "Authorization": "token {}".format(self.token), 
            "Accept": "application/octet-stream"
        }
        test_response = requests.get(url=url, headers=headers)
        if test_response.ok:
            self.token_confirmed = True
            return test_response

        # If the response was bad then try using a server token instead
        self.token = self.load_token(storage="server")
        headers = {
            "Authorization": "token {}".format(self.token), 
            "Accept": "application/octet-stream"
        }
        test_response = requests.get(url=url, headers=headers)
        if test_response.ok:
            self.token_confirmed = True
            return test_response
        
        # If the response was still bad then try using a recovery token instead, if this is bad then let it fail
        self.token = self.load_token(storage="recovery")
        headers = {
            "Authorization": "token {}".format(self.token), 
            "Accept": "application/octet-stream"
        }
        test_response = requests.get(url=url, headers=headers)
        if test_response.ok:
            self.token_confirmed = True
        return test_response