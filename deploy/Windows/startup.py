import os
import sys
import winreg
from win32com.client import Dispatch

APP_NAME = "StarRailCopilot"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

def _open_run_key(access=winreg.KEY_READ):
    return winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, access)

def get_startup_status(app_name: str = APP_NAME) -> bool:
    try:
        with _open_run_key() as k:
            winreg.QueryValueEx(k, app_name)
        return True
    except FileNotFoundError:
        return False

def create_shortcut(target_path, shortcut_path, working_dir, arguments=""):
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.WorkingDirectory = working_dir
    shortcut.Arguments = arguments
    shortcut.save()

def set_startup_status(enabled: bool, app_name: str = APP_NAME) -> None:
    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir
    ))
    
    shortcut_path = os.path.join(root_dir, f"{app_name}.lnk")
    
    if enabled:
        try:
            from module.webui.setting import State
            is_packaged = bool(State.electron)
        except Exception:
            is_packaged = False
        
        if is_packaged:
            target_path = os.path.join(root_dir, "src.exe")
            arguments = "--run src"
        else:
            target_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            arguments = f'"{os.path.join(root_dir, "gui.py")}"'
        
        create_shortcut(target_path, shortcut_path, root_dir, arguments)
        
        with _open_run_key(winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, app_name, 0, winreg.REG_SZ, shortcut_path)
    
    else:
        try:
            with _open_run_key(winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, app_name)
        except FileNotFoundError:
            pass