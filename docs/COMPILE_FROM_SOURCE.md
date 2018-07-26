# Compiling from source code
## Requirements
### Python 3 Interpreter
Latest* version of **Python 3** is needed. See if it is already installed [here](#finding-the-correct-keyword-for-python). If not, download the matching release for your platform [here](https://www.python.org/downloads/) and install it.  
If you are a *Windows* user, selecting **Add Python 3 to PATH** option when installing the software is mandatory.   
  
\* *Use Python 3.6.5 if you encounter an issue*
## Using terminal
### To open it...
- **On Windows 8/8.1/10**: Press the File tab on **Windows Explorer**, click on **Open Windows PowerShell** or **Open Windows Command Prompt** or look for *Command Prompt* or *PowerShell* in *Start Menu*.
  
- **On Windows 7**: Press **WindowsKey+R**, type **cmd** and hit Enter or look for *Command Prompt* or *PowerShell* in *Start Menu*.
  
- **On Linux**: Right-click in a folder and select **Open Terminal** or press **Ctrl+Alt+T** or look for **Terminal** in the programs.
  
- **On MacOS**: Look for an app called **Terminal**.
  
### Navigating to the directory where script is downloaded
Go inside the folder where script.py is located. If you are not familiar with changing directories on command-prompt and terminal read *Changing Directories* in [this article](https://lifehacker.com/5633909/who-needs-a-mouse-learn-to-use-the-command-line-for-almost-anything)

## Finding the correct keyword for Python
Enter these lines to terminal window until it prints out the version you have downloaded and installed:
  
- `python --version`
- `python3 --version`
- `python3.7 --version`
- `python3.6 --version`
- `py --version`
- `py -3 --version`
- `py -3.6 --version`
- `py -3.7 --version`
  
Once it does, your keyword is without the `--version` part. 

## Installing dependencies
Enter the line below to terminal window when you are in the directory where script.py is, use your keyword for Python:
```console
python -m pip install -r requirements.txt
```
  
---
  
Now, you can go to [Using command-line arguments](COMMAND_LINE_ARGUMENTS.md)
