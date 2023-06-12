# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2023 Ferass El Hafidi <vitali64pmemail@protonmail.com>
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

