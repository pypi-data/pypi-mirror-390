T O B O T
=========


**NAME**


|
| ``tobot`` - to bot or not to bot !
|


**SYNOPSIS**


|
| ``tobot <cmd> [key=val] [key==val]``
| ``tobot -cvaw [init=mod1,mod2]``
| ``tobot -d`` 
| ``tobot -s``
|

**DESCRIPTION**


``TOB`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.

``TOB`` contains python3 code to program objects in a functional way.
it provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.

``TOBOT`` is a python3 IRC bot, it can connect to IRC, fetch and
display RSS feeds, take todo notes, keep a shopping list and log
text. You can run it under systemd for 24/7 presence in a IRC channel.


``TOBOT`` and ``TOB`` are Public Domain.


**INSTALL**


installation is done with pipx

|
| ``$ pipx install tobot``
| ``$ pipx ensurepath``
|
| <new terminal>
|
| ``$ tobot srv > tobot.service``
| ``$ sudo mv tobot.service /etc/systemd/system/``
| ``$ sudo systemctl enable tobot --now``
|
| joins ``#tobot`` on localhost
|


**USAGE**


use ``tobot`` to control the program, default it does nothing

|
| ``$ tobot``
| ``$``
|

see list of commands

|
| ``$ tobot cmd``
| ``cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,``
| ``pwd,rem,req,res,rss,srv,syn,tdo,thr,upt``
|

start console

|
| ``$ tobot -c``
|

start console and run irc and rss clients

|
| ``$ tobot -c init=irc,rss``
|

list available modules

|
| ``$ tobot mod``
| ``err,flt,fnd,irc,llm,log,mbx,mdl,mod,req,rss,``
| ``rst,slg,tdo,thr,tmr,udp,upt``
|

start daemon

|
| ``$ tobot -d``
| ``$``
|

start service

|
| ``$ tobot -s``
| ``<runs until ctrl-c>``
|


**COMMANDS**


here is a list of available commands

|
| ``cfg`` - irc configuration
| ``cmd`` - commands
| ``dpl`` - sets display items
| ``err`` - show errors
| ``exp`` - export opml (stdout)
| ``imp`` - import opml
| ``log`` - log text
| ``mre`` - display cached output
| ``pwd`` - sasl nickserv name/pass
| ``rem`` - removes a rss feed
| ``res`` - restore deleted feeds
| ``req`` - reconsider
| ``rss`` - add a feed
| ``syn`` - sync rss feeds
| ``tdo`` - add todo item
| ``thr`` - show running threads
| ``upt`` - show uptime
|

**CONFIGURATION**


irc

|
| ``$ tobot cfg server=<server>``
| ``$ tobot cfg channel=<channel>``
| ``$ tobot cfg nick=<nick>``
|

sasl

|
| ``$ tobot pwd <nsnick> <nspass>``
| ``$ tobot cfg password=<frompwd>``
|

rss

|
| ``$ tobot rss <url>``
| ``$ tobot dpl <url> <item1,item2>``
| ``$ tobot rem <url>``
| ``$ tobot nme <url> <name>``
|

opml

|
| ``$ tobot exp``
| ``$ tobot imp <filename>``
|


**PROGRAMMING**

|
| tobot has it's user modules in the ~/.tobot/mods directory so for a
| hello world command you would  edit a file in ~/.tobot/mods/hello.py
| and add the following
|

::

    def hello(event):
        event.reply("hello world !!")


|
| typing the hello command would result into a nice hello world !!
|

::

    $ tobot hello
    hello world !!


|
| commands run in their own thread and the program borks on exit to enable a
| short debug cycle, output gets flushed on print so exceptions appear in the
| systemd logs. modules can contain your own written python3 code.
|


**FILES**

|
| ``~/.tobot``
| ``~/.local/bin/tobot``
| ``~/.local/pipx/venvs/tobot/*``
|

**AUTHOR**

|
| ``Bart Thate`` <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``TOBOT`` is Public Domain.
|
