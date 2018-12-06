

BASE_URL = 'https://iot-inspector-report.cs.princeton.edu'

NEW_USER_URL = BASE_URL + '/generate_user_key'

REPORT_URL = BASE_URL + '/report/{user_key}'

SUBMIT_URL = BASE_URL + '/submit_data/{user_key}'

UTC_OFFSET_URL = BASE_URL + '/submit_utc_offset/{user_key}/{offset_seconds}'

CHECK_CONSENT_URL = BASE_URL + '/check_consent/{user_key}'

GET_BLACKLIST_URL = BASE_URL + '/get_blacklist/{user_key}'
