from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import os
import openai
import random
import re

app = Flask(__name__)
app.secret_key = 'béber-cuisine'

# Configure OpenAI avec ta clé API (Render)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Mémoires courtes
recent_styles = []
recent_words = []

TONALITES = [
    "positive",
    "positive",
    "négative",
    "mitigée",
    "négative"
]

STYLES_PERSONNAGES = [
    "Le Chapelier Fou d'Alice au pays des merveilles",
    "Le Chat de Cheshire, mystérieux et ironique",
    "La Reine de Cœur, autoritaire et excessive",
    "La Pythie de Delphes, en transe prophétique",
    "Merlin l'enchanteur, un brin farceur mais sage"
]

MOTS_BANALS = {"nuage", "nuages", "chanter", "chantent", "danse", "dansent", "danser", "cosmique", "galaxie", "pluie", "ciel", "étoile", "jubile", "acrobat", "acrobatique", "tournoie", "fête", "musique", "camarade", "chant", "rythme"}
MAX_HISTORY = 3

def nettoyer_texte(texte):
    mots = re.findall(r"\b\w+\b", texte.lower())
    return set(mots)

def racine_simplifiee(mot):
    return re.sub(r'(es|s|x|nt|er|ent|ant|ique|iques)$', '', mot)

def filtrer_repetitions(texte):
    global recent_words
    mots = nettoyer_texte(texte)
    racines = {racine_simplifiee(mot) for mot in mots}

    for mot in racines:
        if mot in MOTS_BANALS:
            return True
        if any(mot in w or w in mot for w in recent_words):
            return True

    recent_words.extend(racines)
    if len(recent_words) > 60:
        recent_words = recent_words[-60:]
    return False

def get_answer(question):
    for _ in range(6):
        tonalite = random.choice(TONALITES)
        style = random.choice(STYLES_PERSONNAGES)
        prompt = f"""
        Tu es un oracle inspiré par {style}.
        Tu réponds à la question suivante avec une tonalité {tonalite}.
        - Sois bref (1 ou 2 phrases max)
        - Pas de généralités ou banalités
        - Adopte un ton marqué par ton personnage : exagéré, mystérieux, absurde ou inquiétant
        - Évite les répétitions ou motifs trop lyriques

        Question : {question}
        Réponds :
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un oracle incarné par un personnage fantasque ou mystique. Tu réponds brièvement et avec un ton tranché, adapté à ta personnalité."},
                    {"role": "user", "content": prompt.strip()}
                ],
                max_tokens=100,
                temperature=1.2,
            )
            texte = response.choices[0].message['content'].strip()
            if not filtrer_repetitions(texte):
                return texte
        except Exception as e:
            return f"Béber est en grève : {str(e)}"

    return "Béber a buggé sur sa boule de cristal."

@app.route('/', methods=['GET', 'POST'])
def oracle():
    if request.method == 'POST':
        question = request.form.get("question", "").strip()

        if question:
            tonalite = random.choice(TONALITES)
            answer = random.choice(STYLES[tonalite])
            session['answer'] = answer

        return redirect(url_for('oracle'))

    answer = session.pop('answer', None)
    return render_template('index.html', answer=answer)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
