
# THE OBSERVER'S CONSTELLATION
# Lesson 7 — Drawing our first galaxy 🌙

from pathlib import Path
import random

# Keep our stars in the same positions
random.seed(7)

# Create the assets folder if needed
Path("assets").mkdir(exist_ok=True)

width = 800
height = 300

# The beginning of our SVG picture
svg = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">

<rect width="100%" height="100%"
      rx="18" fill="#101521"/>

<text x="400" y="42"
      text-anchor="middle"
      fill="#e8c99a"
      font-family="monospace"
      font-size="23">
  THE OBSERVER'S SKY
</text>
"""

# Draw 45 tiny stars
for i in range(45):
    x = random.randint(30, 770)
    y = random.randint(70, 255)
    radius = random.choice([1, 2, 3, 4])

    svg += f"""
    <circle cx="{x}" cy="{y}" r="{radius}"
            fill="#f3d9aa" opacity="0.85"/>
    """

# Add a little message
svg += """
<text x="400" y="280"
      text-anchor="middle"
      fill="#b9a88e"
      font-family="monospace"
      font-size="14">
  Every star holds a little memory.
</text>

</svg>
"""

# Save our picture
Path("assets/constellation.svg").write_text(
    svg, encoding="utf-8"
)

print("Our first constellation is ready! ✨")

