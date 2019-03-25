import sys


if '--test' in sys.argv:
    BASE_URL = 'https://iot-inspector-report.cs.princeton.edu'
else:
    BASE_URL = 'https://inspector.cs.princeton.edu'

NEW_USER_URL = BASE_URL + '/generate_user_key'

SUBMIT_URL = BASE_URL + '/submit_data/{user_key}'

UTC_OFFSET_URL = BASE_URL + '/submit_utc_offset/{user_key}/{offset_seconds}'

CHECK_CONSENT_URL = BASE_URL + '/has_signed_consent_form/{user_key}'
