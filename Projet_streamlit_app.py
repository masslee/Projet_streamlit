# IMPORTATION DES LIBRAIRIES
import streamlit as st                     
import pandas as pd                        
from bs4 import BeautifulSoup as bs       
from requests import get                 
import base64                              
import numpy as np                         
import streamlit.components.v1 as components

# FONCTIONS D'AFFICHAGE ET DE STYLE

def ajout_style_personnalise():
    st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: #ff7613;
    }
    /* Forcer tous les textes à être orange */
    body, .css-18e3th9, .css-1d391kg {
        color: #ff7613;
    }
    div.stButton > button {
        background-color: #ff7613;
        color: black;
        border: 2px solid with;
        border-radius: 10px;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #ff7613;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

def local_css(file_name):
    """
    Charge un fichier CSS local pour appliquer un style supplémentaire.
    """
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def convert_df(df):
    """
    Convertit un DataFrame en CSV encodé en UTF-8 pour le téléchargement.
    Utilisation de cache pour ne pas recalculer si le DataFrame n'a pas changé.
    """
    return df.to_csv(index=False).encode('utf-8')

# FONCTIONS DE SCRAPING AVEC BEAUTIFULSOUP (DONNÉES NETTOYÉES)
def charger_donnees_chaussures(pages):
    df = pd.DataFrame()
    for i in range(pages):
        url = f'https://sn.coinafrique.com/categorie/chaussures-enfants?page={i}'
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')
        data = []
        for container in containers:
            try:
                type_chaussures = container.find('p', class_='ad__card-description').text.strip()
                adresse = container.find('p', class_='ad__card-location').text.strip().replace('location_on', '')
                prix = container.find('p', class_='ad__card-price').text.strip().replace('CFA', '')
                img_link = container.find('img', class_='ad__card-img')['src']
                dic = {
                    'Type_Chaussure': type_chaussures, 
                    'Prix': prix, 
                    'Adresse': adresse,
                    'Image_Lien': img_link 
                }
                data.append(dic)
            except Exception as e:
                # En cas d'erreur, ignorer cette annonce
                pass
        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)
    return df

def charger_donnees_vetements(pages):
    df = pd.DataFrame()
    for i in range(pages):
        url = f'https://sn.coinafrique.com/categorie/vetements-enfants?page={i}'
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')
        data = []
        for container in containers:
            try:
                type_habits = container.find('p', class_='ad__card-description').text.strip()
                adresse = container.find('p', class_='ad__card-location').text.strip().replace('location_on', '')
                prix = container.find('p', class_='ad__card-price').text.strip().replace('CFA', '')
                img_link = container.find('img', class_='ad__card-img')['src']
                dic = {
                    'Type_Habits': type_habits, 
                    'Prix': prix, 
                    'Adresse': adresse,
                    'Image_Lien': img_link 
                }
                data.append(dic)
            except Exception as e:
                # En cas d'erreur, ignorer cette annonce
                pass
        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)
    return df

# FONCTION D'AFFICHAGE ET DE TÉLÉCHARGEMENT DES DONNÉES

def charger_et_afficher_les_donnees (dataframe, title, btn_key):
    """
    Affiche la dimension des données, le DataFrame et propose le téléchargement en CSV.
    """
    if st.button(title, key=btn_key):
        st.subheader("Dimensions des données")
        st.write(f"Le DataFrame contient {dataframe.shape[0]} lignes et {dataframe.shape[1]} colonnes.")
        st.dataframe(dataframe)
        csv = convert_df(dataframe)
        st.download_button(
            label="Télécharger les données en CSV",
            data=csv,
            file_name='coin_afrique_data.csv',
            mime='text/csv'
        )
# CONFIGURATION DE L'INTERFACE ET DU MENU LATÉRAL

# Appliquer le style global (fond noir, texte orange et boutons stylisés)
ajout_style_personnalise()

# Charger le fichier CSS local pour un style supplémentaire (fichier à créer séparément)
local_css('Style_app.css')

