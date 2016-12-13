#!/usr/bin/env python
#
# Basic configuration attributes for scanner client.
#

# 'IP Address' is a list. It can contain one element, or more.
# If you put multiple FSF servers in, the one your client chooses will
# be done at random. A rudimentary way to distribute tasks.
SERVER_CONFIG = {'IP_ADDRESS': ['IP OR HOSTNAME OF YOUR FSF SERVER', 'IP OR HOSTNAME OF YOUR FSF SERVER', ],
                 'PORT': 5800}

# Full path to debug file if run with --suppress-report
CLIENT_CONFIG = {'LOG_FILE': '/path/to/client_dbg.log'}
