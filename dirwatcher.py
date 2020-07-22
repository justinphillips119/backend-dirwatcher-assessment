#!/usr/bin/env python3

__author__ = "Justin Phillips"
#adding this line because I forgot to make a dev branch and need to add to the file lol

import signal
import time
import os
import errno
import logging
from datetime import datetime
import argparse


exit_flag = False
logger = logging.getLogger(__file__)
files = {}


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name
    logger.warn('Received ' + signal.Signals(sig_num).name)
    signal_names = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                    if v.startswith('SIG') and not v.startswith('SIG_'))
    logger.warn('Received ' + signal_names[sig_num])
    global exit_flag


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--ext', action='store', type=str, default='.txt', help='Specifically search this file')
    parser.add_argument('-i', '--interval',action='store', default=1.0, type=float, help='Polling interval')
    parser.add_argument('path', action='store', help='Directory you want to watching')
    parser.add_argument('magic', action='store', help='This is the string you are searching for')
    return parser


def watch_directory(args):
    logger.info('Watch Directory: {}, File Extension: {}, Magic Text: {}, Polling Interval: {}'.format(
        args.path, args.ext, args.magic, args.interval
    ))
    files_list = os.listdir(args.path)
    for f in files_list:
        if f.endswith(args.ext) and f not in files:
            files[f] = 0
            logger.info(f"{f} added to watchlist.")
    for f in list(files):
        if f not in files_list:
            logger.info(f"{f} removed from watchlist.")
            del files[f]
    for f in files:
        files[f] = magic_text_finder(
            os.path.join(args.path, f),
            files[f],
            args.magic
        )


def magic_text_finder(filename, start_line, magic_text):
    line_number = 0
    with open(filename) as f:
        for line_number, line in enumerate(f):
            if line_number >= start_line:
                if magic_text in line:
                    logger.info(
                        f"In file: {filename}  Dirwatcher found:  {magic_text} On line: {line_number + 1}"
                    )
    return line_number + 1


def main():
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s', 
        datefmt='%m-%d-%Y &%H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)
    start_time = datetime.now()

    logger.info(
        '\n\n' +
        '-*'*50 +
        '\n\n'
        '             Running program: {0}\n'
        '             Dirwatcher started: {1}\n\n'.format(__file__, start_time.isoformat()) 
        + '-*'*50 + '\n'
    )
    
    parser = create_parser()
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not exit_flag:
        try:
            watch_directory(args)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(f"{args.path} directory not found")
                time.sleep(2)
            else:
                logger.error(e)
        except Exception as e:
            logger.error(f"UNHANDLED EXCEPTION:{e}")
        time.sleep(int(float(args.interval)))

    
    uptime = datetime.now() - start_time

    logger.info(
        '\n\n' +
        '-*'*50 +
        '\n\n'
        '             Program stopped: {}\n'
        '             Uptime: {}\n\n'.format(__file__, str(uptime))
        + '-*'*50 + '\n'
    )
    logging.shutdown()


if __name__ == "__main__":
    main()