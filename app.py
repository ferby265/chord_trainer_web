from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

easy_chords = [
    'Maj', 'min', 'dim', 'aug',
    'sus2', 'sus4',
    'Maj7', 'min7', 'dom7',
    '6', 'min6', '6/9',
    'add9', 'add4', 'add6'
]


medium_chords = easy_chords + [
    'min6/9',
    '9', 'Maj9', 'min9',
    '11', 'Maj11', 'min11',
    '13', 'Maj13', 'min13',
    'Maj7#11', 'Maj9#11',
    '7sus4', '9sus4', '13sus4',
    'add11', 'add#11', 'add13'
]


hard_chords = medium_chords + [
    'minMaj7', 'minMaj9',
    'halfdim7', 'dim7', 'dim13',
    '7b5', '7#5', '7b9', '7#9',
    '7b5b9', '7#5b9', '7#5#9',
    '7b9b13', '7#9b13',
    '7b13', '7#13', '7#11', '7b5#9', '7b5b13', '7b9#11',
    'Maj7b5', 'Maj7#5',
    'min7b5', 'min9b5', 'min7#5',
    'min7b13', 'min13b5'
]


competition_chords = hard_chords

chord_formulas = {
    # Basic Triads
    'Maj': '1 3 5',
    'min': '1 b3 5',
    'dim': '1 b3 b5',
    'aug': '1 3 #5',
    'sus2': '1 2 5',
    'sus4': '1 4 5',

    # 6th Chords
    '6': '1 3 5 6',
    'min6': '1 b3 5 6',
    '6/9': '1 3 6 9',
    'min6/9': '1 b3 6 9',

    # 7th Chords
    'Maj7': '1 3 5 7',
    'min7': '1 b3 5 b7',
    'dom7': '1 3 5 b7',

    # Extended Chords
    '9': '1 3 5 b7 9',
    'Maj9': '1 3 5 7 9',
    'min9': '1 b3 5 b7 9',
    '11': '1 3 5 b7 11',
    'Maj11': '1 3 5 7 11',
    'min11': '1 b3 5 b7 11',
    '13': '1 3 5 b7 13',
    'Maj13': '1 3 5 7 13',
    'min13': '1 b3 5 b7 13',

    # Lydian Chords
    'Maj7#11': '1 3 5 7 #11',
    'Maj9#11': '1 3 5 7 9 #11',

    # Altered Dominants
    '7b5': '1 3 b5 b7',
    '7#5': '1 3 #5 b7',
    '7b9': '1 3 5 b7 b9',
    '7#9': '1 3 5 b7 #9',
    '7b5b9': '1 3 b5 b7 b9',
    '7#5b9': '1 3 #5 b7 b9',
    '7#5#9': '1 3 #5 b7 #9',
    '7b9b13': '1 3 5 b7 b9 b13',
    '7#9b13': '1 3 5 b7 #9 b13',
    '7b13': '1 3 5 b7 b13',
    '7#13': '1 3 5 b7 #13',
    '7#11': '1 3 5 b7 #11',
    '7b9#11': '1 3 5 b7 b9 #11',

    # Suspended Dominants
    '7sus4': '1 4 5 b7',
    '9sus4': '1 4 5 b7 9',
    '13sus4': '1 4 5 b7 9 13',

    # Minor Variations
    'minMaj7': '1 b3 5 7',
    'min7b5': '1 b3 b5 b7',  # aka halfdim7
    'min9b5': '1 b3 b5 b7 9',
    'min7#5': '1 b3 #5 b7',

    # Diminished Chords
    'dim7': '1 b3 b5 bb7',
    'dim13': '1 b3 b5 bb7 13',

    # Add Chords (Triads + Extensions)
    'add9': '1 3 5 9',
    'add11': '1 3 5 11',
    'add#11': '1 3 5 #11',
    'add13': '1 3 5 13',
    'add4': '1 3 4 5',
    'add6': '1 3 5 6',

    # chord_formulas.update
    'Maj7b5': '1 3 b5 7',
    'Maj7#5': '1 3 #5 7',
    '7b5#9': '1 3 b5 b7 #9',
    '7b5b13': '1 3 b5 b7 b13',
    'minMaj9': '1 b3 5 7 9',
    'min7b13': '1 b3 5 b7 b13',
    'min13b5': '1 b3 b5 b7 13',

}


