# StillMotion

A free, fully client-side tool that turns any photo into a downloadable MP4 or
WebM video clip, right in the browser. No uploads, no server, no account.

This is a **deliberately single-purpose site**. It contains exactly one tool.
There is no navigation to other tools, no tool hub, no shared multi-tool
header. This is a split-out from the AnyConvert multi-tool site
(`~/iCloud/website/anyconvert`) — the conversion logic was adapted from
`anyconvert`'s `image-to-video.astro`, but StillMotion is its own standalone
repo, its own domain, and its own deploy.

**Why single-purpose:** one keyword-matched domain per tool is the whole SEO
strategy for this family of sites. "Photo to video converter" ranks better on
a domain that is *only* about photo-to-video than as one card in a 20-tool
grid. Do not add other tools to this project, and do not add a nav linking
elsewhere. If a new tool idea comes up, it gets its own project under
`~/iCloud/website/<new-name>`, not a page here.

## What it does

1. User picks (or drags in) a still photo — JPG/PNG/WebP natively, or
   iPhone HEIC/HEIF via client-side decode.
2. User picks a duration (1–30s) and output format (MP4 H.264 or WebM VP9).
3. `ffmpeg.wasm` loops the image for the chosen duration and encodes a real
   video file, entirely inside the browser tab.
4. User downloads the resulting video. Nothing is ever uploaded anywhere.

## Stack

- **AstroJS** (static output, `astro build` → `dist/`, zero backend/server).
- **Tailwind v4** via the `@tailwindcss/vite` plugin, imported in
  `src/styles/global.css` with `@import "tailwindcss";` and a `@theme` block
  defining the design tokens below.
- **@ffmpeg/ffmpeg** + **@ffmpeg/util** — client-side video encoding
  (WebAssembly). Core files are fetched lazily from unpkg
  (`https://unpkg.com/@ffmpeg/core@0.12.10/dist/esm/`) — **must be the `esm`
  build, not `umd`**, because `@ffmpeg/ffmpeg`'s worker does
  `await import(coreURL)`, which requires an ES module. The `umd` build
  throws `Error: failed to import ffmpeg-core.js` silently inside the
  worker — check `preview_console_logs` at `level: 'all'` if debugging,
  not just `'error'`, since some ffmpeg.wasm failures only surface inside
  the worker/progress callback.
- **libheif-js** (`libheif-js/wasm-bundle`) — decodes HEIC/HEIF (iPhone
  photos) client-side before handing the decoded PNG to ffmpeg.wasm. NOT
  `heic2any` (unmaintained, throws on modern iPhone HEIC variants).
- **@astrojs/sitemap** — sitemap generation for SEO.
- No other conversion libraries are installed. This project intentionally
  does NOT depend on gifenc, utif2, upscaler/@upscalerjs, @xenova/transformers,
  canvas-confetti, or qr-code-styling — those belong to other AnyConvert-family
  tools, not this one. Only install what StillMotion itself needs.

## Design system (mandatory — do not deviate)

Premium cream/gold editorial look, NOT the generic white/cyan AI-tool
aesthetic used by the multi-tool AnyConvert site.

- Background: `#FAF6EC` (warm cream)
- Card/surface: `#FFFFFF` with a warm `#E8DFC8` border (never gray)
- Headings: `#2B2013` (warm espresso brown, not pure black)
- Body text: `#5C4F3D` (warm brown-gray)
- Accent / CTA / links / active states: `#C9982E` (warm gold), hover `#B8860B`
- Fonts: **Fraunces** (display/headings — soft-serif, editorial, premium
  feel) + **Inter** (body, labels, buttons, all interactive UI). Both loaded
  via Google Fonts `<link>` in `Layout.astro`'s `<head>` with
  `display=swap`. Headings use weight 600–700 and slightly negative
  letter-spacing (`-0.02em`) for a tightened, premium look.
- Generous whitespace, soft shadows only (never harsh), rounded-xl corners,
  no gradients, no dark mode. Cream-only aesthetic is the whole point.
- This must read like a small, confident, boutique SaaS product — not a
  generic free-tool dump.

## Structure

- `src/layouts/Layout.astro` — shared shell: simple header (brand name
  only, no nav to other tools), footer (About/Privacy/FAQ + copyright),
  SEO meta tags, Google Fonts.
- `src/pages/index.astro` — the one tool. Full conversion UI + logic.
- `src/pages/about.astro`, `privacy.astro`, `faq.astro`, `404.astro` —
  required pages for AdSense eligibility, linked from header/footer on
  every page (not just buried in the footer).
- `src/lib/escapeHtml.ts` — shared `escapeHtml()` helper. Any user-controlled
  text (filenames, error messages derived from filenames, etc.) rendered via
  `innerHTML` MUST go through this first. Canonical pattern carried over from
  anyconvert's `json-formatter.astro` / security audit.
- `public/robots.txt` — points to the sitemap.
- `netlify.toml` — sets `Cross-Origin-Opener-Policy: same-origin` +
  `Cross-Origin-Embedder-Policy: require-corp` (required for ffmpeg.wasm)
  plus standard security headers.

## Dev / test

- `npm run dev` — dev server on **port 4334** (distinct from anyconvert's
  4325 and sibling tools in the 4330s, so all projects can run concurrently
  without a port clash).
- File-input-driven tools can't be tested with a real OS file picker in
  headless Playwright. Test by constructing a `File` via
  `new File([blob], name, {type})`, wrapping it in a `DataTransfer`,
  setting `input.files = dt.files`, then dispatching a `change` event —
  then call `document.getElementById('generate-btn').click()` directly
  rather than a coordinate-based click tool (can get intercepted by dev
  toolbar overlays).
- Check `preview_console_logs` at `level: 'all'` when debugging ffmpeg.wasm.

## iCloud sync hygiene

This project lives in iCloud Drive
(`~/Library/Mobile Documents/com~apple~CloudDocs/website/stillmotion`).
`node_modules` is renamed to `node_modules.nosync` with a plain symlink
`node_modules -> node_modules.nosync`, so iCloud does not attempt to sync
hundreds of thousands of tiny dependency files across devices (it chokes on
that file count and can corrupt sync state). `tsconfig.json`'s `exclude`
array includes **both** `"node_modules"` and `"node_modules.nosync"` —
`tsc`/`astro check` does not treat the `.nosync` suffix as implicitly
excluded, and without the explicit entry `astro check` crashes trying to
typecheck the vendored dependency tree.

On a fresh checkout on the other Mac: `npm install` regenerates
`node_modules.nosync` locally (device-local, not synced), then re-create the
symlink if missing:
```
npm install
mv node_modules node_modules.nosync 2>/dev/null; ln -sf node_modules.nosync node_modules
```

## Deploy

Netlify. Deployed via the Netlify CLI using the token in
`~/.claude/credentials/netlify.env` (`NETLIFY_API_KEY` → export as
`NETLIFY_AUTH_TOKEN`).

```
source ~/.claude/credentials/netlify.env
export NETLIFY_AUTH_TOKEN="$NETLIFY_API_KEY"
npm run build
netlify deploy --prod --dir=dist
```

## Still needed before this earns anything (manual, Shreyas)

1. Point a real domain at the Netlify site (ideally photo-to-video /
   still-motion keyword-matched) once the build is confirmed live.
2. Get real traffic before applying for AdSense.
3. Apply for AdSense, then add `public/ads.txt` with the real
   `pub-XXXXXXXXXXXXXXXX` line and the AdSense script + Auto Ads.
4. Submit to Google Search Console + Bing Webmaster Tools.

## Development

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and
`astro dev logs`.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)
