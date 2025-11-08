# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nwcicdsetup']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'aiohttp==3.7.2',
 'asyncio>=3.4.3,<4.0.0',
 'pylint>=2.11.1,<3.0.0',
 'schema>=0.7.4,<0.8.0']

setup_kwargs = {
    'name': 'nwcicdsetup',
    'version': '2.3.0.20251107.dev193',
    'description': '',
    'long_description': 'None',
    'author': 'nativewaves',
    'author_email': 'dev@nativewaves.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
