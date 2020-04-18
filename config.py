import configparser
config = configparser.ConfigParser()
config.read('./config.ini')
config.get('DATABASE', 'HOST')
HOST=config['DATABASE']['HOST']
USER=config['DATABASE']['USERNAME']
PASS=config['DATABASE']['PASSWORD']
DATABASE=config['DATABASE']['DB']
SECRET_KEY=config["KEY"]["SECRET"]
API_KEY=config["KEY"]["API"]