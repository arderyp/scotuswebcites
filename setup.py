#!/usr/bin/env python

import os
import sys
import random
import string
from getpass import getpass, getuser


proceed = raw_input('\n\nHave you already installed and set up mysql on this machine server, and is it running? ')
if proceed not in ['yes', 'y']:
    print('Please take care of that and then run this script again.\n\n')
    sys.exit()

print('\n\nInstalling application requirements...')

try:
    os.system('pip install -r requirements.txt')
except:
    print('Something went wrong.')
    sys.exit()

port = 3306
host = 'localhost'
root_password = getpass('\n\nPlease enter your mysql root user password (this will not be saved '
                        'or stored anywhere), then hit enter: ')

try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'scotus.settings'
    import MySQLdb
    from django.contrib.auth.models import User
    database_connection = db = MySQLdb.connect(host=host, port=port, user='root', passwd=root_password)
    cursor = database_connection.cursor()
except MySQLdb.OperationalError:
    print('ERROR: Could not connect as user root on localhost via port 3306 with '
          'provided password.  Please try again.\n\n')
    sys.exit()

password = getpass("Please enter the new MySQL password to be used for this application's user: ")

application = 'scotuswebcites'
create_database = 'CREATE DATABASE %s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci' % application
create_user = "CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (application, host, password)
grant_privileges = "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s'" % (application, application, host)

try:
    cursor.execute(create_database)
    cursor.execute(create_user)
    cursor.execute(grant_privileges)
except MySQLdb.OperationalError:
    print('ERROR: failed to set up user and database.')
    sys.exit()

print('Created new %s database accessible via full privileges to new %s user using'
      'your provided password' % (application, application))

settings = 'scotus/settings.py'

if os.path.isfile(settings):
    os.remove(settings)

email = raw_input('\n\nPlease enter your email address: ')
enable_perma = raw_input('Do you want to enable Perma.cc archiving? ')

if enable_perma in ['yes', 'y']:
    api_key = raw_input('Please enter your Perma.cc API key: ')
else:
    print('Disabling Perma.cc.  You can always manually enable it later via %s' % settings)

with open('%s.dist' % settings, 'r') as dist:
    with open(settings, 'w') as output:
        for line in dist:
            if 'MYSQL_PASSWORD' in line:
                line = line.replace('MYSQL_PASSWORD', password)
            elif 'YOUR_CONTACT_EMAIL' in line:
                line = line.replace('YOUR_CONTACT_EMAIL', email)
            elif '#ENABLE_PERMA_CC' in line and enable_perma:
                line = line.replace('False', 'True')
            elif 'PERMA_CC_API_KEY' in line and api_key:
                line = line.replace('PERMA_CC_API_KEY', api_key)
            output.write(line)

print('Created %s file with your new credentials.\n\n' % settings)

try:
    print('Initializing database...\n')
    os.system('./manage.py makemigrations && ./manage.py migrate')
    print("\nSuccessfully initiated the database.\n\n")
except:
    print('\nERROR: failed to initialize database\n\n')

unique = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(5))
django_user = ''.join([getuser(), unique])
django_password = getpass('We are almost done! This application uses a single user account to verify citations. '
                          'Your user name is "%s".  Now you need to come up with a password. If you can remember '
                          'it, it is a bad password. So think of something random, long, and complex, then write '
                          'it down on a piece of paper along with your username quoted above.  You will need to '
                          'type/paste it below twice to confirm it. When you are done, store the piece of paper '
                          'somewhere safe. Please enter the password: ' % django_user)
verify = getpass('Please enter the password again: ')

while django_password != verify:
    django_password = getpass("\n\nThe passwords did not match.  Hopefully this means it is complicated!\n"
                              "Let's try this again.  Please enter the password: ")
    verify = getpass('Please enter the password again: ')

User.objects.create_user(username=django_user, email=email, password=django_password)

print('\n\nAll done!\n\n')
