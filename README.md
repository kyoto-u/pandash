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
git clone https://github.com/discogs/python-cas-client

cd python-cas-client
pip install .
```

In addition, it is necessary to install MySQL and prepare a database named "pandash".

## 5.Modify python-cas-client
Python-cas-client as it is does not work.
Following are changes in python-cas-client.
```
in /cas_client/cas_client.py:

L.389          return url
L.390
L.391      def _get_proxy_validate_url(self, ticket):
L.392 -        template = '{validate_url}{auth_prefix}/proxy?'
L.392 +        template = '{validate_url}{auth_prefix}/proxyValidate?'
L.393          template += 'ticket={ticket}&service={proxy_callback}'
L.394          url = template.format(
L.395              auth_prefix=self.auth_prefix,
L.396              proxy_callback=self.proxy_callback,
L.397 -            validate=self.validate_url,
L.397 +            validate_url=self.validate_url,
L.398              ticket=ticket,
L.399              )
L.400          return url

L.409              ticket=ticket,
L.410              )
L.411          if self.proxy_url:
L.412 -            url = '{url}&pgtUrl={proxy_url}'.format(url, self.proxy_url)
L.412 +            url = f'{url}&pgtUrl={self.proxy_url}'
L.413          return url

     def _perform_cas_call(self, url, ticket, headers=None):
```
Afterwards, at pandash/python-cas-client in virtual environments
```
pip install .
```

## 6.Create Files Named "users.txt","users_oa.txt" at pandash/pandash

Currently, students who can use the service are restricted by email address.
In users.txt, enter **email address** of users whom you allow to use pandash.

In users_oa.txt, enter **user_id (in students table)** of the users whom you allow to use OA_tool.

## 7.Run run.py

Issue server certificates
When doing this on a production server, the following points should be noted

- If you use CASProxy authentication, you need to issue a server certificate and register this information with the CAS server and PandA.
- The internal errors that occur can be checked in DEBUG_LOG.log

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
