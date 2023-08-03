import streamlit as st
import core.config as config



LEARN_MORE_LINK = '[Learn more](https://github.com/nyu-mlab/iot-inspector-client/wiki/Frequently-Asked-Questions#why-should-i-donate-my-data-to-the-researchers).'



def show_basic_box(button_key, nudge_text):
    """
    Shows a box to nudge the user toward donating the data. We're a research study! We'd like
    users to donate their data :)

    """
    c1, c2 = st.columns([0.8, 0.2])

    c1.warning(
        body=nudge_text,
        icon="💡"
    )

    c2.button(
        label='Donate Data',
        type='primary',
        use_container_width=True,
        on_click=start_donation,
        key=button_key
    )



def start_donation():
    config.set('should_donate_data', True)
    config.set('has_consented_to_data_donation', 'not_set')



def show_on_device_list(location='below'):

    if config.get('should_donate_data', False):
        return

    st.divider()

    show_basic_box(
        f'donate_data_button_on_device_list_{location}',
        f"Can't identify the devices {location}? Please donate your data to New York University researchers, in exchange for insights about these devices. {LEARN_MORE_LINK}"
    )

    st.divider()



def show_on_device_activities():

    if config.get('should_donate_data', False):
        return

    show_basic_box(
        f'donate_data_button_on_device_activities',
        f"Lots of unknown device activities below? Please donate your data to New York University researchers, in exchange for insights about these unknown activities. {LEARN_MORE_LINK}"
    )

    st.divider()