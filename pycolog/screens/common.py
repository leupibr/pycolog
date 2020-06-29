import curses


def warn(screen, msg):
    screen.addstr(curses.LINES - 2, 0, msg)
    screen.clrtoeol()
