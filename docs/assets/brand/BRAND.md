# Indicium brand kit

Mark files for the Indicium standard.

The mark is a record sheet with three claim lines, bound by a round seal at its lower corner. It is the sibling of the AgenticScienceBuilder (ASB) crane mark: same palette, same stroke weights, no crane and no wordmark. The ASB brand kit (`assets/brand/BRAND.md` in asb-skill-collections) holds the ASB files; this folder holds the Indicium ones.

## Files

Brand folder: `docs/assets/brand/`.

| File | Content | Ground |
|---|---|---|
| `indicium-mark.svg` | mark only, 256 x 256 square | light |
| `indicium-mark-dark.svg` | mark only, 256 x 256 square | dark |
| `indicium-mark-512.png` | `indicium-mark.svg` at 512 x 512 px, transparent | light |
| `favicon.svg` | ecosystem browser-tab icon, 32 x 32 grid | any |
| `favicon.ico` | same icon, 16, 32 and 48 px | any |
| `apple-touch-icon.png` | same icon, 180 x 180 px | any |

Which file where:

| Place | File |
|---|---|
| README header | `indicium-mark.svg` with `indicium-mark-dark.svg` |
| Documentation site header (CNRS blue bar in both schemes) | `indicium-mark-dark.svg` |
| Documentation site home page | `indicium-mark.svg` with `indicium-mark-dark.svg` |
| Browser tab | `favicon.svg`, with `favicon.ico` as fallback |
| Home-screen icon | `apple-touch-icon.png` |
| Tools that refuse SVG | `indicium-mark-512.png` |

The browser-tab icon comes from the ecosystem icon family generated in `holobiomicslab_brand`; do not redraw it here. The two mark SVGs have a `viewBox`, no embedded raster, no `<text>` element, no external font and no external reference. Each carries a `<title>` and a `<desc>`.

## Palette

The palette is the one of the ASB brand kit.

| Token | Hex | Role |
|---|---|---|
| navy | `#00284b` | sheet and claim lines on light grounds (CNRS blue) |
| blue-ink | `#001833` | dark page ground |
| blue-soft | `#0d3a66` | secondary navy |
| orange | `#e06c0a` | seal on light grounds |
| orange-dark | `#f5923a` | seal on dark grounds |
| paper | `#fbf7ef` | light page ground; sheet and claim lines on dark grounds |
| paper-2 | `#f3ecdc` | inset surfaces, code blocks |
| ink | `#16242f` | body text |
| mute | `#5d6a78` | secondary text on light grounds |
| mute-dark | `#aebccb` | secondary text on dark grounds |
| yellow | `#ffeb6e` | CNRS accent; not used in the mark |
| yellow-soft | `#fff5a6` | highlight; not used in the mark |
| teal | `#04919a` | links on the documentation site; not used in the mark |

The mark uses two colours per ground: navy and orange on light, paper and orange-dark on dark.

Contrast (WCAG 2):

| Pair | Ratio |
|---|---|
| navy on white | 14.95 |
| navy on paper | 13.99 |
| orange on white | 3.32 |
| orange on paper | 3.11 |
| paper on `#0d1117` | 17.71 |
| paper on navy | 13.99 |
| orange-dark on `#0d1117` | 8.16 |
| orange-dark on navy | 6.44 |

## Type

The mark carries no text. Pages and slides that set the name next to it use the type of the ASB brand kit:

| Use | Font |
|---|---|
| Text and interface | IBM Plex Sans |
| Headings on the documentation site | IBM Plex Serif |
| Code | IBM Plex Mono |

## Geometry

- The mark is drawn on a 256-unit square.
- Strokes: 7 units for the sheet outline, the folded corner and the three claim lines. Round caps and joins.
- The seal is a filled shape: a ring 5 units wide around a scalloped disc of 16 lobes. The sheet outline stops short of the seal on the bottom and right edges, so the seal reads in front of the sheet.

Do not stretch, rotate, outline or recolour the files. Do not add shadows or gradients. Do not put the light files on dark grounds.

## GitHub README snippet

The `<picture>` element picks the source that matches `prefers-color-scheme`. The `<img>` falls back to the light file.

```html
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/indicium-mark-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/indicium-mark.svg">
    <img alt="Indicium mark" src="docs/assets/brand/indicium-mark.svg" width="120">
  </picture>
</p>
```
