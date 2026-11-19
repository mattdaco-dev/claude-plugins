---
name: proto-bar
description: Adds to an HTML prototype the prototype control bar, always identical (black background, yellow border, PROTOTYPE tag, nominal, loading and error states, reset, labels in English or French), plus the proto's own settings (layout, profile, variant…). Use when creating, changing or updating an HTML prototype or a clickable mockup, unless the user declined the bar for that proto, or when the user says "prototype", "HTML proto", "clickable prototype", "prototype bar", "proto-bar", "proto HTML", "proto cliquable", "barre du proto". Not for a demo page that is not a product prototype.
---

Goal: **every HTML prototype looks the same through its control bar**, whatever the session that
produces it. Only the proto's own settings change; the rest is fixed.

The bar does not belong to the product being mocked up: it drives the demo (change profile, layout,
state). It must therefore stand out clearly from the interface shown, which its style, deliberately
outside any design system, guarantees.

**When to add it**: to a product prototype (mocked-up screens, clickable flow). Not to an HTML page
that is not one (report, export site, technical demo of a library), nor to a proto for which the
user said they did not want it: that refusal holds for the rest of that proto, don't offer it again
at each change.

## 1. Copy the file, never rewrite it

The component is a single standalone file, CSS included: [`proto-bar.js`](proto-bar.js), next to
this `SKILL.md`.

- **Copy it as is** into the prototype's folder (at the proto root or in `assets/`). No link to the
  plugin: a proto must stay standalone, for example to be published as is on static hosting
  (GitHub Pages is the usual case).
- **Never modify the copy**, nor override its `.pb-*` classes from the proto's CSS. If the bar must
  evolve, change the plugin's file, bump the version in its header, then copy it again into the
  protos concerned.
- No "hand-made" reimplementation of a lookalike bar: that is precisely what this skill avoids.

## 2. Wire the bar

Load the script **before** the proto's, then call `ProtoBar.mount()` at startup. `mount()` needs
`document.body`: called earlier (script in the `<head>`), it waits for `DOMContentLoaded` to show
up.

```html
<script src="proto-bar.js"></script>
<script src="app.js"></script>
```

```js
ProtoBar.mount({
  title: 'Room booking, target design',   // name of the proto
  version: 'v1',                          // proto version, bumped at each delivery
  date: '2026-09-29',                     // date of the version, YYYY-MM-DD
  lang: 'en',                             // language of the fixed labels: 'en' (default) or 'fr'
  dateFormat: 'yyyy-mm-dd',               // optional: 'dd/mm/yyyy', 'dd.mm.yyyy' or 'yyyy-mm-dd'
  storagePrefix: 'roombooking.',          // localStorage keys cleared by the reset
  onState: (state) => render(),           // 'ok' | 'loading' | 'error'
  onReset: () => location.reload(),       // optional, this is the default
  controls: [
    { type: 'seg', id: 'layout', label: 'Layout', value: 'new',
      options: [['old', 'Old'], ['new', 'New']], onChange: (v) => setLayout(v) },
    { type: 'select', id: 'profile', label: 'Profile', value: 'member',
      groups: [{ label: 'Internal', options: [['member', 'Employee'], ['facility', 'Facility manager']] },
               { label: 'External', options: [['guest', 'Guest']] }],
      onChange: (v) => setProfile(v) },
    { type: 'button', id: 'tour', label: 'Replay the demo', onClick: () => startTour() },
  ],
});
```

- `lang` switches all the fixed labels of the bar ("mock data", "Settings", "States" and its three
  values, "Reset prototype", accessibility label). It follows the language of the proto. `dateFormat`
  defaults to `yyyy-mm-dd` in English and `dd/mm/yyyy` in French; `dd.mm.yyyy` is available for
  projects that use it. An unknown `lang` or `dateFormat` value is ignored with a console warning,
  and the default applies.
