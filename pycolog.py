#!/usr/bin/env python3
import argparse
import pathlib
import curses

import yaml
import re
from datetime import datetime


class Analyzer:
    def __init__(self, **kwargs):
        self._options = kwargs

        self._line_start = kwargs.get('line_start')

        with open(kwargs.get('file')) as f:
            self._raw_lines = f.readlines()

        self._lines = list(self._find_lines())
        self._total = len(self._lines)

    @property
    def total(self):
        return self._total

    def get_lines(self, slice_):
        return self._lines[slice_]

    def get_line(self, idx):
        return self._lines[idx]

    def _find_lines(self):
        first = True
        current = ''

        for raw in self._raw_lines:
            if not self._line_start.match(raw):
                current += raw
                continue

            if not first:
                yield Line(current.strip(), **self._options)
            first = False
            current = raw
        yield Line(current.strip(), **self._options)


class Line:
    def __init__(self, raw, **kwargs):
        self._options = kwargs
        self._raw = raw
        self._fields = kwargs.get('fields', {})
        self._line_format = kwargs.get('line_format')

        m = self._line_format.match(raw)
        if m:
            self.attributes = self._parse_fields(m.groupdict())
        else:
            self.attributes = {}
        self._lines = self._raw.count('\n')

    def _parse_fields(self, attributes):
        return {k: self._parse_field(k, v) for k, v in attributes.items()}

    def _parse_field(self, field, value):
        setting = self._fields.get(field)
        if not setting:
            return value

        callback = setting.get('callback')
        kwargs = setting.get('kwargs')
        kwargs[setting['argument']] = value
        return callback(**kwargs)

    def __getattr__(self, item):
        return self.attributes.get(item)

    def __getitem__(self, item):
        return self.attributes.get(item)

    def __str__(self):
        return self._raw

    def truncate(self, width):
        msg = self._raw.replace('\n', '\xB6')
        if len(msg) > width:
            return msg[:width - 3] + '...'
        return msg


