#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

from multiprocessing import cpu_count
import os

from kombu import Queue


# Environment based settings
MAX_CPU_CORES = os.getenv('MAX_CPU_CORES', cpu_count())
AM_I_SERVER = (os.getenv('COMPUTER_TYPE') == 'server')

# Parameters
PENDULUM_L1 = int(os.getenv('PENDULUM_L1', 1))
PENDULUM_L2 = int(os.getenv('PENDULUM_L2', 1))
PENDULUM_M1 = int(os.getenv('PENDULUM_M1', 1))
PENDULUM_M2 = int(os.getenv('PENDULUM_M2', 1))
PENDULUM_TMAX = int(os.getenv('PENDULUM_TMAX', 30))
PENDULUM_DT = float(os.getenv('PENDULUM_DT', 0.01))
PENDULUM_THETA_RESOLUTION = int(os.getenv('PENDULUM_THETA_RESOLUTION', 6))
PENDULUM_OUTPUT_FILE = os.getenv('PENDULUM_OUTPUT_FILE', '/output/dis.csv')

# Concurrency settings
CELERYD_CONCURRENCY = MAX_CPU_CORES

# This ensures that each worker will only take one task at a time, when combined
# with late acks. This is the recommended configuration for long-running tasks.
# References:
#   * http://celery.readthedocs.org/en/latest/userguide/optimizing.html#prefetch-limits
#   * http://celery.readthedocs.org/en/latest/userguide/optimizing.html#reserve-one-task-at-a-time
#   * http://celery.readthedocs.org/en/latest/configuration.html#celeryd-prefetch-multiplier
#   * http://stackoverflow.com/questions/16040039/understanding-celery-task-prefetching
#   * https://bugs.launchpad.net/openquake-old/+bug/1092050
#   * https://wiredcraft.com/blog/3-gotchas-for-celery/
#   * http://www.lshift.net/blog/2015/04/30/making-celery-play-nice-with-rabbitmq-and-bigwig/
CELERYD_PREFETCH_MULTIPLIER = 1


# Task result backend settings
CELERY_RESULT_BACKEND = 'redis://redis'

# Message Routing
CELERY_DEFAULT_QUEUE = 'worker'
CELERY_DEFAULT_EXCHANGE = 'tasks'
CELERY_DEFAULT_ROUTING_KEY = 'worker'

if AM_I_SERVER:
    CELERY_QUEUES = (
        Queue('server', routing_key='server'),
    )
else:
    CELERY_QUEUES = (
        Queue('worker', routing_key='worker'),
    )


class ServerTasksRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task.startswith('distributed.server.'):
            return {'queue': 'server'}

        return None


CELERY_ROUTES = (
    ServerTasksRouter(),
)


# Broker Settings
BROKER_URL = "amqp://rabbitmq"
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

# Task execution settings
CELERY_MESSAGE_COMPRESSION = 'bzip2'
CELERY_TASK_RESULT_EXPIRES = None
CELERY_DISABLE_RATE_LIMITS = True
CELERY_TRACK_STARTED = True

# This ensures that the worker acks the task *after* it's completed.
# If the worker crashes or gets killed mid-execution, the task will be returned
# to the broker and restarted on another worker.
# References:
#   * https://wiredcraft.com/blog/3-gotchas-for-celery/
#   * http://celery.readthedocs.org/en/latest/configuration.html#celery-acks-late
#   * http://celery.readthedocs.org/en/latest/faq.html#faq-acks-late-vs-retry
CELERY_ACKS_LATE = True


# Worker settings
if AM_I_SERVER:
    CELERY_IMPORTS = ['distributed.server']
else:
    CELERY_IMPORTS = ['distributed.worker']

# HACK: Prevents weird SymPy related memory leaks
CELERYD_MAX_TASKS_PER_CHILD = 100
