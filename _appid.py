import ctypes
import os

def set_appid(appid: str):
    try:
        # This informs Windows that this process has a specific AppID
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except Exception as e:
        print(f"AppID could not be set: {e}")