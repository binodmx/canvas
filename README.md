# Canvas

Canvas is a docker-based platform that allows users to deploy nicegui-based python web apps (plugins). 
It enables users to build interactive web applications with ease.

<details open>
<summary>Why Canvas?</summary>

We built this platform to simplify the deployment of small Python web apps, especially those developed using **LLM agents (co-pilots)** or **Generative AI IDEs**.
The goal is to make app deployment easy and accessible for everyone.

</details>

<details >
<summary>Who is this platform for?</summary>

- Makers, hobbyists, and developers who love to build and run their own custom apps.
- Anyone looking to deploy apps on personal devices like Raspberry Pi or similar hardware.

</details>

<details>
<summary>What makes it different?</summary>

- Quick and easy deployment — no steep learning curve.
- Optimized for small Python web apps powered by LLMs or GenAI tools.
- Perfect for personal devices — from Raspberry Pi to other lightweight servers.

</details>

# Getting Started

1. Make sure you have Docker installed on your machine.
2. Run the following command to start the Canvas.
    ```
    docker run -d -p 8080:8080 -v $(pwd):/app/data --name canvas binodmx/canvas
    ```
3. Open your web browser and navigate to `http://localhost:8080`.
4. You can now upload [available plugins](#plugins) or your own plugin.
5. View uploaded plugin on `http://localhost:8080/<PluginName>`.

# Plugins
- [Home](https://github.com/binodmx/canvas/blob/main/data/plugins/Home.py)
- [MarkdownEditor](https://github.com/binodmx/canvas/blob/main/data/plugins/MarkdownEditor.py)
- [PasteBin](https://github.com/binodmx/canvas/blob/main/data/plugins/PasteBin.py)
- [PluginManager](https://github.com/binodmx/canvas/blob/main/data/plugins/PluginManager.py)
- [WorldMap](https://github.com/binodmx/canvas/blob/main/data/plugins/WorldMap.py)

# Plugin Development Guide

## 1. Plugin Structure
- Plugins must be Python files (`.py` extension).
- Plugin filename should be in PascalCase (e.g., `MyPlugin.py`).
- Each plugin must import `nicegui.ui`.
- The plugin must define a main class that matches the filename (e.g., class `MyPlugin` in `MyPlugin.py`).
- The class must have an `__init__` method.
- Inside `__init__`, define a page route using `@ui.page('/<PluginName>')`.

    ```python
    from nicegui import ui
    
    class MyPlugin:
        def __init__(self):
            @ui.page('/MyPlugin')
            def index():
                # Your UI code goes here
                pass
    ```
## 2. UI Components
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

## 3. Plugin Functions
- Define functions to handle user interactions.
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
                # UI code...
                
                # Button click handler defined inside the __init__ method
                def handle_button_click():
                    ui.notify('Button clicked!')
                
                ui.button('Click Me', on_click=handle_button_click)
    ```
  
## 4. Data Storage
- Use the `./data/cache/` directory for temporary data storage.
    ```python
    import json
    import os
    
    def load_cache():
        try:
            with open('./data/cache/my_plugin_cache.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            default_data = {"items": []}
            save_cache(default_data)
            return default_data
    
    def save_cache(data):
        os.makedirs('./data/cache', exist_ok=True)
        with open('./data/cache/my_plugin_cache.json', 'w') as f:
            json.dump(data, f)
  
    class MyPlugin:
        ...
    ```
- Use the `./data/db/` directory to store databases as persistent data storage.
    ```python
    import os
    import sqlite3
    
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
            # cursor.execute(f"UPDATE {table_name} SET field2 = ? WHERE field1 = ?", [data[1], data[0]])
    
            # Delete data from the table
            # cursor.execute(f"DELETE FROM {table_name} WHERE field1 = ?", [data[0]])
  
            # Commit the changes
            connection.commit()
  
            # Close the connection
            connection.close()
        except Exception as e:
            print(f"Error saving to database: {e}")

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