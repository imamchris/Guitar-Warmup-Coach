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

@app.route('/scale_diagram', methods=['GET'])
def scale_diagram():
    try:
        # Randomly select a scale
        all_scales = list(scale_library.scales.keys())
        scale_name = random.choice(all_scales)

        # Fetch scale positions from the library
        scale_data = scale_library.get_scale(scale_name)
        positions = scale_data["positions"]
        svg = scale_library.draw_scale(positions)  # Generate the scale diagram as SVG

        return render_template('scale_TAB.html', scale=scale_name, scale_svg=svg)
    except ValueError as e:
        return render_template('scale_TAB.html', error=str(e))
    except Exception as e:
        return render_template('scale_TAB.html', error="An unexpected error occurred.")

@app.route('/chord_progression', methods=['GET'])
def chord_progression():
    try:
        # Randomly generate a chord progression
        all_chords = list(chord_library.chord_positions.keys())
        chord_names = random.sample(all_chords, min(4, len(all_chords)))  # Select 4 random chords

        # Generate chord progression data
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

@app.route('/daily_exercise', methods=['GET'])
def daily_exercise():
    # Get counts from query params (default to 0)
    chord_count = int(request.args.get('chord_count', 0))
    scale_count = int(request.args.get('scale_count', 0))
    max_per_type = 2

    # Decide which exercise types are still available
    available_types = []
    if chord_count < max_per_type:
        available_types.append("chord_progression")
    if scale_count < max_per_type:
        available_types.append("scale")

    # If all exercises are done, show completion
    if not available_types:
        return render_template('daily_exercise.html', completed=True)

    # Randomly pick an available exercise type
    exercise_type = random.choice(available_types)

    if exercise_type == "chord_progression":
        show_chord_charts = random.choice([True, False])
        all_chords = list(chord_library.chord_positions.keys())
        progression = random.sample(all_chords, min(4, len(all_chords)))
        progression_data = chord_library.create_chord_progression(progression)
        chord_svgs = []
        hidden_chord_svgs = []
        if show_chord_charts:
            for chord in progression_data:
                svg = chord_library.draw_chord(chord["positions"], chord["fingers"], chord["name"])
                chord_svgs.append({"name": chord["name"], "svg": svg})
        else:
            for chord in progression_data:
                svg = chord_library.draw_chord(chord["positions"], chord["fingers"], chord["name"])
                hidden_chord_svgs.append({"name": chord["name"], "svg": svg})
        return render_template(
            'daily_exercise.html',
            exercise_type=exercise_type,
            progression=progression_data,
            chord_svgs=chord_svgs,
            hidden_chord_svgs=hidden_chord_svgs,
            show_chord_charts=show_chord_charts,
            chord_count=chord_count + 1,
            scale_count=scale_count
        )
    else:  # scale
        all_scales = list(scale_library.scales.keys())
        scale_name = random.choice(all_scales)
        scale_data = scale_library.get_scale(scale_name)
        scale_positions = scale_data["positions"]
        scale_svg = scale_library.draw_scale(scale_positions)
        return render_template(
            'daily_exercise.html',
            exercise_type=exercise_type,
            scale_name=scale_name,
            scale_svg=scale_svg,
            chord_count=chord_count,
            scale_count=scale_count + 1
        )

if __name__ == '__main__':
    app.run(debug=True)

