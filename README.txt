==================
Welcome to DragTk™
==================

DragTk is a Python application built with Tkinter that makes designing Tkinter GUIs quick and intuitive.
Instead of manually writing layout code, you can drag and drop widgets into a canvas, adjust their properties, and instantly see the results.

Features:
---------

# Visual GUI Designer – Drag and drop widgets (e.g., Labels, Buttons, Entry fields) onto a design canvas.
# Built-in Code Editor – View and edit the generated Python Tkinter code in real time.
# Error Log – See detailed error messages to help you debug quickly.
# Widget Property Editor – Change basic widget properties (text, colours, sizes, etc.) via a simple interface.
# Instant Export – Save your GUI project as a Python file you can run or extend.

Requirements:
-------------

# Python 3.8+
# Tkinter (usually comes pre-installed with Python)
# No extra packages are needed – DragTk is fully self-contained.

Getting Started:
----------------
# Ensure Python 3 is downloaded and installed on your computer.
# Download the DragTk files.
# Run!

Development Notes:
------------------
DragTk is written entirely in Python using the built-in Tkinter library.


User Guidance
=============

Using the editor
================

Adding Code
-----------

You can add your own code into the editor. Make sure you add it between the start and end marking comments as seen in the video!

Code not added between these comments will be overwritten. (This is due to the underlying functionality of how this application works)

Code written between these comments will be safe.




Special Functions
-----------------

DragTK automatically generates functions for button, treeview, combobox, and listbox widgets. References to these functions are automatically generated in the "command" attribute on the widgets creation.

You can add code inside these generated functions.

Code which is written OUTSIDE a generated function in the special functions section will be overwritten. So make sure you indent properly!




GUI Code
--------
Code for the UI is completely auto generated based on your interactions with the canvas, the widgets you add, and how you set their properties. You cannot manually modify code in this section as it will be overwritten. The only property changes you can make within this app are to the properties listed in the properties pane in the app and these properties should only be changed via this interface.

If you wish to make changes more freely, you should ensure you are finished designing your interface. Then you could export the code to its own .py file and continue to edit with another editor freely such as IDLE.




The Canvas
----------
The red dotted line within the canvas indicates what your apps window size will be when it runs. Your apps name and size can be edited in the canvas propties section below the canvas.

- Adding widgets to the canvas
     - Widgets can be dragged around and positioned. They snap every 10 pixels making it easy to align with other widgets
     - Move your cursor to the edge of a widget to click and drag to resize it
     - Right click a widget for copy, paste, and delete options
     - Double click a widget to edit its text property
     - Select a widget and use the usual copy and paste shortcuts or use the delete key to delete it





Intuitive Functionality
-----------------------
The app features some common functions and shortcuts.

- Light/Dark mode can be toggled in the Options menu or with Ctrl + t shortcut
- Use the f5 shortcut to run your app
- Ctrl + s shortcut to save
- Ctrl + c to copy
- Ctrl + v to paste

Running your app
----------------
You can use the run button in the top right to start a subprocess that will run your app.

You can use the 'Check and Run' button to parse your code in the editor for syntax and name errors.

The recommended flow would be to first perform a 'Check and Run'. If this succeeds without errors, it is recommended you close the window that opens and run your app using the 'Run' button. This is because the 'Run' button actually starts a subprocess to run your app while 'Check and Run' exectutes your app via the exec() function. As a result, not all features of your app may work as expected if executing via the 'Check and Run' buttons exec() method.


Save, Load, and Export
----------------------
Under the file menu, you can save and load a project version compatible with this app. Project files for DragTK are saved and loaded from a .json file.

Note that if you make any changes to your Python code in an external editor (e.g. IDLE) and attempt to reuse this code within DragTK, it may not work as expected. It is recommended you do not export or edit your code in another editor until you are sure you are finished designing your interface features through DragTK.

When you are finished, you can use the export option under the File menu or just copy and paste your code out of the code editor into your own .py file.


Debugging
---------
The DragTK download will include a .pyw version and .py version.

- The .pyw version is best to use if you do not want the windows command prompt window to open while using the app.
- The .py version (debug) is best to use if you want to debug your own app built with DragTK as it means when you run your app from within DragTK, you will get a command prompt window where you can check print() output.


========

License:
========

This project is licensed under the MIT License – see the LICENSE file for details.

© 2025 Marcus Douglas. “DragTk” is a trademark of Marcus Douglas.