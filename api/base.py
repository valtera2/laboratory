#	Laboratory - Simple GitLab Frontend.
#	Copyright (C) 2023 Ferass El Hafidi
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
from markupsafe import escape
from pycmarkgfm import gfm_to_html as markdown
from base64 import b64decode # For some reason GitLab encodes file contents
import requests

"""
This API "library" basically turns JSON returned by the GitLab API into valid 
HTML5 that is then embedded in Laboratory templates.
"""

def api_call(url):
	return requests.get(url).json()

def errcheck(instance, repo = None, group = None, username = None):
	# TODO: Better error handling
	try: requests.get('https://%s/api/v4/' % instance)
	except requests.exceptions.ConnectionError: return 404 # ...what?
	if repo != None:
		try:
			api_call('https://%s/api/v4/projects/%s' \
				% (instance, repo))['name']
		except KeyError:
			return 404
	if group != None:
		try:
			api_call('https://%s/api/v4/groups/%s' \
				% (instance, group))['name']
		except KeyError:
			return 404
	if username != None:
		try:
			api_call('https://%s/api/v4/users?username=%s' \
				% (instance, username))[0]
		except IndexError: return 404
		except KeyError: return 404
	return 200

def get_projects_list(instance, search_query = None, group = None, page = 1):
	if search_query is None and group is None:
		projects_list = api_call('https://%s/api/v4/projects?page=%s' \
			% (instance, page))
	elif group is not None and search_query is None: # Groups
		projects_list = api_call('https://%s/api/v4/groups/%s?page=%s' \
			% (instance, group, page))['projects']
	elif group is not None and search_query is not None: # Groups
		projects_list = api_call('https://%s/api/v4/groups/%s?search=%s&page=%s' \
			% (instance, group, search_query, page))['projects']
	else: # Search
		projects_list = api_call(\
			'https://%s/api/v4/projects?search_namespaces=true&search=%s&page=%s' \
			% (instance, search_query, page))
	if projects_list == []:
		return "<p style=\"background-color: orangered; padding: 10px\">" \
			"an error occured: no projects found</p>"
	# Convert to HTML
	projects_list_html = "<table class=\"laboratory_list\"><tbody>"
	projects_list_html += "<tr>" "<th>Name</th>" \
		"<th>Description</th>" "<th>Owner or group</th>" "<th>Idle</th>" "</tr>"
	for project in projects_list:
		projects_list_html += "<tr><td><a href=\"/%s/%s/\">%s</a></th>" % \
			(instance, project['path_with_namespace'], \
				project['path_with_namespace']) + \
			"<td><a href=\"/%s/%s\">%s</a></td>" % (instance, \
				project['path_with_namespace'], project['description']) + \
			"<td><a href=\"/%s/%s\">%s</a></td>" % (instance, \
				project['path_with_namespace'], \
				project['namespace']['name']) + \
			"<td><a href=\"/%s/%s\">%s</a></td></tr>" % (instance, \
				project['path_with_namespace'], project['last_activity_at'])
	projects_list_html += "</tbody></table>"
	projects_list_html += "<a href=\"?page=%s\">Next →</a>" % (page + 1)
	return projects_list_html
