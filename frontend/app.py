import requests
from requests.exceptions import RequestException
import urllib.parse
from functools import wraps 

# This dictionary is to be refactored into a command validating class and the dictionary text, so the later can be
# kept on the server with only valid commands per role being returned to the client for display.
# Would probably also be easier to reproduce the lambda functions via javascript but i'd have to look into that.
menu = {
        "commands": [
            {
                "name": "Login",
                "roles": None,
                "route": "/login",
                "method": "POST",
                "inputs": [
                    {
                        "prompt": "username: ",
                        "tag": "username",
                        "validate": "string",
                        "error_message": "Username must be a valid string."
                    },
                    {
                        "prompt": "password: ",
                        "tag": "password",
                        "validate": "string",
                        "error_message": "Invalid Password format. Please try again."
                    }
                ]
            },{
                "name": "Make reservation",
                "roles": ["admin", "scheduler", "customer"],
                "route": "/reservations",
                "method": "POST",
                "inputs": [
                    {
                        "prompt": "Enter start date (YYYY-MM-DD HH:MM)",
                        "tag": "start_date",
                        "validate": "datetime",
                        "error_message": "Invalid date format or past date entered. Please try again."
                    },
                    {
                        "prompt": "Enter end date (YYYY-MM-DD HH:MM)",
                        "tag": "end_date",
                        "validate": "datetime",
                        "error_message": "Invalid date format or past date entered. Please try again."
                    },
                    {
                        "prompt": "Select the machine type",
                        "tag": "machine",
                        "validate": "enum",
                        "options": ["Type A", "Type B", "Type C"],
                        "error_message": "Invalid machine type selected. Please try again."
                    },
                    {
                        "prompt": "Enter customer name",
                        "tag": "customer",
                        "roles": ["admin", "scheduler"],
                        "validate": "string",
                        "error_message": "Invalid name entered. Please try again."
                    }
                ]
            },
            {
                "name": "Cancel reservation",
                "roles": ["admin", "scheduler", "customer"],
                "route": "/reservation",
                "method": "DELETE",
                "inputs": [
                    {
                        "prompt": "Enter the reservation ID to cancel",
                        "tag": "reservation_id",
                        "validate": "integer",
                        "error_message": "Invalid reservation ID. Please enter a positive integer."
                    }
                ]
            },
            {
                "name": "List reservations by customer and date",
                "roles": ["admin", "scheduler", "customer"],
                "route": "/reservations/customers",
                "method": "GET",
                "inputs": [
                    {
                        "prompt": "Enter start date (YYYY-MM-DD)",
                        "tag": "start_date",
                        "validate": "date",
                        "error_message": "Invalid start date. Please try again."
                    },
                    {
                        "prompt": "Enter end date (YYYY-MM-DD)",
                        "tag": "end_date",
                        "validate": "date",
                        "error_message": "Invalid end date. Please try again."
                    },
                    # {
                    #     "prompt": "Select the machine type",
                    #     "validate": "enum",
                    #     "options": ["Type A", "Type B", "Type C"],
                    #     "error_message": "Invalid machine type selected. Please try again."
                    # },
                    {
                        "prompt": "Enter customer name",
                        "roles": ["admin", "scheduler"],
                        "tag": "customer",
                        "validate": "string",
                        "error_message": "Invalid name entered. Please try again."
                    }
                ]
            },
            {
                "name": "List reservations by machine and date",
                "roles": ["admin", "scheduler", "customer"],
                "route": "/reservations/machines",
                "method": "GET",
                "inputs": [
                    {
                        "prompt": "Enter start date (YYYY-MM-DD)",
                        "tag": "start_date",
                        "validate": "date",
                        "error_message": "Invalid start date. Please try again."
                    },
                    {
                        "prompt": "Enter end date (YYYY-MM-DD)",
                        "tag": "end_date",
                        "validate": "date",
                        "error_message": "Invalid end date. Please try again."
                    },
                    {
                        "prompt": "Select the machine type",
                        "tag": "machine",
                        "validate": "enum",
                        "options": ["scanner", "Type B", "Type C"],
                        "error_message": "Invalid machine type selected. Please try again."
                    }
                    # {
                    #     "prompt": "Enter customer name",
                    #     "roles": ["admin", "scheduler"],
                    #     "tag": "customer_name",
                    #     "validate": "string",
                    #     "error_message": "Invalid name entered. Please try again."
                    # }
                ]
            },
            {
                "name": "Change My Password",
                "roles": ["admin", "scheduler", "customer"],
                "route": "/change-password",
                "method": "POST",
                "inputs": [
                    {
                        "prompt": "Enter your old password",
                        "tag": "old_password",
                        "validate": "password",
                        "error_message": "Invalid password format. Please try again."
                    },
                    {
                        "prompt": "Enter your new password",
                        "tag": "new_password",
                        "validate": "password",
                        "error_message": "Invalid password format. Please try again."
                    }
                ]
            },
            {
                "name": "Logout",
                "route": "/logout",
                "method": "POST",
                "roles": ["admin", "scheduler", "customer"]
            },
            {
                "name": "Exit",
                "roles": ["admin", "scheduler", "customer"]
            },
            {
                "name": "Add user",
                "roles": ["admin"],
                "route": "/users",
                "method": "POST",
                "inputs": [
                    {
                        "prompt": "Enter new username",
                        "tag": "username",
                        "validate": "string",
                        "error_message": "Invalid username. Please try again."
                    },
                    {
                        "prompt": "Enter user role (customer, scheduler, admin)",
                        "tag": "role",
                        "validate": "enum",
                        "options": ["customer", "scheduler", "admin"],
                        "error_message": "Invalid role. Please select from customer, scheduler, admin."
                    },
                    {
                        "prompt": "Enter new password",
                        "tag": "password",
                        "validate": lambda x: len(x) > 0,
                        "error_message": "Invalid password format. Please try again."
                    },
                    {
                        "prompt": "Salt",
                        "tag": "salt",
                        "validate": "string",
                        "error_message": "Invalid password format. Please try again."
                    }
                ]
            },
            {
                "name": "Remove user",
                "roles": ["admin"],
                "route": "/users",
                "method": "DELETE",
                "inputs": [
                    {
                        "prompt": "Enter username of the user to remove",
                        "tag": "username",
                        "validate": "string",
                        "error_message": "Invalid username. Please try again."
                    }
                ]
            },
            {
                "name": "Change user role",
                "roles": ["admin"],
                "route": "/users",
                "method": "POST",
                "inputs": [
                    {
                        "prompt": "Enter username of the user to change role",
                        "tag": "username",
                        "validate": "string",
                        "error_message": "Invalid username. Please try again."
                    },
                    {
                        "prompt": "Enter new role (customer, scheduler, admin)",
                        "tag": "new_role",
                        "validate": "enum",
                        "options": ["customer", "scheduler", "admin"],
                        "error_message": "Invalid role. Please select from customer, scheduler, admin."
                    }
                ]
            },
            {
                "name": "Reset Password",
                "roles": ["admin"],
                "route": "/reset-password",
                "method": "POST",
                "inputs": [
                    {
                        "prompt": "Enter username for password reset",
                        "tag": "username",
                        "validate": "string",
                        "error_message": "Invalid username. Please try again."
                    }
                ]
            }
        ]
    }


