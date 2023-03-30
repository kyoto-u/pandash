# How to Set up PandAsh

## 1.Make a Folder for PandAsh
```
mkdir pandash
cd pandash
```

## 2.Install Python and Git
### Debian
    sudo apt-get install python-dev default-libmysqlclient-dev
    sudo apt-get install python3-dev
 
### RHEL
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

In addition, it is necessary to install MySQL and prepare a database named "pandash".

## 5.Create Files Named "users.txt", "users_oa.txt", "year_semester.json" at pandash/pandash

Currently, students who can use the service are restricted by email address.
In users.txt, enter **email address** of users whom you allow to use pandash.

In users_oa.txt, enter **user_id (in students table)** of the users whom you allow to use OA_tool.

In year_semester.json, enter the following contents.
```
{"valid_year_semester": [10009], "show_year_semester": [10009]}
```

## 6.Run run.py

When doing this on a production server, the following points should be noted

- If you use CAS proxy authentication, you need to issue a server certificate and register this information with the CAS server and PandA.
- If only you use PandAsh, you can use PandAsh without CAS proxy authentication using without_CAS branch. Some additional settings are needed and you need to install library named "Beautiful Soup". See settings_sample.py in without_CAS branch for detail.
- The internal errors that occur can be checked in DEBUG_LOG.log
- when you run the app for the first time, you must update "valid_year_semester" and "show_year_semester". See "Maintenance for New Semester" below for detailed instructions.

# How to Maintain PandA

## Maintenance for New Semester

PandAsh needs to be maintained for new semester.
The procedure is as follows:

1. Log in with OA account
2. Access /manage/oa in Browser
3. Click the button labeled "year_semester の数値を更新する"

## Update Server Certificate

If PandAsh is run for a long period of time, the certificate may expire.
Note that when updating PandAsh's server certificate, it is necessary to update the information about PandAsh's server certificate around PandA's CAS authentication as well.
(in PandA, information about PandAsh's server certificate is nessesary to allow proxy authentication only to PandAsh)

## Check Inquiries

PandAsh implements its own form for inquiries. You can check the received inquiries from /manage/oa in a OA account.
You can reply to inquiries, but note that you cannot undo what you have sent once you have sent it.
