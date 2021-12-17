# How to Set up PandAsh

## 1.Make a Folder for PandAsh
```
mkdir pandash
cd pandash
```

## 2.Install Python and Git
### Debian系
    sudo apt-get install python-dev default-libmysqlclient-dev
    sudo apt-get install python3-dev
 
### RHEL系
    sudo yum install python-devel mysql-devel
    sudo yum install python3-devel

```
sudo yum install git-all
```

## 3. Create Virtual Environments
```
python3 -m venv venv

source venv/bin/activate
```
## 4. Install Nessesary Libraries in Virtual Environments
```
pip install --upgrade pip
<!-- pip install flask, sqlalchemy, mysqlclient -->

git clone https://github.com/kyoto-u/pandash.git
cd pandash
pip install -r requirements.txt

cd ..
git clone https://github.com/MONTplusa/python-cas-client.git

cd python-cas-client
pip install .
```
