# PLKit Mediator

Something to go between an Arduino and browser

## Usage

To get this going you'll need Python 3 and probably `virtualenv` installed.

The way I use it is:

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Then, either double-click on `start` or:

```
$ python mediator.py
```

This will then open a serial port, trying to connect to an Arduino and wait for a browswer to connect.

