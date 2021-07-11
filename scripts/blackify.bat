pushd .
cd ..
call venv\Scripts\activate.bat
python -m black -l 192 longtaskrunnin test_longtaskrunnin
call deactivate
popd