class Screen:
    def __init__(self, analyzer, **kwargs):
        self._options = kwargs
        self._analyzer = analyzer
        self._s = curses.initscr()
        self._highlight = kwargs.get('highlight', [])

        self._slice = slice(0, 0)
        self._idxlen = len(str(self._analyzer.total))
        self._msglen = curses.COLS - 2 - self._idxlen

        self._format = f'{{:{self._idxlen}d}}: {{:.{self._msglen}s}}'
        self._status_format = '{} .. {} / {}'

        self._color_codes = dict()

    def __enter__(self):
        curses.noecho()
        curses.cbreak()
        self._s.keypad(True)
        try:
            curses.start_color()
            curses.use_default_colors()
        except:
            self._highlight = []
        else:
            if self._options.get('color_screen'):
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
        self._first_page()

        self._s.clear()
        self._print_log()
        self._print_status()

        while True:
            key = self._s.getkey()

            if key == 'q':
                break
            elif key == 'd':
                self._details_subroutine()
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
        for hl in self._highlight:
            color = tuple(hl.get('color'))
            if not color:
                continue

            if color in self._color_codes:
                hl['color'] = self._color_codes[color]
                continue

            pos = len(self._color_codes) + 1
            curses.init_pair(pos, color[0], color[1])
            self._color_codes[color] = pos
            hl['color'] = pos

    def _print_log(self):
        ppos = 0
        lpos = self._slice.start
        for line in self._analyzer.get_lines(self._slice):
            self._print_line(ppos, lpos + ppos + 1, line)
            ppos += 1

    def _print_line(self, y, index, line):
        color = self._get_highlight_color(line)
        msg = line.truncate(self._msglen)
        self._s.addstr(y, 0, self._format.format(index, msg), curses.color_pair(color))

    def _print_bg_colors(self, fg):
        self._s.addstr(0, 0, f'Backgrounds ({fg}):\n\n')
        for i in range(0, 255):
            curses.init_pair(i + 1, fg, i)
            self._s.addstr(f' {i:3} ', curses.color_pair(i + 1))
            if (i + 1) % 30 == 0:
                self._s.addstr('\n')
        self._s.addstr(curses.LINES - 1, 0, 'Press any key for next color screen')

    def _print_fg_colors(self, bg):
        self._s.addstr(0, 0, f'Foregrounds ({bg}):\n\n')
        for i in range(0, 255):
            curses.init_pair(i + 1, i, bg)
            self._s.addstr(f' {i:3} ', curses.color_pair(i + 1))
            if (i + 1) % 30 == 0:
                self._s.addstr('\n')
        self._s.addstr(curses.LINES - 1, 0, 'Press any key for next color screen')

    def _print_colors(self):
        for bg in [curses.COLOR_WHITE, curses.COLOR_BLACK]:
            self._s.clear()
            self._print_bg_colors(bg)
            self._s.getch()

        for fg in [curses.COLOR_WHITE, curses.COLOR_BLACK]:
            self._s.clear()
            self._print_fg_colors(fg)
            self._s.getch()

    def _print_status(self):
        last_line = curses.LINES
        self._s.addstr(last_line - 1, 3, self._status_format.format(
            self._slice.start + 1,
            self._slice.stop,
            self._analyzer.total
        ))

    def _get_highlight_color(self, line):
        for hl in self._highlight:
            m = hl.get('match')
            if m == 'field' and line[hl['field']] == hl['is']:
                return hl.get('color', 0)
        return 0

    def _first_page(self):
        self._slice = slice(0, curses.LINES - 2)

    def _next_line(self):
        if self._slice.stop + 1 > self._analyzer.total:
            return
        self._slice = slice(self._slice.start + 1, self._slice.stop + 1)
        self._s.move(0, 0)
        self._s.deleteln()

        self._s.move(curses.LINES - 3, 0)
        self._s.insertln()
        line = self._analyzer.get_line(self._slice.stop - 1)
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
        line = self._analyzer.get_line(self._slice.start)
        self._print_line(0, self._slice.start + 1, line)
        self._print_status()

    def _last_page(self):
        lines_per_page = curses.LINES - 2
        self._slice = slice(self._analyzer.total - lines_per_page, self._analyzer.total)

    def _next_page(self):
        lines_per_page = curses.LINES - 2
        if self._slice.stop + lines_per_page > self._analyzer.total:
            return self._last_page()
        self._slice = slice(self._slice.stop, self._slice.stop + lines_per_page)

    def _previous_page(self):
        lines_per_page = curses.LINES - 2
        if self._slice.start - lines_per_page <= 0:
            return self._first_page()
        self._slice = slice(self._slice.start - lines_per_page, self._slice.start - 1)

    def _details_subroutine(self):
        line_to_display = ''
        while True:
            self._s.move(curses.LINES - 1, 0)
            self._s.addstr(f'd: {line_to_display}')
            self._s.clrtoeol()

            key = self._s.getkey()
            if key in '1234567890':
                line_to_display += key
            elif key == 'KEY_ENTER' or key == '\n':
                break
            elif key == 'KEY_BACKSPACE' or key == '\b':
                line_to_display = line_to_display[:-1]
            elif key == 'q':
                return
            else:
                self._warn(f'Unhandled details key {key}')

        self._s.clear()
        try:
            line = self._analyzer.get_line(int(line_to_display) - 1)
            self._s.addstr(self._format.format(int(line_to_display), line.truncate(self._msglen)))
            y, x = self._s.getyx()
            self._s.move(y + 2, self._idxlen + 2)
            self._s.hline(curses.ACS_HLINE, curses.COLS)
            self._s.move(y + 4, 0)

            self._indent = 20 + 2
            for k, v in line.attributes.items():
                v = str(v).replace('\n', '\n' + ' ' * self._indent)
                self._s.addstr('{:>20s}: {}\n'.format(k, v))
        except IndexError:
            self._s.addstr(f'Unknown log entry {line_to_display}')
        self._s.getkey()
        return

    def _warn(self, msg):
        self._s.addstr(curses.LINES - 2, 0, msg)
        self._s.clrtoeol()


def strptime(date_string, format):
    return datetime.strptime(date_string, format)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=pathlib.Path, help='Path to the log file to be analyzed')
    parser.add_argument('format', type=pathlib.Path, help='Path to the logs format file')

    parser.add_argument('--color-screen', action='store_true',
                        help='Show a color overview screen before starting the default routines')

    yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:python/regexp', lambda l, n: re.compile(l.construct_scalar(n)))
    yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:python/strptime', lambda l, n: strptime)
    yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:python/tuple', lambda l, n: tuple)

    config = parser.parse_args().__dict__
    with open(config.get('format')) as f:
        config.update(yaml.safe_load(f))

    analyzer = Analyzer(**config)
    with Screen(analyzer, **config) as screen:
        screen.run()
