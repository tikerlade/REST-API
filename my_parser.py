from collections import defaultdict
from datetime import datetime

from flask import jsonify


class Parser:

    CITIZEN_ID_ERROR_MSG = '"citizen_id" = "%s" field is not correct.'
    APARTMENT_ERROR_MSG = '"apartment" = "%s" field is not correct.'
    NAME_ERROR_MSG = '"name" = "%s" field is not correct.'
    BIRTH_DATE_ERROR_MSG = '"birth_date" = "%s" field is not correct.'
    GENDER_ERROR_MSG = '"gender" = "%s" field not correct.'
    RELATIVES_ERROR_MSG = 'Some of the "relatives" fields of ' +\
                          'your citizens is not correct.'
    STRING_ERROR_MSG = '"string_value" = "%s" field not correct.'
    STUB_ERROR_MSG = 'You have some fields that are not supported.'

    def __init__(self):
        '''Initialize parser instance and define check-functions.'''

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
        '''Build a response for a bad (failed) request.

        Args:
            message (str): json description
            code (int): response code

        Returns:
            response: response containing description and status_code
        '''

        response = jsonify({'message': message})
        response.status_code = code
        return response

    def check(self, data, action='import', relatives={}):
        '''Check correctness of the data.

        Args:
            data (dict): data to check for correctness
            action (str): action for which to check the data (import/replace)
            relatives (dict): relatives relations from the data

        Returns:
            True: if data is fully correct
            response: message & bad-status_code
                        if some errors are found in the data
        '''

        # If action = import, then data must have 'citizens' field.
        if action == 'import':
            if 'citizens' in data:
                data = data['citizens']

                # Check for unique citizen_id.
                citizen_ids = [citizen['citizen_id'] for citizen in data]

                if len(set(citizen_ids)) != len(citizen_ids):
                    return self.process_bad_request(
                        '"citizen_id" must be unique for upload.')
            else:
                return self.process_bad_request('"citizens" ' +
                                                'is not in json form.')
        # Otherwise change representation of the data.
        else:
            data = [data]

        # If action = replace then citizen_id field can not be in the data.
        if action == 'replace':
            if 'citizen_id' in data[0]:
                return self.process_bad_request('"citizen_id" ' +
                                                'cannot be changed.')

        # Check all fields for every citizen.
        for citizen in data:
            # Number of fields must be 9 if action=import
            if action == 'import' and len(set(citizen)) != 9:
                return self.process_bad_request(
                        'Number of fields not match ' +
                        'the allowed number of fields')

            for field in citizen:
                if field == 'relatives':
                    if type(citizen[field]) != list:
                        return self.process_bad_request(
                            '"relatives" field must be a list.')
                    continue

                # Check field using the relevant check-function.
                result = self.check_functions[field](citizen[field])
                if result is not True:
                    return self.process_bad_request(result)

            if action == 'import':
                relatives[citizen['citizen_id']] = citizen['relatives']

        check_relatives = self.check_relatives(relatives)
        return True if check_relatives is True else\
            self.process_bad_request(check_relatives)

    def check_citizen_id(self, citizen_id):
        '''Check correctness of the `citizen_id` field.

        Args:
            citizen_id (int): id of the citizen

        Returns:
            True: citizen_id is correct
            error_msg: citizen_id is not correct
        '''

        if type(citizen_id) == int and citizen_id >= 0:
            return True
        return self.CITIZEN_ID_ERROR_MSG % citizen_id

    def check_apartment(self, apartment):
        '''Check correctness of the `apartment` field.

        Args:
            apartment (int): citizen's apartment

        Returns:
            True: apartment is correct
            error_msg: apartment is not correct
        '''

        if type(apartment) == int and apartment >= 0:
            return True
        return self.APARTMENT_ERROR_MSG % apartment

    def check_name(self, name):
        '''Check correctness of the `name` field.

        Args:
            name (str): citizen's name

        Returns:
            True: name is correct
            error_msg: name is not correct
        '''

        if type(name) == str and 257 > len(name) > 0:
            return True
        return self.NAME_ERROR_MSG % name

    def check_birth_date(self, birth_date):
        '''Check correctness of the `birth_date` field.
           Expected format: dd.mm.yyyy

        Args:
            birth_date (str): citizen's birthday
        Returns:
            True: birth_date is correct
            error_msg: birth_date is not correct
        '''

        try:
            date = datetime.strptime(birth_date, '%d.%m.%Y').date()
            if date < datetime.today().date():
                return True
        except (ValueError, TypeError) as error:
            pass
        return self.BIRTH_DATE_ERROR_MSG % birth_date

    def check_gender(self, gender):
        '''Check correctness of a `gender` field. Expected: male or female.

        Args:
            gender (str): citizen's gender

        Returns:
            True: gender is correct
            error_msg: gender is not correct
        '''

        if gender == 'male' or gender == 'female':
            return True
        else:
            return self.GENDER_ERROR_MSG % gender

    def check_relatives(self, relatives):
        '''Check correctness of the `relatives` field.

        Args:
            relatives (dict): relations between citizens

        Returns:
            True: relations are correct
            error_msg: relations are not correct
        '''

        for citizen in relatives:
            data = relatives[citizen]

            # Check for same indexes in relatives for one citizen.
            if len(set(data)) < len(data):
                return self.RELATIVES_ERROR_MSG

            for relative in data:
                # Check dtype of the index.
                if type(relative) != int:
                    return self.RELATIVES_ERROR_MSG
        return True

    def check_string_value(self, value):
        '''Check correctness of a string field (e.g. town/street/building).

        Args:
            value (str): value of a string field

        Returns:
            True: field is correct
            error_msg: field is not correct
        '''

        if type(value) == str and value != 'null' and value is not None:
            if any(c.isalnum() for c in value) and len(value) <= 256:
                return True
        return self.STRING_ERROR_MSG % value

    def default_check(self):
        '''Stub check-function for not yet supported fields.

        Returns:
            error_msg: field is not supported
        '''

        return self.STUB_ERROR_MSG
