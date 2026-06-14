@echo off
title GameTracker v3
cd /d %~dp0
call venv312\Scripts\activate
echo.
echo  Acesse: http://localhost:8000
echo  Conta de teste: jogador / gametracker123
echo.
python manage.py runserver
pause
