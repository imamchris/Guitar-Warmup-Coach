from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text
import os, secrets, random
from chordify import ChordLibrary, ScaleLibrary

app = Flask(__name__) # creation of flask app
app.secret_key = secrets.token_hex(16) # Generate a random secret key for session management

# Creation of SQLite database
DATABASE_URI = 'sqlite:///users.db'
engine = create_engine(DATABASE_URI) # Database generation if not pre-existing

with engine.connect() as conn:
    conn.execute(text('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)'))
    conn.commit()

# Core Functional requirements of the Application

chord_library = ChordLibrary() # Create instances of ChordLibrary and ScaleLibrary
scale_library = ScaleLibrary()

@app.route('/')
def index():
    """Show the index page if logged in, otherwise redirect to login."""
    # ... (function body can be collapsed in IDE)
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/scale_diagram', methods=['GET'])
def scale_diagram():
    """Show a random scale diagram, up to a maximum number."""
    # ... (function body can be collapsed in IDE)
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        scale_count = int(request.args.get('scale_count', 0))
        max_scales = 5
        if scale_count >= max_scales:
            return render_template('scale_TAB.html', completed=True, max_scales=max_scales)
        all_scales = list(scale_library.patterns.keys())
        all_keys = list(ScaleLibrary.NOTE_TO_FRET.keys())
        scale_name = random.choice(all_scales)
        key = random.choice(all_keys)
        positions = scale_library.get_scale_positions(scale_name, key)
        scale_svg = scale_library.draw_scale(positions)
        return render_template(
            'scale_TAB.html',
            scale_name=scale_name,
            scale_key=key,
            scale_svg=scale_svg,
            scale_count=scale_count + 1,
            max_scales=max_scales
        )
    except Exception as e:
        return render_template('scale_TAB.html', error=str(e))

@app.route('/chord_progression', methods=['GET'])
def chord_progression():
    """Show a random chord progression, up to a maximum number."""
    # ... (function body can be collapsed in IDE)
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        progression_count = int(request.args.get('progression_count', 0))
        max_progressions = 3
        if progression_count >= max_progressions:
            return render_template('chord_progression.html', completed=True, max_progressions=max_progressions)
        all_chords = list(chord_library.chord_positions.keys())
        chord_names = random.sample(all_chords, min(4, len(all_chords)))
        progression = chord_library.create_chord_progression(chord_names)
        chord_svgs = []
        for chord in progression:
            svg = chord_library.draw_chord(chord["positions"], chord["fingers"], chord["name"])
            chord_svgs.append({"name": chord["name"], "svg": svg})
        return render_template(
            'chord_progression.html',
            progression=progression,
            chord_svgs=chord_svgs,
            progression_count=progression_count + 1,
            max_progressions=max_progressions
        )
    except Exception as e:
        return render_template('chord_progression.html', error=str(e))

@app.route('/daily_exercise', methods=['GET'])
def daily_exercise():
    """Show a daily exercise (chord progression or scale), up to a maximum per type."""
    # ... (function body can be collapsed in IDE)
    if 'user_id' not in session:
        return redirect(url_for('login'))
    chord_count = int(request.args.get('chord_count', 0))
    scale_count = int(request.args.get('scale_count', 0))
    max_per_type = 2
    available_types = []
    if chord_count < max_per_type:
        available_types.append("chord_progression")
    if scale_count < max_per_type:
        available_types.append("scale")
    if not available_types:
        return render_template('daily_exercise.html', completed=True)
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
    else:
        all_scales = list(scale_library.patterns.keys())
        all_keys = list(ScaleLibrary.NOTE_TO_FRET.keys())
        scale_name = random.choice(all_scales)
        key = random.choice(all_keys)
        positions = scale_library.get_scale_positions(scale_name, key)
        scale_svg = scale_library.draw_scale(positions)
        return render_template(
            'daily_exercise.html',
            exercise_type=exercise_type,
            scale_name=scale_name,
            scale_key=key,
            scale_svg=scale_svg,
            chord_count=chord_count,
            scale_count=scale_count + 1
        )

# Signup and Login Functions

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # ... (function body can be collapsed in IDE)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with engine.connect() as conn:
            user = conn.execute(text("SELECT * FROM users WHERE username = :username"), {'username': username}).fetchone()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup."""
    # ... (function body can be collapsed in IDE)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        try:
            with engine.connect() as conn:
                conn.execute(text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"),
                             {'username': username, 'password_hash': password_hash})
                conn.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('Username already exists. Please choose a different one.', 'danger')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Log the user out and clear the session."""
    # ... (function body can be collapsed in IDE)
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login')
)


if __name__ == '__main__':
    app.run(debug=True)

