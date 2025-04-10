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

    def generate_chart(self, chord_name):
        """Generate an SVG diagram for a single chord."""
        if chord_name not in self.chord_positions:
            raise ValueError(f"Chord '{chord_name}' not found in library.")

        chord = self.chord_positions[chord_name]
        positions = chord["positions"]
        fingers = chord["fingers"]

        # Start SVG
        svg = [
            '<svg width="200" height="250" xmlns="http://www.w3.org/2000/svg">',
            '<!-- Guitar strings -->',
        ]

        # Draw strings
        for lines in range(6):
            x = 40 + (lines * 30)
            svg.append(f'<line x1="{x}" y1="30" x2="{x}" y2="191" stroke="black" stroke-width="2"/>')

        # Draw frets
        for lines in range(4):
            y = 70 + (lines * 40)
            svg.append(f'<line x1="40" y1="{y}" x2="190" y2="{y}" stroke="black" stroke-width="3"/>')

        # Draw nut
        svg.append('<line x1="39" y1="30" x2="191" y2="30" stroke="black" stroke-width="5"/>')

        # Draw chord positions and finger numbers
        for lines, pos in enumerate(positions):
            x = 40 + (lines * 30)
            if pos > 0:
                y = 30 + (pos * 32)
                # Draw finger dot
                svg.append(f'<circle cx="{x}" cy="{y}" r="10" fill="black"/>')
                # Draw finger number
                svg.append(
                    f'<text x="{x}" y="{y + 5}" text-anchor="middle" fill="white" font-size="10">{fingers[lines]}</text>'
                )
            elif pos == 0:
                # Open string indicator
                svg.append(
                    f'<text x="{x}" y="20" text-anchor="middle" font-size="12" fill="black">O</text>'
                )
            elif pos == -1:
                # Muted string indicator
                svg.append(
                    f'<text x="{x}" y="20" text-anchor="middle" font-size="12" fill="black">X</text>'
                )

        # Close SVG
        svg.append('</svg>')
        return "\n".join(svg)


class ChordProgression:
    def __init__(self, chord_library):
        """
        Initialize with a ChordLibrary instance.
        :param chord_library: An instance of ChordLibrary to generate chord SVGs.
        """
        self.chord_library = chord_library

    def generate_progression(self, chord_progression):
        """Generate HTML output for a chord progression."""
        html = []

        # Split chords into two rows
        row1 = chord_progression[:3]
        row2 = chord_progression[3:]

        # Generate HTML for the first row
        html.append('<div class="chord-row">')
        for i, chord in enumerate(row1):
            html.append(f'<div class="chord-cell">{chord}</div>')
            if i < len(row1) - 1:
                html.append('<div class="slash">/</div>')
        html.append('</div>')

        # Generate HTML for the second row
        if row2:
            html.append('<div class="chord-row">')
            for i, chord in enumerate(row2):
                html.append(f'<div class="chord-cell">{chord}</div>')
                if i < len(row2) - 1:
                    html.append('<div class="slash">/</div>')
            html.append('</div>')

        return "\n".join(html)


class S_A_Library:
    def __init__(self):
        # Define scales with positions
        self.scales = {
            "gMinorPentatonic": {
                "root": "G",
                "positions": [
                    [3, 6],  # e
                    [3, 6],  # B
                    [3, 5],  # G
                    [3, 5],  # D
                    [3, 5],  # A
                    [3, 6],  # E
                ],
            },
            "eMajorPentatonic": {
                "root": "E",
                "positions": [
                    [0, 2, 4],
                    [0, 2, 4],
                    [1, 2, 4],
                    [1, 2, 4],
                    [0, 2, 4],
                    [0, 2, 4],
                ],
            },
            "bBlues": {
                "root": "B",
                "positions": [
                    [7, 10],
                    [7, 10],
                    [7, 9, 10],
                    [7, 9],
                    [7, 8, 9],
                    [7, 10],
                ],
            },
            "aNaturalMinor": {
                "root": "A",
                "positions": [
                    [5, 7, 8],
                    [5, 7, 8],
                    [4, 5, 7],
                    [5, 7],
                    [5, 7, 8],
                    [5, 7, 8],
                ],
            },
        }

    def generate_scale_TAB(self, scale_name):
        """Generate an SVG diagram for a scale."""
        if scale_name not in self.scales:
            raise ValueError(f"Scale '{scale_name}' not found in library.")

        scale = self.scales[scale_name]
        positions = scale["positions"]

        # Start SVG
        svg = [
            '<svg width="800" height="300" xmlns="http://www.w3.org/2000/svg">',
            '<!-- Guitar strings -->',
        ]

        num_frets = 12
        fret_width = 40
        string_spacing = 30

        # Draw frets
        for i in range(num_frets + 1):
            x = 50 + i * fret_width
            svg.append(
                f'<line x1="{x}" y1="50" x2="{x}" y2="{50 + (len(positions) - 1) * string_spacing}" '
                f'stroke="{"black" if i == 0 else "gray"}" stroke-width="{"5" if i == 0 else "3"}"/>'
            )
            if i > 0:
                svg.append(
                    f'<text x="{x}" y="40" text-anchor="middle" fill="black" font-size="12">{i}</text>'
                )

        # Draw strings
        for string_index, string_positions in enumerate(positions):
            y = 50 + string_index * string_spacing
            svg.append(
                f'<line x1="50" y1="{y}" x2="{50 + num_frets * fret_width}" y2="{y}" stroke="black" stroke-width="2"/>'
            )

            # Draw notes on the string
            for fret in string_positions:
                x = 50 + fret * fret_width
                svg.append(f'<circle cx="{x}" cy="{y}" r="10" fill="black"/>')
                svg.append(
                    f'<text x="{x}" y="{y + 5}" text-anchor="middle" fill="white" font-size="10">{fret}</text>'
                )

        # Close SVG
        svg.append("</svg>")
        return "\n".join(svg)

    def add_scale(self, scale_name, root, positions):
        """Add a new scale to the library."""
        if scale_name in self.scales:
            raise ValueError(f"Scale '{scale_name}' already exists.")
        self.scales[scale_name] = {"root": root, "positions": positions}
