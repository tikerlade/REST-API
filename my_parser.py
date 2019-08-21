from datetime import datetime
from collections import defaultdict

class Parser:

    def __init__(self):
        '''Initialize dict (field_name -> 
        function that checks this field. '''
        self.check_funcs = defaultdict(self.default_check)

        self.check_funcs['citizen_id'] = self.check_citizen_id
        self.check_funcs['town'] = self.check_string_value
        self.check_funcs['street'] = self.check_string_value
        self.check_funcs['building'] = self.check_string_value
        self.check_funcs['apartment'] = self.check_apartment
        self.check_funcs['name'] = self.check_name
        self.check_funcs['birth_date'] = self.check_birth_date
        self.check_funcs['gender'] = self.check_gender

        
    def check(self, data, action='import', relatives={}):
        '''Check correctness of data'''

        # If action = import, then data must have 'citizens' field
        if action == 'import':
            if 'citizens' in data:
                data = data['citizens']
            else:
                return False
        # Otherwise change representation of data
        else:
            data = [data]

        # If action = replace then citizen_id field cannot be in data
        if action == 'replace':
            if 'citizen_id' in data[0]:
                return False


        # Check all fields for every citizen
        for citizen in data:
            # Number of fields must be 9 if action=imports
            if len(citizen) > 9 or (action == 'import' and len(citizen) < 9):
                return False

            for field in citizen:
                # We'll check relatives field later
                if field == 'relatives':
                    continue

                # Check field by it's own check-method]
                correct = self.check_funcs[field](citizen[field])
                if not correct:
                    return False

            if action == 'import':
                relatives[citizen['citizen_id']] = citizen['relatives']
        return self.check_relatives(relatives)

    
    def check_citizen_id(self, citizen_id):
        '''Check correctness of citizen_id field.'''
        
        if type(citizen_id) == int:
            return citizen_id >= 0
        return citizen_id
    

    def check_apartment(self, apartment):
        '''Check correctness of apartment field.'''
        
        if type(apartment) == int:
            return apartment >= 0
        return False
    
    
    def check_name(self, name):
        '''Check correctness of name field.'''
        
        if type(name) == str:
            return len(name) > 0
        return False
    
    
    def check_birth_date(self, birth_day):
        '''Check correctness of birth_day field.'''
        try:
            date = datetime.strptime(birth_day, '%d.%m.%Y').date()
            return date < datetime.today().date()
        except ValueError:
            return False
    
    
    def check_gender(self, gender):
        '''Check correctness of gender field.'''
        
        return gender == 'male' or gender == 'female'
    
    
    def check_relatives(self, relatives):
        '''Check correctness of relatives in data.'''

        for citizen in relatives:
            data = relatives[citizen]

            # Check for same indexes in relatives for one citizen
            if len(set(data)) < len(data):
                return False

            for relative in data:
                # Check dtype of index
                if type(relative) != int:
                    return False
        return True


    def check_string_value(self, value):
        '''Check correctness of town/street/building field.'''

        if type(value) != str or value =='null' or value == None:
            return False
        return value.isalnum() and len(value) <= 256

    def default_check(self):
        '''Returns false, because field name not known.'''
        return False