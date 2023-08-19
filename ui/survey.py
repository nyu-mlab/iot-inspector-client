import os
import time
import streamlit as st
import core.config as config
import core.global_state as global_state


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

    last_completed_survey = config.get('last_completed_survey', '')

    if last_completed_survey == '':
        # Show the pre survey if the user has not completed any surveys yet and that the user has never used inspector
        if not config.get('has_used_inspector', False):
            get_survey_ui('notice_and_choice_pre_survey.md', ask_for_country_info=True)
            st.stop()

    elif last_completed_survey == 'notice_and_choice_pre_survey':
        # Show the post survey only if the user has completed the pre-survey and
        # the user has been collecting data for 10 minutes
        with global_state.global_state_lock:
            time_threshold = 45 if global_state.DEBUG else 600
        if time.time() - donation_start_ts > time_threshold:
            # Skip if we just opened the app; this trick is to avoid showing the
            # survey when the user just opened the app
            with global_state.global_state_lock:
                if global_state.inspector_started_ts > 0 and time.time() - global_state.inspector_started_ts < time_threshold:
                    return
            get_survey_ui('notice_and_choice_post_survey.md')
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

        st.markdown(question_text)

        if question_type == 'YesNo':
            radio_options = ['Yes', 'No', 'N/A']
        elif question_type == '7PtLikert':
            radio_options = ['Strongly disagree', 'Disagree', 'Somewhat disagree', 'Neither agree nor disagree', 'Somewhat agree', 'Agree', 'Strongly agree', 'N/A']
        else:
            raise ValueError(f'Unknown question type: {question_type}')

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

