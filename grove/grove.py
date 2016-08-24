import os
import sys
import json
import logging
import datetime


def set_config(config_obj=None, config_fn=None):
    """Set the attrs of a config object to their corresponding values from a json
    -formatted file located at config_fn
    """
    if not config_fn or not config_obj:
        return
    with open(config_fn) as f:
        for name, value in json.load(f).items():
            setattr(config_obj, name, value)
    return


def get_logger(config=None, debug=True):
    """Initializes and returns a logger with the basic configuration level unless
    specified by the configuration.

    If debug is True, `pipe_logs_and_stderr_to_file` won't be called and the logs
    greater than or equal to the specified level, plus stderr, will output on the
    screen.
    """
    try:
        log_directory = config.log_directory
    except AttributeError:
        log_directory = None
    logger = logging.getLogger(__name__)
    logger.setLevel(config.log_level)
    if not debug:
        pipe_logs_stderr_to_file(log_directory)
        return logger
    print "Debug mode on, logging to stdout."
    msg_fmt = "%(message)s"
    logging.basicConfig(format=msg_fmt)
    return logger


def pipe_logs_stderr_to_file(log_directory=None):
    """Write logs and stderr to a file `mmddyyyyThhmm.log`
    specified by config.log_directory or to stdout.
    Format example: `$LOG_DIRECTORY/2016/June/06072016T1951.log`
    """
    if not log_directory:
        print "No log_directory provided, logs and stderr will be shown on screen."
        print "Check that you ran the program with --config?"
        logging.basicConfig()
        return
    t_now = datetime.datetime.now()
    dir_fmt = (log_directory,
            t_now.strftime("%Y"),       # year
            t_now.strftime("%B"))       # month (name)
    log_fmt = ("%02d" % (t_now.month),  # month (01-12)
            "%02d" % (t_now.day),       # day (01-31)
            t_now.strftime("%Y"),       # year
            "%02d" % (t_now.hour),      # hour
            "%02d" % (t_now.minute))    # minute

    log_path = "%s/%s/%s/" % dir_fmt
    log_fn = "%s%s%sT%s%s.log" % log_fmt
    log_fn = "%s%s" % (log_path, log_fn)
    if not os.path.exists(log_path):
        try:
            os.makedirs(os.path.dirname(log_path))
        except OSError as ose: # prevent race condition
            if ose.errno != errno.EEXIST:
                raise
    print "Logging to %s" % log_fn
    # Append stderr and logging to the logfile
    sys.stderr = open(log_fn, "a")
    msg_fmt = "%(message)s"
    logging.basicConfig(filename=log_fn, format=msg_fmt)
