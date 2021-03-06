"""Utilities tasks and functions"""
from __future__ import print_function

import re
import sys

from fabric.api import env, run


def distro_info():
    """Task which figures out the distro information based on the
    /etc/redhat-release file

    A ``(distro, major_version)`` tuple is returned if called as a function.
    For RHEL X.Y.Z it will return ``('rhel', X)``. For Fedora X it will return
    ``('fedora', X)``. Be aware that the major_version is an integer.

    """
    # Create/manage host cache
    cache = env.get('distro_info_cache')
    host = env['host']
    if cache is None:
        cache = env['distro_info_cache'] = {}

    if host not in cache:
        # Grab the information and store on cache
        release_info = run('cat /etc/redhat-release', quiet=True)
        if release_info.failed:
            print('Failed to read /etc/redhat-release file')
            sys.exit(1)

        # Discover the distro
        if release_info.startswith('Red Hat Enterprise Linux'):
            distro = 'rhel'
        elif release_info.startswith('Fedora'):
            distro = 'fedora'
        else:
            distro = None

        # Discover the version
        match = re.search(r' ([0-9.]+) ', release_info)
        if match is not None:
            parts = match.group(1).split('.')
            # extract the major version
            major_version = int(parts[0])
            # extract the minor version
            if len(parts) > 1:
                minor_version = int(parts[1])
            else:
                minor_version = None
        else:
            major_version = minor_version = None

        if distro is None or major_version is None:
            print('Was not possible to fetch distro information')
            sys.exit(1)

        cache[host] = distro, major_version, minor_version

    distro, major_version, minor_version = cache[host]
    print('{0} {1} {2}'.format(distro, major_version, minor_version))
    return distro, major_version, minor_version


def update_packages(*args, **kwargs):
    """Updates all system packages or only ones specified by `args`

    Use this if you want to simply update all packages or some on system.
    Possibly useful for when doing upgrades, etc.

    """
    if len(args) > 0:
        arguments = ' '.join(args)
    else:
        arguments = ''

    run(
        'yum update -y {0}'.format(arguments),
        quiet=kwargs.get('quiet', False),
        warn_only=kwargs.get('warn_only', False),
    )
