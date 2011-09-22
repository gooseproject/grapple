import web
import json

NOT_SUBMITTED = 0
SUBMITTED = 1

DEFAULT_LIMIT = 10
LIMIT = 'limit'

IP_WHITELIST = ['127.0.0.1', ]

db = web.database(dbn='sqlite', db='grappledb')


def new_commit(package, branch, commit, author, email, status=NOT_SUBMITTED):
    db.insert('grapple',
              package=package,
              branch=branch,
              commit_id=commit,
              author=author,
              email=email,
              status=status)


def get_unsubmitted_commits(count=DEFAULT_LIMIT):
    return db.select('grapple', where='status=0', limit=count)


def set_commit_submitted(commit_id):
    vars = {'id': commit_id}
    db.update('grapple',
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
        if web.ctx.ip not in IP_WHITELIST:
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
        if web.ctx.ip not in IP_WHITELIST:
            raise web.Forbidden()

        commit_id = int(commit_id)
        set_commit_submitted(commit_id)
        return web.seeother('/')


if __name__ == "__main__":
    app.run()
