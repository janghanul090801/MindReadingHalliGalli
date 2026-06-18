def get_clipboard_text():

    from tkinter import Tk

    root = Tk()
    root.withdraw()

    text = root.clipboard_get()

    root.destroy()

    return text.strip().replace("\n", "").replace("\r", "")