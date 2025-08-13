# Welcome to DragTK™

**DragTk** is a Python application built with **Tkinter** that makes designing Tkinter GUIs quick and simple.  
Instead of manually writing layout code, you can drag and drop widgets into a canvas, adjust their properties, and instantly see the results.

This is a simple Python app that lets you build simple Python GUI apps with basic widgets in a drag and drop manor. This app is mainly targeted at earlier education users programming with Python but who want to build Graphic User Interfaces.

---

## ✨ Features

- **Visual GUI Designer** – Drag and drop widgets (e.g., Labels, Buttons, Entry fields) onto a design canvas.
- **Built-in Code Editor** – View and edit the generated Python Tkinter code in real time.
- **Error Log** – See detailed error messages to help you debug quickly.
- **Widget Property Editor** – Change basic widget properties (text, colours, sizes, etc.) via a simple interface.
- **Instant Export** – Save your GUI project as a Python file you can run or extend.

---

## 📦 Requirements

- Python **3.11+** (May work on earlier versions of Python3 but this has not been tested)
- Tkinter (usually comes pre-installed with Python)
- No extra packages are needed – DragTk is fully self-contained.

---

## 🚀 Getting Started

1. Download the Zip folder in this repository - "DragTK.zip"
2. Ensure Python3 is downloaded and installed on your computer.
3. Download the DragTK files.
4. Run!

---

# Development Notes

DragTk is written entirely in Python using the built-in Tkinter library.

---

# User Guidance

## Using the editor

### Adding Code

You can add your own code into the editor. Make sure you add it between the start and end marking comments as seen in the video!

Code not added between these comments will be overwritten. (This is due to the underlying functionality of how this application works)

Code written between these comments will be safe.

<img width="882" height="449" alt="image" src="https://github.com/user-attachments/assets/d7c16096-ce82-4492-9eec-237edd029c7d" />


### Special Functions

DragTK automatically generates functions for button, treeview, combobox, and listbox widgets. References to these functions are automatically generated in the "command" attribute on the widgets creation.

You can add code inside these generated functions.

Code which is written OUTSIDE a generated function in the special functions section will be overwritten. So make sure you indent properly!

<br>
<img width="1705" height="812" alt="image" src="https://github.com/user-attachments/assets/9d6194e6-3be8-4deb-8470-3c6397891462" />

<br>
<img width="1703" height="819" alt="image" src="https://github.com/user-attachments/assets/b8fafa05-4b08-4d4e-a9ff-e7047cd2a7d5" />

<br>
<img width="860" height="615" alt="image" src="https://github.com/user-attachments/assets/f2ad0cca-79d3-4a46-bc38-9455043441ea" />


### GUI Code

Code for the UI is completely auto generated based on your interactions with the canvas, the widgets you add, and how you set their properties. You cannot manually modify code in this section as it will be overwritten. The only property changes you can make within this app are to the properties listed in the properties pane in the app and these properties should only be changed via this interface.

If you wish to make changes more freely, you should ensure you are finished designing your interface. Then you could export the code to its own .py file and continue to edit with another editor freely such as IDLE.

<img width="857" height="315" alt="image" src="https://github.com/user-attachments/assets/5105d116-4c46-4bce-9875-b83ea5f113c8" />


### The Canvas

The red dotted line within the canvas indicates what your apps window size will be when it runs. Your apps name and size can be edited in the canvas propties section below the canvas.

- Adding widgets to the canvas
     - Widgets can be dragged around and positioned. They snap every 10 pixels making it easy to align with other widgets
     - Move your cursor to the edge of a widget to click and drag to resize it
     - Right click a widget for copy, paste, and delete options
     - Double click a widget to edit its text property
     - Select a widget and use the usual copy and paste shortcuts or use the delete key to delete it


<img width="968" height="762" alt="image" src="https://github.com/user-attachments/assets/1add535b-1f59-45b2-9688-906eda1ddaaa" />


### Intuitive Functionality

The app features some common functions and shortcuts.

- Light/Dark mode can be toggled in the Options menu or with Ctrl + t shortcut
- Use the f5 shortcut to run your app
- Ctrl + s shortcut to save
- Ctrl + c to copy
- Ctrl + v to paste

### Running your app

You can use the run button in the top right to start a subprocess that will run your app.

You can use the 'Check and Run' button to parse your code in the editor for syntax and name errors.

The recommended flow would be to first perform a 'Check and Run'. If this succeeds without errors, it is recommended you close the window that opens and run your app using the 'Run' button. This is because the 'Run' button actually starts a subprocess to run your app while 'Check and Run' exectutes your app via the exec() function. As a result, not all features of your app may work as expected if executing via the 'Check and Run' buttons exec() method.

<img width="880" height="253" alt="image" src="https://github.com/user-attachments/assets/13403264-9f4f-4e56-8962-802d2dc18824" />

### Save, Load, and Export

Under the file menu, you can save and load a project version compatible with this app. Project files for DragTK are saved and loaded from a .json file.

Note that if you make any changes to your Python code in an external editor (e.g. IDLE) and attempt to reuse this code within DragTK, it may not work as expected. It is recommended you do not export or edit your code in another editor until you are sure you are finished designing your interface features through DragTK.

When you are finished, you can use the export option under the File menu or just copy and paste your code out of the code editor into your own .py file.


### Debugging

The DragTK download will include a .pyw version and .py version.

- The .pyw version is best to use if you do not want the windows command prompt window to open while using the app.
- The .py version (debug) is best to use if you want to debug your own app built with DragTK as it means when you run your app from within DragTK, you will get a command prompt window where you can check print() output.

<img width="613" height="255" alt="image" src="https://github.com/user-attachments/assets/549e58df-d55e-47bd-ab1a-259e5929b260" />

---

# Widgets

## Radiobuttons

When adding a radiobutton, you will be asked to name a radio group which the radio button will belong to. For example, if you want a user to be able to select one option from three different colors: red, blue, green; you might names the groups "colors".

The next time you add a radiobutton, you should see any previously created groups listed. Just type in the same of a previously existing group (spelling important) to link a radiobutton with an existing group, or, you can of course create a new group.

<img width="758" height="481" alt="image" src="https://github.com/user-attachments/assets/35207a15-6d68-468a-a4ea-8519f71f7436" />

<img width="682" height="474" alt="image" src="https://github.com/user-attachments/assets/92f166ae-b6e1-44e5-9fcf-aad3d23dcddd" />


---

# License

This project is licensed under the MIT License – see the LICENSE file for details.

---

© 2025 Marcus Douglas. “DragTk” is a trademark of Marcus Douglas.
