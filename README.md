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
`gunicorn -w 4 -b 0.0.0.0:8080 main:app`</br>


**Tests**
All tests were divided into 3 parts.
1. Check correctness of server when database doesn't exist.
2. Check correctness of my_parser functionality on broken data.
3. Check correctness of my_parser on data presentation.

The structure of test examples here is:
`METHOD | url | [(what's wrong, what' testing)] | -> status_code`

Test examples:
- First part (Checking statuses when nothing in database. All data and URLs are correct.)
	PATCH /imports/10/citizens/4 -> 404
	GET /imports/30/citizens -> 404
	GET /imports/8/birthdays -> 404
	GET /imports/100/towns/stat/percentile/age -> 404
	POST /imports -> 201

- Second part (Check parser for each field correctness. In each data all except one field are correct. Sometimes data is correct.)
	*citizen_id*
POST /imports (same citizen_id in data) -> 400
POST /imports (citizen_id  = -10) -> 400
POST /imports (citizen_id  = ‘18’) -> 400
POST /imports (citizen_id = 0) -> 201
POST /imports (citizen_id = 120) -> 201
	*town*
POST /imports (town = ‘’) -> 400
POST /imports (town = ‘__’) -> 400
POST /imports (town = 100) -> 400
POST /imports (town length = 270) -> 400
POST /imports (town = ‘Moscow’) -> 201
POST /imports (town = ‘Москва’) -> 201
	*street*
POST /imports (street = ‘’) -> 400
POST /imports (street = ‘_+’) -> 400
POST /imports (street = 78) -> 400
POST /imports (street length = 257) -> 400
POST /imports (street = ‘Заборная’) -> 201
	*building*
POST /imports (building = ‘’) -> 400
POST /imports (building = ‘+-=’) -> 400
POST /imports (building = -1) -> 400
POST /imports (building length = 299) -> 400
POST /imports (building = ‘39’) -> 201
	*apartment*
POST /imports (apartment  = -190) -> 400
POST /imports (apartment  = ‘128’) -> 400
POST /imports (apartment  = 128) -> 201
	*name*
POST /imports (name = ‘’) -> 400
POST /imports (name = 119) -> 400
POST /imports (name length = 299) -> 400
POST /imports (name = ‘++1’) -> 201
	*birth_date*
POST /imports (birth_date = ‘’) -> 400
POST /imports (birth_date = 119) -> 400
POST /imports (birth_date = ‘30.02.1901’) -> 400
POST /imports (birth_date = ‘1986.26.12’) -> 400
POST /imports (birth_date = ‘20-08-2019’) -> 400
POST /imports (birth_date = ‘20.12.2019’) -> 400
POST /imports (birth_date = ‘20.08.2019’) -> 201
	*gender*
POST /imports (gender = ‘’) -> 400
POST /imports (gender = 0) -> 400
POST /imports (gender = ‘Male’) -> 400
POST /imports (gender = ‘fefemale’) -> 400
POST /imports (gender = ‘male’) -> 201
	*relatives*
POST /imports (relatives = ‘’) -> 400
POST /imports (relatives = [1,1,2]) -> 400
POST /imports (relatives = [1,2]) -> 201

- Third part (Check parser another step)
POST /imports (two same fields, but one not included) -> 201
POST /imports ( < 9 fields) -> 400
POST /imports ( > 9 fields) -> 400
POST /imports ( > 9 fields, but unique only 9) -> 400
POST /imports (citizens not in data) -> 400
