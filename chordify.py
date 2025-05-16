class ChordLibrary:
    def __init__(self):
        # Define chord positions and fingerings NOTE: Strings ordered EADGBE, Notes (including muted) are indicated in positions
        self.chord_positions = {
            "G": {"positions": [3, 2, 0, 0, 3, 3], "fingers": [2, 1, 0, 0, 3, 4]},
            "C": {"positions": [-1, 3, 2, 0, 1, 0], "fingers": [0, 3, 2, 0, 1, 0]},
            "D": {"positions": [-1, -1, 0, 2, 3, 2], "fingers": [0, 0, 0, 1, 3, 2]},
            "Em": {"positions": [0, 2, 2, 0, 0, 0], "fingers": [0, 2, 3, 0, 0, 0]},
            "A": {"positions": [-1, 0, 2, 2, 2, 0], "fingers": [0, 0, 1, 2, 3, 0]},
            "B": {"positions": [-1, 2, 4, 4, 4, 2], "fingers": [0, 1, 3, 4, 2, 1]},
            "E": {"positions": [0, 2, 2, 1, 0, 0], "fingers": [0, 2, 3, 1, 0, 0]},
        }

    def get_chord(self, chord_name):
        """Retrieve chord positions and fingerings."""
        if chord_name not in self.chord_positions:
            raise ValueError(f"Chord '{chord_name}' not found in library.")
        return self.chord_positions[chord_name]

    def draw_chord(self, frets, fingers, chord_name=""):
        """Generate an SVG representation of the chord diagram."""
        # Start SVG
        svg = [
            '<svg width="200" height="250" xmlns="http://www.w3.org/2000/svg">',
            '<!-- Guitar strings -->',
        ]

        # Add chord name at the top, position can be adjusted by changing x and y values
        if chord_name:
            svg.append(f'<text x="100" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="black">{chord_name}</text>')

        # Draw strings
        for string_index in range(6):  # 6 strings
            string_x = 40 + (string_index * 30)
            svg.append(f'<line x1="{string_x}" y1="40" x2="{string_x}" y2="200" stroke="black" stroke-width="2"/>')

        # Draw frets
        for fret_index in range(5):  # 4 frets + nut
            fret_y = 40 + (fret_index * 40)
            svg.append(f'<line x1="40" y1="{fret_y}" x2="190" y2="{fret_y}" stroke="black" stroke-width="3"/>')

        svg.append('<line x1="39" y1="40" x2="191" y2="40" stroke="black" stroke-width="5"/>')  # Draw nut

        # Indicate open or muted strings at the top
        for string_index, fret in enumerate(frets):
            string_x = 40 + (string_index * 30)
            if fret == 0:  # Open string indicator
                svg.append(f'<text x="{string_x}" y="30" text-anchor="middle" font-size="12" fill="black">O</text>')
            elif fret == -1:  # Muted string indicator
                svg.append(f'<text x="{string_x}" y="30" text-anchor="middle" font-size="12" fill="black">X</text>')

        # Draw finger positions
        for string_index, fret in enumerate(frets):
            string_x = 40 + (string_index * 30)
            if fret > 0:
                # Adjust fret_y to place the dot in the middle of the fret
                fret_y = 40 + ((fret - 1) * 40) + 20
                # Draw finger dot
                svg.append(f'<circle cx="{string_x}" cy="{fret_y}" r="10" fill="black"/>')
                # Add finger number inside the dot
                finger = fingers[string_index]
                if finger > 0:
                    svg.append(f'<text x="{string_x}" y="{fret_y + 4}" text-anchor="middle" font-size="10" fill="white">{finger}</text>')

        # Close SVG
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
    def __init__(self):
        # Define scale positions (strings ordered EADGBE, frets for each string)
        self.scales = {
            "G Minor Pentatonic": {
                "positions": [
                    [3, 6],  # Low E string
                    [3, 5],  # A string
                    [3, 5],  # D string
                    [3, 5],  # G string
                    [3, 5],  # B string
                    [3, 6],  # High E string
                ]
            },
        }

    def get_scale(self, scale_name):
        """Retrieve scale positions."""
        if scale_name not in self.scales:
            raise ValueError(f"Scale '{scale_name}' not found in library.")
        return self.scales[scale_name]

    def draw_scale(self, positions):
        """Generate an SVG representation of the scale diagram."""
        # Start SVG
        svg = [
            '<svg width="500" height="250" xmlns="http://www.w3.org/2000/svg">',
            '<!-- Guitar strings -->',
        ]

        # Draw strings
        for string_index in range(6):  # 6 strings
            y = 30 + (string_index * 30)
            svg.append(f'<line x1="50" y1="{y}" x2="470" y2="{y}" stroke="black" stroke-width="2"/>')

        # Draw frets
        for fret_index in range(1, 13):  # 12 frets
            x = 50 + (fret_index * 35)
            svg.append(f'<line x1="{x}" y1="30" x2="{x}" y2="180" stroke="black" stroke-width="1"/>')

        # Draw nut (just before the first fret)
        svg.append('<line x1="50" y1="30" x2="50" y2="180" stroke="black" stroke-width="3"/>')

        # Add fret numbers
        for fret_index in range(1, 13):  # 12 frets
            x = 42 + (fret_index * 35)
            svg.append(f'<text x="{x - 10}" y="20" text-anchor="middle" font-size="12" fill="black">{fret_index}</text>')

        # Draw scale positions
        for string_index, frets in enumerate(positions):
            y = 30 + (string_index * 30)
            for fret in frets:
                x = 50 + (fret * 35)
                # Draw circle for scale position
                svg.append(f'<circle cx="{x}" cy="{y}" r="10" fill="black"/>')
                # Add fret number inside the circle
                svg.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle" font-size="10" fill="white">{fret}</text>')

        # Close SVG
        svg.append('</svg>')
        return "\n".join(svg)


# Goals for the code:
# 1. Make a simple dashboard to display a basic interface to access 'daily exercises' X
# 2. Find a a way to combine the chord charts, scales, and progressions together in one big excercise
# 3. Create a login system to save user data and progress
# 4. Create a tutorial on how to read TAB, Chord Charts, and Chord Progressions
# 5. Tailor the exercises to the user based on their progress and data