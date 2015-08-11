from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]

setup(name='logagg',
      version='0.1',
      description="Aggregate log files via a zmq socket",
      author="Kellen Fox",
      author_email="kellen@cablespeed.com",
      packages=['logagg'],
      scripts=['scripts/log-daemon', 'scripts/log-client'])
