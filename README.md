mkdir pandash
cd pandash

# debian系
    sudo apt-get install python-dev default-libmysqlclient-dev
    sudo apt-get install python3-dev
 
# rhel系
    sudo yum install python-devel mysql-devel
    sudo yum install python3-devel

sudo yum install git-all

python3 -m venv pandash

source pandash/bin/activate

pip install --upgrade pip
<!-- pip install flask, sqlalchemy, mysqlclient -->
pip install -r requirements.txt