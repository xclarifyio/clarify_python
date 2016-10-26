.. :changelog:

History
-------

3.1.0 (2016-10-26)
* Added Python 2.7 support

3.0.2 (2016-04-27)
* Added clarify_export script

3.0.1 (2016-01-05)
* Maintenance

3.0.0 (2015-12-01)
++++++++++++++++++

* BREAKING CHANGE: client.bundle_list_map(func) The func is now called
with client as the first parameter.
* Added insight access methods.
* Support for requesting non-autorun insights (ex. transcripts and captions)
* Support for embedding insights when requesting bundles.
* Support for external_id when creating or updating bundles.
* Added behave tests.
* Added unittests.

2.0.0 (2015-04-18)
++++++++++++++++++

* All deprecated code removed.

1.1.1 (2015-04-18)
++++++++++++++++++

* Deprecated use of set_key() in favor of Client class.

1.1.0 (2015-03-08)
++++++++++++++++++

* Switched from http.client to urllib3.
* Eliminated support for setting HTTP debug level. Use Runscope.

1.0.4 (2015-03-08)
++++++++++++++++++

* Added get_item_hrefs() utility function.
* Utility function cleanup.

1.0.3 (2015-03-07)
++++++++++++++++++

* Fixed some encoding bugs.

1.0.2 (2015-03-07)
++++++++++++++++++

* Version increment to work around a PyPI bug. Identical to 1.0.1.

1.0.1 (2015-03-07)
++++++++++++++++++

* Version increment to work around a PyPI bug. Identical to 1.0.0.

1.0.0 (2015-03-07)
++++++++++++++++++

* Port of 1.0.1 python 2 code.

