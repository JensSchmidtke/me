# Wegspiel – building a class activity with simulation

An information-gap map game for German A1 (Netzwerk chapters 1–3), for 5–12 adult learners.
This note documents how the activity was designed with small computer simulations instead of by trial and error in class.

Status: built and checked by computer; **not yet tried in a class**. All timings below are estimates under stated assumptions.

## The activity

- Every participant gets a printed street map (river, park, 17 houses with doors, four named long streets) and a route of four steps, written as fixed phrases: *vom Bahnhof → zum Theater*, *vom Theater → zum Museum*, … (feminine places: *von der Schule → zur Post*, so no dative rule is needed).
- On each map only 6 houses carry their names. The other houses are blank, and the participant writes in the name once they have found the place.
- To find a place you ask someone: **"Wie komme ich vom Bahnhof zum Theater?"** Only a participant whose map shows both places can answer, by reading the route off their own map: **"Gehen Sie links, dann geradeaus, dann rechts."** Everybody else says "Ich weiß nicht, tut mir leid."
- Directions use only *links, rechts, geradeaus*. The first word is taken from the door of the house (left or right along the street), then one word per junction.
- Because a step starts at the previous stop, the steps have to be asked in order.
- Cards stay hidden: information is passed only by speaking.

Language level: all phrases are chapter 3 or lower by the project's chapter check (*Wie bitte?*, *Noch einmal, bitte*, *Ist das richtig?* can be added as repair language). *Ich weiß nicht* (ch. 6) and *tut mir leid* (ch. 5) are used as fixed phrases.

## Who designed what

The activity itself is the teacher's design: the information gap with a map, the chain of stops that forces the order of the questions, the doors as a fixed starting direction for the directions, the competitive element, restricting the language to *links, rechts, geradeaus*, and the decision that nothing may be shown, only said. The simulations only counted and checked what that design needed (who can answer which step, whether every route works on the map, how long a round takes). Every problem listed below was found by the teacher looking at a result.

## Design problems and how simulation solved them

1. **Who can answer what?** Each map labels only some places. For every step of every route there must be a participant who can answer it, for every class size from 5 to 12 (absent participants must not break the game). Too many helpers makes it too fast and too easy.
   - Model: 12 real places + 5 filler houses that are never labelled and never a goal. Participant *i* starts at place *i*. A route = start, 3 stops, a final place (all finals different). A map labels the participant's own start and *k* other places.
   - A random search (`wegspiel_design_search.py`) scores each candidate set of routes and maps over all class sizes 5–12 and counts how many other participants can answer each step. Steps with nobody get a heavy penalty, extra helpers a small one, and small classes weigh more.
   - Result used: 6 labelled houses per map. Exactly 1 possible helper per step for 5, 6 and 7 participants, at most 2 for 8–10, at most 3 for 11–12.
   - Findings from earlier exploratory runs (scripts not kept): with 8 places and 4-stop routes, 5 participants never got more than 1 helper per step while keeping 4 labelled places; labelling too many places per map (8 of 12) left too little to find out; fillers cost nothing in helper counts because they are never part of a step.
2. **A street map where the directions work.**
   - A tree-shaped street plan forced routes to double back through earlier stops, so it was replaced by a grid (5 × 4 junctions) with some streets removed, one river with 2 bridges, and a park.
   - Houses stand beside the street with a door, so "left/right" always starts from a known direction. Places never sit on a bridge or in the park.
   - A second search (`wegspiel_layout.py`) places the 17 houses on street pieces so that the routes needed are short (2–4 words, 3.3 on average) and so that real places and fillers are spread over all four parts of the map. Without that rule the optimiser pushed the fillers to the edge.
   - **Check:** `wegspiel_build_pages.py` walks every route on the map using only the direction words from the door and tests that it ends in the right street.
3. **Time.** `wegspiel_time_sim.py` simulates 5 participants who ask one person at a time, remember who did not know, and wait if the helper is busy. Assumed durations (not measured): failed ask 6–10 s, successful ask 20–30 s, 3 s between asks. Result: about 8 minutes (6 s / 20 s), 10 minutes (8 s / 25 s) or 12 minutes (10 s / 30 s) until everyone finishes. An earlier run that counted rounds, not seconds, gave 27 rounds on average when participants remember who did not know and 44 when they ask at random.
4. **Print layout.** Two maps fit on one A4 portrait page (houses about 22 mm wide, enough to write a word), 6 pages for 12 participants. Printing the HTML from Safari put one map per sheet, so the print version is a PDF made with Chrome (fixed margins).

## Files (all in this folder)

| File | What it is |
|---|---|
| `wegspiel_design_search.py` | Step 1: routes and labelled places (seeded, reproduces `wegspiel_design.json`) |
| `wegspiel_layout.py` | Step 2: street layout and house positions (reproduces `wegspiel_layout.json`) |
| `wegspiel_build_pages.py` | Step 3: walks all routes, writes the HTML pages |
| `wegspiel_time_sim.py` | Step 4: time estimate |
| `wegspiel_design.json`, `wegspiel_layout.json` | Data produced by steps 1 and 2 |
| `wegspiel_schueler.html` / `.pdf` | Participant sheets (2 per A4 page, 12 participants) |
| `wegspiel_lehrer.html` | Teacher sheets: full map with names, one example route per step, who knows what, helper counts |

Run in this order: `python3 wegspiel_design_search.py`, `python3 wegspiel_layout.py`, `python3 wegspiel_build_pages.py`. Check run on 15 November 2026: all three reproduced the existing data files and both HTML files byte for byte, and the time simulation reproduced the numbers above.

PDF from the HTML (Chrome):

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=wegspiel_schueler.pdf "file://$PWD/wegspiel_schueler.html"
```

## Limits

- Searches are random and seeded, not exhaustive. "Best found" is not a proof that nothing better exists.
- The map pages were looked at only as a rendered image of page 1 of the PDF.
- The house names (Bahnhof, Rathaus, Museum, Park, Hotel, Café, Restaurant, Kino, Theater, Schule, Universität, Post; fillers Markt, Stadion, Schwimmbad, Kirche, Hafen) and street names (Hauptstraße, Gartenstraße, Lindenstraße, Goethestraße) are placeholders that can be swapped in `wegspiel_build_pages.py`. Gender (*zum/zur*) is set in the same file.
- The vocabulary check uses `assign_chapters.py` from this project and is not part of these scripts.
