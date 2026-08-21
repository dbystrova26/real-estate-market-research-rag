# Design Note: Why This Doesn't Look Exactly Like Catella's House View

The rendered report in this repo is **styled in the spirit of** institutional real estate
research (clean data-forward layout, accent color bars, pull quotes) —
the same visual register the March 2026 House View uses — but it deliberately does not:

- Use Catella's logo or red square brand mark
- Use Catella's exact corporate typeface (which isn't publicly identified/licensed to me)
- Reproduce any of the report's original text, charts, or chart data

This is on purpose. The report is copyrighted ("© Catella, 2026. All rights reserved")
and its distribution terms explicitly restrict reproduction without written consent. A
portfolio project — especially one built while applying to work there — should read as
*"here's how I'd build the tool,"* not *"here's a copy of your work with my name on it."*

The font used (Inter in HTML, Helvetica in the PDF, matched as closely as matplotlib's
font fallback allows in the charts) is one clean sans-serif family throughout,
open-licensed and freely available, chosen deliberately over a serif/sans mix so
titles read as bold-and-larger within the same typeface rather than as a visually
different one.

If this becomes a real conversation with the team, matching their actual brand guidelines
precisely would obviously be a five-minute fix with the real assets — that's not the hard
part of this project.
