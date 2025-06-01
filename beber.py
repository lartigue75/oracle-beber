from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = 'béber-cuisine'

# Configure OpenAI avec ta clé API (à mettre dans Render comme variable d'environnement)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_answer(question):
    prompt = f"""Tu es l'Oracle Béber. On te pose des questions existentielles, absurdes ou profondes.
Ta réponse doit être courte, drôle, parfois surréaliste, mais toujours dans le style de Béber :
- Une phrase unique, style prophétique ou décalé.
- Pas besoin de reformuler la question.
Question : {question}
Réponds :"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es l'Oracle Béber, un voyant décalé, entre poésie et absurdité prophétique."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.9,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Béber est en grève : {str(e)}"

def get_another_answer():
    question = session.get('last_question', '')
    if question:
        return get_answer(question)
    return "Pose une vraie question."

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
        elif action == 'retry':
            session['answer'] = get_another_answer()

        return redirect(url_for('oracle'))

    answer = session.pop('answer', None)
    return render_template('index.html', answer=answer, input_name=input_name)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
