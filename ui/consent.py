import time
import streamlit as st
import core.config as config
import core.global_state as global_state
import os
import sidebar


def show():

    # Check if we need to show any risk consent
    if not config.get('has_consented_to_overall_risks', False):
        show_overall_risks()
        st.stop()

    # Show the data donation consents if the user has not indicated any choices
    if config.get('has_consented_to_data_donation', 'not_set') == 'not_set':
        show_data_donation_consent()
        st.stop()


def show_overall_risks():

    # Show the consent
    with open(os.path.join(get_current_file_directory(), 'consent_overall_risks.md'), 'r') as f:
        st.markdown(f.read(), unsafe_allow_html=True)

    st.divider()

    # Show a primary button to accept the consent
    consent = st.button('I accept the risks.', type='primary')
    if consent:
        config.set('has_consented_to_overall_risks', True)
        st.experimental_rerun()

    # Show a secondary button to reject the consent and quit
    reject = st.button('I do not accept the risks. I would like to quit IoT Inspector.', type='secondary')
    if reject:
        sidebar.quit()



def show_data_donation_consent():

    # Show the consent
    with open(os.path.join(get_current_file_directory(), 'consent_data_donation.md'), 'r') as f:
        st.markdown(f.read(), unsafe_allow_html=True)

    st.divider()

    config.set('has_consented_to_data_donation', 'not_set')

    c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
    c1.markdown('I want to give consent to participate in this study, which includes\n * donating my network traffic data to the IoT Inspector project\n * receiving personalized feedback from IoT Inspector\n * taking a survey about my experience with IoT Inspector')
    c2.button('Yes', 'yes_donate_with_survey', use_container_width=True, type='primary', on_click=yes_donate_with_survey_callback)
    c3.button('No', 'no_donate_with_survey', use_container_width=True, on_click=no_donate_with_survey_callback)

    if 'show_second_consent' not in st.session_state:
        st.session_state['show_second_consent'] = False

    if st.session_state['show_second_consent']:
        st.divider()
        c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
        c1.markdown('I give consent to data donation and receiving personalized feedback from IoT Inspector, but not taking the survey.')
        c2.button('Yes', 'yes_donate', use_container_width=True, on_click=yes_donate_callback)
        c3.button('No', 'no_donate', use_container_width=True, on_click=no_donate_callback)
        st.session_state['show_second_consent'] = False



def yes_donate_with_survey_callback():

    config.set('has_consented_to_data_donation', 'donation_with_survey')
    yes_callback()



def yes_donate_callback():

    config.set('has_consented_to_data_donation', 'donation_only')
    yes_callback()



def yes_callback():
    config.set('should_donate_data', True)
    config.set('donation_start_ts', int(time.time()))



def no_donate_with_survey_callback():

    st.session_state['show_second_consent'] = True



def no_donate_callback():

    config.set('has_consented_to_data_donation', 'no_consent')
    config.set('should_donate_data', False)
    config.set('donation_start_ts', 0)



def get_current_file_directory():
    """
    Returns the directory where this python file is located.

    """
    return os.path.dirname(os.path.abspath(__file__))

