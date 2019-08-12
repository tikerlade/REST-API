import sqlite3
from flask import jsonify

class SQL_Manager:
    
    def __init__(self):
        self.connection = sqlite3.connect('citizens.db')
        self.cursor = self.connection.cursor()
        
        create_query = '''CREATE TABLE IF NOT EXISTS citizens
                          (import_id INTEGER,
                           citizen_id INTEGER,
                           town TEXT,
                           street TEXT,
                           building TEXT,
                           apartment INTEGER,
                           name TEXT,
                           birth_date TEXT,
                           gender TEXT,
                           relatives TEXT)'''
        
        self.cursor.execute(create_query)
        
    
    def __del__(self):
        '''Commit changes and close the connection to database.'''
        
        self.connection.commit()
        self.connection.close()
    
    
    def get_import_id(self):
        '''Get the import_id for new session.'''
        
        get_query = '''SELECT MAX(import_id)
                       FROM citizens'''
        import_id = self.cursor.execute(get_query).fetchone()[0]
        
        if import_id != None:
            return import_id + 1
        return 0
    
    
    def get_column_names(self, table='citizens'):
        '''Get column names of given table'''
        column_names = list(self.cursor.execute(f'''PRAGMA table_info({table})'''))
        column_names  = [element[1] for element in column_names]
        
        return column_names
    
    
    def import_data(self, data):
        '''Adding new data to database.'''
        
        import_id = self.get_import_id()
        
        # Loop over all citizens
        for citizen in data['citizens']:
            # Loop over all fields
            values = list(citizen.values())
            
            import_query = '''INSERT INTO citizens
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            params = [import_id] + values[:-1] + [str(values[-1])]
            
            self.cursor.executemany(import_query, [params])
        
        answer = {'data': {'import_id':import_id}}
        return jsonify(answer)
    

    def replace_data(self, import_id, citizen_id, new_data):
        '''Replaces data for citizen with indexes to new_data.'''
        
        # Set new_data for SQL UPDATE query form
        new = ', '.join([name + " = '" + str(new_data[name]) + "'" for name in new_data])
        
        
        # Update table
        update_query = f'''UPDATE citizens SET {new}
                           WHERE import_id = {import_id}
                           AND citizen_id = {citizen_id}'''
        self.cursor.execute(update_query)
        
        # Get updated data
        columns = self.get_column_names()
        query = f'''SELECT * FROM citizens
                    WHERE import_id = {import_id}
                    AND citizen_id = {citizen_id}'''
        data = list(self.cursor.execute(query).fetchone())
        
        
        # Generating answer
        answer = {'data': {columns[i]: data[i] for i in range(1, len(columns))}} 
        return jsonify(answer)
    
    
    def get_data(self, import_id):
        '''Retrieves all the data from database which import_id = given id.'''
        
        # Get column names
        columns = self.get_column_names()
        
        # Get all rows with needed import_id
        query = f'''SELECT * FROM citizens
                    WHERE import_id = {import_id}'''
        data = list(self.cursor.execute(query))
        
        # Generating answer
        answer = {'data': []}
        for citizen in data:
            # Start collecting values from 1-index because 0-index is import_id
            values = {columns[i]: citizen[i] for i in range(1, len(columns))}
            answer['data'].append(values)
            
        return jsonify(answer)
    
    
    def get_birthdays(self, import_id):
        pass
    
    
    def get_percentile_age(self, import_id):
        pass
    
    