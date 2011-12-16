from ConfigParser import SafeConfigParser
import io
import json
import os
import urllib2
import subprocess

CONFIG_ENV_VAR = "GRAPPLE_CONF_FILE"
DEFAULT_CONFIG_FILE = "/etc/grapple/grapple.conf"

CLIENT_SECTION = 'client'
QUERYURL_VAR = 'queryurl'
SUBMITTEDURL_VAR = 'submittedurl'
KOJICONFIG_VAR = 'kojiconfig'
KOJITAG_VAR = 'kojitag'
GITURL_VAR = 'giturl'
GITCOMMIT_VAR = 'gitcommit'
REPLACE_CHARS_VAR = 'replace_chars'

CONFIG_DEFAULTS = {GITURL_VAR: '',
        KOJITAG_VAR: '',
        GITCOMMIT_VAR: 'HEAD'
        } 

# Use this for just using defaults if file isn't found
EMPTY_CONFIG = """
[database]

[connections]

[queries]

[client]

"""

config_file = os.environ.get(CONFIG_ENV_VAR, DEFAULT_CONFIG_FILE)
config = SafeConfigParser(CONFIG_DEFAULTS)

config.readfp(io.BytesIO(EMPTY_CONFIG))
values = config.read(config_file)


if not values:
    # Convert to logging?
    print "Configuration file %s not found, using defaults" % config_file


query_url = config.get(CLIENT_SECTION, QUERYURL_VAR)
submitted_url = config.get(CLIENT_SECTION, SUBMITTEDURL_VAR)

def process_commits():

    js = json.load(urllib2.urlopen(query_url))

    kojiconfig = None
    try:
        kojiconfig = config.get(CLIENT_SECTION, KOJICONFIG_VAR)
    except:
        pass

    if len(js):
        print "requesting commits from: %s" % query_url
        print "-----"

    for j in js:
        print "processing commit: %s from package: %s" % (j['commit_id'], j['package'])
        args = ["/usr/bin/koji"]

        if kojiconfig:
            args.append("-c")
            args.append(kojiconfig)

        kojitag = config.get(CLIENT_SECTION, KOJITAG_VAR)
        giturl = config.get(CLIENT_SECTION, GITURL_VAR)
        commit = config.get(CLIENT_SECTION, GITCOMMIT_VAR)

        name = j['package']
        replace_chars = config.get(CLIENT_SECTION, REPLACE_CHARS_VAR)
        for chars in replace_chars.split():
            r, w = chars.split(':')
            name = name.replace(r, w)

        args.append('build')
        args.append('--nowait')
        args.append(kojitag)
        args.append("%s/%s.git#%s" % (giturl, name, commit))

        try:
#            print "args: %s" % args
            p = subprocess.check_call(args)
        except CalledProcessError, e:
            print "unable to build package: %s -- error: %s" % (j['package'], e)

        try:
            print "url: %s/%s" % (submitted_url, j['id'])
            urllib2.urlopen("%s/%s" % (submitted_url, j['id']), 'x=y')
        except Exception, e:
            print "could not mark id %s as submitted -- error: %s" % (j['id'], e)
        

if __name__ == "__main__":
    process_commits()
