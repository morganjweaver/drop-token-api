## Summary

An implementation of Drop Token, a highly Connect-4-like game. The game is run as a 
RESTful API on a simple Flask server sitting behind a gunicorn WSGI for concurrency support.  

## Design Notes

See specific sections.  General structure has been designed defensively, with fault-tolerance in mind--eg, returning bools for many 
functions that may not explicitly need to in order to perform their task, as well as some redundancy in error checking. 

Many expansion points were acknowledged--for larger board sizes, more players, more complex scoring and functionality, but 
this iteration focuses on the basic requirements, assuming horizontal rather than vertical scaling. Notes in the code and 
other details (such as BASIC_BOARD_MODE in api.py and the data_store abstract class + child class) hint at sockets for easy expansion. 

### Data Store:
Though a production database would be required for 
scalability, here there is an abstract parent class for the datastore which functions a bit like an interface, as 
Python is a bit less OO-friendly than Java.  The fake database is actually a pickled Python dictionary. Never fear--
we can instantiate a child class and have it hooked up to AWS Dynamo faster than you can say 'boto3'!

## Developer Setup

Install requirements:
`pip3 install -r requirements.txt`
Let gunicorn handle booting the app + multithreading:
`gunicorn api:app -w 1 --threads 12` 
Hate unicorns and multithreading?  Use plain old Python instead to run with a single, snakey thread:
`python api.py`

### Now it's time to play some games!

Hint: To check the response status instead of text-only, add `-I` to the end of the cURL command

Begin a game:
`curl --header "Content-type: Application/json" -X POST http://127.0.0.1:8000/drop_token -d'{ "players":["A", "B"], "rows":4, "columns":4}'`

Post a move:
`curl --header "Content-type: Application/json" -X POST http://127.0.0.1:8000/drop_token/2740bbc/B -d'{ "column":1}`

Check game status (this is a preloaded game for demo purposes, but you can replace the gameID with your own):
`curl --header "Content-type: Application/json" -X GET http://127.0.0.1:8000/drop_token/2740bbc`

See all games:
`curl --header "Content-type: Application/json" -X GET http://127.0.0.1:8000/drop_token`

Quit your game!
`curl --header "Content-type: Application/json" -X DELETE http://127.0.0.1:8000/drop_token/2740bbc/M`

Get details of all gameplay actions:
`curl --header "Content-type: Application/json" -X GET http://127.0.0.1:8000/drop_token/moves/2740bbc`

Get details of a particular move: 
`curl --header "Content-type: Application/json" -X GET http://127.0.0.1:8000/drop_token/moves/2740bbc/2`

## Things I Would Do With > 8 Hours:

* More focus on potential security issues--some folks get real ticklish about their wins/losses
* Finer attention to separation of responsibility in API functions vs data store vs game
* Hook up a proper AWS/GCP/etc. database so we need not worry about muddling our pickle file, which is not thread-safe
* There are 1-2 places where there is an offset for zero-indexing correction--I left notes, but it would be nicer to 
do this in an elegant and automatic manner so that future devs need not worry about off-by-one errors
* Python doesn't really do structs natively....rewrite the whole thing in C++?
* Implement the specific move range API functionality--it's 1 AM and I've decided to prioritize documentation, because it
is the sane and polite thing to do.  *If no one can understand even the best code in the world, what's the point?*
* Additional testing/validation.  Units, integration, etc. Test automation.
* A CI/CD pipeline would be cool.  GitLab, anyone?
* Additional attention to OO principles

## API Reference
See API ref in enclosed PDF file. 

## General OO Principles Acknowledged and Attempted:

_SOLID+_

Single-responsibility or separation of concerns
Open/Closed Principle (open to/easy extension, closed to modifications)
Liskov Substitution Principle: Subclasses should be able to replace their parents
Interface Segregation Principle: "Many client-specific interfaces are better than one general-purpose interface."
Dependency Inversion Principle: Depend upon abstractions, not concretions.  (e.g, Data Store abstraction)

BONUS! Command-Query Separation (Ok, more imperative than OO, but it makes for tidier code): Commands that perform actions 
shouldn't return query info.  Queries shouldn't change state.  Example: getters vs setters. 