import subprocess
import os
import tempfile

# Create a temporary Python script for the taskbar UI
taskbar_code = """
import curses

TASKBAR_OPTIONS = ["Home", "Browser", "Search", "Exit"]

def draw_taskbar(stdscr, selected_idx):
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(h-1, 0, " " * (w - 1))
    for idx, option in enumerate(TASKBAR_OPTIONS):
        x = idx * (w // len(TASKBAR_OPTIONS))
        if idx == selected_idx:
            stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(h-1, x, option.center(w // len(TASKBAR_OPTIONS) - 1))
        if idx == selected_idx:
            stdscr.attroff(curses.A_REVERSE)
    stdscr.attroff(curses.color_pair(1))

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    selected_idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Taskbar UI - Use arrow keys to navigate. Press ENTER to select.")
        draw_taskbar(stdscr, selected_idx)
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_RIGHT:
            selected_idx = (selected_idx + 1) % len(TASKBAR_OPTIONS)
        elif key == curses.KEY_LEFT:
            selected_idx = (selected_idx - 1) % len(TASKBAR_OPTIONS)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if TASKBAR_OPTIONS[selected_idx] == "Exit":
                break

curses.wrapper(main)
"""

# Save the taskbar UI code to a temporary file
taskbar_script_path = os.path.join(tempfile.gettempdir(), "taskbar_ui.py")
with open(taskbar_script_path, "w") as f:
    f.write(taskbar_code)

# Launch tmux session with two panes
session_name = "tui_browser_session"
subprocess.run(["tmux", "new-session", "-d", "-s", session_name, f"python3 {taskbar_script_path}"])
subprocess.run(["tmux", "split-window", "-h", "-t", session_name, "w3m https://www.example.com"])
subprocess.run(["tmux", "select-pane", "-t", f"{session_name}:0.0"])
subprocess.run(["tmux", "attach-session", "-t", session_name])
