to start:
cd /home/stud/myflaskproj
source venv/bin/activate
python3 pythonserver.py

to start on pi:
cd /home/stud/Projekt
source projektvenv/bin/activate
cd projekt-3-gruppe-14/Kontrolenhed
python3 pythonserver.py


if you break the venv the venv:
cd /home/stud/myflaskproj
python3 -m venv projektvenv --system-site-packages
source projektvenv/bin/activate
    and maybe
pip install flask-cors
pip install flask-login