# Titre et description de l'application
st.markdown("<h1 style='text-align: center;'>Mon application de scraping de données (site: Coin-afrique)</h1>", unsafe_allow_html=True)
st.markdown("""
Cette application permet de scraper et nettoyer les données depuis Coin-Afrique pour les catégories suivantes :
- **Vêtements enfants** : Type d'habits, Prix, Adresse, Lien de l'image
- **Chaussures enfants** : Type de chaussures, Prix, Adresse, Lien de l'image

Vous pouvez également télécharger des données déjà scrapées (non nettoyées) via Web Scraper,
ou remplir un formulaire d’évaluation de l’app via KoboToolbox ou Google Forms.

**Python libraries** : base64, pandas, streamlit, requests, bs4  
**Data source** : [Coin-Afrique](https://sn.coinafrique.com)
""")

# Menu latéral avec choix utilisateur
st.sidebar.header("Options Utilisateur")
# Sélection du nombre de pages à scraper
pages = st.sidebar.number_input("Nombre de pages à scraper", min_value=1, max_value=21, value=5, step=1)

# Sélection de la catégorie à scraper / télécharger
data_choice = st.sidebar.selectbox("Choisir la catégorie", ["Vêtements enfants", "Chaussures enfants"])

# Sélection de l'option de l'application
option = st.sidebar.selectbox("Options", [
    'Récupérer des données avec BS', 
    'Télécharger les données récupérées', 
    'Remplissage formulaire KoboToolbox', 
    'Remplissage formulaire Google Forms'
])

# LOGIQUE PRINCIPALE DE L'APPLICATION EN FONCTION DU CHOIX UTILISATEUR

if option == 'Récupérer des données avec BS':
    st.markdown("<h2>Scraping des données nettoyées</h2>", unsafe_allow_html=True)
    # En fonction de la catégorie sélectionnée, lancer le scraping
    if data_choice == "Chaussures enfants":
        df_data = charger_donnees_chaussures(int(pages))
    else:
        df_data = charger_donnees_vetements(int(pages))
    # Afficher et proposer le téléchargement des données
    charger_et_afficher_les_donnees(df_data, f"Afficher & Télécharger les données de {data_choice}", btn_key="scrape_btn")

elif option == 'Télécharger les données récupérées':
    st.markdown("<h2>Téléchargement des données non nettoyées</h2>", unsafe_allow_html=True)
    # En fonction de la catégorie sélectionnée, charger le fichier CSV correspondant
    if data_choice == "Chaussures enfants":
        try:
            df_download = pd.read_csv("coin_afrique_chaussure.csv")
        except Exception as e:
            st.error("Le fichier 'coin_afrique_chaussure.csv' est introuvable.")
            df_download = pd.DataFrame()
    else:
        try:
            df_download = pd.read_csv("coin_affrique_vetement.csv")
        except Exception as e:
            st.error("Le fichier 'coin_affrique_vetement.csv' est introuvable.")
            df_download = pd.DataFrame()
    # Afficher et proposer le téléchargement
    charger_et_afficher_les_donnees(df_download, f"Afficher & Télécharger les données de {data_choice}", btn_key="download_btn")

elif option == 'Remplissage formulaire KoboToolbox':
    st.markdown("<h2>Formulaire d’évaluation - KoboToolbox</h2>", unsafe_allow_html=True)
    # Intégrer le formulaire KoboToolbox via iframe
    components.html("""
    <iframe src="https://ee.kobotoolbox.org/x/mIgmVqGZ" width="800" height="1100" frameborder="0"></iframe>
    """, height=1100, width=800)

elif option == 'Remplissage formulaire Google Forms':
    st.markdown("<h2>Formulaire d’évaluation - Google Forms</h2>", unsafe_allow_html=True)
    # Intégrer le formulaire Google Forms via iframe
    components.html("""
    <iframe src="https://forms.gle/aiDhdZUPFqLFgnHm6" width="800" height="1100" frameborder="0"></iframe>
    """, height=1100, width=800)
