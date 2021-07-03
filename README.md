# longtaskrunnin

# Discussion

The goal is to run a "long running" task in PyQt without causing the UI to become unresponsive.
In other words, none of the UI processing should block for any sigificant amount of time.

## Process

The process that is going to be run is assumed to be a Python class or function and runs via `multiprocess.Process`.

`multiprocessing.Process` is chosen over `QProcess` since `QProcess` requires that the process being 
run is already an executable (not a Python class or function). The added complexity of creating an executable is 
assumed to be undesirable and/or out of scope for the application.

## Using Process by itself without QThread

It isn't possible to pass in a pyqtSignal to Process. You will get:

`TypeError: cannot pickle 'PyQt5.QtCore.pyqtBoundSignal' object`.

So, this technique can't be used to tell the GUI to update when the process is complete.

## Test Case

PyQt example

Variants
- main thread/worker thread/worker process, shelve
- main thread/worker process, shelve
- main thread/worker thread/worker process, pass results back via signal
- main thread/worker process, pass results back via signal

| QThread  | Process | Error | Return Technique | Result |
| -------- | ------- |-------|------------------|--------|
| False    | True    | False | pqqtSignal       | TypeError: cannot pickle 'PyQt5.QtCore.pyqtBoundSignal' object |
| False    | True    | False | shelve           |        |
| False    | True    | True  | pqqtSignal       |        |
| False    | True    | True  | shelve           |        |
| True     | False   | False | pqqtSignal       |  OK    |
| True     | False   | False | shelve           |        |
| True     | False   | True  | pqqtSignal       | Process finished with exit code -1073740791 (0xC0000409) |
| True     | False   | True  | shelve           |        |
| True     | True    | False | pqqtSignal       |  OK    |
| True     | True    | False | shelve           |  OK    |
| True     | True    | True  | pqqtSignal       | ZeroDivisionError: float division by zero |
| True     | True    | True  | shelve           | ZeroDivisionError: float division by zero |


