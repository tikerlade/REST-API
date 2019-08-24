# REST-API service for Yandex Backend School

**Installation**

- First of all run this command:</br>
`sudo apt update`</br>
`git clone https://github.com/tikerlade/REST-API.git`

- Secondly you need to activae virtual environment</br>
`cd REST-API`</br>
`xargs -a apt_requirements.txt sudo apt install`</br>
`python3 -m venv venv`</br>
`. venv/bin/activate`

- Thirdly you need to change directory and install python packages</br>
`pip install -r pip_requirements.txt`

- Fourthly cleat port and run server</br>
`fuser -k -n tcp 8080`</br>
`gunicorn -w 4 -b 0.0.0.0:8080 main:app`</br></br></br>


**Tests information**</br>

*(Test files can be found in `Tests/Test_files` folder)*</br>

All tests were divided into 3 parts.</br>
1. Check correctness of server when database doesn't exist.</br>
2. Check correctness of my_parser functionality on broken data.</br>
3. Check correctness of my_parser on data presentation.</br></br></br>

**Running tests**</br>

1. Run your server on 0.0.0.0:8080
2. Change directory with `cd Tests` and run python script `python3 tester.py`
3. You will see message `All tests have been passed !`


**Tests structure**</br>

The structure of test files is:</br>
1. First line contains `url`</br>
2. Second line contains `status_code`</br>
3. Third line contains `data` to send</br>
4. Forhth line contains `data` recieved from server</br></br></br>


**Tests examples**</br>

The structure of test examples here is:</br>
`METHOD | url | [(what's wrong, what' testing)] | -> status_code`</br></br>

- First part (Checking statuses when nothing in database. All data and URLs are correct.)</br></br>
PATCH /imports/10/citizens/4 -> 404</br>
GET /imports/30/citizens -> 404</br>
GET /imports/8/birthdays -> 404</br>
GET /imports/100/towns/stat/percentile/age -> 404</br>
POST /imports -> 201</br></br>

- Second part (Check parser for each field correctness. In each data all except one field are correct. Sometimes data is correct.)</br></br>
	*citizen_id*</br>
POST /imports (same citizen_id in data) -> 400</br>
POST /imports (citizen_id  = -10) -> 400</br>
POST /imports (citizen_id  = ‘18’) -> 400</br>
POST /imports (citizen_id = 0) -> 201</br>
POST /imports (citizen_id = 120) -> 201</br></br>
	*town*</br>
POST /imports (town = ‘’) -> 400</br>
POST /imports (town = ‘__’) -> 400</br>
POST /imports (town = 100) -> 400</br>
POST /imports (town length = 270) -> 400</br>
POST /imports (town = ‘Moscow’) -> 201</br>
POST /imports (town = ‘Москва’) -> 201</br></br>
	*street*</br>
POST /imports (street = ‘’) -> 400</br>
POST /imports (street = ‘_+’) -> 400</br>
POST /imports (street = 78) -> 400</br>
POST /imports (street length = 257) -> 400</br>
POST /imports (street = ‘Заборная’) -> 201</br></br>
	*building*</br>
POST /imports (building = ‘’) -> 400</br>
POST /imports (building = ‘+-=’) -> 400</br>
POST /imports (building = -1) -> 400</br>
POST /imports (building length = 299) -> 400</br>
POST /imports (building = ‘39’) -> 201</br></br>
	*apartment*</br>
POST /imports (apartment  = -190) -> 400</br>
POST /imports (apartment  = ‘128’) -> 400</br>
POST /imports (apartment  = 128) -> 201</br></br>
	*name*</br>
POST /imports (name = ‘’) -> 400</br>
POST /imports (name = 119) -> 400</br>
POST /imports (name length = 299) -> 400</br>
POST /imports (name = ‘++1’) -> 201</br></br>
	*birth_date*</br>
POST /imports (birth_date = ‘’) -> 400</br>
POST /imports (birth_date = 119) -> 400</br>
POST /imports (birth_date = ‘30.02.1901’) -> 400</br>
POST /imports (birth_date = ‘1986.26.12’) -> 400</br>
POST /imports (birth_date = ‘20-08-2019’) -> 400</br>
POST /imports (birth_date = ‘20.12.2019’) -> 400</br>
POST /imports (birth_date = ‘20.08.2019’) -> 201</br>
	*gender*</br>
POST /imports (gender = ‘’) -> 400</br>
POST /imports (gender = 0) -> 400</br>
POST /imports (gender = ‘Male’) -> 400</br>
POST /imports (gender = ‘fefemale’) -> 400</br>
POST /imports (gender = ‘male’) -> 201</br></br>
	*relatives*</br>
POST /imports (relatives = ‘’) -> 400</br>
POST /imports (relatives = [1,1,2]) -> 400</br>
POST /imports (relatives = [1,2]) -> 201</br></br>

- Third part (Check parser another step)</br></br>
POST /imports (two same fields, but one not included) -> 201</br>
POST /imports ( < 9 fields) -> 400</br>
POST /imports ( > 9 fields) -> 400</br>
POST /imports ( > 9 fields, but unique only 9) -> 400</br>
POST /imports (citizens not in data) -> 400</br>
PATCH /import/0/citizens/5 (try to change citizen_id) -> 400
