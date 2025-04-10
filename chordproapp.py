from flask import Flask, request, jsonify

import chordify  # Assuming chodify.py contains the required functions

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Guitar Warmup Coach API!"

@app.route('/generate_chord_chart', methods=['POST'])
def generate_chord_chart():
    data = request.json
    chord = data.get('chord')
    if not chord:
        return jsonify({"error": "Chord is required"}), 400
    chart = chordify.generate_chord_chart(chord)  # Replace with actual function from chodify.py
    return jsonify({"chord": chord, "chart": chart})

@app.route('/generate_progression', methods=['POST'])
def generate_progression():
    data = request.json
    key = data.get('key')
    progression_type = data.get('type', 'default')
    if not key:
        return jsonify({"error": "Key is required"}), 400
    progression = chordify.generate_progression(key, progression_type)  # Replace with actual function
    return jsonify({"key": key, "type": progression_type, "progression": progression})

@app.route('/generate_scale', methods=['POST'])
def generate_scale():
    data = request.json
    scale = data.get('scale')
    if not scale:
        return jsonify({"error": "Scale is required"}), 400
    scale_data = chordify.generate_scale(scale)  # Replace with actual function
    return jsonify({"scale": scale, "data": scale_data})

if __name__ == '__main__':
    app.run(debug=True)