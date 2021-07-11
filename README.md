# longtaskrunnin

> *When the big train run*
> 
> *When the train is movin' on, I got to keep on movin'*
> 
> *Keep on movin'*
> 
> *Won't you keep on movin'?*
> 
> *Gonna keep on movin'*
> 
> Long Train Runnin' - The Doobie Brothers © Warner Chappell Music, Inc

## tl;dr

Use `QThread`, `Process` and `pickle` to facilitate long-running tasks:

`app -> QThread -> multiprocessing.Process -> pickle -> back to QThread -> back to app`

Try the demo app here as:

`python -m longtaskrunnin`

## Discussion

The goal is to run a "long-running" task in PyQt without causing the UI to become unresponsive.
In other words, none of the UI processing should block for any significant amount of time.

### Process

The process that is going to be run is assumed to be a Python class or function and runs via `multiprocess.Process`.
An advantage of `Process` over a thread is that it enables parallelism, which using a thread (e.g. `QThread`) does not.

## Some Observations

### Can't use process only (no `QThread`)

It isn't possible to pass in a pyqtSignal to `multiprocessing.Process` since it's not pickle-able. You will get:

`TypeError: cannot pickle 'PyQt5.QtCore.pyqtBoundSignal' object`.

So, Process by itself (no QThread) can't be used to tell the GUI to update when the process is complete.

### An exception in a `QThread` can cause a "crash"

Since Python is an interpreted language, you'd expect an exception to be caught and then provide some debug
information. Unfortunately, if an exception happens in a QThread it can cause 
`Process finished with exit code -1073740791 (0xC0000409)`, which is essentially crash. 

Running under a debugger can trap on the actual offending line, and not just crash. But when you see this 
error message, it's not obvious that using a debugger would avoid this hard "crash".

Also, and probably even worse, is that exception handlers (e.g. Sentry or custom "catch all" exception handlers) 
won't get a chance to notify the user of this error - the program merely crashes.

### Don't try to access a process (from `multiprocessing.Process`) data members

Although it seems to be syntactically correct, and it doesn't throw any errors or exceptions, if you 
try to access the data elements from a class derived from Process the data is from the global instance of a class,
not what you just ran. Those data members won't have the just-processed data.

### Not using `QProcess`
`multiprocessing.Process` is chosen over `QProcess` since `QProcess` requires that the process being 
run is already an executable (not a Python class or function, e.g. a .exe on Windows). The added complexity of 
creating an executable is assumed to be undesirable and/or out of scope for the application.

### Process communication

The input to a Process can be anything that can be pickled. However, there is no "return" and (as mentioned above)
the data elements in a class derived from Process don't actually contain data from the worker.

This implementation has chosen to use `pickle` to deliver the data from the worker back to the consumer code.
See the `InterprocessCommunication` class. It uses a temp directory to write and then read the data. 
The data is read in `interprocess_communication_read()` and that action deletes the pickle file. 
So, even though this data is rather global in that it lives in the file system, in effect that's not an 
issue since its in a temp directory and this implementation causes it to be ephemeral (is immediately 
cleaned up once the data is retrieved from the file system).

### Leaking threads from `QThread`

Apparently `QThreads can create "Dummy" threads (e.g. Dummy-6, etc.) that are daemons and will continue after the 
PyQt window has closed.  I have had problems with getting pytest to finish, since pytest stops after the tests that use PyQt.
This seems to be intermittent, and can be different when running pytest in PyCharm normally, in PyCharm in debug, and 
pytest directly outside of PyCharm. I do not currently have a solution.

I'm using pytest-qt which helps manage the PyQt runtime environment during tests (e.g. the Qt "app"). 
