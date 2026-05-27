# Changelog

---

### 2026-05-27

**Model popup upgraded** - the "Show all" popup now shows pricing, context limits, and feature icons (tools, vision, reasoning, web search, code) right inside each model card. Models are grouped by family and you can search with a short delay so it feels smooth.

**New service status badges** - providers can now show badges like "Aggregator", "Community", "Mirror", "Experimental" etc. right next to their name, so you know what kind of service it is at a glance.

**Better adding providers** - it's now easier for me to add and update providers. The system validates data, supports text formatting (colors, bold), warning badges, and can move providers between pages without breaking anything.

**Behind the scenes** - all update scripts were rewritten to be faster and more reliable. Model pricing is now fetched live from provider APIs where available.

---

### 2026-05-26

- Added **NanoGPT** to *Freemium*
- Added **DeepInfra** to *Paid*

---


### 2026-05-23

- Added **SwiftRouter** to *Paid*

---

### 2026-05-21

**Cleaner tables** - removed rating (planning to improve it so the scoring basis is clear) and testing columns. Provider status and test results are now shown as neat badges right next to the name.

**All icons replaced with SVG** - emojis replaced with clean SVG icons: globe for links, lock for registration, phone, card, warning, and more.

**Hover to learn** - every icon shows a tooltip on hover. On mobile - long press to follow a link (works for warnings).

**Model list in popup** - click "Show all" for any provider to see the full model list. Filter by family (Claude, GPT, Gemini, etc.), click a model name to copy its ID.

**Model lists update automatically** - no more waiting for manual table updates. The site checks available models every 12 hours.

**New "Caution" page** - if a provider raises suspicions but there's no solid proof, it appears here. The warning badge next to the provider name links to this page.

---

### 2026-05-12

- Initial changelog created
