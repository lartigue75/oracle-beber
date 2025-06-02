from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import os
import openai

app = Flask(__name__)
app.secret_key = 'béber-cuisine'

# Configure OpenAI avec ta clé API (à mettre dans Render comme variable d'environnement)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_answer(question):
    prompt = f"""Question : {question}
Réponds en une phrase unique, style oracle : drôle, absurde, poétique ou inattendue. 
Pas de répétition de motifs. Pas de fromage ni de croissants sauf inspiration réelle."""

    try:
        memory = session.get("recent_words", [])
        avoid_words = ', '.join(memory[-5:]) if memory else ""
        system_message = (
            "Tu es l'Oracle Béber. Un voyant non conventionnel, à la fois prophète, poète, clown et vieux sage. "
            "Tu évites les thèmes trop souvent répétés comme la danse, les viennoiseries ou toute image déjà utilisée récemment. "
            f"Évite notamment les mots suivants : {avoid_words}."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=1,
        )

        answer = response.choices[0].message['content'].strip()

        # Mémoriser les mots clés récents
        important_words = [w for w in answer.lower().split() if len(w) > 4]
        memory.extend(important_words[:3])  # on ajoute les 3 premiers mots un peu longs
        session['recent_words'] = memory[-15:]  # garder une mémoire courte (15 mots max)

        return answer

    except Exception as e:
        return f"Béber est en grève : {str(e)}"

def get_another_answer():
    question = session.get('last_question', '')
    if question:
        return get_answer(question)
    return "Pose une vraie question."

def get_raymond_comment(answer):
    commentaires = [
        "Ben ça, j'aurais pas osé.",
        "Et moi qui croyais avoir tout entendu.",
        "Ouais, enfin bon... faut voir.",
        "C’est pas faux, mais c’est pas sûr non plus.",
        "Ah ouais, quand même.",
        "Moi j’dis, faut se méfier des chèvres.",
        "Tu parles d’un oracle...",
        "Encore un qui a trop mangé de croissants.",
        "Ça sent la vieille prophétie mal réchauffée."
    ]
    import random
    return random.choice(commentaires)

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
            session['raymond'] = get_raymond_comment()
        elif action == 'retry':
            session['answer'] = get_another_answer()
            session['raymond'] = get_raymond_comment()

        return redirect(url_for('oracle'))

        answer = session.pop('answer', None)
        raymond = get_raymond_comment(answer) if answer else ""
        return render_template('index.html', answer=answer, input_name=input_name, raymond=raymond)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
