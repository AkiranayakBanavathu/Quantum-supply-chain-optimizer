@echo off
if not exist venv (
  echo Virtual environment not found.
  echo Run the setup commands in README.md first.
  pause
  exit /b 1
)
call venv\Scripts\activate
python app.py
pause
