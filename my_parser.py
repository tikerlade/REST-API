from datetime import datetime
from collections import defaultdict
from flask import jsonify

class Parser:

    def get_check_functions(self):
        '''Returns dict (field_name -> 
        function that checks this field. '''
        functions = defaultdict(self.default_check)

        functions['citizen_id'] = self.check_citizen_id
        functions['town'] = self.check_string_value
        functions['street'] = self.check_string_value
        functions['building'] = self.check_string_value
        functions['apartment'] = self.check_apartment
        functions['name'] = self.check_name
        functions['birth_date'] = self.check_birth_date
        functions['gender'] = self.check_gender

        return functions

    def bad_request(self, message, code = 400):
        response = jsonify({'message': message})
        response.status_code = code
        return response
        
    def check(self, data, action='import', relatives={}):
        '''Check correctness of data'''

        # If action = import, then data must have 'citizens' field
        if action == 'import':
            if 'citizens' in data:
                data = data['citizens']

                # Check for unique citizen_id
                citizen_ids = [citizen['citizen_id'] for citizen in data]

                if len(set(citizen_ids)) != len(citizen_ids):
                    return self.bad_request('\'citizen_id\' must be unique for upload.')
            else:
                return self.bad_request('\'citizens\' not in json form.')
        # Otherwise change representation of data
        else:
            data = [data]

        # If action = replace then citizen_id field cannot be in data
        if action == 'replace':
            if 'citizen_id' in data[0]:
                return self.bad_request('\'citizen_id\' cannot be changed.')


        # Check all fields for every citizen
        check_funcs = self.get_check_functions()
        for citizen in data:
            # Number of fields must be 9 if action=imports
            if len(citizen) > 9 or (action == 'import' and len(set(citizen)) < 9):
                return self.bad_request('Number of fields not match' +\
                 'the allowed number of fields')

            for field in citizen:
                # We'll check relatives field later
                if field == 'relatives':
                    if type(citizen[field]) != list:
                        return self.bad_request('\'relatives\' field must be list.')
                    continue

                # Check field by it's own check-method]
                check = check_funcs[field](citizen[field])
                if check != True:
                    return self.bad_request(check)

            if action == 'import':
                relatives[citizen['citizen_id']] = citizen['relatives']

        check_relatives = self.check_relatives(relatives)
        return True if check_relatives == True else\
                     self.bad_request(check_relatives)

    
    def check_citizen_id(self, citizen_id):
        '''Check correctness of citizen_id field.'''
        error_msg = f'\'citizen_id\' = \'{citizen_id}\' field not correct.'
        
        if type(citizen_id) == int:
            return True if citizen_id >= 0 else error_msg
        return error_msg
    

    def check_apartment(self, apartment):
        '''Check correctness of apartment field.'''
        error_msg = f'\'apartment\' = \'{apartment}\' field not correct.'
        
        if type(apartment) == int:
            return True if apartment >= 0 else error_msg
        return error_msg
    
    
    def check_name(self, name):
        '''Check correctness of name field.'''
        error_msg = f'\'name\' = {name} field not correct.'
        
        if type(name) == str:
            return True if 257 > len(name) > 0 else error_msg
        return error_msg
    
    
    def check_birth_date(self, birth_date):
        '''Check correctness of birth_date field.'''
        error_msg = f'\'birth_date\' = \'{birth_date}\' field not correct.'

        try:
            date = datetime.strptime(birth_date, '%d.%m.%Y').date()
            return True if date < datetime.today().date() else error_msg
        except:
            return error_msg
    
    
    def check_gender(self, gender):
        '''Check correctness of gender field.'''
        error_msg = f'\'gender\' = \'{gender}\' field not correct.'
        
        return True if (gender == 'male' or gender == 'female') else error_msg
    
    
    def check_relatives(self, relatives):
        '''Check correctness of relatives in data.'''
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
        '''Check correctness of town/street/building field.'''
        error_msg = f'\'string_value\' = \'{value}\' field not correct.'

        if type(value) != str or value =='null' or value == None:
            return error_msg
        return True if any(c.isalnum() for c in value)\
                 and len(value) <= 256 else error_msg

    def default_check(self):
        '''Returns false, because field name not known.'''
        error_msg = 'You have some fields that are not supported.'

        return error_msg