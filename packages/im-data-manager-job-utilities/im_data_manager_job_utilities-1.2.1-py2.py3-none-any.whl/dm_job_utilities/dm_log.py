"""Python utilities for Data Manager Jobs
"""
from __future__ import print_function

from datetime import datetime
import logging
from numbers import Number
import sys
import time

import pytz
import six
from wrapt import synchronized

_INFO = logging.getLevelName(logging.INFO)

# Delay between issuing a fatal message
# and calling sys.exit(1)
_FATAL_PRE_EXIT_DELAY_S = 4


class DmLog:
    """Simple methods to provide Data-Manager-compliant messages
    in the stdout of an application.
    """

    cost_sequence_number = 0
    string_buffer = six.StringIO()

    @classmethod
    def reset_cost_sequence_number(cls):
        """Used primarily for testing to reset the sequence  number in COST lines."""
        cls.cost_sequence_number = 0

    @classmethod
    def emit_event(cls, *args, **kwargs):
        """Generate a Data Manager-compliant event message.
        The Data Manager watches stdout and interprets certain formats
        as an 'event'. These are then made available to the client.
        Here we write the message using the expected format.

        kwargs:

        level - Providing a standard Python log-level, like logging.INFO.
                Defaults to INFO.
        """
        # The user message (which may be blank)
        _ = cls.string_buffer.truncate(0)
        print(*args, file=cls.string_buffer)
        msg = cls.string_buffer.getvalue().strip()
        if not msg:
            msg = '(blank)'
        # A UTC date/time
        msg_time = datetime.now(pytz.utc).replace(microsecond=0)
        # A logging level (INFO by default)
        level = kwargs.get('level', logging.INFO)
        print('%s # %s -EVENT- %s' % (msg_time.isoformat(),
                                      logging.getLevelName(level),
                                      msg))

    @classmethod
    def emit_fatal_event(cls, *args, **kwargs):
        """Generate a Data Manager-compliant event message and then force
        an exit of the process by calling sys.exit(). The level used for the
        event, unless modified by 'level' is the built-in value of CRITICAL.

        There is no return from this function!

        The event is emitted, a short pause is enforced (to ensure logging
        has sufficient time to execute) and then the process is killed.

        kwargs:

        level - Providing a standard Python log-level, like logging.INFO.
                Defaults to CRITICAL.
        """
        # The user message (which may be blank)
        _ = cls.string_buffer.truncate(0)
        print(*args, file=cls.string_buffer)
        msg = cls.string_buffer.getvalue().strip()
        if not msg:
            msg = '(blank)'
        # A UTC date/time
        msg_time = datetime.now(pytz.utc).replace(microsecond=0)
        # A logging level (CRITICAL by default)
        level = kwargs.get('level', logging.CRITICAL)
        print('%s # %s -EVENT- %s' % (msg_time.isoformat(),
                                      logging.getLevelName(level),
                                      msg))
        # Pre-exit pause
        time.sleep(_FATAL_PRE_EXIT_DELAY_S)
        # Die
        sys.exit(1)

    @classmethod
    @synchronized
    def emit_cost(cls, cost, incremental=False):
        """Generate a Data Manager-compliant cost message.
        The Data Manager watches stdout and interprets certain formats
        as a 'cost' lines, and they're typically used for billing purposes.

        The cost must be a non-negative number.

        The cost interpreted as a total cost if incremental is False.
        If costs are to be added to existing costs set incremental to False.
        Total cost values are written without a '+' prefix.
        When incremental, the cost values are written
        with a '+' prefix, i.e. '+1' or '+0'.
        """
        # Cost is always expected to be a number that's not negative.
        assert isinstance(cost, Number)

        # Ensure this cost message is unique?
        cls.cost_sequence_number += 1

        cost_str = str(cost)
        assert cost_str[0] != '-'
        if incremental:
            cost_str = '+' + cost_str
        msg_time = datetime.now(pytz.utc).replace(microsecond=0)
        print('%s # %s -COST- %s %d' % (msg_time.isoformat(),
                                        _INFO,
                                        cost_str,
                                        cls.cost_sequence_number))
