import json
import sqlite3
from collections import defaultdict
from datetime import datetime

import numpy as np
from dateutil.relativedelta import relativedelta
from flask import jsonify


class SQL_Manager:

    def __init__(self):
        '''Initialize sql_manager instance. Connect to the database.'''

        self.connection = sqlite3.connect('citizens.db',
                                          check_same_thread=False)
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
        '''Commit changes and close the connection to the database.'''

        self.connection.commit()
        self.connection.close()

    def run_query(self, query):
        '''Run the given query and commit.'''

        self.cursor.execute(query)
        self.connection.commit()

    def get_import_id(self):
        '''Get the import_id for the new session.

        Returns:
            import_id: id for new upload
        '''

        get_query = '''SELECT MAX(import_id) FROM citizens'''
        import_id = self.cursor.execute(get_query).fetchone()[0]

        return import_id + 1 if import_id is not None else 0

    def check_import_id(self, import_id):
        '''Extra check for the import_id.

        Args:
            import_id (int): import ID

        Returns:
            True: import_id is in the database
            response: message & 404-status_code, given import_id
            is not in the database
        '''

        if import_id >= self.get_import_id():
            # Building response for a failed request.
            error_msg = f'No such "import_id" = {import_id} in database.'
            response = jsonify({'message': error_msg})
            response.status_code = 404
            return response
        return True

    def build_good_request(self, data, status_code=200):
        '''From data make request with the good status_code.

        Args:
            data: data for json response
            status_code (int): status_code for the response

        Returns:
            response: complete response from server
        '''

        response = jsonify({'data': data})
        response.status_code = status_code

        return response

    def get_columns(self, table='citizens'):
        '''Get column names of a given table.

        Args:
            table (str): table which columns to return

        Returns:
            columns: column_names of table
        '''

        columns = list(self.cursor.execute(f'''PRAGMA table_info({table})'''))
        columns = [element[1] for element in columns]

        return columns

    def order_import_params(self, data, columns, import_id):
        '''If data is shuffled function will order it.

        Args:
            data: shuffled data to input
            columns: columns names
            import_id (int): id of upload

        Returns:
            new_data: list of values in right order
        '''
        data['import_id'] = import_id

        indexes = {column: i for i, column in enumerate(columns)}
        new_data = [None] * len(indexes)
        for column in data:
            if column == 'relatives':
                continue
            idx = indexes[column]
            new_data[idx] = data[column]

        return new_data

    def get_relatives_for_citizen(self, import_id, citizen_id):
        '''Returns relatives for a given citizen.

        Args:
            import_id (int): id of an import
            citizen_id (int): id of citizen whose relatives to return

        Returns:
            relatives: list of relatives to given person
        '''

        rel_query = f'''SELECT citizen_id, relative
                        FROM relatives
                        WHERE import_id = {import_id}
                        AND (citizen_id = {citizen_id}
                        OR relative = {citizen_id})'''
        rel_data = list(self.cursor.execute(rel_query))

        # Relatives are two-sided.
        rel_data = [rel_data[i][j] for j in range(2)
                    for i in range(len(rel_data))
                    if rel_data[i][j] != citizen_id]

        return list(set(rel_data))

    def get_relatives(self, import_id):
        '''Returns dict of citizens with relations.

        Args:
            import_id (int): id of upload

        Returns:
            relatives: dict citizen -> relatives
        '''

        rel_query = f'''SELECT citizen_id, relative
                        FROM relatives
                        WHERE import_id = {import_id}'''
        data = list(self.cursor.execute(rel_query))

        response = {}
        for pair in data:
            if pair[0] in response:
                response[pair[0]].append(pair[1])
            else:
                response[pair[0]] = [pair[1]]

        return response

    def import_data(self, data):
        '''Imports new data to the database.

        Args:
            data: data to import

        Returns:
            response: complete response for a query
        '''

        data = data['citizens']
        import_id = self.get_import_id()

        main_import_query = '''INSERT INTO citizens
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        relatives_query = '''INSERT INTO relatives
                             VALUES (?, ?, ?)'''

        # Insert main part of data.
        columns = self.get_columns()
        main_params = [self.order_import_params(citizen, columns, import_id)
                       for citizen in data]
        self.cursor.executemany(main_import_query, main_params)
        self.connection.commit()

        # Loop over all citizens.
        for citizen in data:
            # Add relatives.
            citizen_id = citizen['citizen_id']
            values = citizen['relatives']
            rel_params = [[import_id, citizen_id, value]
                          for value in values]
            self.cursor.executemany(relatives_query, rel_params)
        self.connection.commit()

        # Build response.
        return self.build_good_request({'import_id': import_id}, 201)

    def replace_data(self, import_id, citizen_id, new_data):
        '''Replaces data for a given citizen.

        Args:
            import_id (int): id of upload where to seek citizen
            citizen_id (int): id of citizen
            new_data (dict): data which to replace

        Returns:
            response: complete response with an updated info about citizen
        '''

        # Extra check for import_id.
        check_answer = self.check_import_id(import_id)
        if check_answer is not True:
            return check_answer

        # Set new_data for SQL UPDATE query form.
        new = ', '.join([name + ' = "' + str(new_data[name]) + '"'
                         for name in new_data if name != 'relatives'])

        # Update table.
        update_query = f'''UPDATE citizens SET {new}
                           WHERE import_id = {import_id}
                           AND citizen_id = {citizen_id}'''
        self.run_query(update_query)

        # Update relatives table.
        rel_delete_query = f'''DELETE FROM relatives
                               WHERE import_id = {import_id}
                               AND citizen_id = {citizen_id}
                               OR relative = {citizen_id}'''
        self.run_query(rel_delete_query)

        if 'relatives' in new_data:
            # Insert new relatives data.
            rel_insert_query = '''INSERT INTO relatives
                                  VALUES (?, ?, ?)'''
            params = [[import_id, citizen_id, value]
                      for value in new_data['relatives']]
            params += [[import_id, value, citizen_id]
                       for value in new_data['relatives']]
            self.cursor.executemany(rel_insert_query, params)
            self.connection.commit()

        # Get updated data.
        query = f'''SELECT * FROM citizens
                    WHERE import_id = {import_id}
                    AND citizen_id = {citizen_id}'''
        data = self.cursor.execute(query)

        if data is not None:
            data = data.fetchone()

            # Generate the answer.
            columns = self.get_columns()
            answer = {columns[i]: data[i] for i in range(1, len(columns))}
            answer['relatives'] =\
                self.get_relatives_for_citizen(import_id, citizen_id)
        else:

            error_msg = f'citizen with "citizen_id" = ' +\
                   f'{citizen_id} is not in database.'
            response = jsonify({'message': error_msg})
            response.status_code = 404
            return response

        # Build response for the completed query.
        response = jsonify(answer)
        response.status_code = 200
        return response

    def get_data(self, import_id):
        '''Retrieves all data from database for a given `import_id`.

        Args:
            import_id (int): id of upload to return

        Returns:
            response: complete response with info
            about all citizens from a given import
        '''

        # Extra check for import_id.
        check_answer = self.check_import_id(import_id)
        if check_answer is not True:
            return check_answer

        # Get column names.
        columns = self.get_columns()

        # Get all rows with needed import_id.
        query = f'''SELECT * FROM citizens
                    WHERE import_id = {import_id}'''
        data = list(self.cursor.execute(query))

        # Generate the answer.
        answer = []
        for citizen in data:
            # Start collecting values from 1-index
            # because 0-index is import_id.
            values = {columns[i]: citizen[i] for i in range(1, len(columns))}

            citizen_id = citizen[1]
            values['relatives'] =\
                self.get_relatives_for_citizen(import_id, citizen_id)
            answer.append(values)

        return self.build_good_request(answer)

    def get_birthdays(self, import_id):
        '''Returns who and how many presents will buy in each month.

        Args:
            import_id: id of upload

        Returns:
            response: complete response with info per months
        '''

        # Extra check for import_id.
        check_answer = self.check_import_id(import_id)
        if check_answer is not True:
            return check_answer

        # Get all pairs of getter-takers.
        rel_query = f'''SELECT citizen_id, relative
                        FROM relatives
                        WHERE import_id={import_id}'''
        relatives = self.cursor.execute(rel_query).fetchall()

        answer = {month: defaultdict(int) for month in range(1, 13)}
        for pair in relatives:
            # If replace pair[0] and pair[1] -> SOLUTION.
            for (giver, taker) in [(pair[0], pair[1]), (pair[1], pair[0])]:
                # Retrieve month of takers birthday.
                birthday_query = f'''SELECT birth_date FROM citizens
                                    WHERE import_id = {import_id}
                                    AND citizen_id = {taker}'''
                date = self.cursor.execute(birthday_query).fetchone()

                # Increment getters counter for the searched month.
                if date:
                    date = datetime.strptime(date[0], '%d.%m.%Y')
                    month = date.month
                    answer[month][giver] += 1

        # Compile the answer by adding labels.
        for month in answer:
            buyers = [{'citizen_id': who, 'presents': answer[month][who]}
                      for who in answer[month]]
            answer[month] = buyers

        return self.build_good_request(answer)

    def get_percentile_age(self, import_id):
        '''Returns age percentiles (50, 75, 99) for each town.

        Args:
            import_id (int): id of upload

        Returns:
            response: complete response with percentiles for each town
        '''

        # Extra check for import_id.
        check_answer = self.check_import_id(import_id)
        if check_answer is not True:
            return check_answer

        towns_query = f'''SELECT DISTINCT town FROM citizens
                          WHERE import_id = {import_id}'''
        towns = self.cursor.execute(towns_query)

        answer = []
        today = datetime.utcnow().date()

        # Compute percentiles for each town.
        towns = [town[0] for town in towns.fetchall()]
        for town in towns:
            births_query = f'''SELECT birth_date FROM citizens
                              WHERE import_id = {import_id}
                              AND town = {json.dumps(town,
                               ensure_ascii=False)}'''
            dates = self.cursor.execute(births_query)

            # Format the date.
            dates = [datetime.strptime(date[0], '%d.%m.%Y').date()
                     for date in dates.fetchall()]

            # Compute ages.
            ages = [relativedelta(today, date).years
                    for date in dates]

            percentiles = [round(np.percentile(ages, p,
                           interpolation='linear'), 2)
                           for p in [50, 75, 99]]

            town_output = {'town': town,
                           'p50': percentiles[0],
                           'p75': percentiles[1],
                           'p99': percentiles[2]}
            answer.append(town_output)

        return self.build_good_request(answer)
