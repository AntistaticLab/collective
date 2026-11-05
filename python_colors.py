"""
Python Colors
A super simple, human-readable single-file color palette and hue relationship engine for HTML/CSS.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ColorDef:
    name: str
    hex_code: str
    category: str
    hue_angle: float  # Degrees 0-360 for relationship math

class ColorPalette:
    def __init__(self, brand_name: str = "Python Colors"):
        self.brand_name = brand_name
        self._colors: Dict[str, ColorDef] = {}
        
    def add(self, name: str, hex_code: str, category: str = "general", hue_angle: float = 0.0) -> 'ColorPalette':
        key = name.lower().replace(" ", "_")
        self._colors[key] = ColorDef(name=name, hex_code=hex_code, category=category, hue_angle=hue_angle)
        return self

    def get_css_variables(self, prefix: str = "py-color") -> str:
        """Compiles all registered colors into clean CSS custom properties."""
        lines = [":root {"]
        for key, c in self._colors.items():
            lines.append(f"  --{prefix}-{key}: {c.hex_code};")
        lines.append("}")
        return "\n".join(lines)

    def find_complementary(self, color_key: str) -> Optional[ColorDef]:
        """Finds or approximates a complementary hue (approx 180 degrees opposite)."""
        base = self._colors.get(color_key.lower().replace(" ", "_"))
        if not base:
            return None
        target_angle = (base.hue_angle + 180) % 360
        # Find closest match in palette
        closest = min(self._colors.values(), key=lambda c: abs(c.hue_angle - target_angle))
        return closest

# --- Example Usage & Default Core Palette ---
palette = ColorPalette("Python Colors Default")
palette.add("Terminal Slate", "#1e1e2e", "neutral", 240)
palette.add("Phosphor Green", "#a6e3a1", "accent", 120)
palette.add("Cyber Amber", "#fab387", "accent", 35)
palette.add("Deep Void", "#11111b", "neutral", 250)

if __name__ == "__main__":
    print("Generated CSS Output:")
    print(palette.get_css_variables())
