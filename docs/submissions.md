# Submissions

## File Specification
A valid Othello submission consists of a Python 3.x file, with a class called
`Strategy` and a method called `best_strategy`. A minimal example is shown below:
```py
def choose_move(board: str, player: str, still_running, time_limit: float):
    # Implement this method
    return 0


class Strategy:
    # Uncomment the below flags as needed
    # logging = True
    # uses_10x10_board = True
    # uses_10x10_moves = True

    def best_strategy(self, board: str, player: str, best_move, still_running, time_limit: float):
        move = choose_move(board, player, still_running, time_limit)
        best_move.value = move

```

## Method Specification
The `best_strategy` method must accept at least 4 parameters:

- `board`: a string of length 64, containing the characters `#!python {'.', 'x', 'o'}`
  The `.` represents an empty space, `x` represents black, and `o` represents white.
- `player`: a character in `#!python {'x', 'o'}` that represents who your script is playing
  as.
- `best_move`: A `multiprocessing.Value` object of type `int`
- `still_running`: A `multiprocessing.Value` object of type `int`

Once you have determined your move, set `best_move.value` to the index of the board at which
to place your token.

!!! note

    You do *NOT* need to import `multiprocessing` to use the `multiprocessing.Value` objects.

## Time Management
To know when you run out of time, you can use `still_running.value`, which starts as 1 but changes to 0 when
you near the time limit. Alternatively, `best_strategy` can accept an optional 5th argument, `time_limit`.
If included in your method header, it will be set to an integer representing the amount of time (in seconds)
that your script has to determine the best move.

!!! tip "Time Hoarding"

    If your game supports "Good Citizen" timing, exiting the `best_strategy` method before the time limit will give you extra time on the next turn.


!!! warning

    All user code will be run in a daemonized `multiprocessing.Process`. This means your script cannot spawn any Processes of its own.
    If your code does spawn any `multiprocessing.Process` instances, it will error out.

## Logging
In addition to the specifications listed above, your `Strategy` class may contain a `logging` variable.
This variable, if used, must be an attribute of the `Strategy` class.
Therefore it should be defined within `Strategy`'s constructor (as `self.logging`) or inside the class but outside a class method (just `logging`).
For instance, `logging` cannot be defined in the `best_strategy` method of your `Strategy` class or in a helper method defined outside of `Strategy`.

If set to `True`, you will see the output of any `#!python print` statements on either side of the board when playing your script.
Output for scripts that are playing as black will appear on the left-hand side of the Othello board while the output for scripts that are
playing as white will appear on the right-hand side of the Othello board.

If you omit the `logging` variable in your `Strategy` class, it will be assumed that you do not wish to output any `#!python print`
statements.

!!! info

    If you set `logging = True` in your `Strategy` class, you will only be able to view script logs if you are
    currently logged in and own the running script.


## Customizing Board Representation
If you would like to be provided with a 10x10 board instead of the default 8x8 board, you can add a `uses_10x10_board` variable to your strategy class.
This will surround the 8x8 board with an additional layer of `'?'` characters, as shown below.
Similar to the `logging` variable, `uses_10x10_board` must be an attribute of the `Strategy` class and will default to `False` if omitted.

You can also use the `uses_10x10_moves` variable to signify that your submitted `best_move.value` refers to indices in this 10x10 board representation.
If not used, the server will assume that your `best_move.value` refers to indices in the default 8x8 board, irrespective of whether or not `uses_10x10_board` is enabled.

```
                           ? ? ? ? ? ? ? ? ? ?
  . . . . . . . .          ? . . . . . . . . ?
  . . . . . . . .          ? . . . . . . . . ?
  . . . . . . . .          ? . . . . . . . . ?
  . . . o x . . .          ? . . . o x . . . ?
  . . . x o . . .    =>    ? . . . x o . . . ?
  . . . . . . . .          ? . . . . . . . . ?
  . . . . . . . .          ? . . . . . . . . ?
  . . . . . . . .          ? . . . . . . . . ?
                           ? ? ? ? ? ? ? ? ? ?

```
## Upload Errors
When uploading code to the server you may encounter one of the following errors.

- File has invalid syntax
    * The Othello server was unable to validate your code because there was a syntax error somewhere in the file.
      Go back through your code and revise any syntax issues then upload again.
