# oabd_notifier
A notifier application in python with customizable timers.

# Installation & Usage
First, you need a working version of Python, which you can install here, if you don't have one:  
https://www.python.org/downloads/  

After that, in your console / powershell / cmd, move to a suitable directory (typically either 'Downloads' or 'Desktop'), and from there type:  
```git clone https://github.com/pikachoof/oabd_notifier.git```  
  
It will download the application's file into the ```oabd_notifier``` folder.  
Move into the oabd_notifier folder via:  
```cd oabd_notifier```  

Then install the necessary Python dependencies via:  
```pip install -r requirements.txt```  
  
Then launch the script via:  
1) ```python main.py```  
or  
2) ```python3 main.py```  
if the 1st one doesn't work.  
  
# Features:
## Add timer
Create a new timer with a name and set its interval

## Toggle Status of timer
If you don't wanna use, or want to enable a timer, click on the timer, and then press "Toggle Status" to disable/enable it.

## Save timers to "timers.txt"
You can save your newly created timers so they load upon the next launch of the application.

## Load timers from file
In the "timers.txt" file you can set up the timers in text form, and later load them upon launching the application.

## Delete timer
If you don't wanna use a timer anymore, just delete it by cliking on the timer and then clicking "Delete Selected".

# How it works:
1) Upon launching the `main.py` file, the timers will be loaded from the timsers.txt file
2) Manage your timers by Adding, Saving, Toggling and Deleting them.
3) After you launch RobloxPlayerLauncher.exe, the *Active* timers will automatically start their countdowns and print a screen notification that the time is up.

# Video demonstration:
https://streamable.com/nvzqxv
