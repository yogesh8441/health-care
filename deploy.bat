@echo off
echo Committing changes to Git...
git commit -m "Ready for Vercel deployment with all panels working"
if %errorlevel% neq 0 (
    echo Commit failed or nothing to commit
    pause
    exit /b %errorlevel%
)

echo.
echo Pushing to GitHub...
git push -u origin main
if %errorlevel% neq 0 (
    echo Push failed
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================
echo SUCCESS! Code pushed to GitHub!
echo ========================================
echo.
echo Next Steps:
echo 1. Go to https://vercel.com/new
echo 2. Import repository: yogesh8441/health-care
echo 3. Set environment variables (see START_HERE.md)
echo 4. Click Deploy!
echo.
echo See START_HERE.md for complete instructions
echo.
pause
