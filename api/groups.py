# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2023 Ferass El Hafidi <vitali64pmemail@protonmail.com>
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

