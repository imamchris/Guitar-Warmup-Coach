class ChordLibrary:
    def __init__(self):
        self.chord_positions = {
            "A": [
                {
                "positions": [0, 0, 2, 2, 2, 0],
                "fingers": [0, 0, 2, 3, 4, 0],
                "level": "beginner"
                }
            ],
            "C": [
                {
                    "positions": [-1, 3, 2, 0, 1, 0],
                    "fingers": [0, 3, 2, 0, 1, 0],
                    "level": "beginner",
                    "label": "1"
                },
                {
                    "positions": [-1, 1, 3, 3, 3, 1],
                    "fingers": [0, 1, 2, 3, 4, 1],
                    "barre": {"fret": 1, "from_string": 0, "to_string": 5},
                    "level": "intermediate",
                    "label": "2"
                }
            ],
            "F": [
                {
                    "positions": [1, 3, 3, 2, 0, 1],
                    "fingers": [1, 3, 4, 2, 0, 1],
                    "barre": {"fret": 1, "from_string": 0, "to_string": 5},
                    "level": "intermediate",
                    "label": "1"
                }
            ],
            "G": [
                {
                    "positions": [3, 2, 0, 0, 0, 3],
                    "fingers": [2, 1, 0, 0, 0, 3],
                    "level": "beginner",
                    "label": "1"
                }
            ],
            # ...repeat for all chords, wrapping each in a list...
        }

    def get_chord(self, chord_name, variation=0):
        """Get chord data by name and variation index (default to first variation)."""
        return self.chord_positions[chord_name][variation]

    def get_all_chord_variations(self, skill_level):
        """Return all (chord_name, variation_index, label) tuples filtered by skill level."""
        allowed_levels = {
            'beginner': ['beginner'],
            'intermediate': ['beginner', 'intermediate'],
            'expert': ['beginner', 'intermediate', 'expert']
        }
        allowed = allowed_levels.get(skill_level, ['beginner'])
        result = []
        for name, variations in self.chord_positions.items():
            for idx, var in enumerate(variations):
                if var.get("level", "beginner") in allowed:
                    label = var.get("label", f"variation {idx+1}")
                    result.append((name, idx, label))
        return result

    def get_movable_chord(self, base_name, fret, variation=0):
        """
        Move a barre chord shape to a new fret.
        Only works for chords with a 'barre' key.
        """
        base = self.get_chord(base_name, variation)
        if "barre" not in base:
            raise ValueError("Not a movable barre chord.")
        shift = fret - base["barre"]["fret"]
        new_positions = [
            (p + shift if p not in (None, -1, 0) else p)
            for p in base["positions"]
        ]
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
            '<svg width="200" height="270" xmlns="http://www.w3.org/2000/svg">',
            f'<text x="115" y="{top_margin}" text-anchor="middle" font-size="20" font-weight="bold" fill="black">{chord_name}</text>',
        ]

        # --- Calculate fret range to display ---
        min_fret = min([f for f in frets if f > 0], default=1)
        max_fret = max([f for f in frets if f > 0], default=4)
        # Always show at least 4 frets
        display_min = max(1, min_fret)
        display_max = max(display_min + 3, max_fret)
        num_frets = display_max - display_min + 1

        # --- Draw fret numbers on the left ---
        for fret_index in range(num_frets):
            fret_num = display_min + fret_index
            y = 50 + (fret_index * 40) + top_margin + 8
            svg.append(f'<text x="22" y="{y}" text-anchor="middle" font-size="13" fill="#0ea5e9">{fret_num}</text>')

        # Draw strings
        for string_index in range(6):
            string_x = 40 + (string_index * 30)
            svg.append(f'<line x1="{string_x}" y1="{50+top_margin}" x2="{string_x}" y2="{210+top_margin}" stroke="black" stroke-width="2"/>')
        
        # Draw frets
        for fret_index in range(num_frets):
            fret_y = 50 + (fret_index * 40) + top_margin
            svg.append(f'<line x1="40" y1="{fret_y}" x2="190" y2="{fret_y}" stroke="black" stroke-width="3"/>')
        # Top nut (already present)
        svg.append(f'<line x1="39" y1="{50+top_margin}" x2="191" y2="{50+top_margin}" stroke="black" stroke-width="5"/>')
        # --- Add this for the bottom line ---
        bottom_y = 50 + (num_frets * 40) + top_margin
        svg.append(f'<line x1="40" y1="{bottom_y}" x2="190" y2="{bottom_y}" stroke="black" stroke-width="3"/>')

        # Draw barre if present
        if barre:
            fret = barre["fret"]
            from_x = 40 + (barre["from_string"] * 30)
            to_x = 40 + (barre["to_string"] * 30)
            y = 50 + ((fret - display_min) * 40) + 20 + top_margin
            svg.append(f'<rect x="{from_x-7}" y="{y-8}" width="{to_x-from_x+14}" height="16" rx="8" fill="#222" opacity="0.7"/>')

        # Open/muted strings
        for string_index, fret in enumerate(frets):
            string_x = 40 + (string_index * 30)
            if fret == 0:
                svg.append(f'<text x="{string_x}" y="{40+top_margin}" text-anchor="middle" font-size="12" fill="black">O</text>')
            elif fret == -1:
                svg.append(f'<text x="{string_x}" y="{40+top_margin}" text-anchor="middle" font-size="12" fill="black">X</text>')

        # Finger positions (dots and finger numbers inside)
        for string_index, fret in enumerate(frets):
            string_x = 40 + (string_index * 30)
            if fret > 0:
                fret_y = 50 + ((fret - display_min) * 40) + 20 + top_margin
                svg.append(f'<circle cx="{string_x}" cy="{fret_y}" r="10" fill="black"/>')
                finger = fingers[string_index]
                if finger > 0:
                    svg.append(f'<text x="{string_x}" y="{fret_y + 4}" text-anchor="middle" font-size="10" fill="white">{finger}</text>')
    
        svg.append('</svg>')
        return "\n".join(svg)

    def create_chord_progression(self, chord_names, variations=None):
        """
        Create a chord progression from a list of chord names and optional variation indices.

        Args:
            chord_names (list): A list of chord names (e.g., ["G", "C", "D"]).
            variations (list): Optional list of variation indices for each chord.

        Returns:
            list: A list of dictionaries containing chord data (positions and fingerings).
        """
        progression = []
        for i, chord_name in enumerate(chord_names):
            try:
                var_idx = variations[i] if variations and i < len(variations) else 0
                chord_data = self.get_chord(chord_name, var_idx)
                progression.append({
                    "name": chord_name,
                    "variation": var_idx,
                    "positions": chord_data["positions"],
                    "fingers": chord_data["fingers"]
                })
            except Exception as e:
                raise ValueError(f"Error in chord progression: {e}")
        return progression


