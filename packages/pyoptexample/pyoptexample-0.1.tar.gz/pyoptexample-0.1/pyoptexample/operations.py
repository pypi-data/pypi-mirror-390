import ctypes
import os

# Gets the absolute path to the installation folder to import the C/C++ DLLs/SOs
script_directory = os.path.dirname(os.path.abspath(__file__))
folder_modified = script_directory.replace("\\", "/")

# Importing the C/C++ DLLs or SOs
try:
    # For Windows OS users
    cpplibrary = ctypes.CDLL(f"{folder_modified}/sum.dll")
    clibrary = ctypes.CDLL(f"{folder_modified}/difference.dll")
except Exception as e:
    # For Mac/Linux OS users
    cpplibrary = ctypes.CDLL(f"{folder_modified}/sum.so")
    clibrary = ctypes.CDLL(f"{folder_modified}/difference.so")      

def add(a, b):
    """
    This function calls a C++ library to
    add a and b in python at the speed of C++
    """
    
    result = cpplibrary.sum(a, b)
    
    return result


def subtract(a, b):
    
    """
    This function calls a C library called 
    to subtract a and b in python at the speed of C. 
    """

    result = clibrary.difference(a, b)
    
    return result

