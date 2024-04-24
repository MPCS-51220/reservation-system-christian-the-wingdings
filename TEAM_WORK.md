# Team Work Document


## Describe the process your team used to decide who was going to do what.  This might have been very informal. That's OK. Just explain how the decisions were made. The description doesn't have to be long, but please be accurate.

This week we decided by all getting on a zoom call and delimiting the work in an organized fashion. The first step in this process was to figure out what final product we needed, and what objects had to be completed to get us to that end goal. The final goal is pretty clear to us, as we had all previously done the reservation system without FastAPI. So, the product we needed was:
The Reservation System
A FastAPI backend supporting the reservation system data
A console client as a frontend for users to interact with

From here, our process was to come up with tasks and spread them out over the group members. To do this, we came up with a list of API endpoints that had to be implemented as our backbone of the project. The logic is that the reservation system functionality and rules will be implemented in order to make certain endpoints work properly, and so by assigning different endpoints to different members we can delineate the tasks related to the reservation system as well as the FastAPI backend.

In the end, the process was relatively informal but did a good job of splitting up the work equally and at natural break points.


## Then, describe the breakdown of the work - list the tasks and who did (or will do) them. NOTE: In future weeks, you'll use JIRA for tracking allocations and status, but for this week that's not required. If you are comfortable using it this week, you may. (You could even document the work in JIRA after the fact if you've already done it.)

As briefly mentioned above, the breakdown of the work relied on splitting up the endpoints that we came up with, and then doing all code logic for the reservation system associated with those endpoints as well.

We came up with 5 specific API endpoints to complete the reservation system specifications. They are in this table depicted below:

REST API Summary


GET

/reservations?start=start&end=end?

dictionary of lists all reservations


POST

/reservations?params=params

Created new reservation || could not create reservation due to schedule conflict (list of errors)


GET

/reservations/customers/{customer_name}?start=start&end=end?

dictionary of reservations for the customer by date.


GET

/reservations/machines/{machine_name}?start=start&end=end?

Dictionary of reservations by machine name


DELETE

/reservations/{id}

Successfully canceled reservation



We assigned the last two GET methods to Chrstian, the first GET and DELETE to Akshatha, and the one POST to Graham. The POST request was the most logically intense, so that is why we assigned it alone. By filling out all necessary methods and classes to complete the requests, the reservations system logic got pretty evenly split by having this distribution of endpoints to each person. One other thing to mention is that everyone constructed their own tests for their own API endpoints, as it made the most sense to do it that way.

Additionally, we split up the rest of the tasks not covered with the endpoints. Christian did this document, Akshatha did the console client, and Graham did the README.


## Describe the strategy that your team is using this week to avoid collisions in GitHub. e.g., have you agreed on any standards for branching? 

By splitting up the work into different endpoints, we were able to naturally have less overlap on who was doing what code. Graham made a class file (modules.py), and a main file with FastAPI (main.py), to which we could add our methods and class definitions. With this skeleton code, we were able to instantiate things and add endpoints without causing any major conflicts over one another, because we were all cognizant of what the others were doing and limited stepping into anyone else’s code.

We are currently working on standards for branching, though generally whenever someone has a designated section for work or a new feature to implement, they will make a new branch. For this week’s assignment, we started with doing one branch per person for their own changes, but ultimately we ended up adding more branches to confirm our pull requests and do additional features. The idea is when a new branch is created, it should not overlap with other branches much, which will help avoid collisions. Then, we can more easily check each other’s branches before we merge back to main. With a more complex system we will probably do multiple rounds of branches per person for each change or group of changes we make. This project was a bit smaller so we could get away with less overall branches and less rounds of changes per person.

One last thing to mention is that we have a system for who checks others’ branches to make sure the merged changes were okay. Currently, we have it in a cycle where Chrisitan checks Graham, Graham checks Akshatha, and Akshatha checks Christian. After we met to agree on how we use pull requests, we implemented this system. We are still practicing with it, and so it may evolve over future projects.


## Finally, add any other details about your processes. How did you coordinate the work? How did you communicate with each other? etc.

A lot of our coordination happened via slack. We messaged quite often for confirmation about how we were progressing through the work as well as any other small changes or clarifications we needed to make about the code or project as a whole. Also as mentioned earlier, we had multiple zoom meetings to clarify work distributions, figure out pull requests, and also flesh out any other details for what we had to do.

Our process is pretty well-defined as stated above, but we are definitely still getting acclimated to working in the group/project-based environment with github and pull requests, so parts of the process may be tweaked over time. However, generally the process is systematic and efficient.
