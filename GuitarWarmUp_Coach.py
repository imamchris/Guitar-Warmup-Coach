from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text
import secrets
import random
from chordify import ChordLibrary, ScaleLibrary
from datetime import timedelta

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(minutes=30)

DATABASE_URI = 'sqlite:///users.db'
engine = create_engine(DATABASE_URI)

with engine.connect() as conn:
    conn.execute(text(
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)'
    ))
    conn.execute(text(
        'CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, user_id INTEGER, exercise_type TEXT, rating INTEGER, scale_name TEXT, scale_key TEXT, shape_name TEXT)'
    ))
    try:
        conn.execute(text('ALTER TABLE users ADD COLUMN skill_level TEXT'))
    except Exception:
        pass
    try:
        conn.execute(text('ALTER TABLE feedback ADD COLUMN variation_index INTEGER'))
    except Exception:
        pass
    conn.commit()

chord_library = ChordLibrary()
scale_library = ScaleLibrary()

# Signup and Login Routes

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        try:
            with engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"),
                    {'username': username, 'password_hash': password_hash}
                )
                conn.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('Username already exists. Please choose a different one.', 'danger')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with engine.connect() as conn:
            user = conn.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {'username': username}
            ).fetchone()
            if user and check_password_hash(user.password_hash, password):
                session.permanent = True
                session['user_id'] = user.id
                session['username'] = user.username
                session['skill_level'] = user.skill_level if getattr(user, 'skill_level', None) else None
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# Functional Requirements

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/scale_diagram', methods=['GET'])
def scale_diagram():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        scale_count = int(request.args.get('scale_count', 0))
        max_scales = 5
        if scale_count >= max_scales:
            return render_template('scale_TAB.html', completed=True, max_scales=max_scales)

        skill_level = session.get('skill_level', 'beginner')
        all_scales = [name for name, _ in scale_library.get_available_scales(skill_level)]
        all_keys = list(ScaleLibrary.NOTE_TO_FRET.keys())
        scale_key_pairs = [(scale, key) for scale in all_scales for key in all_keys]
        weights = []
        for scale_name, key in scale_key_pairs:
            ratings = get_scale_ratings(scale_name, key)
            avg_rating = sum(ratings) / len(ratings) if ratings else 5
            weights.append(max(11 - avg_rating, 1))
        chosen = random.choices(scale_key_pairs, weights=weights, k=1)[0]
        scale_name, key = chosen

        positions = scale_library.get_scale_positions(scale_name, key)
        scale_svg = scale_library.draw_scale(positions)
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

    exercise_type = request.args.get('exercise_type', 'progression')
    progression_count = int(request.args.get('progression_count', 0))
    single_chord_count = int(request.args.get('single_chord_count', 0))
    max_progressions = 3
    max_single_chords = 3

    if request.method == 'POST':
        rating = int(request.form['rating'])
        exercise_type = request.form.get('exercise_type', 'progression')
        progression_count = int(request.form.get('progression_count', 0))
        single_chord_count = int(request.form.get('single_chord_count', 0))
        chord_name = request.form.get('chord_name')
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO feedback (user_id, exercise_type, rating, chord_name) VALUES (:user_id, :exercise_type, :rating, :chord_name)"),
                {'user_id': session['user_id'], 'exercise_type': exercise_type, 'rating': rating, 'chord_name': chord_name}
            )
            conn.commit()
        flash('Thank you for your feedback!', 'success')
        if exercise_type == 'progression':
            progression_count += 1
            exercise_type = 'single_chord'
        else:
            single_chord_count += 1
            exercise_type = 'progression'
        return redirect(url_for(
            'chord_progression',
            exercise_type=exercise_type,
            progression_count=progression_count,
            single_chord_count=single_chord_count
        ))

    if progression_count >= max_progressions and single_chord_count >= max_single_chords:
        return render_template(
            'chord_progression.html',
            completed=True,
            max_progressions=max_progressions,
            max_single_chords=max_single_chords
        )

    if exercise_type == 'progression' and progression_count < max_progressions:
        all_chords = list(chord_library.chord_positions.keys())
        chord_names = random.sample(all_chords, min(4, len(all_chords)))
        progression = chord_library.create_chord_progression(chord_names)
        chord_svgs = [
            {"name": chord["name"], "svg": chord_library.draw_chord(chord["positions"], chord["fingers"], chord["name"])}
            for chord in progression
        ]
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
        chord_data = chord_library.chord_positions.get(chord_name)
        if chord_data is None:
            chord_data = chord_library.chord_positions[next(iter(chord_library.chord_positions))]
            flash(f"Chord '{chord_name}' not found. Showing a default chord.", "warning")
        # FIX: Select the first variation if chord_data is a list
        if isinstance(chord_data, list):
            chord_data = chord_data[0]
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
        if progression_count < max_progressions:
            return redirect(url_for(
                'chord_progression',
                exercise_type='progression',
                progression_count=progression_count,
                single_chord_count=single_chord_count
            ))
        else:
            return redirect(url_for(
                'chord_progression',
                exercise_type='single_chord',
                progression_count=progression_count,
                single_chord_count=single_chord_count
            ))

