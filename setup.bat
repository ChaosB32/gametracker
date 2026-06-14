@echo off
title GameTracker v2 - Setup
cd /d %~dp0
echo.
echo  ==========================================
echo   GameTracker v2 - Configuracao inicial
echo  ==========================================
echo.

echo [1/5] Instalando dependencias...
pip install -r requirements.txt
echo.

echo [2/5] Criando migrations...
python manage.py makemigrations games
echo.

echo [3/5] Aplicando migrations...
python manage.py migrate
echo.

echo [4/5] Populando banco de dados...
python manage.py seed_data
echo.

echo [5/5] Iniciando servidor...
echo.
echo  Acesse: http://localhost:8000
echo  Conta de teste: jogador / gametracker123
echo.
python manage.py runserver
pause
