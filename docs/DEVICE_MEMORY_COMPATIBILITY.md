# Advisory hardware compatibility (Cantina development contract)

This is experimental metadata for The Cantina Store and matching Razor-Crest development firmware. It is **not** a restriction on manual installation, reinstall, or update.

## Publisher manifest

A plugin, theme pack, or wallpaper pack may declare:

```json
{
  "compatibility": {
    "requires": ["theme.sd.v1"],
    "recommended": {"min_psram_mb": 2},
    "devices": ["x4pro", "sticky"],
    "exclude_devices": ["x3"]
  }
}
```

All fields are optional. `requires` remains the existing firmware-capability declaration; it is not converted into a device rule. `min_psram_mb` measures **installed physical PSRAM capacity** in MiB, not fluctuating free heap. Devices without PSRAM have 0. Model strings are stable IDs, not ESP32 chip models. Both X3 display-controller variants identify as `x3`; X3 and X4 both have no PSRAM.

The generator validates the publisher metadata and emits the existing fields plus `compatibility.advisory`, a compact scalar for the X3-friendly six-field native streaming parser. Example: `models=x4pro|sticky;exclude=x3;psram_mb=2`. Authors should **not** write that scalar manually; it is generated.

For wallpaper collections with multiple display-resolution variants, hardware recommendations must agree across the variants. Actual display resolution still selects the matching installable wallpaper ZIP independently. Per-variant model restrictions are intentionally not supported.

## Discovery and compatibility

- Modern native firmware maps `browse.compatibility.advisory` to `compatibility.advisory` and filters before paging; this works for plugin, theme, and wallpaper catalogs.
- Cantina WebUI filters when `/api/status` provides `deviceModel` and `psramBytes`; if not, the catalog remains visible as before.
- Already-installed browser plugins stay visible so they can still be updated/removed even if not recommended for this device.
- Legacy firmware ignores the new metadata and continues its previous behavior.
- No check is added to any installer. Explicit/manual installation and experimentation remain permitted. Existing ZIP integrity, safe path, format, and display-resolution validation remain in force.

When publishers omit hardware preferences, the item remains visible. Do not invent hardware exclusions purely based on the MCU family or on instantaneous heap readings.

## New firmware status fields

`GET /api/status` also exposes `deviceModel` (e.g. `x3`, `x4`, `x4pro`, `sticky`) and `psramBytes` (actual capacity). `deviceId` remains the separate per-plugin privacy-preserving identifier.

Hardware filtering is advertised via `catalog.hardware_filter.v1` only where implemented.
