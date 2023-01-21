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
import requests

# User-related fetching functions
def get_user_data(instance, user):
	# Unfourtunately GitLab's API doesn't allow us to retrieve much user 
	# data for now, so we're limited to the id, the username, the avatar, 
	# and the state.
	recv = api_call("https://%s/api/v4/users?username=%s" % \
		(instance, user))[0]
	return recv['avatar_url'] if recv['avatar_url'] != None else "", \
		recv['name'], recv['state']

def is_user(instance, user):
	recv = api_call("https://%s/api/v4/users?username=%s" % \
		(instance, user))
	if recv == []: return 0
	return 1

