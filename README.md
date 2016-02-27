# United States Supreme Court 
###### web citation discovery, presentation, and validation

#### Setup
Out of the box, this application depends on a mysql backend, and the instructions below cater to that dependency.  You can easily use another database backend, see the [Django documentation](https://docs.djangoproject.com/en/1.8/ref/settings/#databases) for instructions. Likewise, to run the application in production, you should also install and configure a web server, such a [nginx](http://nginx.com/) or [apache](https://httpd.apache.org/).  Lastly, if you are installing this application on a server or VM where other websties, webapplications, or processes unrelated to this project are running, you should consider using [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) 

Once mysql is installed and configured with a root user account, move into the directory where you want to store this application and then run the following:
```
git clone git@github.com:arderyp/scotuswebcites.io.git
cd scotuswebcites.io
./setup.py
``` 

To run the opinion discovery and web citation process, you can manually run the following from within the ```scotus/``` directory:  

```
./manage.py discover
```  

However, it is more practical to have this process run automatically in your server's crontab.  If you installed this application in your home directory on a unix OS, and your user name is 'abc', you could simply add the following to your crontab: ```/home/abc/scotus/manage.py discover```.  If you are using virtualenv/virtualenvwrapper, you can use the run the following from the ```scotus/``` directory:  

```
cp scripts/discover.sh.dist scripts/discover.sh
chmod 755 scripts/discover.sh
```  

See the ```discover.sh``` file that you created for further instructions on using the script.  For tips on setting up a unix cronjob, see [this documentation](http://www.wikihow.com/Set-up-a-Crontab-File-on-Linux).  

Finally, you have the option to set up on-demand capturing via either webcitation.org, perma.cc, or both!  What this means is that, once a user validates a citation, if that citation is a non-404, the application will utilize the webcitations.org/perma.cc APIs to grab an immediate capture of the citation.  The links for these captures will be stored in your datbase and presented in the applications ```/citations/``` view.  To utlize the webcitation.org API, all you will need is a valid email address to get notifications.  To utilize the perma.cc API, you will need to set up a perma.cc account.  Once that is set up, you will need to log in, click your name in the upper right hand corner, click tools, then click "Generate API key".  You can activate the webcitations.org and/or perma.cc on-demand archiving by again editing the settings.py file.  From within the scotus/ directory, run ```vi scotus/settings.py``` and find the following block:  

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

Simply change ```False``` to ```True``` for the services that you want to enable.  If you'd like to enable perma.cc, you will need to put the API key that you generated in place of ```PERMA_CC_API_KEY```.  Lastly, all discovered opinion PDFs will be saved to your local ```scotus/docs/pdfs``` directory for safe keeping.  That's it!  If you encounter any bugs or experience issues setting up the application, feel free to open a ticket on this repository for further assistance.  


#### Overview Screen
![](https://github.com/orangeoval/scotus/blob/master/static/img/screen_shots/overview_screen.png)

#### Citations Screen
![](https://github.com/orangeoval/scotus/blob/master/static/img/screen_shots/citations_screen.png)

#### Opinions Screen
![](https://github.com/orangeoval/scotus/blob/master/static/img/screen_shots/opinions_screen.png)

#### Justices Screen
![](https://github.com/orangeoval/scotus/blob/master/static/img/screen_shots/justices_screen.png)
