if [ -d "venv_todo" ]
then 
    . venv_todo/bin/activate
else
    python3 -m venv venv_todo
    . venv_todo/bin/activate
    pip install -r requirements.txt
fi