import sqlite3
from collections import defaultdict
from datetime import datetime
from flask import jsonify

class SQL_Manager:
    
    def __init__(self):
        self.connection = sqlite3.connect('citizens.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        
        main_create_query = '''CREATE TABLE IF NOT EXISTS citizens
                          (import_id INTEGER,
                           citizen_id INTEGER,
                           town TEXT,
                           street TEXT,
                           building TEXT,
                           apartment INTEGER,
                           name TEXT,
                           birth_date TEXT,
                           gender TEXT)'''

        relatives_create_query = '''CREATE TABLE IF NOT EXISTS relatives
                              (import_id INTEGER,
                               citizen_id INTEGER,
                               relative INTEGER)'''
        

        self.cursor.execute(main_create_query)
        self.cursor.execute(relatives_create_query)
        
    
    def __del__(self):
        '''Commit changes and close the connection to database.'''
        
        self.connection.commit()
        self.connection.close()
    
    
    def get_import_id(self):
        '''Get the import_id for new session.'''
        
        get_query = '''SELECT MAX(import_id)
                       FROM citizens'''
        import_id = self.cursor.execute(get_query).fetchone()[0]
        
        return import_id + 1 if import_id != None else 0
    
    
    def get_columns(self, table='citizens'):
        '''Get column names of given table'''
        
        columns = list(self.cursor.execute(f'''PRAGMA table_info({table})'''))
        columns  = [element[1] for element in columns]
        
        return columns

    
    def import_data(self, data):
        '''Adding new data to database.'''

        data = data['citizens']
        import_id = self.get_import_id()

        main_import_query = '''INSERT INTO citizens
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        relatives_query = '''INSERT INTO relatives
                             VALUES (?, ?, ?)'''

        # Insert main part of data
        main_params = [[import_id] + list(citizen.values())[:-1]\
                         for citizen in data]
        self.cursor.executemany(main_import_query, main_params)

        # Loop over all citizens
        for citizen in data:
            # Add relatives
            values = list(citizen.values())
            rel_params = [[import_id, values[0], value] for value in values[-1]]
            self.cursor.executemany(relatives_query, rel_params)

        answer = {'data': {'import_id':import_id}}
        return jsonify(answer)
    

    def replace_data(self, import_id, citizen_id, new_data):
        '''Replaces data for citizen with indexes to new_data.'''
        
        # Set new_data for SQL UPDATE query form
        new = ', '.join([name + " = '" + str(new_data[name]) + "'"
                         for name in new_data if name != 'relatives'])
        
        # Update table
        update_query = f'''UPDATE citizens SET {new}
                           WHERE import_id = {import_id}
                           AND citizen_id = {citizen_id}'''
        self.cursor.execute(update_query)

        # Update relatives table
        rel_delete_query = f'''DELETE FROM relatives
                               WHERE import_id = {import_id}
                               AND citizen_id = {citizen_id}'''
        self.cursor.execute(rel_delete_query)

        # Insert new relatives data
        rel_insert_query = '''INSERT INTO relatives
                              VALUES (?, ?, ?)'''
        params = [[import_id, citizen_id, value] for value in new_data['relatives']]
        self.executemany(query, params)

        
        # Get updated data
        query = f'''SELECT * FROM citizens
                    WHERE import_id = {import_id}
                    AND citizen_id = {citizen_id}'''
        data = list(self.cursor.execute(query).fetchone())
        

        # Get updated relatives data
        rel_query = f'''SELECT citizen_id, relative
                        FROM relatives
                        WHERE import_id = {import_id}
                        AND citizen_id = {citizen_id}
                        OR relative = {citizen_id}'''
        rel_data = list(self.cursor.execute(rel_query))

        rel_data =[rel_data[i][j] for j in range(2)\
                    for i in range(len(rel_data))\
                    if rel_data[i][j] != citizen_id]
        
        # Generating answer
        columns = self.get_columns()
        answer = {'data': {columns[i]: data[i] for i in range(1, len(columns))}}
        answer['data']['relatives'] = relatives

        return jsonify(answer)
    
    
    def get_data(self, import_id):
        '''Retrieves all the data from database which import_id = given id.'''
        
        # Get column names
        columns = self.get_columns()
        
        # Get all rows with needed import_id
        query = f'''SELECT * FROM citizens
                    WHERE import_id = {import_id}'''
        data = list(self.cursor.execute(query))

        
        # Generating answer
        answer = {'data': []}
        for citizen in data:
            # Start collecting values from 1-index because 0-index is import_id
            values = {columns[i]: citizen[i] for i in range(1, len(columns))}

            # Getting relatives
            citizen_id = citizen[1]
            rel_query = f'''SELECT citizen_id, relative
                            FROM relatives
                            WHERE import_id = {import_id}
                            AND citizen_id = {citizen_id}
                            OR relative = {citizen_id}'''
            rel_data = list(self.cursor.execute(rel_query))

            rel_data =[rel_data[i][j] for j in range(2)\
                        for i in range(len(rel_data))\
                        if rel_data[i][j] != citizen_id]

            values['relatives'] = rel_data
            answer['data'].append(values)

        return jsonify(answer)
    

    def get_relatives(self, import_id, citizen_id):
        '''Returns dict of citizens with relations.'''

        rel_query = f'''SELECT citizen_id, relative
                        FROM relatives
                        WHERE import_id = {import_id}'''
        data = list(self.cursor.execute(rel_query))

        answer = {}
        for pair in data:
            if pair[0] in answer:
                answer[pair[0]].append(pair[1])
            else:
                answer[pair[0]] = [pair[1]]

        return answer
    
    def get_birthdays(self, import_id):
        '''Description.'''

        # Get all pairs of getter-takers
        rel_query = f'''SELECT citizen_id, relative
                        FROM relatives
                        WHERE import_id={import_id}'''
        relatives = self.cursor.execute(rel_query).fetchall()


        answer = {month:defaultdict(int) for month in range(1, 13)}
        for pair in relatives:
            # Retrieve month of takers birthday
            citizen_id = pair[1]
            birthday_query = f'''SELECT strftime('%m', birth_date) FROM citizens
                                WHERE import_id = {import_id}
                                AND citizen_id = {citizen_id}'''
            date = self.cursor.execute(birthday_query).fetchone()

            # Increment getters counter for searched month
            if date:
                month = int(date[0])
                answer[month][pair[0]] += 1

        # Compile the answer, by adding labels
        for month in answer:
            buyers = [{'citizen_id':who, 'presents':answer[month][who]}\
                         for who in answer[month]]
            answer[month] = buyers

        answer = jsonify({'data': answer})
        return answer
    
    
    def get_percentile_age(self, import_id):
        '''Description'''
        pass