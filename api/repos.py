# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2023 Ferass El Hafidi <vitali64pmemail@protonmail.com>
# Copyright (C) 2023 Leo Gavilieau <xmoo@vern.cc>
from markupsafe import escape
from pycmarkgfm import gfm_to_html as markdown
from base64 import b64decode # For some reason GitLab encodes file contents
from api.base import api_call

# Repositories
def get_repo_primary_branch(instance, repo):
	recv = api_call(\
		'https://%s/api/v4/projects/%s' % (instance, repo))

	if "default_branch" in recv:
		return recv["default_branch"]

	return "<none>"

def get_repo_description(instance, repo):
	recv = api_call("https://%s/api/v4/projects/%s" % \
		(instance, repo))
	if "description" in recv:
		if recv['description'] != None and recv['description'] != "":
			return recv['description']
	return "<none>" # If no conditions match

def get_repo_idle(instance, repo):
	recv = api_call("https://%s/api/v4/projects/%s" % \
		(instance, repo))

	if "last_activity_at" in recv:
		# TODO: I will include a separate patch that prettifies the date soon.
		return recv["last_activity_at"]
	else:
		return "<none>"

def get_repo_cloneurls(instance, repo):
	recv = api_call("https://%s/api/v4/projects/%s" % \
		(instance, repo))

	a = "<none>" # Basic error handling
	b = "<none>"
	if "http_url_to_repo" in recv and recv["http_url_to_repo"] != "":
		a = recv["http_url_to_repo"]
	if "ssh_url_to_repo" in recv and recv["ssh_url_to_repo"] != "":
		b = recv["ssh_url_to_repo"]

	return a,b

def get_repo_brancheslist(instance, repo, page = None):
	branches_list = api_call(\
		'https://%s/api/v4/projects/%s/repository/branches?page=%s&per_page=%s' \
		% (instance, repo, page if page is not None else 1, \
			100 if page is not None else 8))

	if "message" in branches_list:
		return ""

	# Convert to HTML
	branches_list_html = ""
	for branch in branches_list:
		branches_list_html += "<tr><td><a href=\"/%s/%s/-/tree/%s\">%s</a></td>" % \
			(instance, repo.replace("%2F", "/"), branch['name'], branch['name']) + \
			"<td>%s</td>" % branch['commit']['title'] + \
			"<td>%s</td>" % branch['commit']['author_name'] + \
			"<td>%s</td></tr>" % branch['commit']['authored_date']
	return branches_list_html

def get_repo_tagslist(instance, repo, page = None):
	tags_list = api_call(\
		'https://%s/api/v4/projects/%s/repository/tags?page=%s&per_page=%s' \
		% (instance, repo, page if page is not None else 1, \
			100 if page is not None else 8))

	if "message" in tags_list:
		return ""

	# Convert to HTML
	tags_list_html = ""
	for tag in tags_list:
		tags_list_html += "<tr><td><a href=\"/%s/%s/-/tree/%s\">%s</a></td>" % \
			(instance, repo.replace("%2F", "/"), tag['name'], tag['name']) + \
			"<td>%s</td>" % tag['commit']['title'] + \
			"<td>%s</td>" % tag['commit']['author_name'] + \
			"<td>%s</td></tr>" % tag['commit']['authored_date']
	return tags_list_html

def get_repo_commits(instance, repo, page = 1, branch = None, commit = None):
	if commit is None:
		if branch:
			commits_list = api_call(\
				'https://%s/api/v4/projects/%s/repository/commits?page=%s&per_page=%s&ref_name=%s' \
				% (instance, repo, page, 100, branch))
		else:
			commits_list = api_call(\
				'https://%s/api/v4/projects/%s/repository/commits?page=%s&per_page=%s' \
				% (instance, repo, page, 100))

		if "message" in commits_list:
			return "<p class=\"error\">Could not retrieve commits: %s</p>" \
				% (commits_list["message"])

		# Convert to HTML
		commits_list_html = ""
		for commit in commits_list:
			commits_list_html += \
				"<tr><td><a href=\"/%s/%s/-/commit/%s\"><pre>%s</pre></a></td>" % \
				(instance, repo.replace("%2F", "/"), commit['id'], commit['short_id']) + \
				"<td>%s</td>" % commit['title'] + \
				"<td>%s</td>" % commit['author_name'] + \
				"<td>%s</td></tr>" % commit['authored_date']
		commits_list_html += "<tr><td><a href=\"?page=%s\">Next →</a></td></tr>" \
			% (page + 1)
		return commits_list_html
	else:
		commit_info = api_call(\
			'https://%s/api/v4/projects/%s/repository/commits/%s' \
			% (instance, repo, commit))
		try: commit_info['id']
		except KeyError:
			return "<p style=\"background-color: orangered; padding: 10px\">" \
				"an error occured: commit not found</p>"
		commit_diff = api_call(\
			'https://%s/api/v4/projects/%s/repository/commits/%s/diff' \
			% (instance, repo, commit))
		commit_diff_html = ""
		for diff in commit_diff:
			if diff['new_file'] == False:
				commit_diff_html += "--- /dev/null\n"
			else:
				commit_diff_html += "--- a/%s\n" % diff['old_path']
			commit_diff_html += "+++ b/%s\n" % diff['new_path']
			commit_diff_html += diff['diff']
		return commit_info['author_name'], commit_info['committer_name'], \
			commit_info['id'], commit_info['parent_ids'][0], commit_info['message'], \
			commit_diff_html

