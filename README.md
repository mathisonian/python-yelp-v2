python-yelp-v2
==============

A Python wrapper for the Yelp API v2. The structure for this was inspired by the [python-twitter](https://github.com/bear/python-twitter) library, and some internal methods are reused.


Usage
-----

You must have yelp oauth credentials: http://www.yelp.com/developers/getting_started

```python
import yelp

yelp_api = yelp.API(consumer_key=MY_CONSUMER_KEY,
                    consumer_secret=MY_CONSUMER_SECRET,
                    access_token_key=MY_ACCESS_TOKEN,
                    access_token_secret=MY_ACCESS_SECRET)

```

### Searching

```python
search_results = yelp_api.Search(term="my search term")
```

### Getting business info

```python
business = yelp_api.GetBusiness('business_id')
```


Todo
----

* Create classes for categories.
* Improve the location class
* Add usage documentation
* Add setup.py

Notes
-----
This software was developed during my time at [Pontiflex, Inc.](http://www.pontiflex.com), and thus that organization owns the copyright.

Authors
-------

* Matthew Conlen (<a href="http://github.com/mathisonian">mathisonian</a>)
* Chris Clouten (<a href="http://github.com/triplec1988">triplec1988</a>)

License
-------

Copyright 2012, 2013 Pontiflex, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this work except in compliance with the License. You may obtain a copy of the License in the LICENSE file, or at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
