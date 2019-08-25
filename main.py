from flask import Flask, request, json

from my_parser import Parser
from sql_manager import SQL_Manager


app = Flask(__name__)
parser = Parser()
manager = SQL_Manager()


@app.route('/')
def main():
    return 'OK'


@app.route('/imports', methods=['POST'])
def import_data():
    '''Retrieves data from request and adds it to the database.


    Returns:
        import_id & 201-status_code: data was added
        message & 404/400-status_code: some data broken
    '''

    data = json.loads(request.data)
    check = parser.check(data)

    if check is not True:
        return check

    return manager.import_data(data)


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>',
           methods=['POST'])
def update_data(import_id, citizen_id):
    '''Replace data with updated. Cannot update citizen_id.


    Args:
        import_id (int): id of upload where citizen_id located
        citizen_id (int): id of citizen which data to update


    Returns:
        citizen & 200-status_code: data was updated
        message & 404/400-status_code: some data broken
    '''

    data = json.loads(request.data)
    relatives = manager.get_relatives(import_id)
    check = parser.check(data, 'replace', relatives)

    if check is not True:
        return check

    return manager.replace_data(import_id, citizen_id, data)


@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_data(import_id):
    '''Returns data with given import_id.


    Args:
        import_id (int): id of upload which data to return.


    Returns:
        citizens: all data about citizens in import_id upload'''

    return manager.get_data(import_id)


@app.route('/imports/<int:import_id>/birthdays', methods=['GET'])
def get_birthdays(import_id):
    '''Returns data about who and how many
             presents will buy in each month.


    Args:
        import_id (int): id of upload which birthdays
                         relations to return.


    Returns:
        birthdays: who and how many presents will buy in each month

    '''

    return manager.get_birthdays(import_id)


@app.route('/imports/<int:import_id>/towns/stat/percentile/age',
           methods=['GET'])
def get_percentile_age(import_id):
    '''What is the age of percentiles: [50, 75, 99] for each town.


    Args:
        import_id (int): which upload to use for percentiles counting


    Returns:
        percentile_info: for every town info abosut
                         [50, 75, 99] percentiles'''

    return manager.get_percentile_age(import_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
