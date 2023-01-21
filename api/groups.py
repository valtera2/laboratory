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
from api.base import api_call

# Groups
def get_subgroups_list(instance, group, search_query = None, page = 1):
	if search_query is None:
		subgroups_list = api_call('https://%s/api/v4/groups/%s/subgroups?page=%s' \
			% (instance, group, page))
	else: # Search
		subgroups_list = api_call(\
			'https://%s/api/v4/groups/%s/subgroups?search=%s&page=%s' \
			% (instance, group, search_query, page))
	if subgroups_list == []:
		return "<p style=\"background-color: orangered; padding: 10px\">" \
			"an error occured: no subgroups found</p>"
	# Convert to HTML
	subgroups_list_html = "<table class=\"laboratory_list\"><tbody>"
	subgroups_list_html += "<tr>" "<th>Name</th>" \
		"<th>Description</th>" "<th>Created at</th>" "</tr>"
	for subgroup in subgroups_list:
		subgroups_list_html += "<tr><td><a href=\"/%s/%s\">%s</a></th>" % \
			(instance, subgroup['full_path'], \
				subgroup['full_path']) + \
			"<td><a href=\"/%s/%s\">%s</a></td>" % (instance, \
				subgroup['full_path'], subgroup['description']) + \
			"<td><a href=\"/%s/%s\">%s</a></td></tr>" % (instance, \
				subgroup['full_path'], subgroup['created_at'])
	subgroups_list_html += "</tbody></table>"
	subgroups_list_html += "<a href=\"?page=%s\">Next →</a>" % (page + 1)
	return subgroups_list_html

def get_group_data(instance, group):
	recv = api_call("https://%s/api/v4/groups/%s" % \
		(instance, group))
	return recv['avatar_url'] if recv['avatar_url'] != None else "", \
		recv['name'], recv['description']

