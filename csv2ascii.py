#!/usr/bin/env python
# Copyright (c) 2006 Rufus Pollock
# This is Free/Open Source Software available under the MIT License
# http://www.opensource.org/licenses/mit-license.php 
"""Convert csv files to nicely formatted ascii tables.

TODO
====

1. allow output_width of 0 meaning use width necessary to fit all rows on one
   line

2. rather than truncate cell contents wrap it onto two lines (and/or allow
   spillover if adjacent cell is empty)
   
     * wontfix: can let terminal do this: just set width very large ...

3. (?) stream output back rather than returning all at once

4. Add support for limiting number of columns displayed. DONE 2007-08-02
   * TODO: add unittest
"""
import StringIO
import csv

class Formatter(object):

    def __init__(self, sample_rows, output_width=0, number_of_columns=0):
        '''
        @arg output_width: display width (0 means unlimited).
        @arg number_of_columns: number of columns to display.
        '''
        self.output_width = output_width
        maxcols = self._get_maxcols(sample_rows)
        if not number_of_columns:
            self.numcols = maxcols
        else:
            self.numcols = min(number_of_columns, maxcols)
        self.colwidths = []
        self._set_colwidths(sample_rows)
        if self.colwidths[0] < 3:
            msg =\
'''It is not possible to effectively format this many columns of material with
this narrow an output window. Column width is: %s''' % self.colwidths[0]
            raise ValueError(msg)

    def _get_maxcols(self, sample_rows):
        maxcols = 0
        for row in sample_rows:
            maxcols = max(maxcols, len(row))
        return maxcols


    def _set_colwidths(self, sample_rows):
        # subtract -1 so that we have (at least) one spare screen column
        if self.output_width != 0:
            colwidth = int( (self.output_width - 1) / self.numcols)
            for ii in range(self.numcols):
                self.colwidths.append(colwidth)
        else: # make every col as wide as it needs to be
            self.colwidths = [0] * self.numcols
            for row in sample_rows:
                for ii in range(self.numcols):
                    self.colwidths[ii] = max(self.colwidths[ii], len(row[ii]))
            self.colwidths = [ x + 1 for x in self.colwidths ]

    def write(self, row):
        """Return the input 'python' row as an appropriately formatted string.
        """
        result = '|'
        count = 0
        for cell in row[:self.numcols]:
            width = self.colwidths[count]
            result += self._format_cell(width, cell)
            count += 1
        # now pad out with extra cols as necessary
        while count < self.numcols:
            width = self.colwidths[count]
            result += self._format_cell(width, ' ')
            count += 1
        return result + '\n'

    def _format_cell(self, width, content):
        content = content.strip()
        if len(content) > width - 1:
            # be brutal (this *has* to be fixed)
            content = content[:width-1]
        return content.center(width-1) + '|'

    def write_separator(self):
        result = '+'
        for width in self.colwidths:
            result += '-' * (width-1) + '+'
        return result + '\n'


class TestFormatter:

    sample_rows  = [
            ['1', '2', 'head blah', 'blah blah blah'],
            ['a', 'b', 'c', 'd', 'e', 'g' ],
            ['1', '2', 'annakarenina annakarenina annakarenina'],
            ]
    output_width = 60

    formatter = Formatter(sample_rows, output_width)

    def test_1(self):
        assert self.formatter.numcols == 6

    def test_colwidths(self):
        exp = int ((self.output_width -1) / 6)
        assert self.formatter.colwidths[0] == exp
        
    def test_write_1(self):
        out = self.formatter.write(self.sample_rows[0])
        assert len(out) <= self.output_width

    def test_write_2(self):
        out = self.formatter.write(self.sample_rows[0])
        exp = '|   1    |   2    |head bla|blah bla|        |        |\n'
        assert out == exp

    def test_write_separator(self):
        out = self.formatter.write_separator()
        exp = '+--------+--------+--------+--------+--------+--------+\n'


def csv2ascii(fileobj, **kwargs):
    reader = csv.reader(fileobj, skipinitialspace=True)
    result = ''
    formatter = None
    row_cache = []
    count = 0
    # we assume that sample_length is less than number of rows
    # would be good to check this
    sample_length = 2
    for row in reader:
        if count < sample_length:
            row_cache.append(row)
        elif count == sample_length:
            formatter = Formatter(row_cache, **kwargs)
            result += formatter.write_separator()
            for oldrow in row_cache:
                result += formatter.write(oldrow)
                result += formatter.write_separator()
            result += formatter.write(row)
            result += formatter.write_separator()
        else:
            result += formatter.write(row)
            result += formatter.write_separator()
        count += 1
    return result

class TestCsv2Ascii:
    sample = \
'''"YEAR","PH","RPH","RPH_1","LN_RPH","LN_RPH_1","HH","LN_HH"
    1971,7.852361625,43.9168370988587,42.9594500501036,3.78229777955476,3.76025664867788,16185,9.69184016636035
    ,,abc,
    1972,10.504714885,55.1134791192682,43.9168370988587,4.00939431635556,3.78229777955476,16397,9.70485367024987
    , ,,  '''

    expected = \
'''+------+------+------+------+------+------+------+------+
| YEAR |  PH  | RPH  |RPH_1 |LN_RPH|LN_RPH|  HH  |LN_HH |
+------+------+------+------+------+------+------+------+
| 1971 |7.8523|43.916|42.959|3.7822|3.7602|16185 |9.6918|
+------+------+------+------+------+------+------+------+
|      |      | abc  |      |      |      |      |      |
+------+------+------+------+------+------+------+------+
| 1972 |10.504|55.113|43.916|4.0093|3.7822|16397 |9.7048|
+------+------+------+------+------+------+------+------+
|      |      |      |      |      |      |      |      |
+------+------+------+------+------+------+------+------+
'''

    fileobj = StringIO.StringIO(sample)

    def test_1(self):
        out = csv2ascii(self.fileobj, 60)
        # include these extra print statements as dump from failure not that
        # useful
        print out
        print self.expected
        assert self.expected == out


import optparse
import sys
if __name__ == '__main__':
    usage = \
'''usage: %prog [options] <csv-file-path>

Convert csv file at <csv-file-path> to ascii form returning the result on
stdout. If <csv-file-path> = '-' then read from stdin.'''

    parser = optparse.OptionParser(usage)
    parser.add_option('-w', "--width", dest='width', type='int',
        help='Width of ascii output', default=80)
    parser.add_option('-c', "--columns", dest='columns', type='int',
        help='Only display this number of columns', default=0)

    options, args = parser.parse_args()
    
    if len(args) == 0:
        parser.print_help()
        sys.exit(0)
    filepath = args[0]
    if filepath == '-':
        fileobj = sys.stdin
    else:
        fileobj = file(args[0])
    out = csv2ascii(fileobj, output_width=options.width,
            number_of_columns=options.columns)
    print out
