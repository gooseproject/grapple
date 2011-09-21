import web
import json

NOT_SUBMITTED = 0
SUBMITTED = 1

db = web.database(dbn='sqlite', db='grappledb')

def new_commit(package, branch, commit, status=NOT_SUBMITTED):
    db.insert('grapple',
              package=package,
              branch=branch,
              commit_id=commit,
              status=status)

def get_unsubmitted_commits():
    return db.select('grapple', where='status=0', limit=10)

urls = (
  '/', 'index',
  '/add', 'add',
  '/getcommits', 'get_commits'
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
        new_commit(package, branch, commit)

        raise web.seeother('/')

class get_commits:
    def GET(self):
        commits = get_unsubmitted_commits()
        web.header('Content-Type', 'application/json')
        return json.dumps(commits.list())

if __name__ == "__main__":
    app.run()
