from parser import Parser

from flask import Flask, request, json, jsonify, abort


app = Flask(__name__)


@app.route('/imports', methods=['POST'])
def data_imports():
    '''Description'''
#     import_id = 0
#     import_id += 1
    data = json.loads(request.data)
    
    parser = Parser()
    check = parser.check(data)
    
    if check:
        report = (jsonify({'import_id': import_id}), 201)
    else:
        report = abort(400)
        
    return report


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['POST'])
def data_replace(import_id, citizen_id):
    pass


@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_data(import_id):
    pass


@app.route('/imports/<int:import_id>/birthdays', methods=['GET'])
def get_birthdays(import_id):
    pass


@app.route('/imports/<int:import_id>/towns/stat/percentile/age', methods=['GET'])
def get_percentile_age(import_id):
    pass