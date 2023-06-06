call C:\Users\Jaron\miniconda3\Scripts\activate.bat
call conda activate squashutrechtautomatisch

for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (set mydate=%%d-%%b-%%c)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set mytime=%%a-%%b)
python -u D:\safe\Projects\squashutrechtautomatisch\main.py > logs\output_%mydate%_%mytime%.txt 2>&1
