import sqlite3

conn_meows = None
conn_settings = None

conn_meows_cursor = None
conn_settings_cursor = None

# init and stop conn
def open_conns():
    global conn_meows
    global conn_settings

    global conn_meows_cursor
    global conn_settings_cursor

    conn_meows = sqlite3.connect("meows.db")
    conn_settings = sqlite3.connect("settings.db")

    conn_meows_cursor = conn_meows.cursor()
    conn_settings_cursor = conn_settings.cursor()

    print("sqlite conns opened")

def close_conns():
    conn_meows.close()
    conn_settings.close()
    
    print("sqlite conns closed")



# request for the tables to be setup in the case that they do not exist. if the table for the server already exists, ignore.
def setup_tables_for_server(server_id):
    #table meows
    table_name = f"Server_{server_id}"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        name TEXT NOT NULL,
        count INTEGER NOT NULL
    );
    """
    try:
        conn_meows_cursor.execute(create_table_query)
        conn_meows.commit()
    except Exception as e:
        print(f"Error creating table '{table_name}' for meows.db: {e}")

    #table settings
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        name TEXT NOT NULL,
        value DOUBLE NOT NULL
    );
    """
    try:
        conn_meows_cursor.execute(create_table_query)
        conn_meows.commit()
    except Exception as e:
        print(f"Error creating table '{table_name}' for settings.db: {e}")


# query values
def query_meow_value(server_id, user_id):
    table_name = f"Server_{server_id}"
    query = f"SELECT count FROM {table_name} WHERE name = '{user_id}'"
    
    conn_meows_cursor.execute(query)
    result = conn_meows_cursor.fetchone()

    if result:
        return result[0] 
    else:
        print(f"Warning: No entry found for user_id '{user_id}' in table '{table_name}'.")
        return 0

def query_setting_value(server_id, setting_name):
    table_name = f"Server_{server_id}"
    query = f"SELECT value FROM {table_name} WHERE name = '{setting_name}'"
    
    conn_settings_cursor.execute(query)
    result = conn_settings_cursor.fetchone()

    if result:
        return result[0] 
    else:
        print(f"Warning: No entry found for setting '{setting_name}' in table '{table_name}'.")
        return 0

def set_meow_value(server_id, user_id, value):
    table_name = f"Server_{server_id}"
    query = f"INSERT INTO {table_name} (name, count) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET count = ?"
    try:
        conn_meows_cursor.execute(query, (user_id, value, value))
        conn_meows.commit()
    except sqlite3.Error as e:
        print(f"Error updating meow value for user_id '{user_id}' in table '{table_name}': {e}")

def add_meows(server_id, user_id, count):
    set_meow_value(server_id, user_id, query_meow_value(server_id, user_id) + count)

def set_settings_value(server_id, setting_name, value):
    table_name = f"Server_{server_id}"
    query = f"INSERT INTO {table_name} (name, value) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET value = ?"
    try:
        conn_settings_cursor.execute(query, (setting_name, value, value))
        conn_settings.commit()
    except sqlite3.Error as e:
        print(f"Error updating setting value for setting_name '{setting_name}' in table '{table_name}': {e}")

def get_top_meowers(server_id):
    query = f"""
    SELECT name, count FROM Server_{server_id}
    ORDER BY count DESC
    LIMIT 10;
    """
    try:
        conn_meows_cursor.execute(query)
        result = conn_meows_cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error querying top meowers for server {server_id}: {e}")
        return []