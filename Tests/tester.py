import os
import requests


def test_server(path='Test_files', base_url='http://0.0.0.0:8080'):
    '''Run the tests from path.'''

    try:
        for i in range(len(os.listdir(path))):
            with open(path + '/' + str(i) + '.txt', 'r') as f:
                url = f.readline()[:-1]
                code = int(f.readline()[:-1])
                data = f.readline()[:-1]
                answer = f.readline()

            URL = base_url + url

            if url == '/imports' or url.count('/') == 4:
                r = requests.post(URL, data=data)
            else:
                r = requests.get(URL)

            assert(r.status_code == code)

        return 'All tests have been passed !'
    except requests.exceptions.ConnectionError:
        return 'You have not run the server !'
    except AssertionError:
        return 'Some tests have not passed :('


if __name__ == '__main__':
    print(test_server())
