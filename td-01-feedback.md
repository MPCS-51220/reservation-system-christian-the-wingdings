# Team Assignment 1

## Client 10/10 pts
- Client successfully completes the task 10/10

## Server 9/10 pts
- Data Persistence 3/3
- Pre-loaded Data 3/3
- Api 2/2
- Tests 1/2


## Documentation 4 / 5pts
Code is well documented, readme is easy to follow
- Clean, useful code comments 3/3
- Readme is easy to follow and reflects code committed 2/2


## Style/Quality 5pts
Code style, quality and syntax
- Code is clean and organized 2/2
- Functions are concise and logically consistent 2/2
- Code is easy to follow 1/1

Notes
- Code wasn't submitted as one PR with all the changes
- Tests are missing some coverage, if you run `pytest --cov=backend backend/test_main.py --cov-report=term-missing` you'll see where there are some gaps in test coverage
```shell
Name                   Stmts   Miss  Cover   Missing
----------------------------------------------------
backend/main.py           73     19    74%   19, 36-37, 47-58, 77, 84-85, 102, 109-110, 136
backend/modules.py       136     36    74%   36, 38, 45, 57, 61, 104-105, 165-179, 184, 188-192, 198, 202, 213-218, 223, 225, 229-230, 234-235, 239, 262
backend/test_main.py      71      2    97%   30, 53
----------------------------------------------------
TOTAL                    280     57    80%

```
- Also your tests should be in a separate folder called `tests` so that it's easier for pytest to pick up and doesn't get counted in the test coverage report