- `ProtoBar.set(id, value)` resyncs a setting when the proto changes it itself, without calling its
  `onChange`. If `mount()` is still waiting for `DOMContentLoaded` (script loaded in the `<head>`),
  `set` calls are queued and replayed, in order, as soon as the bar is mounted.
- The state selector is a setting like the others, with the reserved key `__state`:
  `ProtoBar.set('__state', 'error')` updates the selector and `ProtoBar.state`, **without** calling
  `onState` (a proto that changes state itself does its own rendering).
- `ProtoBar.state` gives the current state.
- Calling `mount()` again replaces the bar (listeners and observer included, no duplicate) and
  resets the state to `ok` **without** calling `onState`: it is up to the proto to render its
  nominal state again if it needs to. The values chosen in the settings are kept: the bar writes
  them into the `opts` passed (`def.value` is modified), so mounting again with the same `opts`
  finds the current choices. To start from the initial values, pass new `opts`.
- The bar carries the `data-proto-bar` attribute: when mounting, only a previous bar that carries it
  is removed, never a proto element that would use the `.pb` class.
- The bar is **always 56 px** high, at all widths, and stays sticky at the top. It exposes this
  height in `--proto-bar-h`: use it to offset the proto's `sticky` elements
  (`top: var(--proto-bar-h)`), never a hard-coded value.
- The bar sits above everything (`z-index: 2147483647`, the maximum). The **proto's overlays**
  (modals, side panels, scrims) must therefore **start below it**: `inset: var(--proto-bar-h) 0 0 0`
  instead of `inset: 0`, otherwise their header and close button go underneath.

In a living-specs project (`docs/specs/README.md` with `format: living-specs`), each screen
carries its `SC-xx` identifier (container id or `#SC-xx` route) and its sheet is kept up to date
with the `screen-spec` skill, which also captures the bar's states.

## 3. What is fixed, what is free

**Fixed, present in every bar, in this order** (English labels below, French with `lang: 'fr'`):

1. the **PROTOTYPE** tag, the title, then "mock data · version · date";
2. the proto's **own settings**;
3. the **States: Nominal / Loading / Error** selector;
4. the **Reset prototype** button, always last.

**Free:** the list of the proto's own settings (`seg` for 2 to 4 choices, `select` beyond,
`button` for a one-off action). Short labels, in the language of the proto (the same as `lang`),
one name per setting ("Profile", "Layout", "Variant", "Alerts").

## 4. The three states are a contract

The state selector is always there, so **the proto must render them**:

- **Loading**: skeletons in place of, and at the height of, the expected content;
- **Error**: error message that names the cause and offers a way out (`Retry`). If the screen is
  made of independent blocks, make only some of the blocks fail, to show that one block's error
  does not take the others down;
- **Nominal**: the normal screen.

A proto that does not have its states yet handles them anyway: at least a global skeleton and a
global error message, rather than a selector that does nothing.

## 5. Reset

"Reset prototype" clears the `localStorage` keys that start with `storagePrefix`, then calls
`onReset` (page reload by default). **Without `storagePrefix`, nothing is cleared** (the bar logs a
console warning): set it as soon as the proto stores anything. Prefix **all** the proto's keys, so
that a reset really puts the demo back to zero without touching other protos served from the same
domain.

## 6. Narrow widths

The bar never wraps. When the settings no longer fit next to the title, they move one by one,
**starting from the end**, into a dropdown menu opened by the **Settings** button; the order of
section 3 is kept between the bar and the menu. Below 900 px, the "mock data · version · date" line
disappears and the title is truncated. The menu closes with Escape or a click outside. Nothing to do
on the proto side.

## 7. Check

Before delivering the proto:

- the bar shows at the top, identical to the other protos (same file, same version), in the
  language of the proto;
- each own setting acts on the screen;
- the three states render something visible;
- "Reset prototype" brings back the initial state;
- at 390 px, the bar is 56 px high and the Settings button opens the settings.
