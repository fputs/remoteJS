# MIT License
#
# Copyright (c) 2020 fputs
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os

class Session(object):
    """
    Stores information about an active session.
    """

    timeout_timer = 0       # Counts down, when zero is reached, the session is inactive
    command_queue = []      # The queue of commands to execute (Currently, only one command can be loaded at once)
    response_queue = []

    def __init__(self, host):
        self.host = host

    def write_to_file(self):
        """
        Writes a session to file.

        NOT YET IMPLEMENTED
        """
        with open("sessions/{}.json".format(self.host), "w+") as f:
            f.write(json.dumps(self.__dict__))

    def add_command(self, cmd):
        """
        Adds a new command to the session's command queue.
        """
        self.command_queue.append(cmd)

    def get_next_command(self):
        """
        Gets the next command from the queue, or void(0) if the queue is empty.
        """
        cmd = "void(0)"
        if len(self.command_queue) > 0:
            cmd = self.command_queue[0]
            del self.command_queue[0]
        return cmd

    @staticmethod
    def load_session(host):
        """
        Loads a session from file.
        
        NOT YET IMPLEMENTED
        """
        sess = Session(host)
        if os.path.exists(os.path.join("sessions", "{}.json".format(host))):
            with open("sessions/{}.json".format(host), "r") as f:
                sess.__dict__ = json.loads(f.read())
        return sess
