# PyGrep 🐍

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

*A lightweight, feature-rich regular expression engine and `grep`-like command-line utility, built from scratch in Python for academic and portfolio purposes.*

This project is a handcrafted regex engine that demonstrates the core principles of pattern matching, including parsing, backtracking, and state management for features like capture groups and backreferences.

---

## 🚀 Installation

You can install PyGrep directly from the Visual Studio Code Marketplace.

1.  Open the **Extensions** view in VS Code (`Ctrl+Shift+X`).
2.  Search for `PyGrep`.
3.  Click **Install** on the extension published by *Yogvid Wankhede*.

Alternatively, you can [install it directly from the Marketplace website]([YOUR_LINK_HERE](https://marketplace.visualstudio.com/items?itemName=yogvid.pygrep)).

---

## ✨ Features

PyGrep implements a significant subset of standard regex features, all built from the ground up:

* **Atoms & Classes:**
    * ✅ Literal character matching (`a`, `b`, `c`)
    * ✅ Wildcard (`.`)
    * ✅ Character classes (`\d`, `\w`)
    * ✅ Custom character sets (`[abc]`) and negated sets (`[^abc]`) with ranges (`[a-z]`)
* **Quantifiers:**
    * ✅ One or more (`+`)
    * ✅ Zero or one (`?`)
    * ✅ Zero or more (`*`)
* **Grouping & Referencing:**
    * ✅ Grouping with `()`
    * ✅ Alternation (`cat|dog`)
    * ✅ Capturing groups and multiple backreferences (`\1`, `\2`)
* **Anchors:**
    * ✅ Start of string (`^`)
    * ✅ End of string (`$`)
* **CLI Functionality:**
    * ✅ Search standard input (piped text)
    * ✅ Search one or more files
    * ✅ Recursive directory search (`-r` flag)

---

## 🚀 Getting Started

After installing from the VS Code Marketplace, you can use the PyGrep command through the Command Palette.

---

## Usage

1. Open any text file.
2. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on Mac).
3. Type "PyGrep" and select the command **"PyGrep: Search in Current File"**.
4. An input box will appear at the top. Type your regex pattern and press Enter.
5. The search results will be displayed in a "PyGrep Results" output panel.

---

## 🛠 Architectural Overview

This project is built with a clean separation of concerns into two primary classes:

* **`MiniRegex` (The Engine):** This is the core of the project. It takes a raw pattern string and is responsible for parsing it into a logical structure and then executing the match. The matching algorithm is based on **recursive, generator-based backtracking**, which allows it to explore all possible match paths for complex patterns.

* **`CLI` (The Interface):** This class handles all interaction with the user and the operating system. Its responsibilities include parsing command-line arguments, reading from standard input, finding and opening files, and printing the output in the correct format. It uses an instance of the `MiniRegex` engine to perform the actual search on each line of text it reads.

---

## 📝 License

This project is licensed under the MIT License.
