rmdir /S /Q venv
C:"\Program Files\Python310\python.exe" -m venv --clear venv
call venv\Scripts\activate.bat 
python -m pip install --no-deps --upgrade pip
python -m pip install -U setuptools
python -m pip install -U -r requirements.txt
deactivate
