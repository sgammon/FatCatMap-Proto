=====================
Batch marker creation
=====================

This packages provides the possibility to create markers for every N
objects of a given query. This is useful to create batched html pages
or to generate jobs for every N objects.

A list of attribute values are created that represent the end of a
batch at any given position in a given query. The result is stored in
memcache and the key is provided to a callback function.

    >>> from lovely.gae import batch

Let us create some test objects.

    >>> from google.appengine.ext import db
    >>> class Stub(db.Model):
    ...     c_time = db.DateTimeProperty(auto_now_add=True, required=True)
    ...     name = db.StringProperty()
    ...     age = db.IntegerProperty()
    ...     state = db.IntegerProperty()
    ...     def __repr__(self):
    ...         return '<Stub %s>' % self.name

    >>> for i in range(1,13):
    ...     s = Stub(name=str(i), age=i, state=i%2)
    ...     sk = s.put()

    >>> Stub.all().count()
    12

First we make sure that we have no tasks in the queue for testing.

    >>> from lovely.gae.async import get_tasks
    >>> len(get_tasks())
    0

So for example if we want to know any 100th key of a given kind we
could calculate it like shown below. Note that we provide the pprint function
as a callback, so we get the memcache key in the output.

The calculate_markers function returns the memcache key that will be
used to store the result when the calculation is completed.

    >>> from pprint import pprint
    >>> mc_key = batch.create_markers('Stub', callback=pprint)
    >>> mc_key
    'create_markers:...-...-...'

A task gets created.

    >>> tasks = get_tasks()
    >>> len(tasks)
    1

Let us run the task.

    >>> run_tasks(1)
    1

We now have another task left for the callback, which is actually the
pprint function.

    >>> run_tasks()
    'create_markers:...-...-...'
    1

We should now have a result. The result shows that we need no batches
for the given batch size (because we only have 12 objects).

    >>> from google.appengine.api import memcache
    >>> memcache.get(mc_key)
    []

Let us use another batch size. This time without callback.

    >>> mc_key = batch.create_markers('Stub', batchsize=1)
    >>> run_tasks()
    1

We now have exatly 12 keys, because the batch size was 1.

    >>> len(memcache.get(mc_key))
    12

The default attributes returned are the keys.

    >>> memcache.get(mc_key)
    [datastore_types.Key.fro...

We can also use other attributes. Let us get items batched by c_time
descending. Note that it is not checked if values are not unique, so
if a non-unique attribute is used it might be the case that batch
ranges contains objects twice.

    >>> mc_key = batch.create_markers('Stub',
    ...                               attribute='c_time',
    ...                               order='desc',
    ...                               batchsize=3)
    >>> run_tasks()
    1
    >>> markers = memcache.get(mc_key)
    >>> markers
    [datetime.datetime(...
    >>> len(markers)
    4
    >>> sorted(markers, reverse=True) == markers
    True

    >>> mc_key = batch.create_markers('Stub',
    ...                               attribute='c_time',
    ...                               order='asc',
    ...                               batchsize=3)
    >>> run_tasks()
    1
    >>> markers = memcache.get(mc_key)
    >>> markers
    [datetime.datetime(...
    >>> len(markers)
    4
    >>> sorted(markers) == markers
    True


We can also pass filters to be applied to the query for the batch like this:

    >>> mc_key = batch.create_markers('Stub',
    ...                               filters=[('state', 0)],
    ...                               attribute='c_time',
    ...                               order='asc',
    ...                               batchsize=3)
    >>> run_tasks()
    1
    >>> markers = memcache.get(mc_key)
    >>> len(markers)
    2


