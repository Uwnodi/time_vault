@echo off
set versionnum=Default
echo Enter version number: 
set /p versionnum=
"./venv/Scripts/python" -m nuitka --standalone --onefile --output-dir "time_vault_exe" time_vault.py --windows-product-version %versionnum% --windows-company-name MxZ