class ScaleLibrary:
    NOTE_TO_FRET = {
        "E": 0, "F": 1, "F#": 2, "G": 3, "G#": 4, "A": 5, "A#": 6, "B": 7, "C": 8, "C#": 9, "D": 10, "D#": 11
    }
    STRING_TUNINGS = ["E", "A", "D", "G", "B", "E"]

    def __init__(self):
        # Each scale now has a pattern and a minimum skill level
        self.patterns = {
            "Minor Pentatonic": {
                "positions": [
                    [3, 6],  # High E string
                    [3, 6],  # A string
                    [3, 5],  # D string
                    [3, 5],  # G string
                    [3, 5],  # B string
                    [3, 6],  # Low E string
                ],
                "level": "beginner"
            },
            "Major Pentatonic": {
                "positions": [
                    [2, 3, 5],
                    [3, 5],
                    [2, 4, 5],
                    [2, 4, 5],
                    [2, 3, 5],
                    [3, 5],
                ],
                "level": "beginner"
            },
            "Blues Scales": {
                "positions": [
                    [3, 6],
                    [3, 6],
                    [3, 5, 6],
                    [3, 5],
                    [3, 4, 5],
                    [3, 6],
                ],
                "level": "intermediate"
            },
            "Major Scale": {
                "positions": [
                    [2, 5],
                    [2, 5],
                    [2, 4],
                    [2, 4],
                    [2, 4],
                    [5],
                ],
                "level": "intermediate"
            },
            "Natural Minor Scale": {
                "positions": [
                    [3, 5, 6],
                    [3, 4, 6],
                    [2, 3, 5],
                    [3, 5],
                    [3, 5, 6],
                    [3, 5, 6],
                ],
                "level": "intermediate"
            }
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
        for string_pattern in pattern["positions"]:
            row = []
            for fret in string_pattern:
                try:
                    row.append(int(fret) + offset)
                except Exception:
                    continue
            positions.append(row)
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

    def get_available_scales(self, skill_level):
        allowed_levels = {
            'beginner': ['beginner'],
            'intermediate': ['beginner', 'intermediate'],
            'expert': ['beginner', 'intermediate', 'expert']
        }
        allowed = allowed_levels.get(skill_level, ['beginner'])
        return [
            (name, data)
            for name, data in self.patterns.items()
            if data.get("level", "beginner") in allowed
        ]


# Goals for the code:

# 7. Create profile page, maybe a dropdown


