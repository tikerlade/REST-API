from my_parser import Parser
from sql_manager import SQL_Manager

from flask import Flask, request, json, jsonify, abort


app = Flask(__name__)
parser = Parser()
manager = SQL_Manager()


@app.route('/')
def main():
    return 'OK'


@app.route('/imports', methods=['POST'])
def import_data():
    '''Get data in json format, then check it for correctness
    	and then add to database.'''

    data = json.loads(request.data)
    if not parser.check(data):
        return abort(400)
    
    output = manager.import_data(data)
    return output, 201


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>',
            methods=['POST'])
def replace_data(import_id, citizen_id):
    '''Replace data with new.'''
    
    data = json.loads(request.data)
    relatives = manager.get_relatives(import_id, citizen_id)
    check = parser.check(data, 'replace', relatives)
    
    if not check:
        return abort(400)
    return data

    
    output = manager.replace_data(import_id, citizen_id, data)
    return output, 200


@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_data(import_id):
    '''Returns data with given import_id.'''
    
    answer = manager.get_data(import_id)
    return answer, 200


@app.route('/imports/<int:import_id>/birthdays', methods=['GET'])
def get_birthdays(import_id):
    '''Returns data about who and how many data will buy in each month.'''

    answer = manager.get_birthdays(import_id)
    return answer, 200


@app.route('/imports/<int:import_id>/towns/stat/percentile/age', methods=['GET'])
def get_percentile_age(import_id):
    pass

if __name__== '__main__':
    app.run()