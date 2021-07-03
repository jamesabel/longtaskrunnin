# longtaskrunnin

## Discussion

The goal is to run a "long-running" task in PyQt without causing the UI to become unresponsive.
In other words, none of the UI processing should block for any significant amount of time.

### Process

The process that is going to be run is assumed to be a Python class or function and runs via `multiprocess.Process`.

`multiprocessing.Process` is chosen over `QProcess` since `QProcess` requires that the process being 
run is already an executable (not a Python class or function). The added complexity of creating an executable is 
assumed to be undesirable and/or out of scope for the application.

## Some Observations

### Can't use process only (no QThread)

It isn't possible to pass in a pyqtSignal to `multiprocessing.Process`. You will get:

`TypeError: cannot pickle 'PyQt5.QtCore.pyqtBoundSignal' object`.

So, Process by itself (no QThread) can't be used to tell the GUI to update when the process is complete.

### An exception in a QThread can cause a "crash"

Since Python is an interpreted language, you'd expect an exception to be caught and then provide some debug
information. Unfortunately, if an exception happens in a QThread it can cause 
`Process finished with exit code -1073740791 (0xC0000409)`, which is essentially crash. 

Running under a debugger can trap on the actual offending line, and not just crash. But when you see this 
error message, it's not obvious that using a debugger would avoid this hard "crash".

Also, and probably even worse, is that exception handlers (e.g. Sentry or custom "catch all" exception handlers) 
won't get a chance to notify the user of this error - the program merely crashes.

### Can't access Process's updated data members

Although it seems to be syntactically correct, and it doesn't throw any errors or exceptions, if you 
try to access the data elements from a class drived from Process, the data is from the global instance of a class,
and those data members won't have the desired processed data.

### Test Case

Variants:

| Process | Error | Debugger  | Result |
| ------- |-------|-----------|--------|
| False   | False | No Effect | OK     |
| True    | False | No Effect | OK     |
| False   | True  | False     | Process finished with exit code -1073740791 (0xC0000409) |
| False   | True  | True      | ZeroDivisionError: float division by zero |
| True    | True  | No Effect | ZeroDivisionError: float division by zero |

*Process error:
Normal run: 
Debugger: 