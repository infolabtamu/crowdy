.. Crowdy documentation master file, created by
   sphinx-quickstart on Sat Mar 26 11:51:53 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Crowdy's documentation!
==================================

Contents:

.. toctree::
   :maxdepth: 2

Some high level comments:

    * This documentation is a work-in-progress.
    * All methods return JSON.  There are five different types of objects that
      the methods return: a Crowd, a simplified Crowd, a User, their Edges 
      (friends and followers), and a Tweet.
      *FIXME: this would be a great place to put sample objects.*
    * The name of the method determines the url. For example, to run
      api.crowd.id(cid), you can GET /api/1/crowd/id/106582358 or 
      GET /api/1/crowd/id?cid=106582358 . Either way, it returns the profile for      @jeffamcgee.
    * Datetimes are always specified in seconds since the UNIX epoch in UTC.
    * If there is a min_field and a max_field, then it searches for objects
      where min_field<=object.field<field .

.. autofunction:: api.status
.. autofunction:: api.search.crowd
.. autofunction:: api.crowd.id
.. autofunction:: api.crowd.simple
.. autofunction:: api.user.id
.. autofunction:: api.user.edges
.. autofunction:: api.user.tweets
.. autofunction:: api.tweet.id

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

