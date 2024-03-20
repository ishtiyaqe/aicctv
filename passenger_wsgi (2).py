# Continue with the rest of your code
import sys,os
# Force Passenger to run our virtualenv python
INTERP = "/home/aicamer/aicctv/env/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)


from aicctv.wsgi import application as application


# import sys
# import os

# # Force Passenger to run our virtualenv python
# INTERP = "/home/aicamer/aicctv/env/bin/python"
# if sys.executable != INTERP:
#     os.execl(INTERP, INTERP, *sys.argv)
# import daphne

# # Import your WSGI application
# from aicctv.wsgi import application as wsgi_application

# host = '0.0.0.0'  # Listen on all available network interfaces
# port = 8001  # Use port 8001

# # Define the ASGI application using Daphne's Server class with endpoints
# application = daphne aicctv.asgi:application
