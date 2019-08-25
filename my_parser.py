from datetime import datetime
from collections import defaultdict

from flask import jsonify


class Parser:

    def __init__(self):
        '''Initialize parser instance and set check-functions.'''

        self.check_functions = defaultdict(self.default_check)

        self.check_functions['citizen_id'] = self.check_citizen_id
        self.check_functions['town'] = self.check_string_value
        self.check_functions['street'] = self.check_string_value
        self.check_functions['building'] = self.check_string_value
        self.check_functions['apartment'] = self.check_apartment
        self.check_functions['name'] = self.check_name
        self.check_functions['birth_date'] = self.check_birth_date
        self.check_functions['gender'] = self.check_gender

    def process_bad_request(self, message, code=400):
        '''Building bad_request response.

        Args:
            message (str): what to put in json description
            code (int): what code set to response


        Returns:
            response: complete response from server
                     with description and status_code'''

        response = jsonify({'message': message})
        response.status_code = code
        return response

    def check(self, data, action='import', relatives={}):
        '''Check correctness of data.


        Args:
            data (dict): what to check for correctness
            action (str): for what action we check data (import/replace)
            relatives (dict): relatives relations from data


        Returns:
            True: if all the data are correct
            response: message & bad-status_code if some errors in data
        '''

        # If action = import, then data must have 'citizens' field
        if action == 'import':
            if 'citizens' in data:
                data = data['citizens']

                # Check for unique citizen_id
                citizen_ids = [citizen['citizen_id'] for citizen in data]

                if len(set(citizen_ids)) != len(citizen_ids):
                    return self.process_bad_request(
                        '\'citizen_id\' must be unique for upload.')
            else:
                return self.process_bad_request('\'citizens\' ' +
                                                'not in json form.')
        # Otherwise change representation of data
        else:
            data = [data]

        # If action = replace then citizen_id field cannot be in data
        if action == 'replace':
            if 'citizen_id' in data[0]:
                return self.process_bad_request('\'citizen_id\' ' +
                                                'cannot be changed.')

        # Check all fields for every citizen
        for citizen in data:
            # Number of fields must be 9 if action=imports
            if len(citizen) > 9 or (action == 'import' and
                                    len(set(citizen)) < 9):
                return self.process_bad_request(
                        'Number of fields not match ' +
                        'the allowed number of fields')

            for field in citizen:
                # We'll check relatives field later
                if field == 'relatives':
                    if type(citizen[field]) != list:
                        return self.process_bad_request(
                            '\'relatives\' field must be list.')
                    continue

                # Check field by it's own check-method
                check = self.check_functions[field](citizen[field])
                if check is not True:
                    return self.process_bad_request(check)

            if action == 'import':
                relatives[citizen['citizen_id']] = citizen['relatives']

        check_relatives = self.check_relatives(relatives)
        return True if check_relatives is True else\
            self.process_bad_request(check_relatives)

    def check_citizen_id(self, citizen_id):
        '''Check correctness of citizen_id field.

        Args:
            citizen_id (int): id of citizen


        Returns:
            True: citizen_id is correct
            error_msg: citizen_id is not correct
        '''

        error_msg = f'\'citizen_id\' = \'{citizen_id}\' field not correct.'

        if type(citizen_id) == int:
            return True if citizen_id >= 0 else error_msg
        return error_msg

    def check_apartment(self, apartment):
        '''Check correctness of apartment field.


        Args:
            apartment (int): citizen's apartment


        Returns:
            True: apartment is correct
            error_msg: apartment is not correct
        '''

        error_msg = f'\'apartment\' = \'{apartment}\' field not correct.'

        if type(apartment) == int:
            return True if apartment >= 0 else error_msg
        return error_msg

    def check_name(self, name):
        '''Check correctness of name field.


        Args:
            name (str): citizen's name


        Returns:
            True: name is correct
            error_msg: name is not correct
        '''

        error_msg = f'\'name\' = {name} field not correct.'

        if type(name) == str:
            return True if 257 > len(name) > 0 else error_msg
        return error_msg

    def check_birth_date(self, birth_date):
        '''Check correctness of birth_date field. Format: dd.mm.yyyy


        Args:
            birth_date (str): citizen's birthday


        Returns:
            True: birth_date is correct
            error_msg: birth_date is not correct
        '''

        error_msg = f'\'birth_date\' = \'{birth_date}\' field not correct.'

        try:
            date = datetime.strptime(birth_date, '%d.%m.%Y').date()
            return True if date < datetime.today().date() else error_msg
        except (ValueError, TypeError) as error:
            return error_msg

    def check_gender(self, gender):
        '''Check correctness of gender field. male or female accepts.


        Args:
            gender (str): citizen's gender


        Returns:
            True: gender is correct
            error_msg: gender is not correct
        '''
        error_msg = f'\'gender\' = \'{gender}\' field not correct.'

        return True if (gender == 'male' or gender == 'female') else error_msg

    def check_relatives(self, relatives):
        '''Check correctness of relatives in hole data.


        Args:
            relatives (dict): relations between citizens


        Returns:
            True: relations are correct
            error_msg: relations are not correct
        '''
        error_msg = 'Some \'relatives\' field of your citizens is not correct.'

        for citizen in relatives:
            data = relatives[citizen]

            # Check for same indexes in relatives for one citizen
            if len(set(data)) < len(data):
                return error_msg

            for relative in data:
                # Check dtype of index
                if type(relative) != int:
                    return error_msg
        return True

    def check_string_value(self, value):
        '''Check correctness of town/street/building field.


        Args:
            value (str): citizen's town/street/building


        Returns:
            True: field is correct
            error_msg: field is not correct
        '''
        error_msg = f'\'string_value\' = \'{value}\' field not correct.'

        if type(value) != str or value == 'null' or value is None:
            return error_msg
        return True if any(c.isalnum() for c in value) and\
                       len(value) <= 256 else error_msg

    def default_check(self):
        '''Stub check-function for fields, that are not supported.


        Returns:
            error_msg: field not supported'''
        error_msg = 'You have some fields that are not supported.'

        return error_msg
