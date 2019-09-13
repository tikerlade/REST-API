# REST-API service for Yandex Backend School

**Installation**

- First of all run this command:</br>
`sudo apt update`</br>
`sudo apt install git python3-venv python-pip`</br>
`git clone https://github.com/tikerlade/REST-API.git`

- Secondly you need to activae virtual environment</br>
`cd REST-API`</br>
`python3 -m venv venv`</br>
`. venv/bin/activate`

- Thirdly you need to change directory and install python packages</br>
`pip install -r pip_requirements.txt`

- Fourthly cleat port and run server</br>
`fuser -k -n tcp 8080`</br>
`gunicorn -w 4 -b 0.0.0.0:8080 main:app`</br></br></br>
