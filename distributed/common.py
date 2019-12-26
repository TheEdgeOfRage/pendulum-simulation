#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

import numpy as np


def iterate_both_theta(theta_resolution):
    search_space = np.linspace(0, 2 * np.pi, theta_resolution)
    for theta1 in search_space:
        for theta2 in search_space:
            yield theta1, theta2


def iterate_theta(theta_resolution):
    search_space = np.linspace(0, 2 * np.pi, theta_resolution)
    for theta in search_space:
        yield theta
