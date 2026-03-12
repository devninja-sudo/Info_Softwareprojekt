import os
import sys


def resource_path(relative_path:str)->str:
    '''
    Vor.: -relative_path- ist ein relativer Pfad innerhalb des Projekts.
    Eff.: -
    Erg.: Der zur Laufzeit gueltige absolute Pfad ist geliefert, sowohl im Projektordner als auch in einer PyInstaller-Exe.
    '''
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)