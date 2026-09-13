# Community integration icon

`icon.svg` copies the project owner's supplied `icon-pack/icon/tile-gradient.svg`:
the white waveform on a blue/violet tile. Only a final newline was added; artwork
and original SVG metadata are preserved. It requires no external font.

`icon.png` is a 256 × 256 raster export of that same artwork for the Community
Apps profile and Docker template. Docker Manager uses PNG-oriented icon caching
and rendering; the SVG remains the unchanged source asset. From the repository
root, export with:

```sh
rsvg-convert --width 256 --height 256 --output assets/icon.png assets/icon.svg
```

The raster export does not carry the SVG's embedded provenance metadata; that
metadata remains in the original SVG. No artwork was regenerated or redesigned.

On 2026-09-06, the project owner (`lozenge0`) confirmed that the artwork was
generated from scratch using their own prompts with Claude/AI, without supplied
third-party images or assets. This records the owner's provenance statement;
it is not an independent originality, copyright or trademark clearance.

## Artwork licence — CC0 1.0 Universal

On 2026-09-12, the project owner (`lozenge0`) approved applying
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) to
`icon.svg` and its `icon.png` export, to the extent they hold copyright and related rights in them.
The [CC0 legal code](https://creativecommons.org/publicdomain/zero/1.0/legalcode.en)
governs this dedication, including its waiver, fallback licence and disclaimers.
SPDX identifier: `CC0-1.0`.

This does not assert that AI-generated artwork necessarily has copyright
protection, clear third-party rights, or grant trademark rights. This is community
integration artwork, not official audio.cpp branding or endorsement. The root MIT
licence covers integration code/docs; both icon formats are separately covered by CC0.

## Maintainer presentation checks

For this project's presentation, retain the supplied proportions and colours;
this is not a restriction on reuse under CC0. Verify rendering on Unraid's light
and dark themes; if PNG is needed, export it from this SVG without regenerating
the artwork. On 2026-09-12, local raster previews at 32, 48 and 180 pixels on white
and dark backgrounds retained a clear waveform and clean tile edges. These are
private review artifacts, not additional published assets or proof of CA rendering.
The original SVG is unchanged. Read-only inspection of its decoded C2PA metadata
found Anthropic assertions, a signing certificate and asset identifiers, with no
prompt text, account identifier, local path or credential observed. This is not
cryptographic signature/chain validation or independent provenance certification.
