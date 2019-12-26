#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

import numpy as np
from scipy.integrate import odeint

from .app import app
from .common import iterate_theta


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


def compute(L1, L2, m1, m2, tmax, dt, theta1_init, theta2_init):
    y0 = np.array([theta1_init, 0, theta2_init, 0])
    theta1, theta2 = solve(L1, L2, m1, m2, tmax, dt, y0)

    return theta2_init, theta1[-1], theta2[-1]


@app.task
def compute_single(L1, L2, m1, m2, tmax, dt, theta1_init, theta2_init):
    return compute(L1, L2, m1, m2, tmax, dt, theta1_init, theta2_init)


@app.task
def compute_chunk(L1, L2, m1, m2, tmax, dt, theta1_init, theta_resolution):
    return (
        theta1_init,
        [
            compute(L1, L2, m1, m2, tmax, dt, theta1_init, theta2_init)
            for theta2_init in iterate_theta(theta_resolution)
        ]
    )
