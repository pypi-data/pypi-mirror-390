# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['binarycookies']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=2.0.0,<3.0.0', 'typer>=0.12.3,<0.21.0']

entry_points = \
{'console_scripts': ['bcparser = binarycookies.__main__:main']}

setup_kwargs = {
    'name': 'binarycookies',
    'version': '2.3.0',
    'description': 'Python Binary Cookies (de)serializer',
    'long_description': '[![Github Actions Status](https://github.com/dan1elt0m/binary-cookies-reader/workflows/test/badge.svg)](https://github.com/dan1elt0m/binary-cookies-reader/actions/workflows/test.yml)\n<h1>\n  <img src="docs/bincook.png" width="30" style="vertical-align: middle; margin-right: 10px;">\n  Binary Cookies\n</h1>\n\nCLI tool and Python library for reading and writing Binary Cookies.\n\n### Documentation\nFor detailed documentation, please visit the [Binary Cookies Documentation](https://dan1elt0m.github.io/binarycookies/)\n\n### Requirements\n\n- Python >= 3.9\n\n### Installation\n```bash \npip install binarycookies\n```\n\n### CLI example:\n```sh\nbcparser path/to/cookies.binarycookies\n```\n\nOutput:\n```json\n[\n  {\n    "name": "session_id",\n    "value": "abc123",\n    "url": "https://example.com",\n    "path": "/",\n    "create_datetime": "2023-10-01T12:34:56+00:00",\n    "expiry_datetime": "2023-12-31T23:59:59+00:00",\n    "flag": "Secure"\n  },\n  {\n    "name": "user_token",\n    "value": "xyz789",\n    "url": "https://example.com",\n    "path": "/account",\n    "create_datetime": "2023-10-01T12:34:56+00:00",\n    "expiry_datetime": "2023-12-31T23:59:59+00:00",\n    "flag": "HttpOnly"\n  }\n]\n```\n#### Output formats\nThe CLI supports multiple output formats using the --output flag.\n- `json` (default): Outputs cookies in JSON format.\n- `ascii`: Outputs cookies in a human-readable ASCII format with each cookie property on a separate line.\n- `netscape`: Outputs cookies in the Netscape cookie file format.\n\n### Basic Usage Python\n\n#### Deserialization\n\n```python\nimport binarycookies \n\nwith open("path/to/cookies.binarycookies", "rb") as f:\n    cookies = binarycookies.load(f)\n```\n\n#### Serialization\n\n```python\nimport binarycookies \n\ncookie = {\n    "name": "session_id",\n    "value": "abc123",\n    "url": "https://example.com",\n    "path": "/",\n    "create_datetime": "2023-10-01T12:34:56+00:00",\n    "expiry_datetime": "2023-12-31T23:59:59+00:00",\n    "flag": "Secure"\n}\n\nwith open("path/to/cookies.binarycookies", "wb") as f:\n    binarycookies.dump(cookie, f)\n```\n\n### Ethical Use & Responsible Handling\nThis project is intended for lawful, ethical use only. Typical, appropriate uses include:\n- Inspecting Binary Cookies from your own devices or data you are authorized to access\n- DFIR, QA, and security testing performed with explicit, written permission\n- Educational/research work on datasets that are owned by you, anonymized, or publicly released for that purpose\n\nYou must not use this tool to:\n- Access, extract, modify, or distribute cookies from systems or accounts you do not own or have permission to analyze\n- Bypass authentication, session management, DRM, or other technical controls\n- Enable tracking, stalking, doxxing, fraud, or other privacy-invasive or harmful activities\n\n\n### License\nThis project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.\n\n### Contributing\nContributions are welcome! If you find a bug or have a feature request, please open an issue on GitHub. Pull requests are also welcome.\n',
    'author': 'Daniel Tom',
    'author_email': 'd.e.tom89@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
