import time
import win32gui

winname = "test1.py"
hWnd = win32gui.FindWindow(None, winname)

wndpl = win32gui.GetWindowPlacement(hWnd)
old_state = wndpl[1]
old_rect = wndpl[4]
if old_state in [2,3]:
    nCmdShow = 1
    win32gui.ShowWindow(hWnd, nCmdShow)

win32gui.MoveWindow(hWnd, -8, -1, 1300, 540, True)

time.sleep(5)

win32gui.MoveWindow(hWnd, *old_rect, True)

if old_state in [2,3]:
    win32gui.ShowWindow(hWnd, old_state)