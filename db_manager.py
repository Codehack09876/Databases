import os, pickle
from table import Table

class DatabaseManager:
    def __init__(self):
        self.databases = {}  # Dictionary to store databases as {db_name: {table_name: Table instance}}

    def create_database(self, db_name):
        if db_name in self.databases:
            print(f"Database '{db_name}' already exists.")
            return
        self.databases[db_name] = {}

    def delete_database(self, db_name):
        if db_name not in self.databases:
            print(f"Database '{db_name}' does not exist.")
            return
        del self.databases[db_name]

    def list_databases(self):
        return list(self.databases.keys())

    def create_table(self, db_name, table_name, schema, order=8, search_key=None):
        if db_name not in self.databases:
            print(f"Database '{db_name}' does not exist.")
            return
        if table_name in self.databases[db_name]:
            print(f"Table '{table_name}' already exists in database '{db_name}'.")
            return
        self.databases[db_name][table_name] = Table(table_name, schema, order, search_key)
        print(f'Table {table_name} is created successfully in the database {db_name}')
        return

    def delete_table(self, db_name, table_name):
        if db_name not in self.databases:
            print(f"Database '{db_name}' does not exist.")
            return
        if table_name not in self.databases[db_name]:
            print(f"Table '{table_name}' does not exist in database '{db_name}'.")
            return
        del self.databases[db_name][table_name]

    def list_tables(self, db_name):
        if db_name not in self.databases:
            print(f"Database '{db_name}' does not exist.")
            return
        return list(self.databases[db_name].keys())

    def get_table(self, db_name, table_name):
        if db_name not in self.databases:
            print(f"Database '{db_name}' does not exist.")
            return
        if table_name not in self.databases[db_name]:
            print(f"Table '{table_name}' does not exist in database '{db_name}'.")
            return
        return self.databases[db_name][table_name]
    
    def save_database(self, filepath):
        try:
            # Normalize the path and ensure it has a file extension
            filepath = os.path.normpath(filepath)
            if not filepath.endswith('.pkl'):
                filepath += '.pkl'  # Add pickle extension if missing
                
            dir_name = os.path.dirname(filepath)
            if dir_name: 
                os.makedirs(dir_name, exist_ok=True)
                
            # Test directory permissions
            if not os.access(dir_name, os.W_OK):
                raise PermissionError(f"No write permissions for directory: {dir_name}")
                
            with open(filepath, 'wb') as f:
                pickle.dump(self.databases, f, pickle.HIGHEST_PROTOCOL)
            return None, True
            
        except Exception as e:
            error_msg = f"Failed to save database at '{filepath}': {e}"
            print(error_msg)
            return error_msg, False

    def load_database(self, filepath):
        try:
            if not os.path.exists(filepath):
                return f"Load failed: File not found at '{filepath}'.", False
            with open(filepath, 'rb') as f:
                loaded_data = pickle.load(f)
            if not isinstance(loaded_data, dict):
                 raise TypeError("Loaded data is not in the expected dictionary format.")

            self.databases = loaded_data
            return None, True
        except FileNotFoundError:
            error_msg = f"Load failed: File not found at '{filepath}'."
            return error_msg, False
        except (pickle.UnpicklingError, EOFError, TypeError, ImportError, Exception) as e:
            error_msg = f"Failed to load database from '{filepath}': {e}"
            return error_msg, False