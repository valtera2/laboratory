#!/usr/bin/python3
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
from flask.helpers import redirect, url_for
from markupsafe import escape
from sys import argv
from flask import Flask
from flask import request
from flask.templating import render_template
from markupsafe import Markup
from api.base import errcheck, get_projects_list

from api.groups import get_group_data, get_subgroups_list
from api.users import get_user_data, is_user
from api.repos import get_repo_cloneurls, get_repo_commits, \
    get_repo_description, get_repo_brancheslist, \
    get_repo_idle, get_repo_issue, get_repo_issueparticipants, \
    get_repo_issues, get_repo_primary_branch, get_repo_readme, \
	get_repo_tagslist, get_repo_avatar, get_repo_tree, get_repo_blob

app = Flask(__name__)

def abort(code):
	return render_template('common.html', err=code), code

@app.route('/')
def index():
	return render_template('common.html', about='active', title='about')

@app.route('/favicon.ico')
def favicon():
	return "Not found", 404

@app.route('/<name>', methods = ['GET', 'POST'])
@app.route('/projects', methods = ['GET', 'POST'])
def projects(name = None):
	if name is None:
		name = 'gitlab.freedesktop.org'
	if request.args.get('page') is None:
		page = 1
	else:
		page = int(request.args.get('page'))
	if request.method == 'GET':
		if errcheck(name) != 200:
			return abort(404)
		return render_template('common.html', title='projects',
			instance=name, \
			projects='active', projects_list=Markup(get_projects_list(\
				name, None, None, page)))
	elif request.method == 'POST':
		return render_template('common.html', title='search',
			instance=name, \
			projects='active', projects_list=Markup(get_projects_list(name, \
				request.form['laboratory_searchquery'], None, page)))

@app.route('/<instance>/<user>/-/about')
def userinfo(instance = None, user = None):
	if errcheck(instance, username=user) != 200:
		return abort(404)
	user_data = get_user_data(instance, user)
	return render_template('common.html', title='~%s' % (user),\
		user=1, about='active', \
		instance=instance, user_name=user_data[1], user_state=user_data[2], \
		user_avatar=user_data[0], user_url="/%s/%s" % (instance, user))

@app.route('/<instance>/<path:group>', methods = ['GET', 'POST'])
def group_projects(instance = None, group = None):
	if request.args.get('page') is None:
		page = 1
	else:
		page = int(request.args.get('page'))
	group_escaped = group.replace('/', '%2F')
	if is_user(instance, group_escaped):
		return redirect('/%s/%s/-/about' % (instance, group))
	if errcheck(instance, group=group_escaped) != 200:
		return abort(404)
	group_data = get_group_data(instance, group_escaped)
	if request.method == 'POST':
		search_query = request.form['laboratory_searchquery']
	else: search_query = None
	return render_template('common.html', title='%s' % (group),\
		group=1, projects='active', group_url="/%s/%s" % (instance, group), \
		instance=instance, group_name=group_data[1], group_desc=group_data[2], \
		projects_list=Markup(get_projects_list(\
			instance, search_query, group_escaped, page)), \
		group_avatar=group_data[0])

@app.route('/<instance>/<path:group>/-/subgroups', methods = ['GET', 'POST'])
def group_subgroups(instance = None, group = None):
	if request.args.get('page') is None:
		page = 1
	else:
		page = int(request.args.get('page'))
	group_escaped = group.replace('/', '%2F')
	if errcheck(instance, group=group_escaped) != 200:
		return abort(404)
	if is_user(instance, group_escaped):
		return redirect('/%s/%s/-/about' % (instance, group))
	group_data = get_group_data(instance, group_escaped)
	if request.method == 'POST':
		search_query = request.form['laboratory_searchquery']
	else: search_query = None
	return render_template('common.html', title='%s' % (group),\
		group=1, subgroups='active', group_url="/%s/%s" % (instance, group), \
		instance=instance, group_name=group_data[1], group_desc=group_data[2], \
		subgroups_list=Markup(get_subgroups_list(\
			instance, group_escaped, search_query, page)), \
		group_avatar=group_data[0])

@app.route('/<instance>/<path:user_group>/<repo>/')
def repository(instance = None, user_group = None, repo = None):
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, summary='active', \
		repo_description=get_repo_description(instance, full_reponame), \
		repo_idle=get_repo_idle(instance, full_reponame), \
		repo_cloneurl=get_repo_cloneurls(instance, full_reponame)[0], \
		repo_clonessh=get_repo_cloneurls(instance, full_reponame)[1], \
		repo_branches_list=Markup(get_repo_brancheslist(instance, full_reponame)), \
		repo_tags_list=Markup(get_repo_tagslist(instance, full_reponame)), \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		repo_readme=Markup(get_repo_readme(instance, full_reponame)), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

@app.route('/<instance>/<path:user_group>/<repo>/-/branches')
def repo_refs(instance = None, user_group = None, repo = None):
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, refs='active', \
		repo_description=get_repo_description(instance, full_reponame), \
		repo_branches_list=Markup(get_repo_brancheslist(instance, full_reponame, 1)), \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

