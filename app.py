from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

note_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

easy_chords = [
    'Maj', 'min', 'dim', 'aug',
    'sus2', 'sus4',

]


medium_chords = [
    'min6/9', 'Maj7', 'min7', '7',
    '6', 'min6', '6/9',
    'add9', 'add4', 'add6',
    '9', 'Maj9', 'min9',
    '11', 'Maj11', 'min11',
    '13', 'Maj13', 'min13',
    'Maj7#11', 'Maj9#11',
    '7sus4', '9sus4', '13sus4',
    'add11', 'add#11', 'add13'
]


hard_chords = [
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
    '7': '1 3 5 b7',

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
    'halfdim7': '1 b3 b5 b7',

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
    '#5': 8, 'b6': 8, '6': 9, 'bb7': 9, 'b7': 10, '7': 11, '9': 14, 'b9': 13, '#9': 15,
    '11': 17, '#11': 18, 'b13': 20, '13': 21, '#13': 22
}


def parse_intervals(interval_string):
    interval_map = {
        '1': 0, 'b2': 1, '2': 2, '#2': 3, 'b3': 3, '3': 4,
        '4': 5, '#4': 6, 'b5': 6, '5': 7, '#5': 8, 'b6': 8,
        '6': 9, 'bb7': 9, '#6': 10, 'b7': 10, '7': 11,
        'b9': 13, '9': 14, '#9': 15,
        '11': 17, '#11': 18,
        'b13': 20, '13': 21, '#13': 22
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

# --- Accurate diatonic spelling for scales ---


SEMITONE_MAP = {
    'C': 0, 'B#': 0,
    'C#': 1, 'Db': 1,
    'D': 2,
    'D#': 3, 'Eb': 3,
    'E': 4, 'Fb': 4,
    'E#': 5, 'F': 5,
    'F#': 6, 'Gb': 6,
    'G': 7,
    'G#': 8, 'Ab': 8,
    'A': 9,
    'A#': 10, 'Bb': 10,
    'B': 11, 'Cb': 11,
}

# pitch-class -> all enharmonics (shortest names first for a sane fallback)
PC_TO_NAMES = {
    pc: [n for n, v in SEMITONE_MAP.items() if v == pc and len(n) <= 2]
    for pc in range(12)
}

NOTE_LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']


def _preferred_accidental_for_root(root: str) -> str:
    """If root has flats, prefer flats; if sharps, prefer sharps; else neutral."""
    if 'b' in root:
        return 'flat'
    if '#' in root:
        return 'sharp'
    return 'neutral'


def _choose_enharmonic(pc: int, target_letter: str, preference: str) -> str:
    """Pick the enharmonic that matches the target letter; else prefer flats/sharps; else first."""
    candidates = PC_TO_NAMES[pc]
    # 1) exact letter match (e.g., want 'C' vs 'B'/'C')
    for n in candidates:
        if n[0] == target_letter:
            return n
    # 2) prefer flats or sharps based on root
    if preference == 'flat':
        for n in candidates:
            if 'b' in n:
                return n
    if preference == 'sharp':
        for n in candidates:
            if '#' in n:
                return n
    # 3) fallback
    return candidates[0]


def get_scale_notes(root: str, intervals: list[int]) -> list[str]:
    """
    Build a *scale* with correct diatonic letters (A→B→C→...).
    Assumes intervals are ascending semitones from root (no octave 12 included).
    """
    root_pc = SEMITONE_MAP[root]
    pref = _preferred_accidental_for_root(root)
    # rotate letters so we start from root's letter
    start_letter = root[0]
    start_idx = NOTE_LETTERS.index(start_letter)
    letter_cycle = NOTE_LETTERS[start_idx:] + NOTE_LETTERS[:start_idx]

    notes = []
    for i, semi in enumerate(intervals):
        pc = (root_pc + semi) % 12
        target_letter = letter_cycle[i % 7]
        note_name = _choose_enharmonic(pc, target_letter, pref)
        notes.append(note_name)
    return notes


@app.route('/')
def index():
    return render_template('index.html')


valid_shell_chords = set([
    'Maj7', 'min7', '7', 'minMaj7', 'halfdim7', 'dim7', 'dim13',
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
    app.logger.info(f"[generate_chord] {root}{chord_type}")
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


@app.route('/generate_scale', methods=['GET'])
def generate_scale():
    """
    Generate a scale prompt according to the chosen difficulty *within* Scale mode.
    Returns:
        {
          'root': 'D',
          'scale_type': 'dorian',         # machine label
          'correct_notes': [...],         # ordered from root up to 7th degree (no octave)
          'intervals': [...]              # semitones from root
        }
    """
    difficulty = request.args.get('difficulty', 'easy')

    # Core interval blueprints (semitones from root, 0..11; 7-note scales omit the octave 12)
    scale_intervals = {
        # Basics
        'major':           [0, 2, 4, 5, 7, 9, 11],  # Ionian
        'natural_minor':   [0, 2, 3, 5, 7, 8, 10],  # Aeolian
        'harmonic_minor':  [0, 2, 3, 5, 7, 8, 11],
        'melodic_minor':   [0, 2, 3, 5, 7, 9, 11],  # ascending form

        # Church modes (relative to major)
        'ionian':          [0, 2, 4, 5, 7, 9, 11],
        'dorian':          [0, 2, 3, 5, 7, 9, 10],
        'phrygian':        [0, 1, 3, 5, 7, 8, 10],
        'lydian':          [0, 2, 4, 6, 7, 9, 11],
        'mixolydian':      [0, 2, 4, 5, 7, 9, 10],
        'aeolian':         [0, 2, 3, 5, 7, 8, 10],
        'locrian':         [0, 1, 3, 5, 6, 8, 10],

        # Symmetric scales
        'whole_tone':      [0, 2, 4, 6, 8, 10],           # 6-note
        # H-W diminished (dominant)
        'dim_half_whole':  [0, 1, 3, 4, 6, 7, 9, 10],
        # W-H diminished (fully dim)
        'dim_whole_half':  [0, 2, 3, 5, 6, 8, 9, 11],
    }

    # Allowed labels by difficulty (within Scale mode)
    allowed_by_difficulty = {
        'easy': [
            'major', 'natural_minor'
        ],
        'medium': [
            # keep basics + church modes
            'ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian'
        ],
        'hard': [
            # medium + advanced minor + symmetric
            'harmonic_minor', 'melodic_minor',
            'whole_tone', 'dim_half_whole', 'dim_whole_half'
        ],
        'competition': [
            # same as hard
            'major', 'natural_minor',
            'ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian',
            'harmonic_minor', 'melodic_minor',
            'whole_tone', 'dim_half_whole', 'dim_whole_half'
        ]
    }

    allowed = allowed_by_difficulty.get(
        difficulty, allowed_by_difficulty['easy'])
    scale_type = random.choice(allowed)
    root = random.choice(note_names)

    intervals = scale_intervals[scale_type]
    notes = get_scale_notes(root, intervals)  # uses your new 12-name flat map

    return jsonify({
        'root': root,
        'scale_type': scale_type,
        'correct_notes': notes,
        'intervals': intervals
    })


@app.route('/self_test_hard')
def self_test_hard():
    import traceback
    import random
    fails = []
    for _ in range(500):
        chord_type = random.choice(hard_chords)
        try:
            intervals = parse_intervals(chord_formulas[chord_type])
        except Exception as e:
            fails.append({"chord_type": chord_type, "error": str(e)})
    return jsonify({"fail_count": len(fails), "fails": fails[:10]})


def validate_chords():
    bad = []
    for name, formula in chord_formulas.items():
        try:
            parse_intervals(formula)  # will raise if token unknown
        except Exception as e:
            bad.append((name, str(e)))
    if bad:
        print("\n[Chord Validator] Problems found:")
        for n, msg in bad:
            print(f"  - {n}: {msg}")
    else:
        print("\n[Chord Validator] All chord formulas parse OK.")


validate_chords()

if __name__ == '__main__':
    app.run(debug=True)
