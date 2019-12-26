#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

import argparse
import multiprocessing
import numpy as np
import csv

from contextlib import contextmanager
from scipy.integrate import odeint


DEFAULT_RESOLUTION = 6
DEFAULT_TMAX = 30
DEFAULT_DT = 0.01

DEFAULT_L1 = 1
DEFAULT_L2 = 1
DEFAULT_M1 = 1
DEFAULT_M2 = 1

# The gravitational acceleration
g = 9.81


def deriv(y, t, L1, L2, m1, m2):
    theta1, z1, theta2, z2 = y
    c, s = np.cos(theta1 - theta2), np.sin(theta1 - theta2)
    theta1dot = z1
    z1dot = (m2 * g * np.sin(theta2) * c - m2 * s * (L1 * z1**2 * c + L2 * z2**2) - (m1 + m2) * g * np.sin(theta1)) / L1 / (m1 + m2 * s**2)
    theta2dot = z2
    z2dot = ((m1 + m2) * (L1 * z1**2 * s - g * np.sin(theta2) + g * np.sin(theta1) * c) + m2 * L2 * z2**2 * s * c) / L2 / (m1 + m2 * s**2)

    return theta1dot, z1dot, theta2dot, z2dot


def solve(L1, L2, m1, m2, tmax, dt, y0):
    t = np.arange(0, tmax + dt, dt)
    y = odeint(deriv, y0, t, args=(L1, L2, m1, m2))

    return y[:, 0], y[:, 2]


def _init_pool(*data):
    global _pool_data
    _pool_data = data  # L1, L2, m1, m2, tmax, dt


def _worker(args):
    L1, L2, m1, m2, tmax, dt = _pool_data

    theta1_init, theta2_init = args
    y0 = np.array([theta1_init, 0, theta2_init, 0])

    theta1, theta2 = solve(L1, L2, m1, m2, tmax, dt, y0)

    return theta1_init, theta2_init, theta1[-1], theta2[-1]


def gen_simulation_model_params(theta_resolution):
    search_space = np.linspace(0, 2 * np.pi, theta_resolution)
    for theta1_init in search_space:
        for theta2_init in search_space:
            yield theta1_init, theta2_init


@contextmanager
def simulate_pendulum(theta_resolution, dt=DEFAULT_DT, tmax=DEFAULT_TMAX, L1=DEFAULT_L1, L2=DEFAULT_L2, m1=DEFAULT_M1, m2=DEFAULT_M2):
    try:
        pool = multiprocessing.Pool(
            initializer=_init_pool,
            initargs=(L1, L2, m1, m2, tmax, dt)
        )

        yield pool.imap(
            func=_worker,
            iterable=gen_simulation_model_params(theta_resolution),
            chunksize=theta_resolution,
        )
    finally:
        pool.terminate()


def convert_results(results):
    for r in results:
        yield {
            'theta1_init': r[0],
            'theta2_init': r[1],
            'theta1': r[2],
            'theta2': r[3],
        }


def write_csv(file_name, results):
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = ['theta1_init', 'theta2_init', 'theta1', 'theta2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'results_file',
        help="Filename where the results will be stored, in CSV format"
    )
    parser.add_argument(
        '-r',
        '--resolution',
        metavar='NUM',
        type=int,
        default=DEFAULT_RESOLUTION,
        help="Resolution, %d by default" % DEFAULT_RESOLUTION
    )
    parser.add_argument(
        '--tmax',
        metavar='NUM',
        type=float,
        default=DEFAULT_TMAX,
        help="Simulation time, %f by default" % DEFAULT_TMAX
    )
    parser.add_argument(
        '--dt',
        metavar='NUM',
        type=float,
        default=DEFAULT_DT,
        help="Simulation time step, %f by default" % DEFAULT_DT
    )
    args = parser.parse_args()

    with simulate_pendulum(
        theta_resolution=args.resolution,
        dt=args.dt,
        tmax=args.tmax,
    ) as results:
        converted_results = convert_results(results)
        write_csv(args.results_file, converted_results)


if __name__ == '__main__':
    main()