@app.route('/<instance>/<path:user_group>/<repo>/-/commits/')
@app.route('/<instance>/<path:user_group>/<repo>/-/commits/<branch>')
def repo_log(instance = None, user_group = None, repo = None, branch = None):
	if request.args.get('page') is None:
		page = 1
	else:
		page = int(request.args.get('page'))
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, log='active', \
		repo_description=get_repo_description(instance, full_reponame), \
		repo_commits_list=Markup(get_repo_commits(\
			instance, full_reponame, page, branch)), \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

@app.route('/<instance>/<path:user_group>/<repo>/-/commit/<commit_id>')
def repo_showlog(instance = None, user_group = None, repo = None, commit_id = None):
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	commit_info = get_repo_commits(instance, full_reponame, 1, None, commit_id)
	print(commit_info)
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, log='active', \
		repo_description=get_repo_description(instance, full_reponame), \
		repo_commit_author=commit_info[0], \
		repo_commit_committer=commit_info[1], \
		repo_commit_id=commit_info[2], \
		repo_commit_parent=commit_info[3], \
		repo_commit_message=commit_info[4], \
		repo_commit_diff=Markup(commit_info[5]), \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

@app.route('/<instance>/<path:user_group>/<repo>/-/about')
def repo_about(instance = None, user_group = None, repo = None):
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, about='active', \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		repo_readme=Markup(get_repo_readme(instance, full_reponame)), \
		repo_description=get_repo_description(instance, full_reponame), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

@app.route('/<instance>/<path:user_group>/<repo>/-/tree/')
@app.route('/<instance>/<path:user_group>/<repo>/-/tree/<branch>')
@app.route('/<instance>/<path:user_group>/<repo>/-/tree/<branch>/<path:tree>')
def repo_tree(instance = None, user_group = None, repo = None, \
	branch = None, tree = None):
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	if branch == None: branch = get_repo_primary_branch(instance, full_reponame)
	if tree == None: tree = '/'
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, tree='active', \
		repo_tree=Markup(get_repo_tree(instance, full_reponame, tree, branch)), \
		repo_description=get_repo_description(instance, full_reponame), \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

@app.route('/<instance>/<path:user_group>/<repo>/-/blob/<branch>/<path:blob>')
def repo_blob(instance = None, user_group = None, repo = None, \
	branch = None, blob = None):
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	if branch == None: branch = get_repo_primary_branch(instance, full_reponame)
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, tree='active', \
		repo_blob=Markup(get_repo_blob(instance, full_reponame, blob, branch)[0]), \
		repo_bloblines=Markup(get_repo_blob(instance, full_reponame, blob, branch)[1]), \
		repo_description=get_repo_description(instance, full_reponame), \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

@app.route('/<instance>/<path:user_group>/<repo>/-/issues')
@app.route('/<instance>/<path:user_group>/<repo>/-/issues/')
def repo_issues(instance = None, user_group = None, repo = None):
	if request.args.get('page') is None:
		page = 1
	else:
		page = int(request.args.get('page'))
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, issues='active', \
		repo_issueslist=Markup(get_repo_issues(instance, full_reponame, \
			request.args.get('state'), page)), \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		repo_description=get_repo_description(instance, full_reponame), \
		repo_issuesstate=request.args.get('state') \
			if request.args.get('state') is not None else "all", \
		repo_issuesnextpage=str(page + 1), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

@app.route('/<instance>/<path:user_group>/<repo>/-/issues/<iid>')
def repo_issue(instance = None, user_group = None, repo = None, iid = None):
	full_reponame = '%s%%2F%s' % (user_group.replace('/', '%2F'), repo)
	if errcheck(instance, repo=full_reponame) != 200:
		return abort(404)
	issue = get_repo_issue(instance, full_reponame, iid)
	return render_template('common.html', title=Markup(\
		'<a href="/%s/%s">%s</a>/%s' % (instance, user_group, user_group, repo)),\
		repository=1, issues='active', \
		repo_issueid=iid, \
		repo_issuetitle=issue[0], \
		repo_issuestate=issue[1], \
		repo_issueidle=issue[2], \
		repo_issueauthor=issue[3], \
		repo_issue=Markup(issue[4].replace('\n', '<br />')), \
		repo_description=get_repo_description(instance, full_reponame), \
		repo_issueparticipants=get_repo_issueparticipants(instance, \
			full_reponame, iid), \
		repo_avatar=get_repo_avatar(instance, full_reponame), \
		repo_issuesstate=request.args.get('state'), \
		instance=instance, \
		repo_url="/%s/%s/%s" % (instance, user_group, repo))

if __name__ == "__main__":
	print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
	print("=== Laboratory GitLab web frontend ===")
	print("------ Flask Development server ------")
	print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
	if argv[1] == '-h':
		print("Usage: ./app.py [-d]")
		print("\t-d\tEnable debug mode.")
	elif argv[1] == '-d':
		app.run(debug=True)
	else: app.run(debug=False)
