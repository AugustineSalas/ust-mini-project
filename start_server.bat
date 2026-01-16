@echo off
echo Installing dependencies if missing...
pip install -r requirements.txt
echo.
echo Starting Inventory Management System...
echo Access the docs at: http://127.0.0.1:8000/docs
echo.
python -m uvicorn main:app --reload
pause
