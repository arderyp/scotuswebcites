#!/usr/bin/env python

import os
import sys
import time
import random
import string
from getpass import getpass, getuser

def generate_random_alpha_numeric_string(length):
    """Return random alphanumeric string that is 'length' (int) characters long"""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(length))


# Handle requirements
positive = ['yes', 'y']
proceed = raw_input('\n\nHave you already installed pip and set up mysql on this machine, '
                    'and is the latter running right now? ')
if proceed not in positive:
    print('Please take care of that and then run this script again.\n\n')
    sys.exit()
print('\n\nInstalling application requirements...')
try:
    os.system('pip install -r requirements.txt')
except:
    print('Something went wrong.')
    sys.exit()

# Create blank database, application user, and permissions
application = 'scotuswebcites'
port = 3306
host = 'localhost'
root_password = getpass('\n\nPlease enter your mysql root user password (this will not be saved '
                        'or stored anywhere), then hit enter: ')
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'scotus.settings'
    import MySQLdb
    #from django.contrib.auth.models import User
    database_connection = db = MySQLdb.connect(host=host, port=port, user='root', passwd=root_password)
    cursor = database_connection.cursor()
except MySQLdb.OperationalError:
    print('ERROR: Could not connect as user root on localhost via port 3306 with '
          'provided password.  Please try again.\n\n')
    sys.exit()
password = getpass("Please enter the new MySQL password to be used for this application's user: ")
queries = ['CREATE DATABASE %s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci' % application,
           "CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (application, host, password),
           "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s'" % (application, application, host)
           ]
try:
    for query in queries:
        cursor.execute(query)
except MySQLdb.OperationalError:
    print('ERROR: failed to set up user and database.')
    sys.exit()
print('Created new %s database accessible via full privileges to new %s user using '
      'your provided password' % (application, application))

# Determine custom environment settings
settings = 'scotus/settings.py'
email = raw_input('\n\nPlease enter your email address: ')
if raw_input('Is this a production environment? ') in positive:
    is_production = True
    domain = raw_input("Our production domain is scotuswebcites.io, what's yours? ")
else:
    is_production = False
    domain = 'localhost:8000'
if raw_input('Do you want to enable Perma.cc archiving? ') in positive:
    perma_api_key = raw_input('Please enter your Perma.cc API key: ')
    perma_base_folder_id = raw_input('Please enter your Perma.cc base folder ID: ')
else:
    perma_api_key = False
    perma_base_folder_id = False
    print('Disabling Perma.cc.  You can always manually enable it later via %s' % settings)
if raw_input('Would you like to use a gmail account to sent system emails? ') in positive:
    configure_gmail = True
    gmail_address = raw_input("Please enter the gmail address that you'd like to use: ")
    gmail_password = getpass("Please enter the password associated with this account: ")

else:
    configure_gmail = False
    print('Feel free to look at the Django documentation, edit %s, and possibly configure '
          'your server to set up email in for your environment. Bur for the time being, '
          'system emails will not be sent and may cause system errors.')

# Create fresh custom settings.py file
settings = 'scotus/settings.py'
if os.path.isfile(settings):
    os.remove(settings)
with open('%s.dist' % settings, 'r') as dist:
    with open(settings, 'w') as output:
        for line in dist:
            if 'MYSQL_PASSWORD' in line:
                line = line.replace('MYSQL_PASSWORD', password)
            elif 'YOUR_CONTACT_EMAIL' in line:
                line = line.replace('YOUR_CONTACT_EMAIL', email)
            elif 'YOUR_SECRET_KEY' in line:
                line = line.replace('YOUR_SECRET_KEY', generate_random_alpha_numeric_string(75))
            elif 'ALLOWED_HOSTS' in line and domain:
                line = line.replace('[]', "['%s']" % domain)

            if configure_gmail:
                if 'YOUR_GMAIL_ADDRESS' in line:
                    line = line.replace('YOUR_GMAIL_ADDRESS', gmail_address)
                elif 'YOUR_GMAIL_PASSWORD' in line:
                    line = line.replace('YOUR_GMAIL_PASSWORD', gmail_password)

            if perma_api_key:
                if '#ENABLE_PERMA_CC' in line:
                    line = line.replace('False', 'True')
                elif 'PERMA_CC_API_KEY' in line:
                    line = line.replace('PERMA_CC_API_KEY', perma_api_key)
                elif 'PERMA_CC_BASE_FOLDER_ID' in line:
                    line = line.replace('PERMA_CC_BASE_FOLDER_ID', perma_base_folder_id)

            if is_production and 'DEBUG' in line:
                line = line.replace('True', 'False')

            output.write(line)
print('Created %s file with your new credentials.\n\n' % settings)

# Initialize the database schema
try:
    print('Initializing database...\n')
    os.system('./manage.py makemigrations && ./manage.py migrate')
    print("\nSuccessfully initiated the database.\n\n")
except:
    print('\nERROR: failed to initialize database\n\n')
    sys.exit()

# Create django account with custom credentials
django_user = ''.join([getuser(), generate_random_alpha_numeric_string(5)])
django_password = getpass('We are almost done! This application uses a single user account to verify citations. '
                          'Your user name is "%s".  Now you need to come up with a password. If you can remember '
                          'it, it is a bad password. So think of something random, long, and complex, then write '
                          'it down on a piece of paper along with your username quoted above.  You will need to '
                          'type/paste it below twice to confirm it. When you are done, store the piece of paper '
                          'somewhere safe. Please enter the password: ' % django_user)
time.sleep(2)
verify = getpass('\nPlease enter the password again: ')
time.sleep(2)
while django_password != verify:
    django_password = getpass("\n\nThe passwords did not match.  Hopefully this means it is complicated!\n"
                              "Let's try this again.  Please enter the password: ")
    verify = getpass('\nPlease enter the password again: ')

from django.contrib.auth.models import User
user = User.objects.create_user(username=django_user, email=email, password=django_password)

print('\n\nAll done!\n\n')
