"""
Module for main log screen and it's helper function, containing the console interaction and print loop.
"""
import curses

from pycolog.screens.environment import Environment


class LogScreen:
    """
    Main log screen showing the truncated log, message by message.
    This screen will also invoke other screen, depending on the entered commands.
    """
    def __init__(self, analyzer, **kwargs):
        self._e = Environment()
        self._e.options = kwargs
        self._e.log = analyzer
        self._e.screen = curses.initscr()
        self._e.idxlen = len(str(self._e.log.total))
        self._e.msglen = curses.COLS - 2 - self._e.idxlen

        self._slice = slice(0, 0)
        self._s = self._e.screen

        self._highlight = kwargs.get('highlight', [])
        self._color_codes = dict()

    def __enter__(self):
        curses.noecho()
        curses.cbreak()
        self._s.keypad(True)
        try:
            curses.start_color()
            curses.use_default_colors()
        except curses.error:
            self._highlight = []
        else:
            if self._e.options.get('color_screen'):
                self._print_colors()
                print('colors')
            self._init_highlights()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        curses.nocbreak()
        self._s.keypad(False)
        curses.echo()
        curses.endwin()

    def run(self):
        """Main loop of the screen, this shall be the entry point of the console application"""
        self._first_page()

        self._s.clear()
        self._print_log()
        self._print_status()

        while True:
            key = self._s.getkey()

            if key == 'q':
                break

            if key == 'd':
                from pycolog.screens.details_screen import Details  # pylint: disable=import-outside-toplevel
                Details(self._e).show()
            elif key in ('k', 'KEY_UP'):
                self._previous_line()
                continue
            elif key in ('j', 'KEY_DOWN'):
                self._next_line()
                continue
            elif key == 'KEY_HOME':
                self._first_page()
            elif key == 'KEY_END':
                self._last_page()
            elif key == 'KEY_PPAGE':
                self._previous_page()
            elif key in(' ', 'KEY_NPAGE'):
                self._next_page()
            elif key == 'KEY_RESIZE':
                continue
            else:
                self._s.clear()
                self._s.addstr(2, 2, f'Unknown command {key!r}')
                self._s.getkey()

            self._s.clear()
            self._print_log()
            self._print_status()

    def _init_highlights(self):
        for highlight in self._highlight:
            color = tuple(highlight.get('color'))
            if not color:
                continue

            if color in self._color_codes:
                highlight['color'] = self._color_codes[color]
                continue

            pos = len(self._color_codes) + 1
            curses.init_pair(pos, color[0], color[1])
            self._color_codes[color] = pos
            highlight['color'] = pos

    def _print_log(self):
        ppos = 0
        lpos = self._slice.start
        for line in self._e.log.get_entries(self._slice):
            self._print_line(ppos, lpos + ppos + 1, line)
            ppos += 1

    def _print_line(self, y_pos, index, line):
        color = self._get_highlight_color(line)
        msg = line.truncate(self._e.msglen)
        self._s.addstr(y_pos, 0, self._e.line_format.format(index, msg), curses.color_pair(color))

    def _print_bg_colors(self, foreground):
        self._s.addstr(0, 0, f'Backgrounds ({foreground}):\n\n')
        for i in range(0, 255):
            curses.init_pair(i + 1, foreground, i)
            self._s.addstr(f' {i:3} ', curses.color_pair(i + 1))
            if (i + 1) % 30 == 0:
                self._s.addstr('\n')
        self._s.addstr(curses.LINES - 1, 0, 'Press any key for next color screen')

    def _print_fg_colors(self, background):
        self._s.addstr(0, 0, f'Foregrounds ({background}):\n\n')
        for i in range(0, 255):
            curses.init_pair(i + 1, i, background)
            self._s.addstr(f' {i:3} ', curses.color_pair(i + 1))
            if (i + 1) % 30 == 0:
                self._s.addstr('\n')
        self._s.addstr(curses.LINES - 1, 0, 'Press any key for next color screen')

    def _print_colors(self):
        for background in [curses.COLOR_WHITE, curses.COLOR_BLACK]:
            self._s.clear()
            self._print_bg_colors(background)
            self._s.getch()

        for foreground in [curses.COLOR_WHITE, curses.COLOR_BLACK]:
            self._s.clear()
            self._print_fg_colors(foreground)
            self._s.getch()

    def _print_status(self):
        last_line = curses.LINES
        self._s.addstr(last_line - 1, 3, self._e.status_format.format(
            self._slice.start + 1,
            self._slice.stop,
            self._e.log.total
        ))

    def _get_highlight_color(self, line):
        for highlight in self._highlight:
            match = highlight.get('match')
            if match == 'field' and line[highlight['field']] == highlight['is']:
                return highlight.get('color', 0)
        return 0

    def _first_page(self):
        self._slice = slice(0, curses.LINES - 2)

    def _next_line(self):
        if self._slice.stop + 1 > self._e.log.total:
            return
        self._slice = slice(self._slice.start + 1, self._slice.stop + 1)
        self._s.move(0, 0)
        self._s.deleteln()

        self._s.move(curses.LINES - 3, 0)
        self._s.insertln()
        line = self._e.log.get_entry(self._slice.stop - 1)
        self._print_line(curses.LINES - 3, self._slice.stop, line)
        self._print_status()

    def _previous_line(self):
        if self._slice.start <= 0:
            return

        self._slice = slice(self._slice.start - 1, self._slice.stop - 1)
        self._s.move(curses.LINES - 3, 0)
        self._s.deleteln()

        self._s.move(0, 0)
        self._s.insertln()
        entry = self._e.log.get_entry(self._slice.start)
        self._print_line(0, self._slice.start + 1, entry)
        self._print_status()

    def _last_page(self):
        lines_per_page = curses.LINES - 2
        self._slice = slice(self._e.log.total - lines_per_page, self._e.log.total)

    def _next_page(self):
        lines_per_page = curses.LINES - 2
        if self._slice.stop + lines_per_page > self._e.log.total:
            self._last_page()
            return
        self._slice = slice(self._slice.stop, self._slice.stop + lines_per_page)

    def _previous_page(self):
        lines_per_page = curses.LINES - 2
        if self._slice.start - lines_per_page <= 0:
            self._first_page()
            return
        self._slice = slice(self._slice.start - lines_per_page, self._slice.start - 1)
