"""
Simple windowed UI.

See example: https://likegeeks.com/python-gui-examples-tkinter-tutorial/

"""

from tkinter import *


def start_main_ui(url, host_state):

    window = Tk()
    window.title('Princeton IoT Inspector')
    window.geometry('600x400')
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
        'Currently capturing traffic on your local network.\n'
    )

    Label(
        window,
        text="Close this window to stop the capture."
    ).grid(column=0, row=2)

    Label(
        window,
        text="\n\nCopy the URL below to view the IoT Inspector report."
    ).grid(column=0, row=3)

    txt_box = Entry(window, width=len(url), justify='center')
    txt_box.insert(0, url)
    txt_box.grid(column=0, row=4)

    window.mainloop()
