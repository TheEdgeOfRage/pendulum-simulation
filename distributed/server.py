#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

import csv

from celery import chord

from .app import app
from .worker import compute_single, compute_chunk
from .common import iterate_theta, iterate_both_theta


@app.task
def distributed_single(L1, L2, m1, m2, tmax, dt, theta_resolution):
    return chord(
        (
            compute_single.s(L1, L2, m1, m2, tmax, dt, theta1_init, theta2_init)
            for theta1_init, theta2_init in iterate_both_theta(theta_resolution)
        ),
        write_csv.s(),
    ).delay()


@app.task
def distributed_chunk(L1, L2, m1, m2, tmax, dt, theta_resolution):
    return chord(
        (
            compute_chunk.s(L1, L2, m1, m2, tmax, dt, theta1_init, theta_resolution)
            for theta1_init in iterate_theta(theta_resolution)
        ),
        write_csv.s(),
    ).delay()


def result_to_dict(theta1_init, result):
    return {
        'theta1_init': theta1_init,
        'theta2_init': result[0],
        'theta1': result[1],
        'theta2': result[2],
    }


@app.task
def write_csv(results):
    with open(app.conf.PENDULUM_OUTPUT_FILE, 'w', newline='') as csvfile:
        fieldnames = ['theta1_init', 'theta2_init', 'theta1', 'theta2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        for chunk in sorted(results):
            for result in chunk[1]:
                writer.writerow(result_to_dict(chunk[0], result))

    return len(results)
