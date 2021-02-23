import yaml
import requests
import os
import time

def updateData():
    with open('config.yaml') as configfile:
    
        config = yaml.load(configfile, Loader=yaml.FullLoader)

        for country in config:

            for key in config[country]:  
                filename = './data/' + country + '/' + key + '.csv'
                url = config[country][key]

                if (not os.path.isfile(filename)) or (time.time() - os.stat(filename).st_mtime > 24*60*60):
                    print('Downloading', filename, '...')

                    print(url)

                    r = requests.get(url)

                    with open(filename,'wb') as output_file:
                        output_file.write(r.content)

                    print('Done!')
