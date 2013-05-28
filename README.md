Convert csv files to nicely formatted ascii tables.

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

Copyright (c) 2006 Rufus Pollock

This is Free/Open Source Software available under the MIT License
http://www.opensource.org/licenses/mit-license.php 

