#
# Author: Carmelo del Coso Ameijide
# Email: carmelodelcoso@gmail.com
#

from datetime import datetime
from html import escape
import requests
import sys
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server


HOST = "localhost"
PORT = 8555

# https://developer.github.com/v3/search/#search-repositories
REPO_SEARCH_URL = 'https://api.github.com/search/repositories'
# https://developer.github.com/v3/repos/commits/
REPO_COMMIT_URL = 'https://api.github.com/repos/'


# GitHub API date is written in ISO 8601 format (i.e: 2016-02-17T08:00:23Z).
# I need to transform it to '2016-02-17 08:00:23' as per project requirements.
def datetime_converter(git_date):
    date = datetime.strptime(str(git_date), "%Y-%m-%dT%H:%M:%SZ")
    return date.strftime('%Y-%m-%d %H:%M:%S')


def get_rep_by_search_term(search_term):

    # Query GitHub API with this search_term to look for repositories and show
    # them in descending order.
    payload = {'q': search_term, 'order': 'desc'}
    req_repo = requests.get(REPO_SEARCH_URL, params=payload)

    # Take first 5 (newest) repositories.
    data_newest = req_repo.json()['items'][0:5]

    # For each repo, retrieve last commit.
    # [{sha} {commit_message} {commit_author_name}].
    for entry in data_newest:

        owner = entry['owner']['login']
        repo = entry['name']

        # Get commits
        req_commit = \
            requests.get(REPO_COMMIT_URL + owner + '/' + repo + '/commits').json()

        # Get last req_commit (first one, position 0).
        extra_entries = {
            'sha': req_commit[0]['sha'],
            'commit_author_name': req_commit[0]['commit']['author']['name'],
            'commit_message': req_commit[0]['commit']['message']
        }
        entry.update(extra_entries)

        entry['created_at'] = datetime_converter(entry['created_at'])

    # Sort items by creation date in descending order.
    sorted_results = sorted(data_newest, key=lambda x: x['created_at'], reverse=True)

    return sorted_results


def generate_template(results, search_term):

    # Generate the template
    html = ''
    html += '<!DOCTYPE html >'
    html += '<html lang="en">'
    html += '<head>'
    html += '<title> Github Navigator </title >'
    html += '<meta name="author" content="Carmelo del Coso Ameijide">'
    html += '<meta name="email" content="carmelodelcoso@gmail.com">'
    html += '</head>'
    html += '<body>'
    html += '<div>'
    html += '<h1>' + search_term + '</h1>'

    for i in range(0, len(results)):
        html += '<h2>' + str(i + 1) + ' ' + results[i]['name'] + '</h2>'
        html += '<h3> Created ' + results[i]['created_at'] + '</h3>'
        html += '<a href=\"' + results[i]['owner']['html_url'] + \
                '\"> <img src=\"' + \
                results[i]['owner']['avatar_url'] + \
                '" alt=\"avatar\" height=\"42\" width=\"42\"/></a> '
        html += results[i]['owner']['login']
        html += '<h3> LastCommit </h3>'
        html += 'SHA: ' + results[i]['sha'] + '</br>'
        html += 'AUTHOR: ' + results[i]['commit_author_name'] + '</br>'
        html += 'MESSAGE: ' + results[i]['commit_message'] + '</br>'
        html += '<hr/>'

    html += '</div>'
    html += '</body>'
    html += '</html>'

    # Write the file, as per requirements
    text_file = open("template.html", "w")
    text_file.write(html)
    text_file.close()

    return html


def application(environ, start_response):

    # Pass the client GET request to the application.
    param_dictionary = parse_qs(environ['QUERY_STRING'])

    # Get the the search_term field from the request and sanitize it (escape).
    search_term = escape(param_dictionary.get('search_term', [''])[0])

    if search_term:

        # Generate the response data.
        results = get_rep_by_search_term(search_term)

        # Generate the html template and save it.
        response = generate_template(results, search_term)

        try:
            # Define the HTTP headers and status to send back to the server.
            status = '200 OK'
            headers = [('Content-Type', 'text/html; charset=utf-8')]

            # Call the start_response callable to initiate the server response.
            start_response(status, headers)

            # Send the response body back to the server, as an iterable.
            # The response is wrapped into a list, so the server
            # doesn't send it one byte at a time (slower).
            # The response needs to be encoded as UTF-8 to
            # ensure that is sent correctly.
            return [response.encode("utf-8")]
        except:
            # Something went wrong. Use sys.exc_info to show
            # the error trapped by the application.
            # Before this generic except clause, specific error handlers
            # could be defined to detect and print custom messages for
            # exceptions like MemoryError, KeyboardInterrupt, etc.
            status = "500 Internal Error"
            headers = [('content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers, sys.exc_info())
            return ["Error".encode("utf-8")]
    else:
        # No search_term was provided. Return 404.
        start_response('404 NOT FOUND', [('Content-Type',
                                          'text/plain; charset=utf-8')])
        return ['Not Found'.encode("utf-8")]

# Instantiate the server.
httpd = make_server(HOST, PORT, application)
print("Server listening on port " + str(PORT))

# Respond to requests until process is killed.
httpd.serve_forever()
