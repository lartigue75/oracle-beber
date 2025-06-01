from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import random

app = Flask(__name__)
app.secret_key = 'beber-cle'

def get_answer(question):
    return random.choice([
        "Le grille-pain sifflera trois fois.",
        "Les chaussettes sales ont parlé : c’est non.",
        "Demande à la plante verte. Elle sait.",
        "Un pigeon t'observe, mais il hésite."
    ])

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
    app.run(debug=True, port=5001)
