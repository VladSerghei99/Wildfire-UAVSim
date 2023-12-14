# Project description



# Installation setup

In the following subsections, the installation process for executing the project will be explained.

## Installing Pycharm Community Edition IDE

First, downloading and installing Pycharm Community Edition IDE is explained to easily run and set up the project and its dependencies.
Since this project is tested on Ubuntu 22.04.2 LTS, the user can use `snap` command in cmd (pre-installed from Ubuntu 16.04 LTS and later) as a fast installation option. The user must execute the command
`sudo snap install pycharm-community --classic` in cmd for installing Pycharm Community Edition. 

As mentioned, this project was tested on Ubuntu 22.04.2 LTS, so for other OS were not. For checking system requirements, and information about the installation process for other OS, 
visit https://www.jetbrains.com/help/pycharm/installation-guide.html.

## Opening the project

First extract the Wildfire-UAVSim downloaded package in any folder. Second, open Pycharm by executing the command `pycharm-community` in cmd, or searching for the executable in the computer. 
Then, the projects window should be opened. Next, the user has to click on `Open`, select the extracted project folder, and click `OK`. A window should appear to select between light editor, and project editor. 
Select project editor. For openning the project next tiems, repeat same process.

## Installing dependencies
 
Once the project is opened, some dependencies are necessary. To install them, first go to `Settings > Project > Python Interpreter`, then select the desired Python interpreter 
for executing the project. As default `/usr/bin/python3.10` should appear in the `Python Interpreter:` tab, which already contain some default dependencies if Ubuntu 22.04.2 LTS is installed. For other Python interpreters,
other dependencies may be needed to be installed. On the same Pycharm configuration window, click on `+` icon, and search for the following dependencies (selecting the version should be done for testing project same way as 
it was done for the research paper. It can be done with the `Specify version` checkbox):

<ul>
  <li>Mesa (v.1.2.1)</li>
  <li>numpy (v1.24.2)</li>
  <li>matplotlib (v3.7.1)</li>
</ul> 

## Execution of the project

Once project is opened, and dependencies were installed, `main.py` can be executed by selecting the file, right mouse click, and clicking on `Run 'main'` (shortcut should be `Ctrl+Mayus+F10`). 
A web page interface should appear, with the wildfire grid, and buttons for configuring the simulation.

# Graphical interface functionalities

# Common variables configuration

## Main variables description

## Configuration examples
