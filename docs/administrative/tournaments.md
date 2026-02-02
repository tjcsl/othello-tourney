# Creating a Tournament

This document details:

- An explanation of the different tournament pairing algorithms
- How to create a tournament

## Pairing Algorithms
Othello implements several different algorithms for pairing students
in a tournaments:

- Round Robin: each student plays every other student as both `x` and `o`.
  By default, this happens twice (i.e. each student will play as `x` and `o` twice), although
  it is customizable in the management form.
- Random: randomly pairs each player with one other player.
- Danish: pairs the 1st and second 2nd place, 3rd and 4th place, and so on.
  Both players will get a chance to play as both `x` and `o`.
- Swiss: Danish pairing, but tries to avoid rematches whenever possible.

## Tournament Creation
In order to create a tournament, you must either be a teacher, staff, or superuser.
The creation form is located at Tournaments->Tournament Management.
Simply fill out the form, making sure the start date is in the future, and the tournament
will start at the scheduled time.
