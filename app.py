"""
=============================================================
  SANTE+  — Système de Surveillance Épidémiologique
  TP INF232 EC2 | Application de collecte & analyse des données
=============================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import os
import hashlib
import json

# ─────────────────────────────────────────────
#  CONFIG PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SANTE+ | Surveillance Épidémiologique",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  CSS PERSONNALISÉ
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] {
      font-family: 'Sora', sans-serif;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
      background: linear-gradient(160deg, #0a1628 0%, #0d2137 50%, #0a1628 100%);
      border-right: 1px solid #1e3a5f;
  }
  [data-testid="stSidebar"] * { color: #e2f0ff !important; }

  /* Main background */
  .stApp {
      background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 50%, #f5f0ff 100%);
  }

  /* Cards métriques */
  .metric-card {
      background: white;
      border-radius: 16px;
      padding: 20px 24px;
      box-shadow: 0 4px 24px rgba(0,100,200,0.08);
      border-left: 4px solid #2563eb;
      margin-bottom: 12px;
  }
  .metric-card.warning { border-left-color: #f59e0b; }
  .metric-card.danger  { border-left-color: #ef4444; }
  .metric-card.success { border-left-color: #10b981; }

  .metric-value {
      font-size: 2.4rem;
      font-weight: 800;
      color: #1e3a5f;
      line-height: 1;
  }
  .metric-label {
      font-size: 0.82rem;
      color: #64748b;
      margin-top: 4px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
  }

  /* Hero header */
  .hero {
      background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 50%, #2563eb 100%);
      border-radius: 20px;
      padding: 32px 40px;
      color: white;
      margin-bottom: 28px;
      box-shadow: 0 8px 32px rgba(37,99,235,0.25);
      position: relative;
      overflow: hidden;
  }
  .hero::before {
      content: '🏥';
      font-size: 120px;
      position: absolute;
      right: 40px;
      top: -10px;
      opacity: 0.15;
  }
  .hero h1 { font-size: 2rem; font-weight: 800; margin: 0; }
  .hero p  { opacity: 0.85; margin: 6px 0 0; font-size: 1rem; }

  /* Boutons */
  .stButton > button {
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: white;
      border: none;
      border-radius: 10px;
      padding: 10px 28px;
      font-weight: 600;
      font-family: 'Sora', sans-serif;
      font-size: 0.9rem;
      transition: all 0.2s;
      box-shadow: 0 4px 12px rgba(37,99,235,0.3);
  }
  .stButton > button:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(37,99,235,0.4);
  }

  /* Formulaire */
  .stTextInput > div > input,
  .stSelectbox > div > div,
  .stNumberInput > div > input {
      border-radius: 10px !important;
      border: 1.5px solid #dbeafe !important;
      font-family: 'Sora', sans-serif !important;
  }

  /* Section titles */
  .section-title {
      font-size: 1.25rem;
      font-weight: 700;
      color: #1e3a5f;
      border-bottom: 2px solid #dbeafe;
      padding-bottom: 8px;
      margin-bottom: 16px;
  }

  /* Alert banners */
  .alert-banner {
      background: #fef3c7;
      border: 1px solid #f59e0b;
      border-radius: 10px;
      padding: 12px 18px;
      margin: 8px 0;
      font-size: 0.9rem;
      color: #92400e;
  }
  .success-banner {
      background: #d1fae5;
      border: 1px solid #10b981;
      border-radius: 10px;
      padding: 12px 18px;
      margin: 8px 0;
      font-size: 0.9rem;
      color: #065f46;
  }

  /* Table styling */
  .dataframe { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }

  /* Hide streamlit branding */
  #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  BASE DE DONNÉES SQLITE
# ─────────────────────────────────────────────
DB_PATH = "sante_data.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_patient TEXT UNIQUE,
            date_collecte TEXT,
            age INTEGER,
            sexe TEXT,
            region TEXT,
            poids REAL,
            taille REAL,
            imc REAL,
            temperature REAL,
            tension_sys INTEGER,
            tension_dia INTEGER,
            frequence_cardiaque INTEGER,
            saturation_oxygene REAL,
            glycemie REAL,
            symptomes TEXT,
            maladies_chroniques TEXT,
            vaccinations TEXT,
            tabac TEXT,
            alcool TEXT,
            activite_physique TEXT,
            score_risque REAL,
            niveau_risque TEXT,
            notes TEXT,
            ts_insertion TEXT
        )
    """)
    con.commit()
    con.close()

