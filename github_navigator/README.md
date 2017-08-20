Small proof-of-concept WSGI application to search GitHub repositories that uses 
the bundled-in wsgiref Python implementation to set up a WSGI server. 

wsgiref implements the WSGI specification (PEP 333). 

	https://docs.python.org/3.6/library/wsgiref.html
	https://www.python.org/dev/peps/pep-0333/called GitHub navigator. 

The tool is able to search GitHub repositories by a given search term and present 
the results as an html page. The tool takes one parameter "search_term" as input an 
it queries GitHub API with this search_term to look for repositories. Then it takes 
the first page of search results and sort the items by the creation date in 
descending order. The info about first 5 (newest) repositories is rendered into 
an html template together with some information about latest commit in this 
repository.

Example output can be seen on example.html.

Steps:

    1. Install Python (app tested on Python 3.x).

    2. Install the requests library
        1. Install Pip if it is not installed
            - Download get-pip.py
            https://pip.pypa.io/en/stable/installing/
            - Run python 'get-pip.py' from command line to install pip
        2. Install Requests (latest version available)
            - Run 'pip install requests' from command line
            
    3. Run 'python application.py' to start the WSGI server. The server will
    start listening on Port 8555. If 8555 is being used by another program
    edit the PORT constant in 'application.py' and set an unused port.
	
    4. Open a browser and do a GET request to
    'http://localhost:8555/?search_term=<value>'
    (i.e: http://localhost:8555/?search_term=arrow)
	
    5. A template.html for the given search_term will be generated on the application
    directory and the results will be displayed.



		
		
		
		