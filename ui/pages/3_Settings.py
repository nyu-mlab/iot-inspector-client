import os
import time
import streamlit as st
import template
import core.config as config
import core.model as model
import core.common as common
import core.global_state as global_state
import sidebar


template.show(
    'Settings'
)


def show_settings():

    st.markdown('### Data Management')

    st.markdown('The operations below are permanent. Proceed with caution.')

    st.divider()

    column_width_list = [0.3, 0.7]

    c1, c2 = st.columns(column_width_list)
    c2.markdown('Delete all data collected locally, reset IoT Inspector, and shut down IoT Inspector. Feel free to restart manually.')
    reset_button = c1.button('Reset IoT Inspector', use_container_width=True)
    if reset_button:
        c1l, c1r = c1.columns(2)
        c1l.button('Confirm', type='primary', on_click=reset_local_data)
        c1r.button('Cancel', type='secondary')

    user_key = config.get('user_key', '')
    if user_key:
        st.divider()
        c1, c2 = st.columns(column_width_list)
        c2.markdown(f'Delete all data donated to New York University (associated with your randomly generated `user_key`: `{user_key}`). This operation does not affect the data collected locally.')
        reset_button = c1.button('Delete all donated data', use_container_width=True)
        if reset_button:
            c1l, c1r = c1.columns(2)
            c1l.button('Confirm', type='primary', on_click=delete_donated_data, args=[c1])
            c1r.button('Cancel', type='secondary')



def reset_local_data():

    with model.write_lock:

        # Path of the SQLite database
        db_path = model.db_path

        # Delete the entire database file plus any auxiliary files
        for filename in [db_path, db_path + '-wal', db_path + '-shm']:
            if os.path.exists(filename):
                os.remove(filename)

    sidebar.quit()



def delete_donated_data(col):

    user_key = config.get('user_key', '')
    if not user_key:
        return

    with col.empty():

        st.info('Deleting donated data...')
        time.sleep(1)
        try:
            common.http_request(
                method='get',
                args=[global_state.DELETE_DATA_URL + f'/{user_key}']
            )
        except IOError:
            st.error('Failed to delete donated data.')
        else:
            # Reset donation state
            config.set('should_donate_data', False)
            config.set('donation_start_ts', 0)
            st.success('Deleted.')
        finally:
            time.sleep(4)
            st.write('')



show_settings()