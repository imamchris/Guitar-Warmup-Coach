class ChordLibrary:
    def __init__(self):
        # Chord definitions. Barre chords have a 'barre' key.
        self.chord_positions = {
            "F": {"positions": [1, 3, 3, 2, 0, 1],"fingers": [1, 3, 4, 2, 0, 1], "barre": {"fret": 1, "from_string": 0, "to_string": 5}},
            "C": {"positions": [-1, 1, 3, 3, 3, 1],"fingers": [0, 1, 2, 3, 4, 1], "barre": {"fret": 1, "from_string": 0, "to_string": 5}},
            "Fm": {"positions": [1, 3, 3, 0, 0, 1],"fingers": [1, 3, 4, 0, 0, 1], "barre": {"fret": 1, "from_string": 0, "to_string": 5}},
            "Cm": {"positions": [-1, 1, 3, 3, 2, 1],"fingers": [0, 1, 3, 4, 2, 1], "barre": {"fret": 1, "from_string": 0, "to_string": 5}},
            "Fsus4": {"positions": [1, 3, 3, 3, 0, 1],"fingers": [1, 2, 3, 4, 0, 1], "barre": {"fret": 1, "from_string": 0, "to_string": 5}},
            "Csus4": {"positions": [-1, 1, 3, 3, 4, 1],"fingers": [0, 1, 2, 3, 4, 1], "barre": {"fret": 1, "from_string": 0, "to_string": 5}},
            "F7": {"positions": [1, 0, 2, 3, 1, -1],"fingers": [1, 0, 2, 3, 1, 0], "barre": {"fret": 1, "from_string": 0, "to_string": 5}},


            "G": {"positions": [3, 2, 0, 0, 3, 3], "fingers": [2, 1, 0, 0, 3, 4]},
            "C": {"positions": [-1, 3, 2, 0, 1, 0], "fingers": [0, 3, 2, 0, 1, 0]},
            "D": {"positions": [-1, -1, 0, 2, 3, 2], "fingers": [0, 0, 0, 1, 3, 2]},
            "Em": {"positions": [0, 2, 2, 0, 0, 0], "fingers": [0, 2, 3, 0, 0, 0]},
            "A": {"positions": [-1, 0, 2, 2, 2, 0], "fingers": [0, 0, 1, 2, 3, 0]},
            "B": {"positions": [-1, 2, 4, 4, 4, 2], "fingers": [0, 1, 3, 4, 2, 1]},
            "E": {"positions": [0, 2, 2, 1, 0, 0], "fingers": [0, 2, 3, 1, 0, 0]},


            
            # Add more barre chords as needed...
        }

    def get_chord(self, chord_name):
        """Get chord data by name."""
        return self.chord_positions[chord_name]

    def get_movable_chord(self, base_name, fret):
        """
        Move a barre chord shape to a new fret.
        Only works for chords with a 'barre' key.
        """
        base = self.get_chord(base_name)
        if "barre" not in base:
            raise ValueError("Not a movable barre chord.")
        shift = fret - base["barre"]["fret"]
        # Shift all positions by the fret difference
        new_positions = [
            (p + shift if p not in (None, -1, 0) else p)
            for p in base["positions"]
        ]
        # Update barre info
        new_barre = base["barre"].copy()
        new_barre["fret"] = fret
        return {
            "positions": new_positions,
            "fingers": base["fingers"],
            "barre": new_barre
        }

    def draw_chord(self, frets, fingers, chord_name="", barre=None):
        top_margin = 20
        svg = [
            '<svg width="200" height="250" xmlns="http://www.w3.org/2000/svg">',
            f'<text x="115" y="{top_margin}" text-anchor="middle" font-size="20" font-weight="bold" fill="black">{chord_name}</text>',
        ]
        # Draw strings
        for string_index in range(6):
            string_x = 40 + (string_index * 30)
            svg.append(f'<line x1="{string_x}" y1="{50+top_margin}" x2="{string_x}" y2="{210+top_margin}" stroke="black" stroke-width="2"/>')
        
        # Draw frets
        for fret_index in range(5):
            fret_y = 50 + (fret_index * 40) + top_margin
            svg.append(f'<line x1="40" y1="{fret_y}" x2="190" y2="{fret_y}" stroke="black" stroke-width="3"/>')
        svg.append(f'<line x1="39" y1="{50+top_margin}" x2="191" y2="{50+top_margin}" stroke="black" stroke-width="5"/>')
        
        # Draw barre if present
        if barre:
            fret = barre["fret"]
            from_x = 40 + (barre["from_string"] * 30)
            to_x = 40 + (barre["to_string"] * 30)
            y = 50 + ((fret - 1) * 40) + 20 + top_margin
            svg.append(f'<rect x="{from_x-7}" y="{y-8}" width="{to_x-from_x+14}" height="16" rx="8" fill="#222" opacity="0.7"/>')

        # Open/muted strings
        for string_index, fret in enumerate(frets):
            string_x = 40 + (string_index * 30)
            if fret == 0:
                svg.append(f'<text x="{string_x}" y="{40+top_margin}" text-anchor="middle" font-size="12" fill="black">O</text>')
            elif fret == -1:
                svg.append(f'<text x="{string_x}" y="{40+top_margin}" text-anchor="middle" font-size="12" fill="black">X</text>')
        
        # Finger positions
        for string_index, fret in enumerate(frets):
            string_x = 40 + (string_index * 30)
            if fret > 0:
                fret_y = 50 + ((fret - 1) * 40) + 20 + top_margin
                svg.append(f'<circle cx="{string_x}" cy="{fret_y}" r="10" fill="black"/>')
                finger = fingers[string_index]
                if finger > 0:
                    svg.append(f'<text x="{string_x}" y="{fret_y + 4}" text-anchor="middle" font-size="10" fill="white">{finger}</text>')
        
        svg.append('</svg>')
        return "\n".join(svg)

    def create_chord_progression(self, chord_names):
        """
        Create a chord progression from a list of chord names.

        Args:
            chord_names (list): A list of chord names (e.g., ["G", "C", "D"]).

        Returns:
            list: A list of dictionaries containing chord data (positions and fingerings).
        """
        progression = []
        for chord_name in chord_names:
            try:
                chord_data = self.get_chord(chord_name)
                progression.append({"name": chord_name, "positions": chord_data["positions"], "fingers": chord_data["fingers"]})
            except ValueError as e:
                raise ValueError(f"Error in chord progression: {e}")
        return progression