@app.route('/daily_exercise', methods=['GET'])
def daily_exercise():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    chord_count = int(request.args.get('chord_count', 0))
    scale_count = int(request.args.get('scale_count', 0))
    max_chords = 5
    max_scales = 2

    available_types = []
    if chord_count < max_chords:
        available_types.append("single_chord")
    if scale_count < max_scales:
        available_types.append("scale")
    if not available_types:
        return render_template('daily_exercise.html', completed=True)

    exercise_type = random.choice(available_types)
    skill_level = session.get('skill_level', 'beginner')

    if exercise_type == "single_chord":
        chord_name, variation_index, label = pick_weighted_chord_variation(skill_level)
        chord_data = chord_library.get_chord(chord_name, variation_index)
        chord_svg = chord_library.draw_chord(
            chord_data["positions"], chord_data["fingers"], f"{chord_name} ({label})"
        )
        return render_template(
            'daily_exercise.html',
            exercise_type=exercise_type,
            chord_name=chord_name,
            variation_index=variation_index,
            chord_label=label,
            chord_svg=chord_svg,
            chord_count=chord_count + 1,
            scale_count=scale_count
        )
    else:
        all_scales = [name for name, _ in scale_library.get_available_scales(skill_level)]
        if not all_scales:
            return render_template(
                'daily_exercise.html',
                completed=True,
                message="No scales available for your skill level."
            )
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

@app.route('/tutorial')
def tutorial():
    chord_name = "A"
    chord_data = chord_library.get_chord(chord_name)
    chord_svg = chord_library.draw_chord(chord_data["positions"], chord_data["fingers"], chord_name)

    scale_name = "Minor Pentatonic"
    scale_key = "A"
    scale_positions = scale_library.get_scale_positions(scale_name, scale_key)
    scale_svg = scale_library.draw_scale(scale_positions)

    return render_template('tutorial.html', chord_svg=chord_svg, scale_svg=scale_svg)

@app.route('/set_skill_level', methods=['POST'])
def set_skill_level():
    if 'user_id' not in session:
        return '', 401
    level = request.json.get('level')
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE users SET skill_level=:level WHERE id=:user_id"),
            {'level': level, 'user_id': session['user_id']}
        )
        conn.commit()
    session['skill_level'] = level
    return '', 204

# Feedback Submission

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    rating = int(request.form['rating'])
    exercise_type = request.form.get('exercise_type', 'unknown')
    scale_name = request.form.get('scale_name')
    scale_key = request.form.get('scale_key')
    shape_name = request.form.get('shape_name')
    chord_name = request.form.get('chord_name')
    variation_index = request.form.get('variation_index')

    with engine.connect() as conn:
        if exercise_type == 'scale':
            conn.execute(
                text("INSERT INTO feedback (user_id, exercise_type, rating, scale_name, scale_key, shape_name) VALUES (:user_id, :exercise_type, :rating, :scale_name, :scale_key, :shape_name)"),
                {'user_id': session['user_id'], 'exercise_type': exercise_type, 'rating': rating, 'scale_name': scale_name, 'scale_key': scale_key, 'shape_name': shape_name}
            )
        elif exercise_type == 'single_chord':
            conn.execute(
                text("INSERT INTO feedback (user_id, exercise_type, rating, chord_name, variation_index) VALUES (:user_id, :exercise_type, :rating, :chord_name, :variation_index)"),
                {'user_id': session['user_id'], 'exercise_type': exercise_type, 'rating': rating, 'chord_name': chord_name, 'variation_index': variation_index}
            )
        else:
            conn.execute(
                text("INSERT INTO feedback (user_id, exercise_type, rating) VALUES (:user_id, :exercise_type, :rating)"),
                {'user_id': session['user_id'], 'exercise_type': exercise_type, 'rating': rating}
            )
        conn.commit()
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
        return [row.rating for row in result.fetchall()]

