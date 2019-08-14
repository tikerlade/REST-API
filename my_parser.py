import datetime
from sql_manager import SQL_Manager

class Parser:
    
    def check(self, data, action='import', relatives={}):
        '''Check correctness of data'''
        
        # If action = import, then data must have 'citizens' field
        print('Checking')
        if action == 'import':
            if 'citizens' in data:
                print('Cool')
                data = data['citizens']
            else:
                print('Trash')
                return False
        print('Loop')
        # Loop over all citizens
        for citizen in data:
            # Number of fields must be 9 if action=import
            print('length')
            if action == 'import' and len(citizen) != 9:
                print('Not enough data')
                return False

            # Loop over all fields
            for field in citizen:
                # Checking of correct field name
                if field == 'relatives':
                    continue
                try:
                    check_func = getattr(self, 'check_'+field)
                except AttributeError:
                    print('Attribute', field, citizen)
                    return False

                # Check field by it's own check-method
                answer = check_func(citizen[field])
                if answer != True:
                    return answer

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
        print(town)
        return town != 'null' and any([town[i].isalnum() for i in range(len(town))])
    
    
    def check_street(self, street):
        '''Check correctness of street field.'''
        print(street)
        return street != 'null' and any([street[i].isalnum() for i in range(len(street))])
    
    
    def check_building(self, building):
        '''Check correctness of building field.'''
        print(building)
        return building != 'null' and any([building[i].isalnum() for i in range(len(building))])
    
    
    def check_apartment(self, apartment):
        '''Check correctness of apartment field.'''
        
        if type(apartment) == int:
            return apartment >= 0
        return apartment
    
    
    def check_name(self, name):
        '''Check correctness of name field.'''
        
        if type(name) == str:
            return len(name) > 0
        return False
    
    
    def check_birth_date(self, birth_day):
        '''Check correctness of birth_day field.'''
        try:
            d = datetime.datetime.strptime(birth_day, '%d.%m.%Y')
            return True
        except ValueError:
            return birth_day
    
    
    def check_gender(self, gender):
        '''Check correctness of gender field.'''
        
        return gender == 'male' or gender == 'female'
    
    
    def check_relatives(self, relatives):
        '''Check correctness of relatives in data.'''
        print(relatives)

        for person in relatives:
            data = relatives[person]
            print(data)

            # Check for same indexes in relatives for one person
            if len(set(data)) < len(data):
                return False

            for person1 in data:
                # Check dtype of index
                if type(person1) != int:
                    return False
        return True