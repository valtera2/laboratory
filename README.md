<img src="static/logo.png" width=300px>

*A Simple GitLab frontend.*

## How does it work?

Laboratory uses GitLab's REST API to fetch data about users/groups and 
repositories (those so-called 'projects').

Then it parses that data and shows it in a JS-free lightweight webpage 
inspired by [Cgit](https://git.zx2c4.org/) and [SourceHut](https://sr.ht/).

## Dependencies

* `pycmarkgfm`
* `requests`
* `flask` and all its dependencies

## Features

### Basic

* List projects for any instance
* List group projects
* List group subgroups

### Repositories

* Issues (no comments though)
* Wikis
* Tree
* Show a commit
* Log
* Partial README rendering
* Refs
* Description
* Idle
* Avatar

### Groups

* Subgroups
* Repositories
* Avatar

### Users

* Avatar
* State

Unfourtunately, accessing more data about users requires authentication, 
so don't expect Laboratory to fetch more than that unless GitLab changes 
that.

## TODO

* Implement Merge Requests (currently all API calls to MRs must be 
  authenticated)
* Implement Logging in (possibly just a matter of getting the token key and 
  using it for all requests, plus some other features like creating repos)
* Group wikis
* Proper support for project wikis that aren't really repositories
* And more

## Known Issues

* When searching for a repository in GitLab.com, the API returns an internal 
  server error. This is GitLab.com's problem, not ours.
* Laboratory is very sensitive about URLs
* Laboratory currently cannot render RST-formatted README files
* Laboratory freaks out when a blob is not a "normal" file (e.g. an image)

## Instances

For an instance to be listed here, it needs to meet the following 
requirements: 

* Instances MUST have been up for at least a month before it can be added 
  to this list.
* Instances MUST have been updated in the last month. An instance that hasn't 
  been updated in the last month is considered unmaintained and is removed 
  from the list.
* Instances MUST be served via domain name.
* Instances MUST be served via HTTPS (or/and onion).
* Instances using any man-in-the-middle service MUST be marked as such 
  (e.g. Cloudflare, DDoS-Guard...).
* Instances using any type of anti-bot protection MUST be marked as such.
* Instances MUST NOT use any type of analytics.
* Instances running a modified source code MUST respect the AGPL by publishing 
  their source code and stating their changes before they are added to the 
  list and MUST contain a link to both the modified and original source code 
  of Laboratory in the footer.
* Instances MUST NOT serve ads NOR promote products.
* Instances MUST NOT restrict or disallow the access / usage to any 
  [natural person](https://en.wikipedia.org/wiki/Natural_person) 
  (e.g. a country's IP range MUST NOT be blocked, access by a natural 
  person MUST NOT be disallowed for arbirary reason) - this rule doesn't 
  apply to juridical persons.

***Note***: If you see any instance in this list not following the rules, 
please let us know.

| URL | Author | Vanilla/Modified/...? | Note | Has an onion site? |
|-----|--------|-----------------------|------|--------------------|
| https://lab.vern.cc | ~vern team | Vanilla. | Has alternate subdomains. Sometimes down. | Yes |
| https://laboratory.vitali64.duckdns.org | Ferass | [Patched](https://git.vitali64.duckdns.org/misc/laboratory.vitali64.duckdns.org.git). | Used as a testing ground. | Yes |

## Screenshots

These screenshots may be outdated.

<img src="screenshots/main.png">Main page</img>

<img src="screenshots/group.png">Browsing Group repositories</img>

<img src="screenshots/repo.png">Browsing a repository</img>
