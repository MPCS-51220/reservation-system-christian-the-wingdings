$(document).ready(function() {
    class LoginForm {
        constructor(formContainerId) {
            this.formContainer = document.getElementById(formContainerId);
            this.menuContainer = document.getElementById('menu-container');
            this.commandContainer = document.getElementById('command-container');
            this.resultsContainer = document.getElementById('results-container');
            this.initialize();
            this.hideAll();
        }

        initialize() {
            this.fetchLoginFormConfig();
        }

        fetchLoginFormConfig() {
            fetch('/login-form')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        this.displayError(data.error);
                    } else {
                        this.buildLoginForm(data);
                        this.showOnly(this.formContainer);
                    }
                })
                .catch(error => {
                    console.error('Error fetching login form:', error);
                    this.displayError('Error loading login form. Please try again later.');
                });
        }

        displayError(message) {
            this.formContainer.innerHTML = `<p>${message}</p>`;
        }

        buildLoginForm(formConfig) {
            console.log('Form config:', formConfig);
            const form = document.createElement('form');
            form.setAttribute('id', 'login-form');
            formConfig.commands.forEach(command => {
                command.inputs.forEach(input => {
                    const label = document.createElement('label');
                    label.textContent = input.prompt;
                    if (!input.optional) {
                        label.classList.add('required');
                    }
                    form.appendChild(label);

                    let inputField;
                    if (input.validate === 'enum') {
                        inputField = document.createElement('select');
                        inputField.classList.add(input.optional ? 'optional' : 'required');

                        if (input.optional) {
                            const blankOption = document.createElement('option');
                            blankOption.value = "";
                            blankOption.textContent = "";
                            inputField.appendChild(blankOption);
                        }

                        input.options.forEach(option => {
                            const optionElement = document.createElement('option');
                            optionElement.value = option;
                            optionElement.textContent = option;
                            inputField.appendChild(optionElement);
                        });
                    } else {
                        inputField = document.createElement('input');
                        inputField.setAttribute('type', input.tag === 'password' ? 'password' : 'text');
                    }

                    inputField.setAttribute('name', input.tag);
                    if (!input.optional) {
                        inputField.setAttribute('required', true);
                    }
                    form.appendChild(inputField);
                    form.appendChild(document.createElement('br'));
                });

                const submitButton = document.createElement('button');
                submitButton.setAttribute('type', 'submit');
                submitButton.textContent = 'Login';
                form.appendChild(submitButton);

                this.formContainer.appendChild(form);

                // Add event listener for form submission
                form.addEventListener('submit', (event) => this.handleSubmit(event, form, command));
            });
        }

        handleSubmit(event, form, command) {
            event.preventDefault();
            const formData = new FormData(form);
            const jsonData = {};
            formData.forEach((value, key) => {
                jsonData[key] = value;
            });

            // Send login request
            fetch(command.route, {
                method: command.method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.access_token) {
                    localStorage.setItem('token', data.access_token);
                    this.buildInterface(data.interface);
                    this.showOnly(this.menuContainer);
                } else {
                    this.displayError('Login failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error during login:', error);
            });
        }

        buildInterface(menuJson) {
            const menuContainer = document.getElementById('menu-container');
            menuContainer.innerHTML = ''; // Clear any existing menu items

            menuJson.commands.forEach(command => {
                const menuItem = document.createElement('li');
                menuItem.textContent = command.name;
                menuItem.dataset.command = JSON.stringify(command);
                menuItem.addEventListener('click', () => {
                    if (command.name.toLowerCase() === 'logout') {
                        this.logout();
                    } else {
                        this.executeCommand(command);
                        this.highlightMenuItem(menuItem);
                        this.showCommandAndHideResults();
                    }
                });
                menuContainer.appendChild(menuItem);
            });
            menuContainer.classList.remove('hide');
        }

        logout() {
            const token = localStorage.getItem('token');
            fetch('/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (response.ok) {
                    localStorage.removeItem('token');
                    window.location.href = '/';
                } else {
                    console.error('Logout failed');
                }
            })
            .catch(error => {
                console.error('Error during logout:', error);
            });
        }

        executeCommand(command) {
            const commandContainer = document.getElementById('command-container');
            commandContainer.innerHTML = ''; // Clear existing command form

            const form = document.createElement('form');
            form.setAttribute('id', 'command-form');

            command.inputs.forEach(input => {
                const label = document.createElement('label');
                label.textContent = input.prompt;
                if (!input.optional) {
                    label.classList.add('required');
                }
                form.appendChild(label);

                let inputField;
                if (input.validate === 'enum') {
                    inputField = document.createElement('select');
                    inputField.classList.add(input.optional ? 'optional' : 'required');

                    if (input.optional) {
                        const blankOption = document.createElement('option');
                        blankOption.value = "";
                        blankOption.textContent = "";
                        inputField.appendChild(blankOption);
                    }

                    input.options.forEach(option => {
                        const optionElement = document.createElement('option');
                        optionElement.value = option;
                        optionElement.textContent = option;
                        inputField.appendChild(optionElement);
                    });
                } else {
                    inputField = document.createElement('input');
                    inputField.setAttribute('type', input.validate === 'password' ? 'password' : 'text');
                }

                inputField.setAttribute('name', input.tag);
                if (!input.optional) {
                    inputField.setAttribute('required', true);
                }
                form.appendChild(inputField);
                form.appendChild(document.createElement('br'));
            });

            const submitButton = document.createElement('button');
            submitButton.setAttribute('type', 'submit');
            submitButton.textContent = 'Submit';
            form.appendChild(submitButton);

            commandContainer.appendChild(form);

            form.addEventListener('submit', (event) => this.handleCommandSubmit(event, form, command));
            commandContainer.classList.remove('hide');
        }

        handleCommandSubmit(event, form, command) {
            event.preventDefault();
            const formData = new FormData(form);
            const jsonData = {};
            formData.forEach((value, key) => {
                jsonData[key] = value;
            });

            const accessToken = localStorage.getItem('token');

            let url = command.route;
            let fetchOptions = {
                method: command.method,
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            };

            if (command.method.toLowerCase() === 'get' || command.method.toLowerCase() === 'delete') {
                // Include only non-empty values and optional parameters
                const queryParams = {};
                command.inputs.forEach(input => {
                    const value = jsonData[input.tag];
                    if (value && (input.optional || value.trim() !== '')) {
                        queryParams[input.tag] = value;
                    }
                });
                url += '?' + new URLSearchParams(queryParams).toString();
            } else {
                fetchOptions.headers['Content-Type'] = 'application/json';
                fetchOptions.body = JSON.stringify(jsonData);
            }

            fetch(url, fetchOptions)
            .then(response => response.json())
            .then(data => {
                console.log('Command response:', data);
                this.displayResults(data);
                this.showResults();
            })
            .catch(error => {
                console.error('Error executing command:', error);
            });
        }

        displayResults(results) {
            const resultsContainer = document.getElementById('results-container');
            resultsContainer.innerHTML = ''; // Clear existing results

            const createCard = (item) => {
                const card = document.createElement('div');
                card.className = 'result-card';
                for (const [key, value] of Object.entries(item)) {
                    const paragraph = document.createElement('p');
                    if (typeof value === 'object' && value !== null) {
                        paragraph.textContent = `${key}:`;
                        const nestedDiv = document.createElement('div');
                        nestedDiv.className = 'nested-result';
                        for (const [nestedKey, nestedValue] of Object.entries(value)) {
                            const nestedParagraph = document.createElement('p');
                            nestedParagraph.textContent = `${nestedKey}: ${nestedValue}`;
                            nestedDiv.appendChild(nestedParagraph);
                        }
                        paragraph.appendChild(nestedDiv);
                    } else {
                        paragraph.textContent = `${key}: ${value}`;
                    }
                    card.appendChild(paragraph);
                }
                return card;
            };

            if (Array.isArray(results)) {
                results.forEach(item => {
                    resultsContainer.appendChild(createCard(item));
                });
            } else {
                for (const [key, value] of Object.entries(results)) {
                    if (Array.isArray(value)) {
                        value.forEach(item => {
                            resultsContainer.appendChild(createCard(item));
                        });
                    } else {
                        resultsContainer.appendChild(createCard({ [key]: value }));
                    }
                }
            }
            resultsContainer.classList.remove('hide');
        }

        showOnly(element) {
            [this.formContainer, this.menuContainer, this.commandContainer, this.resultsContainer].forEach(el => {
                if (el === element) {
                    el.classList.remove('hide');
                } else {
                    el.classList.add('hide');
                }
            });
        }

        hideAll() {
            [this.formContainer, this.menuContainer, this.commandContainer, this.resultsContainer].forEach(el => {
                el.classList.add('hide');
            });
        }

        showCommandAndHideResults() {
            this.commandContainer.classList.remove('hide');
            this.resultsContainer.classList.add('hide');
        }

        showResults() {
            this.resultsContainer.classList.remove('hide');
        }

        highlightMenuItem(menuItem) {
            document.querySelectorAll('#menu-container li').forEach(item => {
                item.classList.remove('highlight');
            });
            menuItem.classList.add('highlight');
        }
    }

    // Initialize the LoginForm with the ID of the container element
    const loginForm = new LoginForm('login-form-container');
});