def insert_patient(data: dict):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO patients
        (code_patient, date_collecte, age, sexe, region,
         poids, taille, imc, temperature, tension_sys, tension_dia,
         frequence_cardiaque, saturation_oxygene, glycemie,
         symptomes, maladies_chroniques, vaccinations,
         tabac, alcool, activite_physique,
         score_risque, niveau_risque, notes, ts_insertion)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data["code_patient"], data["date_collecte"], data["age"], data["sexe"], data["region"],
        data["poids"], data["taille"], data["imc"], data["temperature"],
        data["tension_sys"], data["tension_dia"],
        data["frequence_cardiaque"], data["saturation_oxygene"], data["glycemie"],
        data["symptomes"], data["maladies_chroniques"], data["vaccinations"],
        data["tabac"], data["alcool"], data["activite_physique"],
        data["score_risque"], data["niveau_risque"], data["notes"],
        datetime.now().isoformat()
    ))
    con.commit()
    con.close()

def load_data() -> pd.DataFrame:
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM patients ORDER BY ts_insertion DESC", con)
    con.close()
    return df

def delete_patient(code: str):
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM patients WHERE code_patient=?", (code,))
    con.commit()
    con.close()

# ─────────────────────────────────────────────
#  LOGIQUE MÉTIER
# ─────────────────────────────────────────────
def calc_imc(poids, taille_cm):
    if taille_cm > 0:
        return round(poids / (taille_cm / 100) ** 2, 2)
    return 0.0

def calc_risque(age, imc, temperature, tension_sys, sat_o2, glycemie,
                maladies, tabac, symptomes_list):
    """Score de risque composite (0-100)."""
    score = 0

    # Âge
    if age >= 70: score += 20
    elif age >= 60: score += 14
    elif age >= 50: score += 8
    elif age >= 40: score += 4

    # IMC
    if imc >= 35: score += 15
    elif imc >= 30: score += 10
    elif imc < 18.5: score += 8
    elif imc >= 25: score += 4

    # Température
    if temperature >= 39.5: score += 12
    elif temperature >= 38: score += 6
    elif temperature < 36: score += 5

    # Tension
    if tension_sys >= 180: score += 15
    elif tension_sys >= 140: score += 8
    elif tension_sys < 90: score += 8

    # Saturation O2
    if sat_o2 < 90: score += 20
    elif sat_o2 < 95: score += 10

    # Glycémie
    if glycemie > 12: score += 10
    elif glycemie > 7: score += 5
    elif glycemie < 3.5: score += 8

    # Maladies chroniques
    score += len(maladies) * 5

    # Tabac
    if tabac == "Oui — fumeur actif": score += 8

    # Symptômes graves
    graves = {"Douleur thoracique", "Difficulté respiratoire", "Perte de conscience"}
    score += len(set(symptomes_list) & graves) * 10

    score = min(score, 100)

    if score >= 70: niveau = "🔴 CRITIQUE"
    elif score >= 45: niveau = "🟠 ÉLEVÉ"
    elif score >= 25: niveau = "🟡 MODÉRÉ"
    else: niveau = "🟢 FAIBLE"

    return round(score, 1), niveau

def gen_code(region, age, sexe):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    h  = hashlib.md5(ts.encode()).hexdigest()[:5].upper()
    pfx = region[:3].upper()
    s   = "M" if sexe == "Masculin" else "F"
    return f"{pfx}-{s}{age}-{h}"


# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
init_db()

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px;'>
      <div style='font-size:2.5rem'>🏥</div>
      <div style='font-size:1.2rem; font-weight:800; color:#60a5fa;'>SANTE+</div>
      <div style='font-size:0.72rem; color:#93c5fd; margin-top:2px;'>
        Surveillance Épidémiologique
      </div>
    </div>
    <hr style='border-color:#1e3a5f; margin: 12px 0;'>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "🏠 Accueil",
        "📋 Collecte des données",
        "📊 Analyse descriptive",
        "🗃️ Base de données",
        "🔔 Alertes & Risques",
        "📤 Export"
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color:#1e3a5f; margin:16px 0;'>", unsafe_allow_html=True)

    df_all = load_data()
    n = len(df_all)
    critiques = len(df_all[df_all["niveau_risque"].str.contains("CRITIQUE", na=False)]) if n > 0 else 0

    st.markdown(f"""
    <div style='font-size:0.78rem; color:#93c5fd; padding: 4px 0;'>
      📌 <b>{n}</b> patient(s) enregistré(s)<br>
      🚨 <b style='color:#f87171'>{critiques}</b> cas critique(s)
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE : ACCUEIL
# ─────────────────────────────────────────────
if page == "🏠 Accueil":
    st.markdown("""
    <div class='hero'>
      <h1>SANTE+ — Surveillance Épidémiologique</h1>
      <p>Collecte intelligente & analyse descriptive des données de santé communautaire</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric-card success'>
          <div class='metric-value'>{len(df)}</div>
          <div class='metric-label'>Patients enregistrés</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        crit = len(df[df["niveau_risque"].str.contains("CRITIQUE", na=False)]) if len(df) > 0 else 0
        st.markdown(f"""
        <div class='metric-card danger'>
          <div class='metric-value'>{crit}</div>
          <div class='metric-label'>Cas critiques</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        age_moy = round(df["age"].mean(), 1) if len(df) > 0 else "—"
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-value'>{age_moy}</div>
          <div class='metric-label'>Âge moyen (ans)</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        imc_moy = round(df["imc"].mean(), 1) if len(df) > 0 else "—"
        st.markdown(f"""
        <div class='metric-card warning'>
          <div class='metric-value'>{imc_moy}</div>
          <div class='metric-label'>IMC moyen</div>
        </div>""", unsafe_allow_html=True)

    if len(df) > 0:
        st.markdown("<div class='section-title'>📈 Tendances récentes</div>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            dist_risque = df["niveau_risque"].value_counts().reset_index()
            dist_risque.columns = ["Niveau", "Nombre"]
            colors = {"🟢 FAIBLE": "#10b981", "🟡 MODÉRÉ": "#f59e0b",
                      "🟠 ÉLEVÉ": "#f97316", "🔴 CRITIQUE": "#ef4444"}
            fig = px.pie(dist_risque, names="Niveau", values="Nombre",
                         color="Niveau", color_discrete_map=colors,
                         title="Répartition des niveaux de risque",
                         hole=0.5)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_family="Sora", title_font_size=14)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            if "region" in df.columns:
                reg_cnt = df["region"].value_counts().reset_index()
                reg_cnt.columns = ["Région", "Patients"]
                fig2 = px.bar(reg_cnt, x="Région", y="Patients",
                              title="Patients par région",
                              color="Patients",
                              color_continuous_scale="Blues")
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                   plot_bgcolor="rgba(0,0,0,0)",
                                   font_family="Sora", title_font_size=14)
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.markdown("""
        <div class='alert-banner'>
          ℹ️ Aucune donnée encore collectée. Rendez-vous dans <b>📋 Collecte des données</b> pour commencer.
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class='section-title' style='margin-top:24px;'>🎯 Fonctionnalités clés</div>
    """, unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    for col, icon, titre, desc in [
        (fc1, "📋", "Collecte structurée", "Formulaire complet : données vitales, symptômes, antécédents, habitudes de vie"),
        (fc2, "📊", "Analyse descriptive", "Statistiques, distributions, corrélations, histogrammes, boxplots automatiques"),
        (fc3, "🔔", "Score de risque", "Algorithme composite multi-facteurs pour identifier les cas prioritaires"),
    ]:
        with col:
            st.markdown(f"""
            <div class='metric-card' style='border-left-color:#8b5cf6;'>
              <div style='font-size:1.6rem'>{icon}</div>
              <div style='font-weight:700; color:#1e3a5f; margin:4px 0;'>{titre}</div>
              <div style='font-size:0.82rem; color:#64748b;'>{desc}</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE : COLLECTE DES DONNÉES
# ─────────────────────────────────────────────
elif page == "📋 Collecte des données":
    st.markdown("<div class='hero'><h1>📋 Formulaire de collecte</h1><p>Renseignez les informations du patient avec précision</p></div>", unsafe_allow_html=True)

    with st.form("form_patient", clear_on_submit=True):

        # ── SECTION 1 : Identité
        st.markdown("<div class='section-title'>👤 Identité & Localisation</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Âge (ans)", 0, 120, 35, help="Âge du patient en années")
        with c2:
            sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])
        with c3:
            region = st.selectbox("Région", [
                "Centre", "Littoral", "Ouest", "Nord-Ouest", "Sud-Ouest",
                "Adamaoua", "Est", "Extrême-Nord", "Nord", "Sud"
            ])

        date_collecte = st.date_input("Date de collecte", date.today())

        # ── SECTION 2 : Données vitales
        st.markdown("<div class='section-title' style='margin-top:20px;'>💗 Données vitales</div>", unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1:
            poids  = st.number_input("Poids (kg)", 10.0, 300.0, 70.0, step=0.5)
            taille = st.number_input("Taille (cm)", 50, 250, 170)
        with v2:
            temperature = st.number_input("Température (°C)", 30.0, 45.0, 37.0, step=0.1)
            tension_sys = st.number_input("Tension systolique (mmHg)", 50, 300, 120)
        with v3:
            tension_dia        = st.number_input("Tension diastolique (mmHg)", 30, 200, 80)
            frequence_cardiaque = st.number_input("Fréquence cardiaque (bpm)", 20, 250, 75)

        sv1, sv2 = st.columns(2)
        with sv1:
            saturation_oxygene = st.number_input("Saturation O₂ (%)", 50.0, 100.0, 98.0, step=0.1)
        with sv2:
            glycemie = st.number_input("Glycémie (mmol/L)", 1.0, 40.0, 5.0, step=0.1)

        # ── SECTION 3 : Symptômes
        st.markdown("<div class='section-title' style='margin-top:20px;'>🤒 Symptômes déclarés</div>", unsafe_allow_html=True)
        symptomes_options = [
            "Fièvre", "Toux", "Maux de tête", "Fatigue", "Douleur thoracique",
            "Difficulté respiratoire", "Nausées/Vomissements", "Diarrhée",
            "Douleurs musculaires", "Éruption cutanée", "Perte de conscience",
            "Vertiges", "Perte d'odorat/goût", "Œdème", "Aucun"
        ]
        symptomes = st.multiselect("Sélectionnez les symptômes présents :", symptomes_options)

        # ── SECTION 4 : Antécédents
        st.markdown("<div class='section-title' style='margin-top:20px;'>📁 Antécédents médicaux</div>", unsafe_allow_html=True)
        maladies_options = [
            "Hypertension artérielle", "Diabète type 2", "Diabète type 1",
            "Insuffisance cardiaque", "Asthme", "BPCO", "Cancer",
            "Insuffisance rénale", "VIH/SIDA", "Tuberculose",
            "Paludisme chronique", "Drépanocytose", "Aucune"
        ]
        maladies = st.multiselect("Maladies chroniques :", maladies_options)

        vaccins_options = [
            "COVID-19", "Rougeole-Oreillons-Rubéole", "Hépatite B",
            "Fièvre jaune", "Méningite", "Polio", "Tétanos", "Aucun"
        ]
        vaccinations = st.multiselect("Vaccinations reçues :", vaccins_options)

        # ── SECTION 5 : Habitudes de vie
        st.markdown("<div class='section-title' style='margin-top:20px;'>🌿 Habitudes de vie</div>", unsafe_allow_html=True)
        h1, h2, h3 = st.columns(3)
        with h1:
            tabac = st.selectbox("Tabagisme", ["Non-fumeur", "Oui — fumeur actif", "Ex-fumeur"])
        with h2:
            alcool = st.selectbox("Consommation d'alcool", ["Jamais", "Occasionnel", "Régulier", "Excessif"])
        with h3:
            activite = st.selectbox("Activité physique", ["Sédentaire", "Légère", "Modérée", "Intense"])

        notes = st.text_area("Notes cliniques (optionnel)", height=80)

        submitted = st.form_submit_button("✅ Enregistrer le patient", use_container_width=True)

    if submitted:
        imc = calc_imc(poids, taille)
        score, niveau = calc_risque(
            age, imc, temperature, tension_sys,
            saturation_oxygene, glycemie,
            [m for m in maladies if m != "Aucune"],
            tabac,
            symptomes
        )
        code = gen_code(region, age, sexe)

        data = dict(
            code_patient=code,
            date_collecte=str(date_collecte),
            age=age, sexe=sexe, region=region,
            poids=poids, taille=taille, imc=imc,
            temperature=temperature, tension_sys=tension_sys,
            tension_dia=tension_dia, frequence_cardiaque=frequence_cardiaque,
            saturation_oxygene=saturation_oxygene, glycemie=glycemie,
            symptomes=", ".join(symptomes) if symptomes else "Aucun",
            maladies_chroniques=", ".join(maladies) if maladies else "Aucune",
            vaccinations=", ".join(vaccinations) if vaccinations else "Aucune",
            tabac=tabac, alcool=alcool, activite_physique=activite,
            score_risque=score, niveau_risque=niveau,
            notes=notes
        )
        insert_patient(data)

        color = {"🟢 FAIBLE": "#d1fae5", "🟡 MODÉRÉ": "#fef9c3",
                 "🟠 ÉLEVÉ": "#ffedd5", "🔴 CRITIQUE": "#fee2e2"}.get(niveau, "#f0f7ff")

        st.markdown(f"""
        <div style='background:{color}; border-radius:14px; padding:20px 28px; margin-top:16px;
                    border: 1.5px solid rgba(0,0,0,0.08); box-shadow: 0 4px 12px rgba(0,0,0,0.06);'>
          <div style='font-size:1.1rem; font-weight:700;'>✅ Patient enregistré avec succès</div>
          <div style='margin-top:8px; font-size:0.9rem;'>
            Code : <b style='font-family:monospace'>{code}</b> &nbsp;|&nbsp;
            IMC : <b>{imc}</b> &nbsp;|&nbsp;
            Score de risque : <b>{score}/100</b> &nbsp;|&nbsp;
            Niveau : <b>{niveau}</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if "CRITIQUE" in niveau:
            st.error("🚨 Ce patient présente un profil de risque CRITIQUE — prise en charge prioritaire recommandée.")
        elif "ÉLEVÉ" in niveau:
            st.warning("⚠️ Risque élevé détecté — suivi rapproché conseillé.")


# ─────────────────────────────────────────────
#  PAGE : ANALYSE DESCRIPTIVE
# ─────────────────────────────────────────────
elif page == "📊 Analyse descriptive":
    st.markdown("<div class='hero'><h1>📊 Analyse descriptive</h1><p>Explorez et visualisez les données collectées</p></div>", unsafe_allow_html=True)

    df = load_data()
    if len(df) == 0:
        st.warning("Aucune donnée disponible. Commencez par enregistrer des patients.")
        st.stop()

    # Colonnes numériques
    num_cols = ["age", "poids", "taille", "imc", "temperature",
                "tension_sys", "tension_dia", "frequence_cardiaque",
                "saturation_oxygene", "glycemie", "score_risque"]
    df_num = df[num_cols].dropna()

    # ── Stats descriptives
    st.markdown("<div class='section-title'>📐 Statistiques descriptives</div>", unsafe_allow_html=True)
    stats = df_num.describe().T.round(2)
    stats.index.name = "Variable"
    st.dataframe(stats, use_container_width=True)

    # ── Distributions
    st.markdown("<div class='section-title' style='margin-top:24px;'>📉 Distributions des variables vitales</div>", unsafe_allow_html=True)
    var = st.selectbox("Variable à visualiser :", num_cols, index=3)

    col_h, col_b = st.columns(2)
    with col_h:
        fig_hist = px.histogram(df, x=var, nbins=20,
                                title=f"Distribution — {var}",
                                color_discrete_sequence=["#3b82f6"],
                                marginal="box")
        fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(250,252,255,1)",
                               font_family="Sora")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        fig_box = px.box(df, x="sexe", y=var, color="sexe",
                         title=f"{var} par sexe",
                         color_discrete_map={"Masculin": "#3b82f6", "Féminin": "#ec4899"})
        fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(250,252,255,1)",
                              font_family="Sora")
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Corrélations
    st.markdown("<div class='section-title' style='margin-top:24px;'>🔗 Matrice de corrélation</div>", unsafe_allow_html=True)
    corr = df_num.corr().round(2)
    fig_corr = px.imshow(corr, text_auto=True,
                         color_continuous_scale="RdBu_r",
                         title="Corrélations entre variables numériques",
                         aspect="auto")
    fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                           font_family="Sora", height=500)
    st.plotly_chart(fig_corr, use_container_width=True)

    # ── Scatter plot
    st.markdown("<div class='section-title' style='margin-top:24px;'>🔍 Analyse bivariée</div>", unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        x_var = st.selectbox("Variable X :", num_cols, index=0)
    with sc2:
        y_var = st.selectbox("Variable Y :", num_cols, index=3)

    fig_sc = px.scatter(df, x=x_var, y=y_var, color="niveau_risque",
                        size="score_risque",
                        color_discrete_map={
                            "🟢 FAIBLE": "#10b981", "🟡 MODÉRÉ": "#f59e0b",
                            "🟠 ÉLEVÉ": "#f97316", "🔴 CRITIQUE": "#ef4444"
                        },
                        hover_data=["code_patient", "region", "sexe"],
                        title=f"{x_var} vs {y_var} — coloré par niveau de risque",
                        trendline="ols")
    fig_sc.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                         plot_bgcolor="rgba(250,252,255,1)",
                         font_family="Sora", height=420)
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Répartition par région
    st.markdown("<div class='section-title' style='margin-top:24px;'>🗺️ Analyse géographique</div>", unsafe_allow_html=True)
    reg_risq = df.groupby(["region", "niveau_risque"]).size().reset_index(name="count")
    fig_reg = px.bar(reg_risq, x="region", y="count", color="niveau_risque",
                     barmode="stack",
                     color_discrete_map={
                         "🟢 FAIBLE": "#10b981", "🟡 MODÉRÉ": "#f59e0b",
                         "🟠 ÉLEVÉ": "#f97316", "🔴 CRITIQUE": "#ef4444"
                     },
                     title="Distribution des niveaux de risque par région")
    fig_reg.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(250,252,255,1)",
                          font_family="Sora")
    st.plotly_chart(fig_reg, use_container_width=True)


# ─────────────────────────────────────────────
#  PAGE : BASE DE DONNÉES
# ─────────────────────────────────────────────
elif page == "🗃️ Base de données":
    st.markdown("<div class='hero'><h1>🗃️ Base de données patients</h1><p>Consultez et gérez les enregistrements</p></div>", unsafe_allow_html=True)

    df = load_data()
    if len(df) == 0:
        st.warning("Aucun patient enregistré.")
        st.stop()

    # Filtres
    f1, f2, f3 = st.columns(3)
    with f1:
        filtre_region = st.multiselect("Filtrer par région :", df["region"].unique().tolist())
    with f2:
        filtre_sexe = st.multiselect("Filtrer par sexe :", df["sexe"].unique().tolist())
    with f3:
        filtre_risque = st.multiselect("Filtrer par risque :", df["niveau_risque"].unique().tolist())

    df_show = df.copy()
    if filtre_region: df_show = df_show[df_show["region"].isin(filtre_region)]
    if filtre_sexe:   df_show = df_show[df_show["sexe"].isin(filtre_sexe)]
    if filtre_risque: df_show = df_show[df_show["niveau_risque"].isin(filtre_risque)]

    cols_display = ["code_patient", "date_collecte", "age", "sexe", "region",
                    "imc", "temperature", "tension_sys", "saturation_oxygene",
                    "glycemie", "score_risque", "niveau_risque"]

    st.dataframe(df_show[cols_display], use_container_width=True, height=400)
    st.caption(f"Affichage : {len(df_show)} / {len(df)} patients")

    # Suppression
    with st.expander("🗑️ Supprimer un patient"):
        code_del = st.text_input("Code patient à supprimer :")
        if st.button("Supprimer") and code_del:
            delete_patient(code_del)
            st.success(f"Patient {code_del} supprimé.")
            st.rerun()


# ─────────────────────────────────────────────
#  PAGE : ALERTES & RISQUES
# ─────────────────────────────────────────────
elif page == "🔔 Alertes & Risques":
    st.markdown("<div class='hero'><h1>🔔 Tableau de bord des risques</h1><p>Patients nécessitant une attention prioritaire</p></div>", unsafe_allow_html=True)

    df = load_data()
    if len(df) == 0:
        st.warning("Aucune donnée.")
        st.stop()

    crit = df[df["niveau_risque"].str.contains("CRITIQUE", na=False)].copy()
    elev = df[df["niveau_risque"].str.contains("ÉLEVÉ", na=False)].copy()

    st.markdown(f"### 🔴 Cas Critiques ({len(crit)} patients)")
    if len(crit) > 0:
        for _, row in crit.iterrows():
            st.markdown(f"""
            <div style='background:#fee2e2; border:1.5px solid #fca5a5; border-radius:12px;
                        padding:16px 20px; margin:8px 0;'>
              <b style='font-size:1rem; color:#991b1b;'>🚨 {row.code_patient}</b>
              — {row.sexe}, {row.age} ans, {row.region}<br>
              <span style='font-size:0.88rem; color:#7f1d1d;'>
                Score : {row.score_risque}/100 &nbsp;|&nbsp;
                IMC : {row.imc} &nbsp;|&nbsp;
                Temp : {row.temperature}°C &nbsp;|&nbsp;
                SatO₂ : {row.saturation_oxygene}% &nbsp;|&nbsp;
                Glycémie : {row.glycemie} mmol/L
              </span><br>
              <span style='font-size:0.82rem; color:#9b1c1c;'>
                Symptômes : {row.symptomes} &nbsp;|&nbsp; Maladies : {row.maladies_chroniques}
              </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='success-banner'>✅ Aucun cas critique actuellement.</div>", unsafe_allow_html=True)

    st.markdown(f"### 🟠 Cas à Risque Élevé ({len(elev)} patients)")
    if len(elev) > 0:
        for _, row in elev.iterrows():
            st.markdown(f"""
            <div style='background:#ffedd5; border:1.5px solid #fdba74; border-radius:12px;
                        padding:14px 18px; margin:8px 0;'>
              <b style='color:#7c2d12;'>⚠️ {row.code_patient}</b>
              — {row.sexe}, {row.age} ans, {row.region} |
              Score : {row.score_risque}/100
            </div>
            """, unsafe_allow_html=True)

    # Évolution du score de risque
    st.markdown("<div class='section-title' style='margin-top:24px;'>📈 Distribution des scores de risque</div>", unsafe_allow_html=True)
    fig = px.histogram(df, x="score_risque", nbins=15,
                       color="niveau_risque",
                       color_discrete_map={
                           "🟢 FAIBLE": "#10b981", "🟡 MODÉRÉ": "#f59e0b",
                           "🟠 ÉLEVÉ": "#f97316", "🔴 CRITIQUE": "#ef4444"
                       },
                       title="Distribution des scores de risque composite")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="Sora")
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  PAGE : EXPORT
# ─────────────────────────────────────────────
elif page == "📤 Export":
    st.markdown("<div class='hero'><h1>📤 Export des données</h1><p>Téléchargez vos données pour analyses complémentaires</p></div>", unsafe_allow_html=True)

    df = load_data()
    if len(df) == 0:
        st.warning("Aucune donnée à exporter.")
        st.stop()

    st.markdown("### Télécharger en CSV")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Télécharger les données (CSV)",
        data=csv,
        file_name=f"sante_plus_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("### Aperçu complet des données")
    st.dataframe(df, use_container_width=True)

    st.markdown("### Rapport statistique synthétique")
    num_cols = ["age", "poids", "imc", "temperature", "tension_sys",
                "saturation_oxygene", "glycemie", "score_risque"]
    st.dataframe(df[num_cols].describe().round(2), use_container_width=True)

