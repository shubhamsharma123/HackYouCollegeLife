# Assignment: python

## Q1. what is virtual enviorments ?
**Virtual environments in Python**

A virtual environment is a self‑contained folder that holds its own Python interpreter, libraries, and scripts.  
- **Why use it?**  
  - Keeps project libraries separate so one project’s packages don’t interfere with another’s.  
  - Makes it easy to install exact versions of libraries needed for that project.  
- **What it contains:**  
  - A copy of the Python executable.  
  - A `pip` tool that installs packages only in that folder.  
- **How to create one:**  
  1. Open a terminal.  
  2. Run `python -m venv myenv` (replace *myenv* with a name).  
  3. Activate it:  
     - Windows: `myenv\Scripts\activate`  
     - macOS/Linux: `source myenv/bin/activate`  
- **After activation:**  
  - `pip install <package>` installs the package only inside the environment.  
  - To stop using it, type `deactivate`.  

Virtual environments keep your projects clean, reproducible, and free from conflicting package versions.

## Q2. what are python libraries
Python libraries are collections of ready‑made code that you can use in your own programs.  
- **What they do** – They add new functions, classes, or tools so you don’t have to write everything from scratch.  
- **How they’re used** – You install them (often with pip) and import them with the `import` statement.  
- **Common types**  
  - *Standard library* – built‑in modules like `math`, `datetime`, `random`.  
  - *Third‑party libraries* – external packages such as:
    - `NumPy` – fast math and array operations.  
    - `Pandas` – data analysis and table handling.  
    - `Requests` – easy HTTP requests.  
    - `Matplotlib` – drawing charts and graphs.  
    - `Scikit‑learn` – machine‑learning tools.  
- **Benefits** – Saves time, improves reliability, and lets you focus on your project’s unique ideas.