class APIHandler:
    '''
    This class is responsible for making requests to the backend API.

    Attributes:
        base_url (str): The base URL of the API.
        headers (dict): The headers to be sent with each request.
    
    Methods:
        set_token(token): Sets the token in the headers for authorization once recieved from logging in
        make_request(command, data): Makes a request to the API with the given command (from menu) and data (from user input).
    '''
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {}

    def set_token(self, token):
        self.headers['Authorization'] = f'Bearer {token}'

    def make_request(self, command, data):
        '''
        make_request makes a request to the API with the given command and data.
        
        Args:
            command (dict): The command to be executed from the menu. 
        Formatted { name: str,
                    roles: list,
                    route: str, 
                    method: str, 
                    inputs: list of dicts }
        data (dict): The data to be sent with the request. Formatted { tag: value }.

        Returns:
            JSON: The response from the API as a JSON object.
        '''
        headers = self.headers
        method = getattr(requests, command["method"].lower(), requests.post)
        call_method = command["method"].lower()
        print(f'data = {data}')
        try:
            if call_method == 'get' or call_method == 'delete':
                response = method(f'{self.base_url}{command["route"]}', params=data, headers=headers)
            else:
                response = method(f'{self.base_url}{command["route"]}', json=data, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.json()      
        
        except RequestException as e:
            print(f"Request failed: {e}")
            return None

def retry_input(input_def):
    '''
    retry_input is a decorator that prompts the user for input and retries until the input is valid or 'exit' is entered.
    The input_def dictionary contains the prompt, validation function, and error message for the input.
    Args:
        input_def (dict): Formatted: {  prompt: str,
                                        tag: str,
                                        validate: function, 
                                        error_message: str }
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                print(f'wrapper running and input_def = {input_def}\n')
                user_input = input(input_def["prompt"])
                if user_input.lower() == 'exit':
                    return None
           #     if input_def["validate"](user_input):
                else:
                    return func(*args, **kwargs, user_input=user_input)
                # print(input_def["error_message"])
        return wrapper
    return decorator

class CLI:
    '''
    This class is responsible for handling the command line interface for the user.

    Attributes:
        api_handler (APIHandler): The APIHandler object for making requests to the backend.
        is_active (bool): A flag to determine if the CLI is still active.
    
    Methods:
        select_command(): Prompts the user to select a command from the menu dictionary
        run(): Runs the CLI and prompts the user for input of command index until the user types 'exit'
    '''
    def __init__(self, api_handler):
        self.api_handler = api_handler
        self.is_active = True

    # @retry_input({"prompt": "Select a command or type 'exit' to quit: ", "validate": lambda x: x.isdigit()})
    def select_command(self):
        '''
        select_command prompts the user to select a command from the menu dictionary.

        Returns:
            int: The index of the selected command in the menu dictionary.
        '''
        while True:
            choice = input("Select a command or type 'exit' to quit: ")
            if choice.lower() == 'exit':
                return None
            if choice.isdigit() and 0 < int(choice) <= len(menu["commands"]):
                return int(choice) - 1
            print("Invalid selection, please try again.")


    def run(self):
        '''
        run runs the CLI and prompts the user for input of command index until the user types 'exit'.

        '''
        while self.is_active:
            print("\nAvailable commands:")
            for idx, cmd in enumerate(menu["commands"], 1):
                print(f"{idx}. {cmd['name']}")
            command_index = self.select_command()
            if command_index is None:
                self.is_active = False
                continue
            selected_command = menu["commands"][command_index]
            self.handle_prompt(selected_command)

    def handle_prompt(self, command_index):
        '''
        handle_prompt prompts the user for input based on the selected command's input requirements 
        and sends the data to the API.

        Args:
            command_index (int): The index of the selected command in the menu dictionary.
        
        returns:
            None: If the user types 'exit' during the prompt.
            
        '''
        command = command_index
        data = {}
        call_method = command["method"].lower()
        for input_def in command["inputs"]:
            user_input = self.prompt_input(input_def)
            if user_input is None:  # User typed 'exit'
                return
            if call_method == 'get' or call_method == 'delete':
                data[input_def["tag"]] = urllib.parse.quote(user_input)
            else:
                data[input_def["tag"]] = user_input

        response = self.api_handler.make_request(command, data)
        if command["name"] == "Login" and response:
            self.api_handler.set_token(response['access_token'])
        print("Response:", response if response else "Failed to get a valid response from the server.")


    @retry_input({"prompt": "Select a command or type 'exit' to quit: ", "validate": lambda x: x.isdigit()})
    def select_command(self, user_input):
        '''
        select_command takes the user response to select a command from the menu dictionary.

        Args:
            user_input (str): string representation of int to select a command from the menu dictionary.

        Returns:
            int: _description_
        '''
        command_index = int(user_input) - 1
        if command_index < len(menu["commands"]):
            return command_index
        print("Invalid selection, please try again.")
        return None

    # @retry_input({"prompt": "", "validate": lambda x: True})  # Placeholder for actual validation logic
    def prompt_input(self, input_def):
        while True:
            user_input = input(input_def["prompt"])
            if user_input.lower() == 'exit':
                return None
            # if input_def["validate"](user_input):
            return user_input
            print(input_def["error_message"])


# Main execution
if __name__ == "__main__":
    api_handler = APIHandler('http://localhost:8000')
    cli = CLI(api_handler)
    cli.run()
