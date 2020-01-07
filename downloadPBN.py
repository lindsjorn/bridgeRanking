import requests
from bs4 import BeautifulSoup



def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = requests.get(url)
        # write to file
        file.write(response.content)

files_url = r'http://bridge.no/var/ruter/html/0179/'

soup = BeautifulSoup(requests.get(files_url).text)

filelist = [x['href'] for x in soup.find_all('a', href=True) if x['href'].endswith('pbn')]

for fileN in filelist:
    download(files_url + fileN, r'C:\Users\u35249\git\bridgeRanking\Spiren' + '\\' + fileN) 
    
