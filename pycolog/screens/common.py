import curses


def warn(screen, msg):
    """
    Helper to write warning message on the correct line
    """
    screen.addstr(curses.LINES - 2, 0, msg)
    screen.clrtoeol()
