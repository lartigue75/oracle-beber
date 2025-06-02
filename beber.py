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

STYLE_PROMPTS = [
    "Un proverbe de bistrot, version Béber.",
    "Une prédiction absurde façon devin d'Alice au pays des merveilles.",
    "Une sentence poético-fumiste à la Béber.",
    "Un slogan de pub des années 80 détourné par un prophète en slip.",
    "Un avertissement façon science-fiction cheap des années 60.",
    "Une parabole animalière sortie d’un cerveau embrumé.",
    "Une réflexion noire de bistrot, à la Audiard fatigué.",
    "Un murmure énigmatique d’un oracle qui a trop lu Kafka."
]

MOTS_BANALS = {"nuage", "nuages", "chanter", "chantent", "danse", "dansent", "danser", "cosmique", "galaxie", "pluie", "ciel", "étoile", "jubile", "acrobat", "acrobatique", "tournoie", "fête", "musique", "camarade", "chant", "rythme"}
MAX_HISTORY = 3


def nettoyer_texte(texte):
    mots = re.findall(r"\b\w+\b", texte.lower())
    return set(mots)

def racine_simplifiee(mot):
    return re.sub(r'(es|s|x|nt|er|ent|ant|ique|iques)$', '', mot)

def get_fresh_style():
    global recent_styles
    styles_disponibles = [s for s in STYLE_PROMPTS if s not in recent_styles]
    if not styles_disponibles:
        recent_styles = []
        styles_disponibles = STYLE_PROMPTS[:]
    nouveau = random.choice(styles_disponibles)
    recent_styles.append(nouveau)
    if len(recent_styles) > MAX_HISTORY:
        recent_styles.pop(0)
    return nouveau

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
        style = get_fresh_style()
        prompt = f"""
        Tu es l'Oracle Béber. On te pose des questions existentielles, absurdes ou profondes.
        Tu réponds dans un style prophétique, toujours original.
        Ta réponse doit être :
        - Courte (1 ou 2 phrases),
        - Parfois drôle, poétique, absurde ou ironique,
        - Pas forcément positive : tu peux être enthousiaste, sceptique, pessimiste ou encourageant.

        Style suggéré : {style}
        Question : {question}
        Réponds :
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es l'Oracle Béber, un voyant décalé, entre poésie et absurdité prophétique."},
                    {"role": "user", "content": prompt.strip()}
                ],
                max_tokens=60,
                temperature=1.1,
            )
            texte = response.choices[0].message['content'].strip()
            if not filtrer_repetitions(texte):
                return texte
        except Exception as e:
            return f"Béber est en grève : {str(e)}"

    return "Béber a buggé sur sa boule de cristal."

def get_another_answer():
    question = session.get('last_question', '')
    if question:
        return get_answer(question)
    return "Pose une vraie question."

def get_jacqueline_comment(answer):
    commentaires = [
        "Ben ça, j'aurais pas osé.",
        "Et moi qui croyais avoir tout entendu.",
        "D'accord à 120 %",
        "C’est pas faux, mais c’est pas sûr non plus.",
        "Très bonne réponse !",
        "Moi j’dis, faut se méfier des chèvres.",
        "Tu parles d’un oracle...",
        "Encore un qui a trop mangé de croissants.",
        "Ça sent la vieille prophétie mal réchauffée."
    ]
    return f"Jacqueline : {random.choice(commentaires)}"

@app.route('/', methods=['GET', 'POST'])
def oracle():
    input_name = f"question_{uuid.uuid4().hex[:8]}"

    if request.method == 'POST':
        field_name = next((k for k in request.form if k.startswith('question_')), None)
        question = request.form.get(field_name, '').strip()
        action = request.form.get('action')

        if action == 'ask' and question:
            session['last_question'] = question
            session['answer'] = get_answer(question)
            session['jacqueline'] = get_jacqueline_comment(session['answer'])
        elif action == 'retry':
            session['answer'] = get_another_answer()
            session['jacqueline'] = get_jacqueline_comment(session['answer'])

        return redirect(url_for('oracle'))

    answer = session.pop('answer', None)
    jacqueline = session.pop('jacqueline', '')
    return render_template('index.html', answer=answer, raymond=jacqueline, input_name=input_name)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
