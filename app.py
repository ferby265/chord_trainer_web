from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

easy_chords = [
    'Maj', 'min', 'dim', 'aug', 'sus2', 'sus4', 'Maj7', 'min7', 'dom7'
]

medium_chords = easy_chords + [
    '6', 'min6', '9', 'Maj9', 'min9', '11', 'Maj11', 'min11', '13', 'Maj13', 'min13'
]

hard_chords = medium_chords + [
    'minMaj7', 'halfdim7', 'dim7', '7b5', '7#5',
    '7b9', '7#9', '7b5b9', '7#5b9', '7#5#9', '7b9b13', '7#9b13'
]

chord_formulas = {
    'Maj': [0, 4, 7], 'min': [0, 3, 7], 'dim': [0, 3, 6], 'aug': [0, 4, 8],
    'sus2': [0, 2, 7], 'sus4': [0, 5, 7], 'Maj7': [0, 4, 7, 11], 'min7': [0, 3, 7, 10],
    'dom7': [0, 4, 7, 10], '6': [0, 4, 7, 9], 'min6': [0, 3, 7, 9],
    '9': [0, 4, 7, 10, 14], 'Maj9': [0, 4, 7, 11, 14], 'min9': [0, 3, 7, 10, 14],
    '11': [0, 4, 7, 10, 14, 17], 'Maj11': [0, 4, 7, 11, 14, 17], 'min11': [0, 3, 7, 10, 14, 17],
    '13': [0, 4, 7, 10, 21], 'Maj13': [0, 4, 7, 11, 21], 'min13': [0, 3, 7, 10, 21],
    'minMaj7': [0, 3, 7, 11], 'halfdim7': [0, 3, 6, 10], 'dim7': [0, 3, 6, 9],
    '7b5': [0, 4, 6, 10], '7#5': [0, 4, 8, 10], '7b9': [0, 4, 7, 10, 13], '7#9': [0, 4, 7, 10, 15],
    '7b5b9': [0, 4, 6, 10, 13], '7#5b9': [0, 4, 8, 10, 13], '7#5#9': [0, 4, 8, 10, 15],
    '7b9b13': [0, 4, 7, 10, 13, 20], '7#9b13': [0, 4, 7, 10, 15, 20],
}

def get_notes(root, intervals):
    root_index = note_names.index(root)
    return [note_names[(root_index + i) % 12] for i in intervals]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_chord', methods=['GET'])
def generate_chord():
    difficulty = request.args.get('difficulty', 'easy')

    if difficulty == 'medium':
        chord_pool = medium_chords
    elif difficulty == 'hard' or difficulty == 'competition':
        chord_pool = hard_chords
    else:
        chord_pool = easy_chords

    root = random.choice(note_names)
    chord_type = random.choice(chord_pool)
    correct_notes = get_notes(root, chord_formulas[chord_type])

    return jsonify({'root': root, 'chord_type': chord_type, 'correct_notes': correct_notes})

if __name__ == '__main__':
    app.run(debug=True)

