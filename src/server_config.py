import sys


BASE_URL = 'https://dashboard.iotinspector.org'

NEW_USER_URL = BASE_URL + '/generate_user_key'

SUBMIT_URL = BASE_URL + '/submit_data/{user_key}'

UTC_OFFSET_URL = BASE_URL + '/submit_utc_offset/{user_key}/{offset_seconds}'

CHECK_CONSENT_URL = BASE_URL + '/has_signed_consent_form/{user_key}'

INIT_URL = BASE_URL + '/setup?started_from_app=yes'

NPCAP_ERROR_URL = 'https://iotinspector.org/npcap-error/'

NETMASK_ERROR_URL = 'https://iotinspector.org/netmask-error/'