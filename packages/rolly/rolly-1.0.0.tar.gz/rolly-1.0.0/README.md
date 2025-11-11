![Rolly Mascot](mascot.png)

# Rolly

Rolling dice the boring way.

## Introduction

A roll is expressed as a single string of text that contains a
sequence of instructions. Whitespace between instructions is entirely
ignored. There are different ways to express the same roll,
some being shorter than others. Below, we roll 3 D20s with
advantage in three different ways.

```
d20 d20 d20+

d20 x3+

d20 d20x2 +
```

## Instructions

The available instructions are listed below.

  * A die to be rolled: `dN`, `N` is the number of sides
  * Roll multiple dice: `xM`, `M` is the number of the previous die to roll
  * Advantage on the roll: `+` anywhere in the string
  * Disadvantage on the roll: `-` anywhere in the string

## Examples

So a number prefixed with `d` implies `x1` and a space between a number
and a count is ignored. Advantage is indicated by a `+` anywhere in the
string, disadvantage is a `-`.

```
d20x2 +
a d20 d20
d20x2-
```

## CLI

The CLI is straightforward. Once the package is installed, it can be run
as a module:

```
$ python -m rolly
```

This will show the help text. The primary command is `roll`, which takes
a string of instructions and displays the result.

```
$ python -m rolly roll d20x3
   ▄▄▄▄              ▄▄▄     ▄▄▄▄▄▄▄▄           ▄▄▄▄▄
  ██▀▀▀█            █▀██     ▀▀▀▀▀███          █▀▀▀▀██▄
 ██ ▄▄▄               ██         ▄██                ▄██
 ███▀▀██▄             ██         ██              █████
 ██    ██             ██        ██                  ▀██
 ▀██▄▄██▀          ▄▄▄██▄▄▄    ██              █▄▄▄▄██▀
   ▀▀▀▀            ▀▀▀▀▀▀▀▀   ▀▀                ▀▀▀▀▀
```

The default uses ASCII art, but passing the `--plain` (`-p`) flag will
cause it to use plain text.
```
$ python -m rolly roll d20x3
6 17 3
```

It is also possible to sum the dice automatically using the `--add` (`-a`)
flag:

```
$ python -m rolly roll -ap d20x3
16 12 7
= 35
```

The ASCII art theme can be changed with the `--theme` (`-t`) option and
the available themes can be listed with the `themes` command.
