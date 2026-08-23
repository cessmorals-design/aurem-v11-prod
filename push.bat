@echo off
echo Pushing to GitHub...
git init
git add.
git commit -m "V11 PROD"
git branch -M main
set /p USERNAME="Enter GitHub username: "
git remote add origin https://github.com/%USERNAME%/aurem-v11-prod.git
git push -u origin main
pause
