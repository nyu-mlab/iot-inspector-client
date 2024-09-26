import os
import time
import streamlit as st
import core.config as config
import core.global_state as global_state
import core.common as common
import hashlib
import uuid


DEBUG_TIMING = False


def show():

    # Make sure that the user has consented to donate data with survey
    try:
        if config.get('has_consented_to_data_donation') != 'donation_with_survey':
            return
    except KeyError:
        return

    # Make sure that data donation is turned on
    try:
        donation_start_ts = config.get('donation_start_ts')
        if donation_start_ts == 0:
            return
    except KeyError:
        return

    # Make sure that the user has used Inspector
    if not config.get('has_used_inspector', False):
        return

    # Make sure that the Qualtrics ID has been set
    qualtrics_id = config.get('qualtrics_id', '')
    if not qualtrics_id:
        return

    # Make sure that the user hasn't taken the qualtrics survey
    has_completed_qualtrics_survey = config.get('has_completed_qualtrics_survey', False)
    if has_completed_qualtrics_survey:
        return

    # Block the entire UI if the survey has shown but the user hasn't taken the survey
    if config.get('survey_should_be_blocking_ui', False):
        show_survey_text(qualtrics_id)

    # Show the post survey only if the user has been collecting data for 8 minutes
    with global_state.global_state_lock:
        time_threshold = 15 if global_state.DEBUG else (60 if DEBUG_TIMING else 8 * 60)
    if time.time() - donation_start_ts < time_threshold:
        time_remaining = int(time_threshold - (time.time() - donation_start_ts))
        common.log(f'[Survey] A: {time_remaining} seconds remaining before showing the survey')
        return

    # Skip if we just opened the app; this trick is to avoid showing the
    # survey when the user just opened the app
    with global_state.global_state_lock:
        if global_state.inspector_started_ts > 0 and time.time() - global_state.inspector_started_ts < time_threshold:
            time_remaining = int(time_threshold - (time.time() - donation_start_ts))
            common.log(f'[Survey] B: {time_remaining} seconds remaining before showing the survey')
            return

    show_survey_text(qualtrics_id)


def show_survey_text(qualtrics_id):

    # Show the post survey link
    survey_url = f'https://nyu.qualtrics.com/jfe/form/SV_6rubUTxywdNeaGi?UID={qualtrics_id}'

    with st.empty():
        with st.container():

            st.markdown('## IoT Inspector Survey')
            st.markdown(f'Please take [this survey]({survey_url}) to help us understand how you use IoT Inspector. ')

            config.set('survey_should_be_blocking_ui', True)
            if config.get('survey_first_shown_ts', 0) == 0:
                config.set('survey_first_shown_ts', time.time())

            # Show the option to enter the completion code only after 2 minutes
            if time.time() - config.get('survey_first_shown_ts') < (10 if DEBUG_TIMING else 2 * 60):
                for _ in range(100):
                    st.markdown('')
                time.sleep(5)
                st.experimental_rerun()

            for _ in range(10):
                st.markdown('')
            st.markdown('---')
            st.markdown('Once you have completed the survey, the survey will provide you with a completion code on the last page. Please paste the code below to return to IoT Inspector. ')

            def _exit_survey():
                completion_code = st.session_state.get('survey_completion_code', '')
                if len(completion_code) < 4:
                    st.error('Invalid completion code. Please try again.')
                    return
                config.set('has_completed_qualtrics_survey', True)

            # Show a textbox to enter the completion code
            st.text_input(
                label='Enter the completion code here',
                key='survey_completion_code',
                on_change=_exit_survey
            )

    st.stop()


def get_survey_ui(survey_filename, ask_for_country_info=False):

    st.markdown('## User Survey')

    st.markdown('Please help us improve IoT Inspector by answering a few questions. Your responses will be used for research purposes only. Thank you!')

    if ask_for_country_info:

        st.divider()

        # Load a list of countries
        country_list = []
        with open(os.path.join(os.path.dirname(__file__), 'country_list.txt'), 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    country_list.append(line)

        # Show a dropbox box with a list of known countries
        question_key = 'survey_question:demographics:country'
        st.selectbox(
            'Please select your country or region', country_list,
            key=question_key,
            on_change=save_survey_responses,
            args=(question_key,)
        )


    st.divider()

    question_list = parse_survey_questions(survey_filename)
    survey_name = survey_filename.split('.')[0]

    for question_dict in question_list:

        question_type = question_dict['question_type']
        question_text = question_dict['question_text']

        if question_type == 'YesNo':
            radio_options = ['Yes', 'No', 'N/A']
        elif question_type == '7PtLikert':
            radio_options = ['Strongly disagree', 'Disagree', 'Somewhat disagree', 'Neither agree nor disagree', 'Somewhat agree', 'Agree', 'Strongly agree', 'N/A']
        elif question_type == 'MCQ':
            question_text, choices = question_text.split('|', 1)
            question_text = question_text.strip()
            radio_options = [s.strip() for s in choices.split('*')]
        else:
            raise ValueError(f'Unknown question type: {question_type}')

        st.markdown(question_text)
        question_key = f'survey_question:{survey_name}:{question_text}'

        st.radio(
            label='Please make a selection',
            options=radio_options,
            index=len(radio_options) - 1,
            key=question_key,
            on_change=save_survey_responses,
            args=(question_key,),
            label_visibility='hidden',
            horizontal=False
        )

        st.divider()

    st.button(
        label='I have answered the questions above. Continue using IoT Inspector.',
        on_click=exit_survey,
        args=(survey_name,),
        type='primary'
    )



def get_survey_completion_code() -> str:

    # Generate a random UUID string
    random_code = str(uuid.uuid4()).replace('-', '')[0:12].upper()

    # Hash the UUID string
    hash_str = hashlib.sha256(random_code.encode('utf-8')).hexdigest()[0:4].upper()

    return random_code + hash_str



def exit_survey(survey_name):

    config.set('last_completed_survey', survey_name)



def save_survey_responses(question_key):
    """
    Save the survey question and response to the Configuration table.

    """
    question_text = question_key.split(':', 1)[1]

    # Modify existing responses
    current_survey_responses = config.get('survey_responses', {})
    current_survey_responses.setdefault(question_text, []).append({
        'response': st.session_state[question_key],
        'response_ts': time.time()
    })

    # Write back to DB
    config.set('survey_responses', current_survey_responses)
    config.set('survey_response_updated_ts', int(time.time()))



def parse_survey_questions(survey_filename):
    """
    Parses the survey file. Returns a list of dictionaries: {'question_type': str, 'question_text': str}

    """
    question_list = []

    survey_filename = os.path.join(
        os.path.dirname(__file__),
        'surveys',
        survey_filename
    )

    with open(survey_filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Extract the question type and the question
            question_type, question_text = line.split(':', 1)
            question_type = question_type.strip()
            question_text = question_text.strip()

            # Add the question to the list
            question_list.append({
                'question_type': question_type,
                'question_text': question_text
            })

    return question_list

