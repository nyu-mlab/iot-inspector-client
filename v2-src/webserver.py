from flask import Flask
from flask_cors import CORS
import inspector
import threading


app = Flask(__name__)
cors = CORS(
    app,
    resources={r"/*": {"origins": "https://inspector.cs.princeton.edu"}}
)


context = {
    'host_state': None,
    'quit': False
}


def start_thread():

    th = threading.Thread(
        target=app.run,
        kwargs={'port': 46241}
    )
    th.daemon = True
    th.start()


@app.route('/get_status_text', methods=['GET'])
def get_status_text():

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            return host_state.status_text

    return ''


@app.route('/is_inspecting_traffic', methods=['GET'])
def is_inspecting_traffic():

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            return str(host_state.is_inspecting_traffic).lower()

    return 'false'


@app.route('/get_user_key', methods=['GET'])
def get_user_key():

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            if host_state.user_key is not None:
                return host_state.user_key

    return ''


@app.route('/start_fast_arp_discovery', methods=['GET'])
def start_fast_arp_discovery():

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            host_state.fast_arp_scan = True

    return 'OK'


@app.route('/start_inspecting_traffic', methods=['GET'])
def start_inspecting_traffic():

    inspector.enable_ip_forwarding()

    # Start inspecting
    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            host_state.is_inspecting_traffic = True

    return 'OK'


@app.route('/pause_inspecting_traffic', methods=['GET'])
def pause_inspecting_traffic():

    inspector.disable_ip_forwarding()

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            host_state.is_inspecting_traffic = False

    return 'OK'


@app.route('/exit', methods=['GET'])
def exit_inspector():

    inspector.disable_ip_forwarding()

    context['quit'] = True

    return 'OK'
