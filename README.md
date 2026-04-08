# Canvas
Canvas is a Docker-based platform for deploying Python and NiceGUI-based single-page applications. 
It makes it easy to build and run interactive web apps, particularly those created with LLM agents, co-pilots, or AI IDEs. 
Canvas is designed for makers, hobbyists, and developers who want to ship custom apps quickly, whether on a cloud server or personal hardware like a Raspberry Pi.

# Getting Started

## Running Docker Image

1. Make sure you have Docker installed on your host machine.
2. Run the following command to start the Canvas docker container.
    ```bash
    docker run -d -p 8080:8080 -v $(pwd):/app/data --name canvas binodmx/canvas
    ```
3. Open your web browser and navigate to `http://localhost:8080`.
4. You can now upload [available plugins](#plugins), or your own plugin that follows the [plugin development guide](#plugin-development-guide).
5. View uploaded plugin on `http://localhost:8080/<PluginName>`.

## Running Python App

1. Make sure you have Python installed on your host machine.
2. Run the following commands to setup and run Canvas Python app.
    ```bash
    git clone https://github.com/binodmx/canvas.git
    cd canvas
    pip install -r requirements.txt
    python app.py
    ```
3. Open your web browser and navigate to `http://localhost:8080`.
4. You can now upload [available plugins](#plugins), or your own plugin that follows the [plugin development guide](#plugin-development-guide).
5. View uploaded plugin on `http://localhost:8080/<PluginName>`.

# Plugins

## Published Plugins
| Name | Description |
| ---- | ----------- |
| [Home](https://github.com/binodmx/canvas/blob/main/data/plugins/Home.py)                      | Landing page listing down all the available plugins. |
| [PluginManager](https://github.com/binodmx/canvas/blob/main/data/plugins/PluginManager.py)    | Add or edit plugins with built-in code editor to edit plugin's code. |
| [MarkdownEditor](https://github.com/binodmx/canvas/blob/main/data/plugins/MarkdownEditor.py)  | Real-time markdown editor. |
| [PasteBin](https://github.com/binodmx/canvas/blob/main/data/plugins/PasteBin.py)              | Save texts and retrieve from any device. |

## Plugin Development Guide

### 1. Plugin Structure
- Plugins must be Python files (`.py` extension).
- Plugin filename should be in PascalCase (e.g., `MyPlugin.py`).
- Each plugin must import `nicegui.ui`.
- The plugin must define a main class that matches the filename (e.g., class `MyPlugin` in `MyPlugin.py`).
- The main class must have an `__init__` method.
- Inside `__init__`, define a page route using `@ui.page('/<PluginName>')`.
- See [UI Components](#2-ui-components), [Functions](#3-functions), and [Data Storage](#4-data-storage) 
- Explore already published [plugins](#plugins) for more information.

    ```python
    from nicegui import ui
    
    class MyPlugin:
        def __init__(self):
            @ui.page('/MyPlugin')
            def index():
                # Your UI code goes here
                pass
    ```

### 2. UI Components
- Use NiceGUI components to build your interface.

    ```python
    class MyPlugin:
        def __init__(self):
            @ui.page('/MyPlugin')
            def index():
                # Header example
                with ui.header().classes('bg-primary text-white h-16'):
                    with ui.row().classes('w-full h-full items-center justify-between px-4'):
                        ui.link('Canvas', '/').classes('no-underline text-2xl font-bold text-white')
                
                # Body example
                with ui.column().classes('w-full max-w-3xl mx-auto gap-4 p-4'):
                    ui.markdown("## My Plugin")
                    with ui.card().classes('w-full'):
                        text_input = ui.textarea(placeholder="Type text here").classes('w-full text-base')
    ```

### 3. Functions
- You can define functions to handle user interactions.
- Functions can be defined within the `__init__` method or outside the plugin class.
- Functions as instance, class, or static methods are also allowed even though not recommended.

    ```python 
    # Utility functions defined outside the class
    def util_function():
        print("util_function called.")
    
    class MyPlugin:
        def __init__(self):
            @ui.page('/MyPlugin')
            def index():
                # Handlers defined inside the __init__ method
                def handle_button_click():
                    ui.notify('Button clicked!')

                # UI structural code...
                
                # UI functional code      
                ui.button('Click Me', on_click=handle_button_click)
    ```
  
### 4. Data Storage
- Use `./data/cache/` directory for temporary data storage.
- Use `./data/db/` directory to store databases as persistent data storage.
- Use `./data/configs/` directory to store configurations.

    ```python
    import json
    import os
    import sqlite3
    
    # Load cache example
    def load_cache():
        try:
            with open('./data/cache/my_plugin_cache.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            default_data = {"items": []}
            save_cache(default_data)
            return default_data
    
    # Save cache example
    def save_cache(data):
        os.makedirs('./data/cache', exist_ok=True)
        with open('./data/cache/my_plugin_cache.json', 'w') as f:
            json.dump(data, f)

    # Update db example
    def update_db(data):
        try:
            # Create a connection to a SQLite database
            db_name = "./data/db/my_plugin_db.db"
            connection = sqlite3.connect(db_name)
            table_name = "table_name"
            cursor = connection.cursor()
    
            # Create the table if it does not exist
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (field1 TEXT PRIMARY KEY, field2 INTEGER)")
    
            # Insert data into the table
            cursor.execute(f"INSERT INTO {table_name} VALUES (?, ?)", [data[0], data[1]])
            
            # Update data in the table
            cursor.execute(f"UPDATE {table_name} SET field2 = ? WHERE field1 = ?", [data[1], data[0]])
    
            # Delete data from the table
            cursor.execute(f"DELETE FROM {table_name} WHERE field1 = ?", [data[0]])
  
            # Commit the changes
            connection.commit()
  
            # Close the connection
            connection.close()
        except Exception as e:
            print(f"Error saving to database: {e}")

    # Read db example
    def get_db():
        try:
            # Create a connection to a SQLite database
            db_name = "./data/db/my_plugin_db.db"
            connection = sqlite3.connect(db_name)
            table_name = "table_name"
            cursor = connection.cursor()
    
            # Create the table if it does not exist
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (field1 TEXT PRIMARY KEY, field2 INTEGER)")
    
            # Get rows from the table
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY field1 ASC")
            rows = cursor.fetchall()
            
            # Close the connection
            connection.close()
            return rows
        except Exception as e:
            print(f"Error reading from database: {e}")
            return None
  
    class MyPlugin:
        ...
    ```

# Contributing
Want to publish a plugin, report a bug, or improve documentation? Excellent! fork this repository and start contributing.

Love Canvas? Give this repo a star ⭐