class ScaleLibrary:
    NOTE_TO_FRET = {
        "E": 0, "F": 1, "F#": 2, "G": 3, "G#": 4, "A": 5, "A#": 6, "B": 7, "C": 8, "C#": 9, "D": 10, "D#": 11
    }
    STRING_TUNINGS = ["E", "A", "D", "G", "B", "E"]

    def __init__(self):
        # Patterns written as if root is at 3rd fret (G) on low E string
        self.patterns = {
            "Minor Pentatonic": [
                [3, 6],  # High E string
                [3, 6],  # A string
                [3, 5],  # D string
                [3, 5],  # G string
                [3, 5],  # B string
                [3, 6],  # Low E string
            ],
            "Major Pentatonic": [
                [2, 3, 5],
                [3, 5],
                [2, 4, 5],
                [2, 4, 5],
                [2, 3, 5],
                [3, 5],  
            ],

            "Blues Scales": [
                [3, 6],  
                [3, 6],
                [3, 5, 6],  
                [3, 5],  
                [3, 4, 5],  
                [3, 6],  
            ],

            "Major Scale": [
                [2, 5],
                [2, 5],
                [2, 4],
                [2, 4], 
                [2, 4],
                [5], 
            ],

            "Natural Minor Scale": [
                [3, 5, 6],
                [3, 4, 6],
                [2, 3, 5],
                [3, 5],
                [3, 5, 6],
                [3, 5, 6],
            ]
        }

    def get_scale_positions(self, pattern_name, key, root_string=0):
        """
        Generate scale positions for a given pattern and key.
        Patterns are defined as if root is at 3rd fret (G).
        """
        pattern = self.patterns[pattern_name]
        g_fret = self.NOTE_TO_FRET["G"]
        key_fret = self.NOTE_TO_FRET[key]
        offset = key_fret - g_fret
        positions = []
        for string_pattern in pattern:
            positions.append([fret + offset for fret in string_pattern])
        return positions

    def draw_scale(self, positions):
        """Generate an SVG representation of the scale diagram, only showing used frets."""
        # Flatten all frets into a single list
        all_frets = [fret for string in positions for fret in string]
        min_fret = min(all_frets)
        max_fret = max(all_frets)

        # Add padding (show one fret below and above if possible)
        display_min = max(1, min_fret - 1)
        display_max = max_fret + 1

        num_frets = display_max - display_min + 1

        # Larger SVG dimensions
        fret_width = 55
        string_height = 45
        left_margin = 70
        top_margin = 60
        bottom_margin = 40
        svg_width = left_margin + num_frets * fret_width + 30
        svg_height = top_margin + 5 * string_height + bottom_margin

        svg = [
            f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg" style="background:white">',
            '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
            '<!-- Guitar strings -->',
        ]

        # Draw strings (6 strings)
        for string_index in range(6):
            y = top_margin + (string_index * string_height)
            svg.append(f'<line x1="{left_margin}" y1="{y}" x2="{left_margin + num_frets * fret_width}" y2="{y}" stroke="black" stroke-width="3"/>')

        # Draw frets
        for fret_index in range(num_frets + 1):  # +1 to draw the last fret line
            x = left_margin + (fret_index * fret_width)
            svg.append(f'<line x1="{x}" y1="{top_margin}" x2="{x}" y2="{top_margin + 5 * string_height}" stroke="black" stroke-width="4" />')

        # Draw nut if the first displayed fret is 1
        if display_min == 1:
            svg.append(f'<rect x="{left_margin - 4}" y="{top_margin - 2}" width="8" height="{5 * string_height + 4}" fill="black" />')

        # Add fret numbers
        for i in range(num_frets):
            fret_num = display_min + i
            x = left_margin + (i * fret_width) + fret_width / 2
            svg.append(f'<text x="{x}" y="{top_margin - 18}" text-anchor="middle" font-size="22" font-weight="bold" fill="black">{fret_num}</text>')

        # Draw scale positions (smaller circles, no red stroke)
        for string_index, frets in enumerate(positions):
            y = top_margin + (string_index * string_height)
            for fret in frets:
                if display_min <= fret <= display_max:
                    x = left_margin + ((fret - display_min) * fret_width) + fret_width / 2
                    svg.append(f'<circle cx="{x}" cy="{y}" r="12" fill="black"/>')
                    svg.append(f'<text x="{x}" y="{y + 5}" text-anchor="middle" font-size="14" font-weight="bold" fill="white">{fret}</text>')

        svg.append('</svg>')
        return "\n".join(svg)


# Goals for the code:
# 1. Make a simple dashboard to display a basic interface to access 'daily exercises' X
# 2. Find a a way to combine the chord charts, scales, and progressions together in one big excercise x
# 3. Create a login system to save user data and progress x
# 4. Create a tutorial on how to read TAB, Chord Charts, and Chord Progressions x
# 5. Tailor the exercises to the user based on their progress and data x