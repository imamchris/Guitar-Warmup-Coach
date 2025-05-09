from flask import Flask, render_template, request, jsonify
from chordify import ChordLibrary, ScaleLibrary
import random  # Import the random module

app = Flask(__name__)
chord_library = ChordLibrary()  # Initialize the chord library
scale_library = ScaleLibrary()  # Initialize the scale library

@app.route('/')
def index():
    # Render the index page (index.html)
    return render_template('index.html')

@app.route('/scale_diagram', methods=['GET', 'POST'])
def scale_diagram():
    if request.method == 'POST':
        scale_name = request.form.get('scale')  # Fixed missing scale_name assignment
        if not scale_name:
            return render_template('scale_TAB.html', error="Please enter a scale name.")

        try:
            # Fetch scale positions from the library
            scale_data = scale_library.get_scale(scale_name)
            positions = scale_data["positions"]
            svg = scale_library.draw_scale(positions)  # Generate the scale diagram as SVG
            return render_template('scale_TAB.html', scale=scale_name, scale_svg=svg)
        except ValueError as e:
            return render_template('scale_TAB.html', error=str(e))
        except Exception as e:
            return render_template('scale_TAB.html', error="An unexpected error occurred.")
    else:
        # Render the scale generation page
        return render_template('scale_TAB.html')

@app.route('/chord_progression', methods=['GET', 'POST'])
def chord_progression():
    if request.method == 'POST':
        progression_input = request.form.get('progression')
        if not progression_input:
            return render_template('chord_progression.html', error="Please enter a chord progression.")

        try:
            # Parse the input into a list of chord names
            chord_names = [chord.strip() for chord in progression_input.split(",")]
            progression = chord_library.create_chord_progression(chord_names)

            # Generate chord charts for each chord in the progression
            chord_svgs = []
            for chord in progression:
                svg = chord_library.draw_chord(chord["positions"], chord["fingers"])
                chord_svgs.append({"name": chord["name"], "svg": svg})

            return render_template(
                'chord_progression.html',
                progression=progression,
                chord_svgs=chord_svgs
            )
        except ValueError as e:
            return render_template('chord_progression.html', error=str(e))
    else:
        # Render the chord progression page
        return render_template('chord_progression.html')

@app.route('/daily_exercise', methods=['GET'])
def daily_exercise():
    try:
        # Randomly select a chord progression
        all_chords = list(chord_library.chord_positions.keys())
        progression = random.sample(all_chords, min(4, len(all_chords)))  # Select 4 random chords

        # Randomly select a scale
        all_scales = list(scale_library.scales.keys())
        scale_name = random.choice(all_scales)

        # Generate chord progression data
        progression_data = chord_library.create_chord_progression(progression)

        # Generate scale diagram
        scale_data = scale_library.get_scale(scale_name)
        scale_positions = scale_data["positions"]
        scale_svg = scale_library.draw_scale(scale_positions)

        # Generate individual chord diagrams
        chord_svgs = []
        for chord in progression_data:
            svg = chord_library.draw_chord(chord["positions"], chord["fingers"])
            chord_svgs.append({"name": chord["name"], "svg": svg})

        return render_template(
            'daily_exercise.html',
            progression=progression_data,
            scale_name=scale_name,
            scale_svg=scale_svg,
            chord_svgs=chord_svgs
        )
    except ValueError as e:
        return render_template('daily_exercise.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)