def get_chord_ratings(chord_name):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT rating FROM feedback WHERE exercise_type='single_chord' AND chord_name=:chord_name"),
            {'chord_name': chord_name}
        )
        return [row.rating for row in result.fetchall()]

def get_available_chords(skill_level):
    if skill_level == 'beginner':
        return [
            name for name, variations in chord_library.chord_positions.items()
            if variations and variations[0].get('level', 'beginner') == 'beginner'
        ]
    elif skill_level == 'intermediate':
        return [
            name for name, variations in chord_library.chord_positions.items()
            if variations and variations[0].get('level', 'beginner') in ['beginner', 'intermediate']
        ]
    else:
        return list(chord_library.chord_positions.keys())

def pick_weighted_chord_variation(skill_level):
    available = chord_library.get_all_chord_variations(skill_level)
    weights = []
    for name, idx, label in available:
        ratings = get_chord_variation_ratings(name, idx)
        avg_rating = sum(ratings) / len(ratings) if ratings else 5
        weights.append(max(11 - avg_rating, 1))
    chosen = random.choices(available, weights=weights, k=1)[0]
    return chosen

def get_chord_variation_ratings(chord_name, variation_index):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT rating FROM feedback WHERE exercise_type='single_chord' AND chord_name=:chord_name AND variation_index=:variation_index"),
            {'chord_name': chord_name, 'variation_index': variation_index}
        )
    return [row.rating for row in result.fetchall()]

# Other Routes

@app.route('/about')
def about():
    scale_name = "Minor Pentatonic"
    scale_key = "A"
    scale_positions = scale_library.get_scale_positions(scale_name, scale_key)
    scale_svg = scale_library.draw_scale(scale_positions)
    return render_template('about.html', scale_svg=scale_svg, scale_name=scale_name, scale_key=scale_key)

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST' and 'skill_level' in request.form:
        new_level = request.form['skill_level']
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE users SET skill_level=:level WHERE id=:user_id"),
                {'level': new_level, 'user_id': session['user_id']}
            )
            conn.commit()
        session['skill_level'] = new_level
        flash('Skill level updated!', 'success')
        return redirect(url_for('preferences'))

    if request.method == 'POST' and 'delete_pattern' in request.form:
        pattern_type = request.form['pattern_type']
        if pattern_type == 'single_chord':
            chord_name = request.form['chord_name']
            variation_index = int(request.form['variation_index'])
            with engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM feedback WHERE user_id=:user_id AND exercise_type='single_chord' AND chord_name=:chord_name AND variation_index=:variation_index"),
                    {'user_id': session['user_id'], 'chord_name': chord_name, 'variation_index': variation_index}
                )
                conn.commit()
        elif pattern_type == 'scale':
            scale_name = request.form['scale_name']
            scale_key = request.form['scale_key']
            with engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM feedback WHERE user_id=:user_id AND exercise_type='scale' AND scale_name=:scale_name AND scale_key=:scale_key"),
                    {'user_id': session['user_id'], 'scale_name': scale_name, 'scale_key': scale_key}
                )
                conn.commit()
        flash('All feedback for this pattern deleted.', 'success')
        
    with engine.connect() as conn:
        chord_feedback = conn.execute(
            text("""
                SELECT chord_name, variation_index, AVG(rating) as avg_rating, COUNT(*) as count
                FROM feedback
                WHERE user_id=:user_id AND exercise_type='single_chord'
                GROUP BY chord_name, variation_index
            """),
            {'user_id': session['user_id']}
        ).fetchall()

        scale_feedback = conn.execute(
            text("""
                SELECT scale_name, scale_key, AVG(rating) as avg_rating, COUNT(*) as count
                FROM feedback
                WHERE user_id=:user_id AND exercise_type='scale'
                GROUP BY scale_name, scale_key
            """),
            {'user_id': session['user_id']}
        ).fetchall()

    skill_level = session.get('skill_level', 'beginner')
    return render_template(
        'preferences.html',
        chord_feedback=chord_feedback,
        scale_feedback=scale_feedback,
        skill_level=skill_level
    )

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

if __name__ == '__main__':
    app.run(debug=True)