- Cannot find attribute `Strategy.best_strategy` in file
    * Your code does not follow the specifications listed above.
      Reread the specifications and revise your code before submitting again.
- Attribute `Strategy.best_strategy` has an invalid amount of parameters
    * Your code does not follow the specifications listed above.
      Specifically regarding the amount of parameters `Strategy.best_strategy` should take.
      Reread the specifications and revise your code before submitting again.
- Code takes too long to validate!
    * Your file has some code that is outside a function or outside an `#!python if __name__ == '__main__'` block.
      Any code that is outside such block must terminate after 1s.
      Go back through your file and ensure that code that runs on import terminates quickly.

If you encounter another error message that you cannot interpret, email othello@tjhsst.edu
a screenshot of the error message as well as your code.

## Playing Games and Errors

To play a game, go to the Games->Play page and select two players.
To watch a game, go to the Games->Watch page and select one of the listed games.
If there are no games currently being played, no games will be listed.


When playing games, if your script behaves incorrectly, the server will interpret this as an `UserError`.
When the server encounters an `UserError`, your script will automatically forfeit the game and your opponent will be awarded the win.
The `UserError` will be reported in either log area, regardless if the playing script set the `logging` variable.
The following are the possible `UserError` codes and their meanings:

- An error code of `#!python -1` is a `NO_MOVE_ERROR`, meaning your script did not submit any move before the time limit
- An error code of `#!python -2` is a `READ_INVALID` error, meaning your script submitted something to
  the `best_move` variable but it was not an integer in the range 0-63, inclusive.
- An error code of `#!python -3` is an `INVALID_MOVE` error, meaning your script submitted an integer
  in the range 0-63, inclusive, but it was not a valid move given the current board state.

If any other error code is outputted, namely an error code within `#!python {-4,-5,-6, -7, -8}`, this means the server has
encountered an error while running your game. In this case, the game will be marked as a tie between both players, but
you should email othello@tjhsst.edu a screenshot of the game along with your code
so we can investigate and fix this error.

Finally, when running a non-tournament game, the server continuously checks if the browser which initiated the game is
still watching the game. If not, the game will be terminated and the game will end in a tie. Meaning, if you start
a game but then close the window with the game still running, the game will be terminated and end in a tie.


## Multiple Submissions
You may submit code any amount of times, and the Othello server will record and store all your submissions. If you wish, you may retrieve any
previously submitted script from the upload page. However, the Othello Server will only run your most recent submission.

All your code submissions will persist on the Othello server, and you can retrieve previous submissions through the Games->Upload page.
The Othello server will always use your most recent code submission when running your AI against other players.
(If you were to submit twice, your second submission would be used to play against other users)

!!! note "Labeling Scripts"

    When uploading a script, you will be given an option to attach a "name" or "label" to that script.
    Adding a "name" to your script will make it easier to identify previous submissions if you wish to retrieve them later.
    If omitted, your script's "name" will default to the time it was submitted.


## Running Multiple Files

As of now the Othello server will only run the most recently uploaded script.
You should try to put all your code in a single file and upload that file.
Any files created by your code will persist between runs and games.
If you do in fact need other files for your code to work, and it is infeasible to include it in one file,
contact othello@tjhsst.edu or your AI teacher about your situation.

!!! warning

    When your code is uploaded, it is stored under a different, randomly-generated filename. Submitting two Python files and expecting to be
    able to import the other file by name is infeasible.


## Replaying Past Games


After either playing or watching a game, you may download a text-formatted version of the game using the "Download Game" button below the game board.
You may choose to download the game in a format that is pretty-printed and easy to interpret visually or in a format that is more easily parsed programmatically.
The exact specifications for both formats, and a preview, are shown when downloading a game.

In addition to downloading games, you can upload this file to the Games->Replay page and more closely interact with the downloaded game file.
After uploading the game file, you will be able to step forward and step back through all the turns played in that game.

!!! warning

    Logging data is not saved in game files and will not be displayed during replays


## Other Info

If your code fails to return a move, returns an invalid move, or errors for whatever reason, it will be treated as a forfeit.
As such, make sure you code works on your computer before using this website to test against other AIs.
Just as a reminder, if your code is caught cheating during the tournament in any way, you **will** be given an integrity violation, so just don't do it.

