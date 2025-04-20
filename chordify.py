import matplotlib.pyplot as plt
import os

def draw_chord(frets):
    # Start SVG
    svg = [
        '<svg width="200" height="250" xmlns="http://www.w3.org/2000/svg">',
        '<!-- Guitar strings -->',
    ]

    # Draw strings
    for i in range(6):  # 6 strings
        x = 40 + (i * 30)
        svg.append(f'<line x1="{x}" y1="30" x2="{x}" y2="190" stroke="black" stroke-width="2"/>')

    # Draw frets
    for i in range(5):  # 4 frets + nut
        y = 30 + (i * 40)
        svg.append(f'<line x1="40" y1="{y}" x2="190" y2="{y}" stroke="black" stroke-width="3"/>')

    # Draw nut
    svg.append('<line x1="39" y1="30" x2="191" y2="30" stroke="black" stroke-width="5"/>')

    # Draw finger positions
    for string, fret in enumerate(frets):
        x = 40 + (string * 30)
        if fret > 0:
            y = 30 + (fret * 40)
            # Draw finger dot
            svg.append(f'<circle cx="{x}" cy="{y}" r="10" fill="black"/>')
        elif fret == 0:
            # Open string indicator
            svg.append(f'<text x="{x}" y="20" text-anchor="middle" font-size="12" fill="black">O</text>')
        elif fret == -1:
            # Muted string indicator
            svg.append(f'<text x="{x}" y="20" text-anchor="middle" font-size="12" fill="black">X</text>')

    # Close SVG
    svg.append('</svg>')
    return "\n".join(svg)

class ChordLibrary:
    def __init__(self):
        # Define chord positions and fingerings
        self.chord_positions = {
            "G": {"positions": [3, 2, 0, 0, 3, 3], "fingers": [2, 1, 0, 0, 3, 4]},
            "C": {"positions": [0, 3, 2, 0, 1, 0], "fingers": [0, 3, 2, 0, 1, 0]},
            "D": {"positions": [0, 0, 0, 2, 3, 2], "fingers": [0, 0, 0, 1, 3, 2]},
            "Em": {"positions": [0, 2, 2, 0, 0, 0], "fingers": [0, 2, 3, 0, 0, 0]},
            "A": {"positions": [0, 0, 2, 2, 2, 0], "fingers": [0, 0, 1, 2, 3, 0]},
            "B": {"positions": [-1, 2, 4, 4, 4, 2], "fingers": [0, 1, 3, 4, 2, 1]},
            "E": {"positions": [0, 2, 2, 1, 0, 0], "fingers": [0, 2, 3, 1, 0, 0]},
        }

    def get_chord(self, chord_name):
        """Retrieve chord positions and fingerings."""
        if chord_name not in self.chord_positions:
            raise ValueError(f"Chord '{chord_name}' not found in library.")
        return self.chord_positions[chord_name]