def get_repo_readme(instance, repo):
	recv = api_call(\
		'https://%s/api/v4/projects/%s' % (instance, repo))
	readme_decoded = "" # No readme

	if not "readme_url" in recv:
		return ""

	if recv['readme_url']:
		readme = api_call(\
			'https://%s/api/v4/projects/%s/repository/files/%s?ref=%s' \
			% (instance, repo, recv['readme_url'].split('/')[-1], \
			get_repo_primary_branch(instance, repo)))['content']
		readme_decoded = b64decode(readme).decode('utf-8')#.replace(\
		#	"https://%s/" % instance, "/%s/" % instance)
		if recv['readme_url'].split('/')[-1].split('.')[-1] == 'md':
			readme_decoded = markdown(readme_decoded)
		else: readme_decoded = "<pre>" + readme_decoded + "</pre>"
		return readme_decoded

def get_repo_avatar(instance, repo):
	recv = api_call(\
		'https://%s/api/v4/projects/%s' % (instance, repo))
	if recv['avatar_url'] is None:
		return ""
	return recv['avatar_url']

def get_repo_tree(instance, repo, path, branch = None):
	recv = api_call(\
		'https://%s/api/v4/projects/%s' % (instance, repo))
	if branch is None: branch = recv['default_branch']
	tree = api_call(\
		'https://%s/api/v4/projects/%s/repository/tree?path=%s&per_page=100&ref=%s' % \
		(instance, repo, path, branch))

	if "message" in tree:
		return "<p class=\"error\">Could not retrieve tree list: %s</p>" \
			% (tree["message"])

	tree_html = ""
	for file in tree:
		tree_html += "<tr><td>%s</td>" % file['mode'] + \
			"<td><a href=\"/%s/%s/-/%s/%s/%s\">%s</a></td>" % (instance, \
				recv['path_with_namespace'], file['type'], branch, \
				escape(file['path']), file['name']) + \
			"<td>%s</td>" % file['type']
	return tree_html

def get_repo_blob(instance, repo, blob, branch = None):
	blob_decoded = "" # blob
	lines = ""
	line = 1
	if branch is None: branch = get_repo_primary_branch(instance, repo)
	blob_file = api_call(\
		'https://%s/api/v4/projects/%s/repository/files/%s?ref=%s' \
		% (instance, repo, blob.replace('/', '%2F'), # TODO: Replace replace() \
		branch))['content']
	blob_decoded = b64decode(blob_file).decode('utf-8')
	while line <= blob_decoded.count("\n"):
		lines += "%d\n" % line
		line += 1
	return blob_decoded, lines

def get_repo_issues(instance, repo, state = None, page = None):
	if state is None: state = "all"
	if page is None: page = 1
	issues_list = api_call(\
		'https://%s/api/v4/projects/%s/issues?state=%s&page=%s' \
		% (instance, repo, state, page))
	issues_list_html = ""
	for issue in issues_list:
		issues_list_html += "<tr><td>#<a href=\"/%s/%s/-/issues/%s\">%s</a></td>" \
			% (instance, repo.replace('%2F', '/'), issue['iid'], issue['iid']) + \
			"<td><a href=\"/%s/%s/-/issues/%s\">%s</a></td>" \
				% (instance, repo.replace('%2F', '/'), issue['iid'], issue['title']) + \
			"<td>%s</td>" % issue['author']['name'] + \
			"<td>%s</td>" % issue['state'] + \
			"<td>%s</td></tr>" % issue['updated_at']
	return issues_list_html

def get_repo_issue(instance, repo, iid):
	issue = api_call(\
		'https://%s/api/v4/projects/%s/issues/%s' \
		% (instance, repo, iid))
	return issue['title'], issue['state'], issue['updated_at'], issue['author']['name'], \
		markdown(issue['description']).replace('<p>', '').replace('</p>', '')

def get_repo_issueparticipants(instance, repo, iid):
	recv = api_call(\
		'https://%s/api/v4/projects/%s/issues/%s/participants' \
		% (instance, repo, iid))
	issue_participants = []
	for participant in recv:
		issue_participants.append(participant['name'])
	return issue_participants
