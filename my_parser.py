from datetime import datetime

class Parser:
    
    def check(self, data, action='import', relatives = {}):
        '''Check correctness of data'''
        
        # If action = import, then data must have 'citizens' field
        if action == 'import':
            if 'citizens' in data:
                data = data['citizens']
            else:
                return False

        # Loop over all citizens
        for citizen in data:
            # Number of fields must be 9 if action=imports
            if len(citizen) > 9 or (action == 'import' and len(citizen) < 9):
                return False

            # Loop over all fields
            for field in citizen:
                # We'll check relatives field later
                if field == 'relatives':
                    continue

                # Checking of correct field name
                try:
                    print(field)
                    check_func = getattr(self, 'check_'+field)
                except AttributeError:
                    return False

                # Check field by it's own check-method]
                if not check_func(citizen[field]):
                    return False
            
            if action == 'import':
                relatives[citizen['citizen_id']] = citizen['relatives']
        return self.check_relatives(relatives)
    
    
    def check_citizen_id(self, citizen_id):
        '''Check correctness of citizen_id field.'''
        
        if type(citizen_id) == int:
            return citizen_id >= 0
        return citizen_id
    
    
    def check_town(self, town):
        '''Check correctness of town field.'''

        return self.check_string_value(town)
    
    
    def check_street(self, street):
        '''Check correctness of street field.'''

        return self.check_string_value(street)

    
    def check_building(self, building):
        '''Check correctness of building field.'''

        return self.check_string_value(building)
    

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
        return value.isalnum()