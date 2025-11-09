set shell := ["/bin/bash", "-c"]

# Run the full test suite
ci:
	uv run pytest

# Regenerate all release JSON files
regen:
	uv run python -m glove80 generate

# Regenerate a single layout/variant (usage: just regen-one tailorkey windows)
regen-one layout variant:
	uv run python -m glove80 generate --layout {{layout}} --variant {{variant}}
