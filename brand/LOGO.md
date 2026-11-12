# Lanewright logo: the lane L

Lanewright is the paid skill pack (formerly sold under the working name scrum-kit; the free MIT
plugin keeps the scrum-kit name). The first mark, three stepped capsules, was dropped on
2026-11-06 because it closely matched an existing app logo (FastChapters).

## Brief

| Question | Answer |
|---|---|
| Who stands behind it | A neutral indie brand; the maker appears only in the credits. |
| The idea it must carry | Team and relay: roles hand work to each other. |
| Character | Firm and trustworthy: calm, tidy geometry, few colours, no mascot. |
| Form | Icon + wordmark, monochrome, with a dark version; the icon must read at 96 px and 16 px. |
| Distinctiveness | Vertical lanes (like board columns) forming the name's initial, not stepped horizontal bars. |

## The mark

On a 64 × 64 grid:

```
█   │   │
█   │   │
█   │   │
█   │   │
█
██████████
```

- **The L is one strong lane.** It bends into the floor: the role that owns the work carries it to
  the shared base.
- **The two thin lanes are the other roles.** They stand side by side, never touching each other
  or the L, the same way a role's worktree never writes into another region.
- **The base is the handoff.** Every lane ends above the same floor. That floor is the merge
  request, the one place where work from separate lanes meets, and only after review and green CI.
- **It is a letter on purpose.** The shape reads as L for Lanewright, so the mark stays tied to the
  name and is unlike abstract bar marks.

Geometry: stem and base 9 units thick with round caps, thin lanes 3 units, a gap of 7.5 units
between the thin lanes and the base. No gradients and no outlines.

## Wordmark

`Lanewright` with a capital L, in a bold geometric sans with slightly tight tracking (Inter Bold,
−0.5). For print or image editors, convert the text to outlines.

## Colour

| Use | Light background | Dark background |
|---|---|---|
| Mark and wordmark | `#111111` | `#F2F2F2` |

Monochrome is the main identity. One accent is allowed, for the app icon only, to stand out in a
crowded marketplace grid: a solid tile in `#1D4ED8` with the mark in white (contrast 6.7 : 1). Use
it flat: no gradient, no glow, no second blue, and never on the wordmark.

Three lanes, three roles: the L is the implementer's lane, the two thin lanes are QA and the
reviewer. The count is fixed; adding lanes turns the mark into a pattern and loses the letter.

The mark is drawn by hand in SVG on the grid above. Do not regenerate it with an image generator:
the geometry would drift, and a fully AI-generated logo is hard to protect as your own.

## Files

| File | What |
|---|---|
| `mark.svg`, `mark-dark.svg` | Mark only |
| `logo.svg`, `logo-dark.svg` | Mark + wordmark, horizontal (README header) |
| `logo-square.svg`, `logo-square-dark.svg` | 1:1 logo, mark above the wordmark (512 × 512) |
| `icon-tile.svg`, `icon-tile-light.svg` | 1:1 app icon: the mark on a rounded tile, readable at 96 × 96 |
| `icon-tile-blue.svg` | 1:1 app icon with the one allowed accent (`#1D4ED8` tile, white mark) |

PNGs for the Agensi upload are rendered into `dist/listing-images/`. At 96 × 96, use an icon tile;
the wordmark is too small to read at that size.

## Icon of the paid pack in publications (decided 2026-11-13)

Every publication of the paid Lanewright pack (its Agensi listing, posts, releases) uses the blue tile:
`icon-tile-blue.svg`, rendered as `icon-blue-512.png`. The Agensi listing was switched to it on 2026-11-13. The free
Lanewright Planning skills keep their own green tile; this decision does not change them.

## Don't

- Don't turn the lanes horizontal or stagger them into steps (that is the dropped mark).
- Don't let the thin lanes touch the base or each other.
- Don't add a second colour, a gradient or an outline.
