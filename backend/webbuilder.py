import json

class WebBuilder:

    def __init__(self, user_role = 'unverified'):
        self.menu = {
        "commands": [
            {
                "name": "Login",
                "roles": 'unverified',
                "route": "/login",
                "method": "POST",
                "inputs": [
                    {
                        "prompt": "username: ",
                        "tag": "username",
                        "validate": "string",
                        "optional": False,
                        "error_message": "Username must be a valid string."
                    },
                    {
                        "prompt": "password: ",
                        "tag": "password",
                        "validate": "string",
                        "optional": False,
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
                        "optional": False,
                        "error_message": "Invalid date format or past date entered. Please try again."
                    },
                    {
                        "prompt": "Enter end date (YYYY-MM-DD HH:MM)",
                        "tag": "end_date",
                        "validate": "datetime",
                        "optional": False,
                        "error_message": "Invalid date format or past date entered. Please try again."
                    },
                    {
                        "prompt": "Select the machine type",
                        "tag": "machine",
                        "validate": "enum",
                        "options": ["Scanner", "Scooper", "Harvester"],
                        "optional": False,
                        "error_message": "Invalid machine type selected. Please try again."
                    },
                    {
                        "prompt": "Enter customer name",
                        "tag": "customer",
                        "roles": ["admin", "scheduler"],
                        "validate": "string",
                        "optional": False,
                        "error_message": "Invalid name entered. Please try again."
                    }
                ]
            },
            {
                "name": "Cancel reservation",
                "roles": ["admin", "scheduler", "customer"],
                "route": "/reservations",
                "method": "DELETE",
                "inputs": [
                    {
                        "prompt": "Enter the reservation ID to cancel",
                        "tag": "reservation_id",
                        "validate": "integer",
                        "optional": False,
                        "error_message": "Invalid reservation ID. Please enter a positive integer."
                    }
                ]
            },
            {
                "name": "List Reservations", # by customer and date",
                "roles": ["admin", "scheduler", "customer"],
                "route": "/reservations",
                "method": "GET",
                "inputs": [
                    {
                        "prompt": "Enter start date (YYYY-MM-DD HH:MM)",
                        "tag": "start_date",
                        "validate": "date",
                        "optional": False,
                        "error_message": "Invalid start date. Please try again."
                    },
                    {
                        "prompt": "Enter end date (YYYY-MM-DD HH:MM)",
                        "tag": "end_date",
                        "validate": "date",
                        "optional": False,
                        "error_message": "Invalid end date. Please try again."
                    },
                    {
                        "prompt": "Select the machine type",
                        "tag": "machine",
                        "validate": "enum",
                        "options": ["scanner", "scooper", "harvester"],
                        "optional": True,
                        "error_message": "Invalid machine type selected. Please try again."
                    },
                    {
                        "prompt": "Enter customer name",
                        "roles": ["admin", "scheduler"],
                        "tag": "customer",
                        "validate": "string",
                        "optional": True,
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
                "name": "Reset Password",
                "roles": ["admin", "customer"],
                "route": "/users/password",
                "method": "PATCH",
                "inputs": [
                    {
                        "prompt": "Enter the username of the user leave blank to reset your own password",
                        "tag": "username",
                        "roles": ["admin"],
                        "validate": "string",
                        "optional": True,
                        "error_message": "Invalid string format. Please try again."
                    },
                    {
                        "prompt": "Enter new password",
                        "tag": "password",
                        "validate": "password",
                        "optional": False,
                        "error_message": "Invalid password format. Please try again."
                    },
                    {
                        "prompt": "Enter a salt",
                        "tag": "salt",
                        "roles": ["admin"],
                        "validate": "string",
                        "optional": True,
                        "error_message": "Invalid salt format. Please try again."
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
                "route": "/exit",
                "method": "POST",
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
                        "optional": False,
                        "error_message": "Invalid username. Please try again."
                    },
                    {
                        "prompt": "Select user role",
                        "tag": "role",
                        "validate": "enum",
                        "options": ["customer", "scheduler", "admin"],
                        "optional": False,
                        "error_message": "Invalid role. Please select from customer, scheduler, admin."
                    },
                    {
                        "prompt": "Enter new password",
                        "tag": "password",
                        "validate": "password",
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
                        "optional": False,
                        "error_message": "Invalid username. Please try again."
                    }
                ]
            },
            {
                "name": "Change user role",
                "roles": ["admin"],
                "route": "/users/role",
                "method": "PATCH",
                "inputs": [
                    {
                        "prompt": "Enter username of the user to change role",
                        "tag": "username",
                        "validate": "string",
                        "optional": False,
                        "error_message": "Invalid username. Please try again."
                    },
                    {
                        "prompt": "Select new role",
                        "tag": "role",
                        "validate": "enum",
                        "options": ["customer", "scheduler", "admin"],
                        "optional": False,
                        "error_message": "Invalid role. Please select from customer, scheduler, admin."
                    }
                ]
            },
            {
                "name": "Reset Password",
                "roles": ["admin"],
                "route": "/users/password",
                "method": "PATCH",
                "inputs": [
                    {
                        "prompt": "Enter username for password reset",
                        "tag": "username",
                        "validate": "string",
                        "optional": False,
                        "error_message": "Invalid username. Please try again."
                    }
                ]
            },
            {
                "name": "Configure Business Rules",
                "roles": ["admin"],
                "route": "/business-rules",
                "method": "POST",
                "inputs": [
                    {
                        "prompt": "Select the rule",
                        "tag": "rule",
                        "validate": "enum",
                        "options": ["harvester_price", "scooper_price_per_hour",
                                    "scanner_price_per_hour", "number_of_scoopers",
                                    "number_of_scanners", "weekday_start", "weekday_end",
                                    "weekend_start", "weekend_end", "week_refund", "two_day_refund"
                                    ],
                        "optional": False,
                        "error_message": "Invalid rule format. Please try again."
                    },
                    {
                        "prompt": "Enter the value you want for the rule",
                        "tag": "value",
                        "validate": "string",
                        "optional": False,
                        "error_message": "Invalid value format. Please try again."
                    }
                ]
            },
             {
                "name": "Deactivate user",
                "roles": ["admin"],
                "route": "/users/deactivate",
                "method": "PATCH",
                "inputs": [
                    {
                        "prompt": "Enter username to deactivate",
                        "tag": "username",
                        "validate": "string",
                        "optional": False,
                        "error_message": "Invalid username. Please try again."
                    }
                ]
            },
            {
                "name": "Activate user",
                "roles": ["admin"],
                "route": "/users/activate",
                "method": "PATCH",
                "inputs": [
                    {
                        "prompt": "Enter username to activate",
                        "tag": "username",
                        "validate": "string",
                        "optional": False,
                        "error_message": "Invalid username. Please try again."
                    }
                ]
            },
            {
                "name": "List activation state of users",
                "roles": ["admin"],
                "route": "/users",
                # "inputs":[],
                "method": "GET",
            }


        ]
    }
        self.user_role = user_role

    def build_menu(self):
        return self._filter_menu(self.menu, self.user_role)

    def _filter_menu(self, menu, user_role):
        filtered_menu = {"commands": []}
        for command in menu["commands"]:
            if user_role in command["roles"]:
                filtered_command = {
                    "name": command["name"],
                    "route": command["route"],
                    "method": command["method"],
                    "inputs": []
                }
                if "inputs" in command:
                    for input_field in command["inputs"]:
                        if "roles" not in input_field or user_role in input_field["roles"]:
                            filtered_command["inputs"].append(input_field)
                filtered_menu["commands"].append(filtered_command)
        return filtered_menu
