# Optimization-of-IEDR-for-Feature-Extraction-in-Opinion-Mining

This project is the implementation of the feature extraction approach described in the paper [An effective approach of intrinsic and extrinsic domain relevance technique for feature extraction in opinion mining](https://ieeexplore.ieee.org/document/7760040). A dummy dataset is included in this project for the test purpose.

## Platform 
#### Language
* [Python3.6.9](https://www.python.org/downloads/release/python-369/)
#### Framework / Library 
* [PyQt5](https://pypi.org/project/PyQt5/)
* [SQLAlchemy](sqlalchemy.org)
* [PyMySQL](https://github.com/PyMySQL/PyMySQL) 
* [NLTK](https://www.nltk.org/)
* [PyStanfordDependencies](https://pypi.org/project/PyStanfordDependencies/) 
* [JPype1](https://pypi.org/project/JPype1/)
#### Database Management System
* [MySQL](https://dev.mysql.com/)
## Installation
#### Prerequisite
The installation has been tested in [Ubuntu 18.04.4 LTS](https://ubuntu.com/). So Ubuntu is prerequisite as operating system. The whole installation process is an bit clumsy though. Stay with me:
#### Downloading & installing parser
* From [here](https://nlp.stanford.edu/software/lex-parser.shtml#Download) download [The Stanford Parser (version 3.5.2)]( https://nlp.stanford.edu/software/stanford-parser-full-2015-04-20.zip)
* Extract the downloaded `.zip` file in `/home/your_user_name` directory
* Go to the extracted directory & again extract `stanford-parser-3.5.2-models.jar` file there 

#### Installing required libraries & packages

* Open terminal (```Ctrl + Alt + T```) and use the following commands:
```bash
cd ~
sudo apt-get install python-pip python3-pip python-dev python3-dev g++ libblas-dev liblapack-dev libatlas-base-dev gfortran libfreetype6-dev libxft-dev build-essential libqt4-dev pyqt5-dev-tools qttools5-dev-tools python3-pyqt5 default-jdk mysql-server
```
* After that enter the following command:
```bash
gedit ~/.bashrc
```
* In the editor add the following line at the end of the file: 
```bash
export JAVA_HOME="/usr/lib/jvm/openjdk-11"
```
* Then save the `.bashrc` file with new changes and close the editor

#### Installing Virtual Environment & Activating
```bash
cd ~
sudo pip3 install virtualenv
export WORKON_HOME=$HOME/.virtualenvs
virtualenv -p /usr/bin/python3 TestEnv
source TestEnv/bin/activate
```

#### Installing Python Libraries
```bash
pip3 install SQLAlchemy PyMySQL nltk PyStanfordDependencies JPype1 
```

Additionally need to download `nltk` data:
```bash
python3
```
Then on the python console use the following code snippet to download nltk data:
```python
>>> import nltk
>>> nltk.download('punkt')
>>> exit()
``` 

#### Configuring DBMS
For the following command use current user's password first, then for mysql password just hit enter:
```bash
sudo mysql -u root -p 
```
```
use mysql;
UPDATE user SET plugin = 'mysql_native_password' WHERE User = 'root';
FLUSH PRIVILEGES;
CREATE DATABASE IEDR;
exit
```

## Usage

* First copy the `Dataset` folder included with the project to a local directory ( preferably in `/home/your_user_name/` )

* Go to the saved directory of the download source:
```bash
# Example
cd ~/Optimization-of-IEDR-for-Feature-Extraction-in-Opinion-Mining/
```

* Activate the virtual environment if not activated already:
```bash
source ~/TestEnv/bin/activate
```

* Run `script.py`:
```bash
python3 script.py
```

* Set corpus as followings from `Dataset` folder:
<img src="https://user-images.githubusercontent.com/14239584/76014727-4cda2100-5f44-11ea-9831-8f4fa3009f04.png" align="middle" height="295" width="470" >

* Extract candidate feature for both domain dependent & domain independent corpus. This may take a bit time:
<img src="https://user-images.githubusercontent.com/14239584/76014729-4d72b780-5f44-11ea-9fae-2aeddf263c05.png" align="middle" height="295" width="470" >

* Calculate domain relevance for both domain dependent & domain independent corpus. At the beginning of the process (calculating domain relevance of dependent corpus) you would like to clear the previous data from database:
<img src="https://user-images.githubusercontent.com/14239584/76014720-4b105d80-5f44-11ea-8f6e-1e3bb264bd57.jpg" align="middle" height="295" width="950" >

* Now time to extract actual features. Set threshold value and extract:
<img src="https://user-images.githubusercontent.com/14239584/76014737-4ea3e480-5f44-11ea-96d4-c76f58aed460.jpg" align="middle" height="295" width="950" >
