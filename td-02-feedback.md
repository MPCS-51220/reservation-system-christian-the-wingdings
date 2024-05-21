# Team Assignment 2

## Client 10/10 pts
- Client successfully completes the task 10/10

## Server 9/10 pts
- Data Persistence 3/3
- Username login/authentication 3/3
- Api 2/2
- Tests 1/2


## Documentation 5 / 5pts
Code is well documented, readme is easy to follow
- Clean, useful code comments 3/3
- Readme is easy to follow and reflects code committed 2/2


## Style/Quality 5pts
Code style, quality and syntax
- Code is clean and organized 2/2
- Functions are concise and logically consistent 2/2
- Code is easy to follow 1/1

Notes
- Don't leave big blocks of commented out code in your code. (main.py line 30+)
- some issues with tests, I don't see a /login route for the test_user roles test?
FAILED test_main.py::test_user_roles[admin-adminpass-admin] - assert 404 == 200
FAILED test_main.py::test_user_roles[user-userpass-user] - assert 404 == 200
FAILED test_main.py::test_user_roles[guest-guestpass-guest] - assert 404 == 200
FAILED test_main.py::test_get_reservations_by_customer_with_dates - AssertionError: assert 'reservations' in {'message': 'No reservations found for this customer.'}
FAILED test_main.py::test_cancel_invalid_reservation - assert 500 == 404
=========================================================================== 5 failed, 7 passed in 1.11s ===========================================================================