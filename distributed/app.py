#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

from celery import Celery
from celery.signals import worker_ready


app = Celery('distributed')
app.config_from_object('distributed.celeryconfig')


if app.conf.AM_I_SERVER:
    @worker_ready.connect
    def bootstrap(**kwargs):
        from .server import distributed_chunk

        delay_time = 2
        print(f'Getting ready to automatically seed computations in {delay_time} seconds...')
        kwargs = {
            'L1': app.conf.PENDULUM_L1,
            'L2': app.conf.PENDULUM_L2,
            'm1': app.conf.PENDULUM_M1,
            'm2': app.conf.PENDULUM_M2,
            'tmax': app.conf.PENDULUM_TMAX,
            'dt': app.conf.PENDULUM_DT,
            'theta_resolution': app.conf.PENDULUM_THETA_RESOLUTION,
        }
        distributed_chunk.apply_async(kwargs=kwargs, countdown=delay_time)


if __name__ == '__main__':
    app.start()
