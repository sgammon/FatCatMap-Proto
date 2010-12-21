================
lovely.gae.async
================

This package executes jobs asynchronously, it uses the appengine
taskqueue to exectue the jobs.

    >>> from lovely.gae.async import defer, get_tasks

The defer function executes a handler asynchronously as a job. We
create 3 jobs that have the same signature.

    >>> import time
    >>> for i in range(3):
    ...     print defer(time.sleep, [0.3])
    <google.appengine.api.labs.taskqueue.taskqueue.Task object at ...>
    None
    None

Let us have a look on what jobs are there. Note that there is only one
because all the 3 jobs we added were the same.

    >>> len(get_tasks())
    1

If we change the signature of the job, a new one will be added.

    >>> added = defer(time.sleep, [0.4])
    >>> len(get_tasks())
    2

Normally jobs are automatically executed by the taskqueueapi, we have
a test method which executes the jobs and returns the number of jobs
done.

    >>> run_tasks()
    2

Now we can add the same signature again.

    >>> added = defer(time.sleep, [0.4])
    >>> run_tasks()
    1

We can also set only_once to false to execute a worker many times with
the same signature.

    >>> from pprint import pprint
    >>> defer(pprint, ['hello'], once_only=False)
    <google.appengine.api.labs.taskqueue.taskqueue.Task object at ...>
    >>> defer(pprint, ['hello'], once_only=False)
    <google.appengine.api.labs.taskqueue.taskqueue.Task object at ...>
    >>> run_tasks()
    'hello'
    'hello'
    2




