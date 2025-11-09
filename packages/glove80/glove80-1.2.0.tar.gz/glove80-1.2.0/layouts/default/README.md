# Default Layout Examples

Glove80 ships several stock layouts curated by MoErgo.
The `layouts/default/releases` directory tracks the JSON artifacts exported from the layout editor so they can be referenced alongside TailorKey and QuantumTouch.

## Canonical Layouts (accessed 8 Nov 2025)
- [Glove80 Factory Default Layout](https://my.glove80.com/#/layout/glove80) (accessed 8 Nov 2025)
- [Glove80 Factory Default Layout for macOS](https://my.glove80.com/#/layout/glove80-macos) (accessed 8 Nov 2025)
- [Mouse Emulation Example](https://my.glove80.com/#/layout/mouse-emulation) (accessed 8 Nov 2025)
- [Colemak Layout](https://my.glove80.com/#/layout/colemak) (accessed 8 Nov 2025)
- [Colemak-DH Layout](https://my.glove80.com/#/layout/colemak-dh) (accessed 8 Nov 2025)
- [Dvorak Layout](https://my.glove80.com/#/layout/dvorak) (accessed 8 Nov 2025)
- [Workman Layout](https://my.glove80.com/#/layout/workman) (accessed 8 Nov 2025)
- [Kinesis Advantage-like Layout](https://my.glove80.com/#/layout/kinesis) (accessed 8 Nov 2025)

These JSON files are mirrored in the Python sources under `src/glove80/families/default`, where each layout is described as declarative layer specs similar to TailorKey and QuantumTouch.
Keeping them under version control ensures we can diff against MoErgo’s published versions while treating the code-driven specs as the source of truth.
