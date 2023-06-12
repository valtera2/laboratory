# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2023 Leo Gavilieau <xmoo@vern.cc>
from pycmarkgfm import gfm_to_html as markdown
from api.base import api_call

def get_project_wiki_sitemap(instance, full_reponame):
    recv = api_call('https://%s/api/v4/projects/%s/wikis' \
		% (instance, full_reponame))

    if 'message' in recv:
        return "Could not retrieve pages: " + recv["message"]

    pages_html = "" # Convert JSON to HTML

    categories = {} # For storing links to pages inside categories
    individual = {} # For storing links to individual pages

    for subdict in recv:
        if "/" in subdict["slug"]:
            slashcount = subdict["slug"].count("/")
            slashlist = subdict["slug"].split("/")

            category = ""
            for i in range(slashcount):
                if i - 1 == slashcount:
                    continue
                category += slashlist[i]

            try:
                tmp = categories[category]
            except:
                tmp = ""

            tmp += '&#9;<a class="project_wiki_category_link" \
                href="/%s/%s/-/wikis/%s">%s</a> (%s)<br>\n' \
                % (instance, full_reponame.replace("%2F", "/"), \
                subdict["slug"], subdict["title"], subdict["format"])

            categories[category] = tmp
        else:
            if subdict["slug"] in categories:
                continue

            individual[subdict["slug"]] = '<a class="project_wiki_link" \
                href="/%s/%s/-/wikis/%s">%s</a> (%s)<br>\n' \
                % (instance, full_reponame.replace("%2F","/"), \
                subdict["slug"], subdict["title"], subdict["format"])


    # We parse individual and categories at the end
    # So we can get rid of redundant entries
    categories_html = ""
    if len(categories) > 0:
        for key,val in categories.items():
            categories_html += '<h3><a class="project_wiki_category" \
                href="/%s/%s/-/wikis/%s">%s</a></h3>\n%s' \
                % (instance, full_reponame.replace("%2F","/"), key, key, val)

    if len(individual) > 0:
        for key,val in individual.items():
            if key in categories:
                continue
            pages_html += val

    return pages_html + categories_html

def get_project_wiki_page(instance, full_reponame, wiki = ""):
	slug = '%s' % (wiki.replace('/', '%2F'))

	# Check if user is requesting a real wiki page
	# or the "Pages" wikipage, which is a sitemap with a special API
	recv = api_call('https://%s/api/v4/projects/%s/wikis/%s'\
		% (instance, full_reponame, slug))

	if 'message' in recv:
		# Error detected!
		return "Could not retrieve wiki: %s" % recv["message"]
	else:
		if 'content' in recv:
			# Now to decode the markdown...
			decode = markdown(recv["content"])
			# We want to replace all instance links with a link
			# to the frontend
			decode = decode.replace("https://" + instance, "/" + instance)
			decode = decode.replace("http://" + instance, "/" + instance)
			return decode
		else:
			return "Could not retrieve content..."

