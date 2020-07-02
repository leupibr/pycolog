"""Module containing the details view for single messages"""
import curses

from pycolog.screens.common import warn


class Details:
    """
    Screen that shows allows to select a specific log message
    and show the details of this particular message.
    """
    def __init__(self, environment):
        self._e = environment
        self._s = self._e.screen

    def show(self):
        """Entry point of the sub-screen routine"""
        entry_to_display = ''
        while True:
            self._s.move(curses.LINES - 1, 0)
            self._s.addstr(f'd: {entry_to_display}')
            self._s.clrtoeol()

            key = self._s.getkey()
            if key in '1234567890':
                entry_to_display += key
            elif key in ('KEY_ENTER', '\n'):
                break
            elif key in ('KEY_BACKSPACE', '\b'):
                entry_to_display = entry_to_display[:-1]
            elif key == 'q':
                return
            else:
                warn(self._s, f'Unhandled details key {key}')

        self._s.clear()
        try:
            line = self._e.log.get_entry(int(entry_to_display) - 1)
            self._s.addstr(self._e.line_format.format(int(entry_to_display), line.truncate(self._e.msglen)))
            y_pos, _ = self._s.getyx()
            self._s.move(y_pos + 2, self._e.idxlen + 2)
            self._s.hline(curses.ACS_HLINE, curses.COLS)
            self._s.move(y_pos + 4, 0)

            indent = 20 + 2
            for key, value in line.attributes.items():
                value = str(value).replace('\n', '\n' + ' ' * indent)
                self._s.addstr('{:>20s}: {}\n'.format(key, value))
        except IndexError:
            self._s.addstr(f'Unknown log entry {entry_to_display}')
        self._s.getkey()
        return
