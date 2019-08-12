from parser import Parser
from sql_manager import SQL_Manager

from flask import Flask, request, json, jsonify, abort


app = Flask(__name__)
parser = Parser()
manager = SQL_Manager()


@app.route('/imports', methods=['POST'])
def import_data():
    '''Description'''
    data = json.loads(request.data)
    check = parser.check(data['citizens'])
    
    if not check:
        return abort(400)
    
    output = manager.import_data(data)
    return output, 201


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['POST'])
def replace_data(import_id, citizen_id):
    '''Description.'''
    data = json.loads(request.data)
    check = parser.check(data, action='replace')
    
    if not check:
        return abort(400)
    
    output = manager.replace_data(import_id, citizen_id, data)
    return output, 200


@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_data(import_id):
    '''Returns data with given import_id.'''
    
    answer = manager.get_data(import_id)
    return answer, 200


@app.route('/imports/<int:import_id>/birthdays', methods=['GET'])
def get_birthdays(import_id):
    pass


@app.route('/imports/<int:import_id>/towns/stat/percentile/age', methods=['GET'])
def get_percentile_age(import_id):
    pass