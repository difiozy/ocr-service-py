set _pwd=%cd%
echo
echo %_pwd%
set _res=%_pwd:~-7%

echo %_res%

if %_pwd:~-7% == scripts dir