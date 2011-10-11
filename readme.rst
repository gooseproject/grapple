Grapple README
==============

Overview
--------

Grapple is a tool to respond to `Github post-receive hooks`_
 and then kick off a package build in Koji. The main portion of
the tool is a webservice that responds to POST requests from github, a
query about builds that need to be submitted, and an action to update
the status of a given build. A unique build is a given commit on a given
branch.

.. _Github post-receive hooks: http://help.github.com/post-receive-hooks/

Requirements
------------

General:
Python >= 2.5
web.py

For database setup:
sqlite3

For testing:
curl

Quick setup for testing
-----------------------

- This process will be moved to a Makefile soon

- Download test data

  - edit tests/grab\_test\_data.py and fill in the POSTBIN url for the
    sample requests
  - cd tests && python grab\_test\_data.py

- create the sqlite database

  - [ -f grappledb ] && rm grappledb ; sqlite grappledb < schema.sql

- start the server

  - python grapple.py

- Try adding commits

  - cd tests && for i in \*.json; do curl -X POST -d @$i http://localhost:8080/add; done

- Query for commits

  - curl http://localhost:8080/getcommits

- Change the state to successfully submitted on a few

  - for i in 1 3 5 6; do curl -X POST http://localhost:8080/submitted/$i; done

- Query for commits

  - curl http://localhost:8080/getcommits


License
-------

Grapple is licensed under the GPLv2, and is part of the tools for the
Goose Linux Project.

Upcoming tasks and plans
------------------------

In no particular order or guarantee, here are possible improvements
and refinements to Grapple:

-  Create Makefile to automate testing and setup
-  Have index return an API summary.
-  Review for needed error handling
-  Add logging
-  Make a decorator to limit a url from being called from just whitelists
-  Become more PEP8 compliant
-  Add license and copyright header in source
-  Move status definition to DB?
-  For methods not returning data, what's the proper output?
-  Verify the build has not already been seen before adding
-  Create init scripts
-  Create RPMs
-  Create a versioning scheme
