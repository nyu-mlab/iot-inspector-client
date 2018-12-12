"""
Simple windowed UI.

See example: https://likegeeks.com/python-gui-examples-tkinter-tutorial/

"""

from tkinter import *


def start_main_ui(url, host_state):

    window = Tk()
    window.title('Princeton IoT Inspector')
    window.geometry('500x300')
    window.attributes("-topmost", True)
    window.grid_columnconfigure(0, weight=1)

    Label(
        window,
        text="\nPrinceton IoT Inspector\n",
        font=("Arial Bold", 30)
    ).grid(column=0, row=0)

    host_state.status_text = StringVar()
    Label(
        window, textvariable=host_state.status_text
    ).grid(column=0, row=1)

    host_state.status_text.set(
        'Initializing...\n'
    )

    Label(
        window,
        text="Keep this window open\n" +
             "so that we can continuously analyze your network.\n" +
             "\n\nTo stop the analysis, simply close this window."
    ).grid(column=0, row=2)

    with host_state.lock:
        host_state.ui_is_ready = True

    window.mainloop()