INTERVAL_MAP = {
    '1': 0, 'b2': 1, '2': 2, '#2': 3, 'b3': 3, '3': 4, '4': 5, '#4': 6, 'b5': 6, '5': 7,
    '#5': 8, 'b6': 8, '6': 9, 'b7': 10, '7': 11, '9': 14, 'b9': 13, '#9': 15,
    '11': 17, '#11': 18, 'b13': 20, '13': 21
}

def parse_intervals(interval_string):
    interval_map = {
        '1': 0,
        'b2': 1, '2': 2, '#2': 3, 'b3': 3, '3': 4,
        '4': 5, '#4': 6, 'b5': 6, '5': 7, '#5': 8, 'b6': 8,
        '6': 9, '#6': 10, 'b7': 10, '7': 11,
        'b9': 13, '9': 14, '#9': 15,
        '11': 17, '#11': 18,
        'b13': 20, '13': 21
    }

    intervals = []
    steps = interval_string.split()
    for step in steps:
        if step in interval_map:
            intervals.append(interval_map[step])
        else:
            raise ValueError(f"Unknown interval: {step}")
    return intervals

def formula_to_intervals(formula):
    symbols = formula.split()
    intervals = [INTERVAL_MAP[sym] for sym in symbols]
    return intervals

def filter_shell_intervals(intervals):
    essential_degrees = {0, 3, 4, 10, 11}
    extensions = {9, 13, 14, 15, 20, 21}
    altered_fifth = {6, 8}
    sharp_11 = {18}
    natural_11 = {17}

    shell_intervals = []
    for i in intervals:
        if (
            i in essential_degrees
            or i in extensions
            or i in altered_fifth
            or i in sharp_11
            or i in natural_11
        ):
            shell_intervals.append(i)

    return sorted(shell_intervals)


def get_notes(root, intervals):
    root_index = note_names.index(root)
    return [note_names[(root_index + i) % 12] for i in intervals]

@app.route('/')
def index():
    return render_template('index.html')

valid_shell_chords = set([
    'Maj7', 'min7', 'dom7', 'minMaj7', 'halfdim7', 'dim7', 'dim13',
    '6', 'min6', '6/9', 'min6/9',
    '9', 'Maj9', 'min9',
    '11', 'Maj11', 'min11',
    '13', 'Maj13', 'min13',
    '7b5', '7#5', '7b9', '7#9',
    '7b5b9', '7#5b9', '7#5#9',
    '7b9b13', '7#9b13',
    '7b13', '7#13', '7#11', '7b5#9', '7b5b13', '7b9#11',
    'Maj7b5', 'Maj7#5',
    'min7b5', 'min9b5', 'min7#5',
    'min7b13', 'min13b5'
])

@app.route('/generate_chord', methods=['GET'])
def generate_chord():
    difficulty = request.args.get('difficulty', 'easy')
    shell_mode = request.args.get('shell_mode') == 'true'

    if difficulty == 'medium':
        chord_pool = medium_chords
    elif difficulty == 'hard' or difficulty == 'competition':
        chord_pool = hard_chords
    else:
        chord_pool = easy_chords

    root = random.choice(note_names)
    chord_type = random.choice(chord_pool)
    intervals = parse_intervals(chord_formulas[chord_type])

    if shell_mode and chord_type not in valid_shell_chords:
        # Skip this chord and pick a new one if it’s invalid for Shell Mode
        return generate_chord()

    if shell_mode:
        intervals = filter_shell_intervals(intervals)

    correct_notes = get_notes(root, intervals)

    return jsonify({
        'root': root,
        'chord_type': chord_type,
        'correct_notes': correct_notes,
        'intervals': intervals
    })


if __name__ == '__main__':
    app.run(debug=True)

