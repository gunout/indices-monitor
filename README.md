# indices-monitor
📊 Trading Monitor - Application de Surveillance des Marchés Financiers on localhost:5001 .

📝 Description

Trading Monitor est une application web de surveillance des marchés financiers en temps réel, développée avec Flask et yfinance. Elle permet de suivre plus de 45 indices, actions, matières premières, devises et cryptomonnaies à travers une interface moderne et intuitive.

L'application intègre des indicateurs techniques avancés (RSI, MACD, SMA, Bollinger Bands, Stochastic, Volatilité) et génère des signaux d'achat/vente basés sur une analyse multi-indicateurs, le tout agrémenté d'une interface sombre de type "salle de marché".

✨ Fonctionnalités
📈 Surveillance multi-actifs

    12 catégories d'actifs : US Principaux, US Mid & Small, Europe, Asie, Amériques, Taux Obligataires, Volatilité, Devises, Matières Premières, Crypto, Marchés Émergents, Mondial

    45+ symboles incluant indices (S&P 500, Dow Jones, Nasdaq, CAC 40, DAX, Nikkei, etc.), actions (AAPL, MSFT, GOOGL, etc.), ETFs, commodités, forex et cryptos

📊 Visualisation des données

    Graphiques en chandeliers (candlestick) interactifs avec Lightweight Charts

    Vue d'ensemble avec tous les actifs disposés en grille

    Vue par catégorie pour une analyse sectorielle ciblée

    Sparklines (mini-graphiques) pour visualiser les tendances récentes

🔧 Indicateurs techniques

    RSI (Relative Strength Index) - avec zones de survente/surachat

    MACD (Moving Average Convergence Divergence)

    SMA (Simple Moving Average) - 20, 50, 200 périodes

    Bollinger Bands - avec signaux de franchissement

    Stochastic Oscillator - avec zones de surachat/survente

    Volatilité historique

    Momentum - tendance à court terme

# CREER UN ENV VIRTUEL PYTHON :

    python -m venv mon38

# Windows
    
    mon38\Scripts\activate

# Linux/Mac
    
    source mon38/bin/activate

# INSTALLATION DES DEPENDENCES :

    pip install -r requirements.txt

# Ou     
    
    pip install flask flask-cors yfinance pandas numpy scikit-learn pytz

# RUN APP :

    python serv.py

# Ouvrir Navigateur Web :    
    
    http://localhost:5001
    
# EXAMPLE .

<img width="1577" height="747" alt="Screenshot 2026-07-27 at 14-45-14 Indices Monitor - 12 Categories" src="https://github.com/user-attachments/assets/03120d5e-265c-44e7-b452-9c45deedf2b5" />

<img width="1577" height="747" alt="Screenshot 2026-07-27 at 14-50-44 Indices Monitor - 12 Categories" src="https://github.com/user-attachments/assets/364eac86-2e0f-4dc0-88b8-83a538f39efc" />


By Gleaphe 2026 .
