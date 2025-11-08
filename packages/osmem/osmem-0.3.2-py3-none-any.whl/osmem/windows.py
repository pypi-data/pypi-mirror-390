# windows.py - windows specific acceleration for process information extraction
# Copyright (C) 2024 Jonas Tingeborn

# Fast PID -> PPID generation, since psutil is incredibly slow for this operation on windows (fast on *nix though).
# about 3-5ms vs several seconds with psutil
import sys

if sys.platform.startswith('win32'):
    import ctypes
    from ctypes.wintypes import DWORD, BOOL, HANDLE
    from typing import Dict

    # https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot
    TH32CS_SNAPPROCESS = 0x00000002

    # https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/ns-tlhelp32-processentry32
    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [("dwSize", DWORD),
                    ("cntUsage", DWORD),
                    ("th32ProcessID", DWORD),
                    ("th32DefaultHeapID", ctypes.POINTER(DWORD)),
                    ("th32ModuleID", DWORD),
                    ("cntThreads", DWORD),
                    ("th32ParentProcessID", DWORD),
                    ("pcPriClassBase", DWORD),
                    ("dwFlags", DWORD),
                    ("szExeFile", ctypes.c_char * 260)]

    # Load Library
    kernel32 = ctypes.WinDLL('kernel32')

    CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
    CreateToolhelp32Snapshot.argtypes = [DWORD, DWORD]
    CreateToolhelp32Snapshot.restype = HANDLE

    Process32First = kernel32.Process32First
    Process32First.argtypes = [HANDLE, ctypes.POINTER(PROCESSENTRY32)]
    Process32First.restype = BOOL

    Process32Next = kernel32.Process32Next
    Process32Next.argtypes = [HANDLE, ctypes.POINTER(PROCESSENTRY32)]
    Process32Next.restype = BOOL

    CloseHandle = kernel32.CloseHandle
    CloseHandle.argtypes = [HANDLE]
    CloseHandle.restype = BOOL

    def get_pid_map() -> Dict[int, int]:
        """Returns a child->parent pid map for all processes on the system"""
        hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
        out = {}
        if Process32First(hSnapshot, ctypes.byref(pe)):
            while True:
                pid, ppid = pe.th32ProcessID, pe.th32ParentProcessID
                out[pid] = ppid
                if not Process32Next(hSnapshot, ctypes.byref(pe)):
                    break
        CloseHandle(hSnapshot)
        return out

else:
    get_pid_map = None
