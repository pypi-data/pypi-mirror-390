
pyytorch-helper
===============

Small helper package that exposes a `download_data()` helper to fetch an
example dataset (from a GitHub zip) and extract it into the user's home
directory under `~/.pyytorch_data`.

Usage
-----

Import and call the downloader manually:

```python
from pyytorch_helper.downloader import download_data
download_data()
```

Or call the exposed package function:

```python
import pyytorch_helper
pyytorch_helper.download_data()
```

Notes for publishing
--------------------

- The package currently performs an explicit download when the `download_data()`
	function is invoked. Historically some users try to run that during package
	install; that is fragile because pip installs wheels which do not execute
	setup.py install hooks. Provide an explicit CLI or lazy-download-on-first-use
	for reliable behavior.

License
-------
MIT
