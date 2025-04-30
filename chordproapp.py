# app.py
from flask import Flask, render_template, request, jsonify
from chordify import ChordLibrary

app = Flask(__name__)
chord_library = ChordLibrary()  # Initialize the chord library

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        chord_name = request.form['chord']
        try:
            # Fetch chord positions and fingerings from the library
            chord_data = chord_library.get_chord(chord_name)
            positions = chord_data["positions"]
            fingers = chord_data["fingers"]
            svg = chord_library.draw_chord(positions, fingers)  # Generate the chord diagram as SVG
            return render_template('testing.html', chord=chord_name, chord_svg=svg)
        except ValueError as e:
            return render_template('testing.html', chord=None, error=str(e))
        except Exception as e:
            return render_template('testing.html', chord=None, error="An unexpected error occurred.")

    return render_template('testing.html', chord=None)

@app.route('/generate_chord_chart', methods=['GET'])
def generate_chord_chart():
    chord_name = request.args.get('chord')
    if not chord_name:
        return jsonify({"error": "Chord is required"}), 400

    try:
        # Fetch chord positions and fingerings from the library
        chord_data = chord_library.get_chord(chord_name)
        positions = chord_data["positions"]
        fingers = chord_data["fingers"]
        svg = chord_library.draw_chord(positions, fingers)  # Generate the chord diagram as SVG
        return jsonify({"positions": positions, "fingers": fingers, "svg": svg})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)

