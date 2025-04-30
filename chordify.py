import matplotlib.pyplot as plt
import os

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

    def draw_chord(self, frets, fingers):
        """Generate an SVG representation of the chord diagram."""
        # Start SVG
        svg = [
            '<svg width="200" height="250" xmlns="http://www.w3.org/2000/svg">',
            '<!-- Guitar strings -->',
        ]

        # Draw strings
        for string_index in range(6):  # 6 strings
            string_x = 40 + (string_index * 30)
            svg.append(f'<line x1="{string_x}" y1="30" x2="{string_x}" y2="190" stroke="black" stroke-width="2"/>')

        # Draw frets
        for fret_index in range(5):  # 4 frets + nut
            fret_y = 30 + (fret_index * 40)
            svg.append(f'<line x1="40" y1="{fret_y}" x2="190" y2="{fret_y}" stroke="black" stroke-width="3"/>')

        svg.append('<line x1="39" y1="30" x2="191" y2="30" stroke="black" stroke-width="5"/>')  # Draw nut

        # Indicate open or muted strings at the top
        for string_index, fret in enumerate(frets):
            string_x = 40 + (string_index * 30)
            if fret == 0:  # Open string indicator
                svg.append(f'<text x="{string_x}" y="20" text-anchor="middle" font-size="12" fill="black">O</text>')
            elif fret == -1:  # Muted string indicator
                svg.append(f'<text x="{string_x}" y="20" text-anchor="middle" font-size="12" fill="black">X</text>')

        # Draw finger positions
        for string_index, fret in enumerate(frets):
            string_x = 40 + (string_index * 30)
            if fret > 0:
                # Adjust fret_y to place the dot in the middle of the fret
                fret_y = 30 + ((fret - 1) * 40) + 20
                # Draw finger dot
                svg.append(f'<circle cx="{string_x}" cy="{fret_y}" r="10" fill="black"/>')
                # Add finger number inside the dot
                finger = fingers[string_index]
                if finger > 0:
                    svg.append(f'<text x="{string_x}" y="{fret_y + 4}" text-anchor="middle" font-size="10" fill="white">{finger}</text>')

        # Close SVG
        svg.append('</svg>')
        return "\n".join(svg)