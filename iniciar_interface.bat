@echo off
echo.
echo  ======================================================
echo   TRIBUNAL IA PORTUGAL — Interface Web
echo  ======================================================
echo.
echo  A iniciar a interface no browser...
echo  Para parar: Ctrl+C nesta janela
echo.
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
