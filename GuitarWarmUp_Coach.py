from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text
import os, secrets, random
from chordify import ChordLibrary, ScaleLibrary

# Flask App Setup
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database Setup
DATABASE_URI = 'sqlite:///users.db'
engine = create_engine(DATABASE_URI)

with engine.connect() as conn:
    conn.execute(text(
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)'
    ))
    conn.execute(text(
        'CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, user_id INTEGER, exercise_type TEXT, rating INTEGER, scale_name TEXT, scale_key TEXT, shape_name TEXT)'
    ))
    conn.commit()

# Chordify Libraries
chord_library = ChordLibrary()
scale_library = ScaleLibrary()

# Authentication Routes

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup."""
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
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

@app.route('/logout')
def logout():
    """Log the user out and clear the session."""
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# Functional Requirements

@app.route('/')
def index():
    """Show the index page if logged in, otherwise redirect to login."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/scale_diagram', methods=['GET'])
def scale_diagram():
    """Show a random scale diagram, up to a maximum number, weighted by feedback.
    Scales with lower (worse) feedback ratings are more likely to be selected.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        scale_count = int(request.args.get('scale_count', 0))
        max_scales = 5
        if scale_count >= max_scales:
            return render_template('scale_TAB.html', completed=True, max_scales=max_scales)

        all_scales = list(scale_library.patterns.keys())
        all_keys = list(ScaleLibrary.NOTE_TO_FRET.keys())

        # Build all possible (scale, key) pairs
        scale_key_pairs = [(scale, key) for scale in all_scales for key in all_keys]

        # Calculate weights: lower average rating = higher weight
        weights = []
        for scale_name, key in scale_key_pairs:
            ratings = get_scale_ratings(scale_name, key)
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
            else:
                avg_rating = 5  # Neutral default if no feedback
            # Lower ratings (worse feedback) -> higher weight
            weight = 11 - avg_rating  # e.g. rating 1 = weight 10, rating 10 = weight 1
            weights.append(max(weight, 1))  # Avoid zero or negative weights

        # Choose a scale/key pair based on weights
        chosen = random.choices(scale_key_pairs, weights=weights, k=1)[0]
        scale_name, key = chosen

        positions = scale_library.get_scale_positions(scale_name, key)
        scale_svg = scale_library.draw_scale(positions)
        # You can set shape_name based on your logic or randomly for now
        shape_name = random.choice(["barre", "open", "power", "jazz"])
        ratings = get_scale_ratings(scale_name, key)
        return render_template(
            'scale_TAB.html',
            scale_name=scale_name,
            scale_key=key,
            scale_svg=scale_svg,
            scale_count=scale_count + 1,
            max_scales=max_scales,
            shape_name=shape_name,
            ratings=ratings
        )
    except Exception as e:
        return render_template('scale_TAB.html', error=str(e))

@app.route('/chord_progression', methods=['GET', 'POST'])
def chord_progression():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Determine which exercise to show
    exercise_type = request.args.get('exercise_type', 'progression')
    progression_count = int(request.args.get('progression_count', 0))
    single_chord_count = int(request.args.get('single_chord_count', 0))
    max_progressions = 3
    max_single_chords = 3

    # Handle feedback submission
    if request.method == 'POST':
        rating = int(request.form['rating'])
        exercise_type = request.form.get('exercise_type', 'progression')
        progression_count = int(request.form.get('progression_count', 0))
        single_chord_count = int(request.form.get('single_chord_count', 0))
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO feedback (user_id, exercise_type, rating) VALUES (:user_id, :exercise_type, :rating)"),
                {'user_id': session['user_id'], 'exercise_type': exercise_type, 'rating': rating}
            )
            conn.commit()
        flash('Thank you for your feedback!', 'success')
        # Alternate exercise type after feedback
        if exercise_type == 'progression':
            progression_count += 1
            exercise_type = 'single_chord'
        else:
            single_chord_count += 1
            exercise_type = 'progression'
        return redirect(url_for('chord_progression', 
                                exercise_type=exercise_type, 
                                progression_count=progression_count, 
                                single_chord_count=single_chord_count))

    # Completion check
    if progression_count >= max_progressions and single_chord_count >= max_single_chords:
        return render_template('chord_progression.html', completed=True, max_progressions=max_progressions, max_single_chords=max_single_chords)

    # Show progression or single chord
    if exercise_type == 'progression' and progression_count < max_progressions:
        all_chords = list(chord_library.chord_positions.keys())
        chord_names = random.sample(all_chords, min(4, len(all_chords)))
        progression = chord_library.create_chord_progression(chord_names)
        chord_svgs = []
        for chord in progression:
            svg = chord_library.draw_chord(chord["positions"], chord["fingers"], chord["name"])
            chord_svgs.append({"name": chord["name"], "svg": svg})
        return render_template(
            'chord_progression.html',
            exercise_type='progression',
            progression=progression,
            chord_svgs=chord_svgs,
            progression_count=progression_count,
            single_chord_count=single_chord_count,
            max_progressions=max_progressions,
            max_single_chords=max_single_chords,
            show_feedback=True
        )
    elif exercise_type == 'single_chord' and single_chord_count < max_single_chords:
        all_chords = list(chord_library.chord_positions.keys())
        chord_name = random.choice(all_chords)
        chord_data = chord_library.get_chord(chord_name)
        chord_svg = chord_library.draw_chord(chord_data["positions"], chord_data["fingers"], chord_name)
        return render_template(
            'chord_progression.html',
            exercise_type='single_chord',
            single_chord_name=chord_name,
            single_chord_svg=chord_svg,
            progression_count=progression_count,
            single_chord_count=single_chord_count,
            max_progressions=max_progressions,
            max_single_chords=max_single_chords,
            show_feedback=True
        )
    else:
        # If one type is finished, continue with the other
        if progression_count < max_progressions:
            return redirect(url_for('chord_progression', exercise_type='progression', progression_count=progression_count, single_chord_count=single_chord_count))
        else:
            return redirect(url_for('chord_progression', exercise_type='single_chord', progression_count=progression_count, single_chord_count=single_chord_count))


# @app.route('/single_chord', methods=['GET'])
# def single_chord():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     all_chords = list(chord_library.chord_positions.keys())
#     chord_name = random.choice(all_chords)
#     chord_data = chord_library.get_chord(chord_name)
#     chord_svg = chord_library.draw_chord(chord_data["positions"], chord_data["fingers"], chord_name)
#     return render_template('single_chord.html', chord_name=chord_name, chord_svg=chord_svg)


@app.route('/daily_exercise', methods=['GET'])
def daily_exercise():
    """Show a daily exercise (chord progression or scale), up to a maximum per type."""
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

# Feedback Route

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    rating = int(request.form['rating'])
    exercise_type = request.form.get('exercise_type', 'unknown')
    scale_name = request.form.get('scale_name')
    scale_key = request.form.get('scale_key')
    shape_name = request.form.get('shape_name')  # NEW: get shape_name if present
    with engine.connect() as conn:
        if exercise_type == 'scale':
            conn.execute(
                text("INSERT INTO feedback (user_id, exercise_type, rating, scale_name, scale_key, shape_name) VALUES (:user_id, :exercise_type, :rating, :scale_name, :scale_key, :shape_name)"),
                {'user_id': session['user_id'], 'exercise_type': exercise_type, 'rating': rating, 'scale_name': scale_name, 'scale_key': scale_key, 'shape_name': shape_name}
            )
        else:
            conn.execute(
                text("INSERT INTO feedback (user_id, exercise_type, rating) VALUES (:user_id, :exercise_type, :rating)"),
                {'user_id': session['user_id'], 'exercise_type': exercise_type, 'rating': rating}
            )
        conn.commit()
    # Redirect based on exercise_type
    if exercise_type == 'chord_progression':
        progression_count = int(request.form.get('progression_count', 0)) + 1
        return redirect(url_for('chord_progression', progression_count=progression_count))
    elif exercise_type == 'scale':
        scale_count = int(request.form.get('scale_count', 0)) + 1
        return redirect(url_for('scale_diagram', scale_count=scale_count))
    else:
        chord_count = int(request.form.get('chord_count', 0))
        scale_count = int(request.form.get('scale_count', 0))
        if exercise_type == 'chord_progression':
            chord_count += 1
        elif exercise_type == 'scale':
            scale_count += 1
        return redirect(url_for('daily_exercise', chord_count=chord_count, scale_count=scale_count))

def get_scale_ratings(scale_name, scale_key=None):
    """Return a list of ratings for a given scale (and key, if provided)."""
    with engine.connect() as conn:
        if scale_key:
            result = conn.execute(
                text("SELECT rating FROM feedback WHERE exercise_type='scale' AND scale_name=:scale_name AND scale_key=:scale_key"),
                {'scale_name': scale_name, 'scale_key': scale_key}
            )
        else:
            result = conn.execute(
                text("SELECT rating FROM feedback WHERE exercise_type='scale' AND scale_name=:scale_name"),
                {'scale_name': scale_name}
            )
        ratings = [row.rating for row in result.fetchall()]
    return ratings

# Other

@app.route('/about')
def about():
    return render_template('about.html')

# Main

# with engine.connect() as conn:
#     conn.execute(text("DELETE FROM feedback"))
#     conn.commit()

if __name__ == '__main__':
    app.run(debug=True)
