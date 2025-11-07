import sys, os
import platform
from pathlib import Path

def enable_autostart_windows(app_name='PyPanelPro', exe_path=None):
    try:
        import winreg
        if exe_path is None:
            exe_path = sys.executable + ' ' + str(Path(__file__).resolve().parents[1] / 'main.py')
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        key.Close()
        return True
    except Exception as e:
        return False

def disable_autostart_windows(app_name='PyPanelPro'):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, app_name)
        key.Close()
        return True
    except Exception:
        return False
