from flask import Flask, render_template, request, jsonify
from chordify import ChordLibrary, ScaleLibrary

app = Flask(__name__)
chord_library = ChordLibrary()  # Initialize the chord library
scale_library = ScaleLibrary()  # Initialize the scale library

@app.route('/')
def index():
    # Render the index page (index.html)
    return render_template('index.html')

@app.route('/chord_chart', methods=['GET', 'POST'])
def chord_chart():
    if request.method == 'POST':
        chord_name = request.form.get('chord')
        if not chord_name:
            return render_template('chord_chart.html', error="Please enter a chord name.")

        try:
            # Fetch chord positions and fingerings from the library
            chord_data = chord_library.get_chord(chord_name)
            positions = chord_data["positions"]
            fingers = chord_data["fingers"]
            svg = chord_library.draw_chord(positions, fingers)  # Generate the chord diagram as SVG
            return render_template('chord_chart.html', chord=chord_name, chord_svg=svg)
        except ValueError as e:
            return render_template('chord_chart.html', error=str(e))
        except Exception as e:
            return render_template('chord_chart.html', error="An unexpected error occurred.")
    else:
        # Render the chord chart generation page
        return render_template('chord_chart.html')

@app.route('/scale_diagram', methods=['GET', 'POST'])
def scale_diagram():
    if request.method == 'POST':
        scale_name = request.form.get('scale')
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
            return render_template('chord_progression.html', progression=progression)
        except ValueError as e:
            return render_template('chord_progression.html', error=str(e))
    else:
        # Render the chord progression page
        return render_template('chord_progression.html')

if __name__ == '__main__':
    app.run(debug=True)

