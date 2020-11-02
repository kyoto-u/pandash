mkdir pandash
cd pandash

# debian系
    sudo apt-get install python-dev default-libmysqlclient-dev
    sudo apt-get install python3-dev
 
# rhel系
    sudo yum install python-devel mysql-devel
    sudo yum install python3-devel

sudo yum install git-all

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip
<!-- pip install flask, sqlalchemy, mysqlclient -->

git clone https://github.com/kyoto-u/pandash.git
cd pandash
pip install -r requirements.txt

cd ..
git clone https://github.com/discogs/python-cas-client

cd python-cas-client
pip install python-cas-client
