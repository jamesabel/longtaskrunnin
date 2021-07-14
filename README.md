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

The technique used here is to create a worker class derived from `Process` that is instantiated and started by a `QThread`.
The `InterprocessCommunication` class facilitates communication between the worker process and the `QThread`. 
An instance of `InterprocessCommunication` is pickle-able, and is passed to the `Process` instance to provide the
input. The output result from `Process` is passed back in a pickle in a temporary directory which is deleted upon 
read (the user is responsible use or save the result when its read).

### Process

The process that is going to be run is assumed to be a Python class or function and runs via `multiprocess.Process`.
An advantage of `Process` over a thread is that it enables parallelism, which using a thread (e.g. `QThread`) does not.

## Some Observations

### Can't use process only (no `QThread`)

It isn't possible to pass in a pyqtSignal to `multiprocessing.Process` since a pyqtSignal is not pickle-able. You will get:

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

Apparently `QThreads` can create "Dummy" threads (e.g. Dummy-6, etc.) that are daemons and will continue after the 
PyQt window has closed. However, these seem to be benign: these extra threads don't seem to stop pytest from running
all the tests and I get `Process finished with exit code 0` (i.e. no errors).

The leaking threads do seem to cause `pytest-threadleak` to fail however. So `pytest-threadleak` is turned off in `pytest.ini`:

```
[pytest]
threadleak = False
```
Alternatively just don't use `pytest-threadleak` at all.

### pytest-qt

I'm using `pytest-qt` which helps manage the PyQt runtime environment during tests (e.g. the Qt "app").  I use 
`qtbot` fixture built-in to `pytest-qt`, which seems convenient and seems to work. See the tests for the example.

### pytest-qt likes to use (emulated) mouse clicks, but that's about it

Use `qtbot.mouseClick(q_push_button_instance)` to give control stimulus to a PyQt window (e.g. a `QDialog` dialog box). This 
works well. What doesn't work well is trying to directly send a signal or directly call a function, even if it's merely what 
the button is connected to. This can make it impossible to emulate closing a window by clicking the Window's built-in 
"X" icon. There is no widget that is the "X" to do a mouseClick on. One way to deal with this is to always create 
a "Close" button (or exit or whatever).

You *can* do things like select a tab using `window.setCurrentIndex(tab_number)`, which will expose the tab (and its buttons) so 
the buttons can be (virtually) "clicked" via `qtbot.mouseClick()`.

### `qtbot` context manager?

I had problems getting the app to close when using `qtbot` as a context manager. The test would hang or get a runtime
error. I was better off emulating a mouse click on a "close" button and using `waitUntil` on a special method.
See the test case.

### Subclassing `QThread` controversy

There seems to be a lot of controversy around subclassing `QThread` or not. While subclassing `QThread` seems to be
the easiest way *and it seems to work* (it's what I use in this example), some people claim you have to instantiate 
a `QThread` and your worker `QObject`, then do a `moveToThread` to move your worker to the `QThread` instance. Also, 
the communication via signals and slots would have to be managed. This seems like an awkward pattern.
