"""
Python Colors Engine v2.0
Supports OKLCH color spaces, automated hue relationship generation, and single-file HTML preview export.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class ColorDef:
    name: str
    oklch: str      # e.g., "oklch(0.65 0.18 140)"
    hex_fallback: str
    category: str = "general"
    hue_angle: float = 0.0  # 0 to 360 degrees

class ColorPalette:
    def __init__(self, brand_name: str = "Python Colors"):
        self.brand_name = brand_name
        self._colors: Dict[str, ColorDef] = {}
        
    def add(self, name: str, oklch: str, hex_fallback: str, category: str = "general", hue_angle: float = 0.0) -> 'ColorPalette':
        key = name.lower().replace(" ", "_")
        self._colors[key] = ColorDef(
            name=name,
            oklch=oklch,
            hex_fallback=hex_fallback,
            category=category,
            hue_angle=hue_angle
        )
        return self

    def generate_harmonies(self, base_key: str) -> Dict[str, List[ColorDef]]:
        """Automatically calculates analogous, triadic, and complementary relationships."""
        base = self._colors.get(base_key.lower().replace(" ", "_"))
        if not base:
            return {}
        
        harmonies = {
            "complementary": [],
            "analogous": [],
            "triadic": []
        }
        
        for c in self._colors.values():
            if c.name == base.name:
                continue
            diff = abs(c.hue_angle - base.hue_angle) % 360
            if diff > 180:
                diff = 360 - diff
                
            # Complementary (~180°)
            if abs(diff - 180) <= 15:
                harmonies["complementary"].append(c)
            # Analogous (within ~30°)
            elif diff <= 35:
                harmonies["analogous"].append(c)
            # Triadic (~120°)
            elif abs(diff - 120) <= 15:
                harmonies["triadic"].append(c)
                
        return harmonies

    def export_css(self, prefix: str = "py") -> str:
        lines = [":root {", f"  /* Brand: {self.brand_name} */"]
        for key, c in self._colors.items():
            lines.append(f"  --{prefix}-{key}-oklch: {c.oklch};")
            lines.append(f"  --{prefix}-{key}: {c.hex_fallback};")
        lines.append("}")
        return "\n".join(lines)

    def export_html_preview(self) -> str:
        """Generates a complete single-file HTML document showcasing the palette and swatches."""
        swatch_cards = []
        for key, c in self._colors.items():
            swatch_cards.append(f"""
            <div style="background: var(--py-{key}); color: #111; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 8px 0; font-family: monospace;">{c.name}</h3>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">OKLCH: {c.oklch}</p>
                <p style="margin: 4px 0 0 0; font-size: 0.9rem; font-family: monospace;">Hex: {c.hex_fallback}</p>
            </div>
            """)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{self.brand_name} - Palette Preview</title>
    <style>
        {self.export_css()}
        body {{ font-family: system-ui, sans-serif; background: #0f111a; color: #f8f9fc; padding: 40px; max-width: 1200px; margin: 0 auto; }}
        h1 {{ border-bottom: 2px solid #3b4252; padding-bottom: 12px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; margin-top: 24px; }}
    </style>
</head>
<body>
    <h1>{self.brand_name}</h1>
    <p>Human-readable CSS color relationships compiled from Python.</p>
    <div class="grid">
        {"".join(swatch_cards)}
    </div>
</body>
</html>"""
        return html

# Example initialization
palette = ColorPalette("Antistatic Lab & Python Colors")
palette.add("Terminal Slate", "oklch(0.22 0.02 260)", "#1e1e2e", "neutral", 260)
palette.add("Phosphor Green", "oklch(0.88 0.16 142)", "#a6e3a1", "accent", 142)
palette.add("Cyber Amber", "oklch(0.80 0.15 65)", "#fab387", "accent", 65)
palette.add("Deep Void", "oklch(0.12 0.01 270)", "#11111b", "neutral", 270)
