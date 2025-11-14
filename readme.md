# DX Python Tools for Isadora  
*User Actors for enhancing Python workflows in Isadora (Windows & macOS)*

## Overview  
**DX Python Tools** is a collection of user actors designed to streamline Python development inside Isadora’s built-in Pythoner environment. These actors complement Isadora’s native Python support with advanced tools for managing virtual environments, external editors, modules, and the full Python toolchain on both Windows and macOS.

Whether you’re building custom Python modules, linking to external IDEs like PyCharm or VS Code, or creating side-car utilities that integrate with Isadora, these actors help you work more efficiently and robustly.

---

## Included User Actors

### 1. **DX – PY – Virtual Environment Manager**  
Provide full control of Python virtual environments from inside Isadora:

- Create a new `venv` using a `requirements.txt` file  
- Generate a `requirements.txt` from an active environment (excluding system-level packages)  
- Update the `ActiveVirtualEnvironmentPath.txt` to align with your project workspace  
- Validate `requirements.txt` entries against PyPI to warn about missing or incompatible wheels  

### 2. **DX – PY – Helpers**  
Utility tools for file, folder, and Python environment management:

- Display key system and Python environment configuration paths  
- Open project folders and dialogs via native OS UI  
- Create or clear directories, manage cache files  
- Quick install or uninstall of modules inside the active `venv`  
- Clear module caches so that changes in external files are recognized by Pythoner  

---

## 🚀 Getting Started  
The User Actors are Published for use with Isadora at: https://troikatronix.com/add-ons/dx-python-tools-for-isadora/

1. Once downloaded, **Place** the actor files into your Isadora user actor folder.  
2. In your Isadora project, add the actor(s) to your scene.  
   - *DX – PY – Helpers* is recommended in all projects that use Pythoner.  
3. Open the *Information Panel* in Isadora to view help tool-tips for each actor input/output.  
4. Open the Monitor window to inspect status messages.  
5. **Recommended Workflow**:
   - Create a dedicated folder for your Isadora project.  
   - Save your `.izz` project file in that folder.  
   - Use the Virtual Environment Manager to create or select a `venv`.  
     *If you have a `requirements.txt`, use “Create VENV”; if not, use “Create VENV in virtual_env”.*  
   - Use Helpers to manage modules, paths, and caches.  
   - Store your Python modules in a `python_modules` folder; link them via Pythoner’s “ext file” input.  
   - When editing in an external IDE, use the Helpers to clear caches so Isadora detects file changes.  

---

## ✅ Why Use These Tools?  
- Integrates external Python editors/IDEs into your Isadora development workflow  
- Keeps your dependencies and environments clean and shareable  
- Enables faster iteration when building Python-based side-car apps  
- Ensures smooth cross-platform support (Windows & macOS)  
- Ideal for installations, live performance setups, visual-coding workflows  

---

## ✏️ Contributions & Feedback  
If you encounter bugs or have feature suggestions, please open an issue or contribute a pull request.  
Both actors have been tested on Windows and macOS — some module-validation features require internet access or elevated privileges.
Alternatively, you can post your feedback to the Isadora User Forums: https://community.troikatronix.com/
---

## 📜 License  
This software is released under the terms of the **MIT License**.

---

## 🎉 Thanks  
Thanks for using DX Python Tools! If you build something cool using these actors, we’d love to hear about it in the Isadora community forum.

---

## 🙏 **Credits**

This project was created by **Ryan Webber (DusX)**  
Toronto-based multimedia programmer, creative technologist, and member of the TroikaTronix development team.

You are free to use, modify, and build upon this project.  
If you do, **please include attribution**:

**Credit:**  
_“Includes code or assets by Ryan Webber (DusX)”_  
https://dusxproductions.com

### 📄 License
This project uses a **dual-license model**:

- **Code:** MIT License — free to use commercially or non-commercially with attribution  
- **Media, documentation & artistic assets:** Creative Commons Attribution 4.0 (CC-BY 4.0)

See the included `LICENSE.txt` for full details.

## 🙏 **Credits**

This project was created by **Ryan Webber (DusX)**  
Toronto-based multimedia programmer, creative technologist, and member of the TroikaTronix development team.

You are free to use, modify, and build upon this project.  
If you do, **please include attribution**:

**Credit:**  
_“Includes code or assets by Ryan Webber (DusX)”_  
https://dusxproductions.com

### 📄 License
This project uses a **dual-license model**:

- **Code:** MIT License — free to use commercially or non-commercially with attribution  
- **Media, documentation & artistic assets:** Creative Commons Attribution 4.0 (CC-BY 4.0)

See the included `LICENSE.txt` for full details.

[![MIT License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE.txt)
[![CC BY 4.0](https://img.shields.io/badge/License-CC--BY--4.0-blue?style=for-the-badge)](https://creativecommons.org/licenses/by/4.0/)

[![Author](https://img.shields.io/badge/Author-Ryan%20Webber%20(DusX)-lightgrey?style=for-the-badge)](https://dusxproductions.com)

![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows)
![macOS](https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple)

![Creative Coding](https://img.shields.io/badge/Creative%20Coding-purple?style=for-the-badge)
![Isadora](https://img.shields.io/badge/TroikaTronix-Isadora-8e44ad?style=for-the-badge)

![Python](https://img.shields.io/badge/Pythoner-Compatible-306998?style=for-the-badge&logo=python)
