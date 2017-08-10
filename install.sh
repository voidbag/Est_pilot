Distribution=$(lsb_release -i | cut -f 2-)

#echo $Distribution
if [ $Distribution == "CentOS" ]
then
	sudo yum install python
	sudo yum install python-pip
	sudo yum install python3
	sudo yum install python3-pip
elif [ $Distribution == "Ubuntu" ]
then
	sudo apt-get install python3
	sudo apt-get install python
	sudo apt-get install python3-pip
	sudo apt-get install python-pip
else
	echo 'Unsupported OS:'$Distribution
	exit 1
fi

echo 'installing virtualenv..'
sudo pip install virtualenv
virtualenv -p python3 venv
source venv/bin/activate

echo 'installing pybuilder..'
pip install unittest-xml-reporting #TODO problem
pip install --upgrade pybuilder

