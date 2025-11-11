# Overview
[ranger](https://ranger.fm) integration for xonsh shell

## Installation

To install use pip:

``` bash
xpip install xontrib-ranger
```

## Usage
It adds `r` alias function. So commands like `cd` will work from broot.
``` bash
$ xontrib load ranger
$ r 
```

<!-- `broot` can also be launched with shortcut `Ctrl+N`.  -->
<!-- This can be changed by `$XONSH_BROOT_KEY="c-n"` or disabled with `$XONSH_BROOT_KEY=""`.  -->
<!-- (PS [PTK's keybinding guide](https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html#list-of-special-keys)  -->
<!-- for full list of key names.) -->

## Credits

Originally forked from jnoortheen's [`xontrib-broot`](https://github.com/jnoortheen/xontrib-broot).
