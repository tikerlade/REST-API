import datetime

class Parser:
    
    def __init__(self):
        pass

    
    def check(self, data):
        '''Check correctness of data'''
        
        if 'citizens' not in data:
            return False
        
        # Loop over all citizens
        for citizen in data['citizens']:
            # Number of fields must be 9
            if len(citizen) != 9:
                return False

            # Loop over all fields
            for field in citizen:
                # Checking of correct field name
                try:
                    check_func = getattr(self, 'check_'+field)
                except AttributeError:
                    return field

                # Check field by it's own check-method
                answer = check_func(citizen[field])
                if not answer:
                    return False
        return True
    
    
    def check_citizen_id(self, citizen_id):
        '''Check correctness of citizen_id field.'''
        
        if type(citizen_id) == int:
            return citizen_id >= 0
        return False
    
    
    def check_town(self, town):
        '''Check correctness of town field.'''
        
        return town != 'null' and any([town[i].isalnum() for i in range(len(town))])
    
    
    def check_street(self, street):
        '''Check correctness of street field.'''
        
        return street != 'null' and any([street[i].isalnum() for i in range(len(street))])
    
    
    def check_building(self, building):
        '''Check correctness of building field.'''
        
        return building != 'null' and any([building[i].isalnum() for i in range(len(building))])
    
    
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
            d = datetime.datetime.strptime(birth_day, '%d.%m.%Y')
            return d
        except ValueError:
            return False
    
    
    def check_gender(self, gender):
        '''Check correctness of gender field.'''
        
        return gender == 'male' or gender == 'female'
    
    
    def check_relatives(self, relatives):
        return True