#!/bin/bash
echo ""
echo " ======================================================"
echo "  TRIBUNAL IA PORTUGAL — Interface Web"
echo " ======================================================"
echo ""
echo " A iniciar a interface no browser..."
echo " Para parar: Ctrl+C"
echo ""
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
