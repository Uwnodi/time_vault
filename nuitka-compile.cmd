@echo off
set versionnum=Default
echo Enter version number: 
set /p versionnum=
"./venv/Scripts/python" -m nuitka time_vault.py --standalone --onefile --output-dir "time_vault_exe" -o time_vault_exe/time_vault_v%versionnum%.exe --windows-product-version %versionnum% --windows-company-name MxZ