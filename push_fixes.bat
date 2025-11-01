@echo off
echo Pushing fixes to GitHub...
git commit -m "Fix Python version for Vercel"
git push origin main
echo.
echo Done! Vercel will auto-redeploy now.
pause
