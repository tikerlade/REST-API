from my_parser import Parser
from sql_manager import SQL_Manager

from flask import Flask, request, json, jsonify, abort, Response


app = Flask(__name__)
parser = Parser()
manager = SQL_Manager()


@app.route('/')
def main():
    return 'OK'


@app.route('/imports', methods=['POST'])
def import_data():
    '''Get data in json format, check its for correctness
    	and then add to database.'''

    data = json.loads(request.data)
    check = parser.check(data)
    
    if check != True:
        return check
    
    return manager.import_data(data)


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>',
            methods=['POST'])
def replace_data(import_id, citizen_id):
    '''Replace data with new.'''
    
    data = json.loads(request.data)
    relatives = manager.get_relatives(import_id, citizen_id)
    check = parser.check(data, 'replace', relatives)

    if check != True:
        return check
    
    return manager.replace_data(import_id, citizen_id, data)


@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_data(import_id):
    '''Returns data with given import_id.'''
    
    return manager.get_data(import_id)


@app.route('/imports/<int:import_id>/birthdays', methods=['GET'])
def get_birthdays(import_id):
    '''Returns data about who and how
         many data will buy in each month.'''
    
    return manager.get_birthdays(import_id)


@app.route('/imports/<int:import_id>/towns/stat/percentile/age',
             methods=['GET'])
def get_percentile_age(import_id):
    '''Returns percentiles of age for each town.'''

    return manager.get_percentile_age(import_id)


if __name__== '__main__':
    app.run(host="0.0.0.0", port=8080)