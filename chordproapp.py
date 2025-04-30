from flask import Flask, render_template, request, jsonify
from chordify import ChordLibrary, ScaleLibrary

app = Flask(__name__)
chord_library = ChordLibrary()  # Initialize the chord library
scale_library = ScaleLibrary()  # Initialize the scale library

@app.route('/')
def index():
    # Render the index page (testing.html)
    return render_template('testing.html')

@app.route('/generate_chord_chart_page', methods=['GET', 'POST'])
def generate_chord_chart_page():
    if request.method == 'POST':
        chord_name = request.form.get('chord')
        if not chord_name:
            return render_template('generate_chord_chart.html', error="Please enter a chord name.")

        try:
            # Fetch chord positions and fingerings from the library
            chord_data = chord_library.get_chord(chord_name)
            positions = chord_data["positions"]
            fingers = chord_data["fingers"]
            svg = chord_library.draw_chord(positions, fingers)  # Generate the chord diagram as SVG
            return render_template('generate_chord_chart.html', chord=chord_name, chord_svg=svg)
        except ValueError as e:
            return render_template('generate_chord_chart.html', error=str(e))
        except Exception as e:
            return render_template('generate_chord_chart.html', error="An unexpected error occurred.")
    else:
        # Render the chord chart generation page
        return render_template('generate_chord_chart.html')

@app.route('/generate_scale_page', methods=['GET', 'POST'])
def generate_scale_page():
    if request.method == 'POST':
        scale_name = request.form.get('scale')
        if not scale_name:
            return render_template('scales.html', error="Please enter a scale name.")

        try:
            # Fetch scale positions from the library
            scale_data = scale_library.get_scale(scale_name)
            positions = scale_data["positions"]
            svg = scale_library.draw_scale(positions)  # Generate the scale diagram as SVG
            return render_template('scales.html', scale=scale_name, scale_svg=svg)
        except ValueError as e:
            return render_template('scales.html', error=str(e))
        except Exception as e:
            return render_template('scales.html', error="An unexpected error occurred.")
    else:
        # Render the scale generation page
        return render_template('scales.html')

if __name__ == '__main__':
    app.run(debug=True)

