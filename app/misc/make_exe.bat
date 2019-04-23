del /q *.spec *.zip
rd /s /q dist build
C:/Python36-32/Scripts/pyinstaller.exe --onefile -w ../k1921vkx_flasher.py
"C:\Program Files (x86)\7-Zip\7z.exe" a k1921vkx_flasher_v%1_win32.zip dist/k1921vkx_flasher.exe
