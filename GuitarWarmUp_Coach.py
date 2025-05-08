from flask import Flask, render_template, request, jsonify
from chordify import ChordLibrary, ScaleLibrary

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

@app.route('/daily_exercise', methods=['GET', 'POST'])
def daily_exercise():
    if request.method == 'POST':
        # Get user input for the exercise
        progression_input = request.form.get('progression')
        scale_name = request.form.get('scale')

        if not progression_input or not scale_name:
            return render_template('daily_exercise.html', error="Please enter a chord progression and a scale.")

        try:
            # Generate chord progression
            chord_names = [chord.strip() for chord in progression_input.split(",")]
            progression = chord_library.create_chord_progression(chord_names)

            # Generate scale diagram
            scale_data = scale_library.get_scale(scale_name)
            scale_positions = scale_data["positions"]
            scale_svg = scale_library.draw_scale(scale_positions)

            # Generate individual chord diagrams, removing duplicates
            chord_svgs = []
            seen_chords = set()
            for chord in progression:
                if chord["name"] not in seen_chords:
                    svg = chord_library.draw_chord(chord["positions"], chord["fingers"])
                    chord_svgs.append({"name": chord["name"], "svg": svg})
                    seen_chords.add(chord["name"])  # Track unique chord names

            return render_template(
                'daily_exercise.html',
                progression=progression,
                scale_name=scale_name,
                scale_svg=scale_svg,
                chord_svgs=chord_svgs  # Pass unique chord diagrams
            )
        except ValueError as e:
            return render_template('daily_exercise.html', error=str(e))
    else:
        # Render the exercise page
        return render_template('daily_exercise.html')

if __name__ == '__main__':
    app.run(debug=True)

