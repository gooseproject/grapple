from ConfigParser import SafeConfigParser
import io
import json
import os
import re

import web

NOT_SUBMITTED = 0
SUBMITTED = 1
LIMIT = 'limit'

CONFIG_ENV_VAR = "GRAPPLE_CONF_FILE"
DEFAULT_CONFIG_FILE = "/etc/grapple.conf"

# Configuration variables and constants
DB_SECTION = 'database'
DBTYPE_VAR = 'dbtype'
DBNAME_VAR = 'dbname'
TABLENAME_VAR = 'tablename'

CONNECTIONS_SECTION = 'connections'
WHITELIST_VAR = 'whitelist'

QUERIES_SECTION = 'queries'
DEFAULTLIMIT_VAR = 'defaultlimit'

CONFIG_DEFAULTS = {DBTYPE_VAR: 'sqlite',
                   DBNAME_VAR: 'grappledb',
                   TABLENAME_VAR: 'grapple',
                   WHITELIST_VAR: '127.0.0.1',
                   DEFAULTLIMIT_VAR: '10'}

# Use this for just using defaults if file isn't found
EMPTY_CONFIG = """
[database]

[connections]

[queries]

"""

config_file = os.environ.get(CONFIG_ENV_VAR, DEFAULT_CONFIG_FILE)
config = SafeConfigParser(CONFIG_DEFAULTS)

config.readfp(io.BytesIO(EMPTY_CONFIG))
values = config.read(config_file)
if not values:
    # Convert to logging?
    print "Configuration file %s not found, using defaults" % config_file

dbtype = config.get(DB_SECTION, DBTYPE_VAR)
dbname = config.get(DB_SECTION, DBNAME_VAR)
tablename = config.get(DB_SECTION, TABLENAME_VAR)

ip_regex = re.compile(r'\b25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.\
25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.25[0-5]|2[0-4][0-9]|[01]?\
[0-9][0-9]?\.25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\b')

whitelist_str = config.get(CONNECTIONS_SECTION, WHITELIST_VAR)
ip_whitelist = [ip for ip in whitelist_str.split(',')
                if ip_regex.match(ip)]

default_limit = config.getint(QUERIES_SECTION, DEFAULTLIMIT_VAR)


db = web.database(dbn=dbtype, db=dbname)


def new_commit(package, branch, commit, author, email, status=NOT_SUBMITTED):
    db.insert(tablename,
              package=package,
              branch=branch,
              commit_id=commit,
              author=author,
              email=email,
              status=status)


def get_unsubmitted_commits(count=default_limit):
    return db.select(tablename, where='status=0', limit=count)


def set_commit_submitted(commit_id):
    vars = {'id': commit_id}
    db.update(tablename,
              where='id=$id',
              status=SUBMITTED,
              vars=vars)


urls = (
  '/', 'index',
  '/add', 'add',
  '/getcommits\?{0,1}(.*)', 'get_commits',
  '/submitted/(.*)', 'submitted'
)

app = web.application(urls, globals())


class index:
    def GET(self):
        return "Hello, world!"


class add:
    def POST(self):
        data = json.loads(web.data())
        package = data['repository']['name']
        branch = data['ref'].split('/')[-1]
        commit = data['after']
        author = data['commits'][0]['author']['name']
        email = data['commits'][0]['author']['email']
        new_commit(package, branch, commit, author, email)

        # Figure out correct response here
        raise web.seeother('/')


class get_commits:
    def GET(self, id):
        if web.ctx.ip not in ip_whitelist:
            raise web.Forbidden()

        input = web.input()

        if LIMIT in input:
            limit = int(input[LIMIT])
            commits = get_unsubmitted_commits(limit)
        else:
            commits = get_unsubmitted_commits()

        web.header('Content-Type', 'application/json')
        return json.dumps(commits.list())


class submitted:
    def POST(self, commit_id):
        if web.ctx.ip not in ip_whitelist:
            raise web.Forbidden()

        commit_id = int(commit_id)
        set_commit_submitted(commit_id)
        return web.seeother('/')


if __name__ == "__main__":
    app.run()
