"""
Utility functions and configuration for integration tests
"""

import os
from payagency_api import PayAgencyApi

# Create the API client with the same credentials as Node.js tests
api = PayAgencyApi(
    base_url="https://api.pay.agency",
    encryption_key=os.getenv("ENCRYPTION_KEY", "89ca59fb3b49ada55851021df12cfbc5"),
    secret_key=os.getenv("AUTH_TOKEN", "PA_TEST_94bf3520bcbe435f2ed558c31ac664f3e72dfa3114a3232e436e25f9"),
)
