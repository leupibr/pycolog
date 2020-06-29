import curses

from pycolog.screens.common import warn


class Details:
    def __init__(self, environment):
        self._e = environment
        self._s = self._e.screen

    def show(self):
        entry_to_display = ''
        while True:
            self._s.move(curses.LINES - 1, 0)
            self._s.addstr(f'd: {entry_to_display}')
            self._s.clrtoeol()

            key = self._s.getkey()
            if key in '1234567890':
                entry_to_display += key
            elif key == 'KEY_ENTER' or key == '\n':
                break
            elif key == 'KEY_BACKSPACE' or key == '\b':
                entry_to_display = entry_to_display[:-1]
            elif key == 'q':
                return
            else:
                warn(self._s, f'Unhandled details key {key}')

        self._s.clear()
        try:
            line = self._e.log.get_entry(int(entry_to_display) - 1)
            self._s.addstr(self._e.line_format.format(int(entry_to_display), line.truncate(self._e.msglen)))
            y, x = self._s.getyx()
            self._s.move(y + 2, self._e.idxlen + 2)
            self._s.hline(curses.ACS_HLINE, curses.COLS)
            self._s.move(y + 4, 0)

            self._indent = 20 + 2
            for k, v in line.attributes.items():
                v = str(v).replace('\n', '\n' + ' ' * self._indent)
                self._s.addstr('{:>20s}: {}\n'.format(k, v))
        except IndexError:
            self._s.addstr(f'Unknown log entry {entry_to_display}')
        self._s.getkey()
        return
