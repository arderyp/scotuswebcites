# Supreme Court of the United States : opinions
###### web citation discovery, presentation, and validation

#### Setup
Out of the box, this application depends on a mysql backend, and the instructions below cater to that dependency.
You can easily use another database backend, see the
[Django documentation](https://docs.djangoproject.com/en/1.8/ref/settings/#databases) for instructions.
Likewise, to run the application in production, you should also install and configure a web server, such a
[nginx](http://nginx.com/) or [apache](https://httpd.apache.org/).  Lastly, if you are installing this application
on a server or VM where other websties, webapplications, or processes unrelated to this project are running, you
should consider using [virtualenv](https://pypi.python.org/pypi/virtualenv) and
[virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper)

To follow the directions below, you will also need to install [pip](http://pypi.python.org/pypi/pip), which is
used to fetch the application requirements. Once that's taken care of, an mysql is installed and configured with
a root user account, move into the directory where you want to store this application and then run the following:
```
git clone git@github.com:arderyp/scotuswebcites.git
cd scotuswebcites
./setup.py
``` 

To run the opinion and web citation discovery, you can manually run the following from within the ```scotus/```
directory:

```
./manage.py discover
```  

However, it is more practical to have this process run automatically in your server's crontab.  If you installed
this application in your home directory on a unix OS, and your user name is 'abc', you could simply add the
following to your crontab: ```/home/abc/scotus/manage.py discover```.  If you are using virtualenv/virtualenvwrapper,
you can use the run the following from the ```scotus/``` directory:

```
cp scripts/discover.sh.dist scripts/discover.sh
chmod 755 scripts/discover.sh
```  

See the ```discover.sh``` file that you created for further instructions on using the script.  For tips on setting
up a unix cronjob, see [this documentation](http://www.wikihow.com/Set-up-a-Crontab-File-on-Linux).

Finally, you have the option to set up on-demand capturing via either webcitation.org, perma.cc, or both!  What
this means is that, once a user validates a citation, if that citation is a non-404, the application will utilize
the webcitations.org/perma.cc APIs to grab an immediate capture of the citation.  The links for these captures will
be stored in your datbase and presented in the applications ```/citations/``` view.  To utlize the webcitation.org
API, all you will need is a valid email address to get notifications.  To utilize the perma.cc API, you will need to
set up a perma.cc account.  Once that is set up, you will need to log in, click your name in the upper right hand
corner, click tools, then click "Generate API key".  You should then contact perma.cc and ask them to cerate a shared
folder for you to use with this application, then make note of the folder_id.  You can activate the webcitations.org
and/or perma.cc on-demand archiving by again editing the settings.py file.  From within the scotus/ directory,
run ```vi scotus/settings.py``` and find the following block:

```
WEBCITE = {
    'enabled': False,
    'api_query': 'http://www.webcitation.org/archive?returnxml=true&url=%s&email=%s',
}
PERMA = {
    'enabled': False,
    'archive_base': 'https://perma.cc',
    'api_key': 'PERMA_CC_API_KEY',
    'api_query': 'https://api.perma.cc/v1/archives/?api_key=%s'
}
```  

Simply change ```False``` to ```True``` for the services that you want to enable.  If you'd like to enable perma.cc,
you will need to put the API key that you generated in place of ```PERMA_CC_API_KEY```, and your shared folder_id
in place of 'PERMA_CC_SHARED_FOLDER_ID'. If you don't know what these are, contact someone at perma.cc for assistance.

Whether or not you have enabled archiving, you will need to validate citatons that are dicovered.  The scraper and
the Opinion PDFs are imperfect, which means that some web citations are scraped improperly.  Consequently,
newly discovered citations need to be validated by a human to ensure that they are accurate.  Most seem to be accurate
these days.  Once the citation is verified, if you have archiving enabled, the archives will be automatically generated
and integrated.  If you have enabled the gmail notification system via ```setup.py```, you can now notify your
subscribers that you have verified newly discovered citations with:

```
manage.py notifysubscribers
```

Again, it's best to let your system's cron handle this for you on a regular basis.  You could stagger the
discovery process to run every other hour, and have the notification process run every hour in between, which
will give you (the admin) an hour to verify newly discovered citations before your system notifies your
subscribers of the validations.  This a long enough period to let you get your work done, but hopeuflly a
short enough period that the cited website has not changed since we discovered it.


Lastly, all discovered opinion PDFs will be saved to your local
```scotus/docs/pdfs``` directory for safe keeping.  All discovery and notification logs are written to
```logs/```, and each day gets it's  own log file.  That's it!  If you encounter any bugs or experience issues
setting up the application, feel free to open a ticket on this repository for further assistance.


#### Overview Screen
![](https://github.com/orangeoval/scotus/blob/master/static/img/screen_shots/overview_screen.png)

#### Citations Screen
![](https://github.com/orangeoval/scotus/blob/master/static/img/screen_shots/citations_screen.png)

#### Opinions Screen
![](https://github.com/orangeoval/scotus/blob/master/static/img/screen_shots/opinions_screen.png)

#### Justices Screen
![](https://github.com/orangeoval/scotus/blob/master/static/img/screen_shots/justices_screen.png)
