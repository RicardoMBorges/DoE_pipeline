@echo off
setlocal

rem Get the directory path where the batch file is located
set "script_dir=%~dp0"

rem Check if the virtual environment already exists in the script's directory
if exist "%script_dir%\DoE_pipeline\Scripts\activate" (
    echo DoE_pipeline already exists. Activating...
    call "%script_dir%\DoE_pipeline\Scripts\activate"
) else (
    echo Creating virtual environment in "%script_dir%\DoE_pipeline"...
    py -3.11 -m venv "%script_dir%\DoE_pipeline"
    call "%script_dir%\DoE_pipeline\Scripts\activate"

    echo Installing the requirements...
    call "%script_dir%\DoE_pipeline\Scripts\python.exe" -m pip install -r requirements.txt
    
    echo Installing Jupyter Notebook...
    call "%script_dir%\DoE_pipeline\Scripts\python.exe" -m pip install jupyter notebook==6.5.2
    call "%script_dir%\DoE_pipeline\Scripts\python.exe" -m pip install traitlets==5.9.0
)

rem Start Jupyter Notebook
call jupyter notebook 

pause
