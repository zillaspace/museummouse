# Every museum on Earth

An interactive satellite map for Museum Mouse. Pins come from Wikidata, imagery from Esri, no keys or accounts needed.

## Open it

1. Put `index.html` and `fetch_museums.py` in one folder.
2. Double click `index.html`. It opens in your browser with an empty planet.
3. Click **Load from Wikidata**. It walks the world one country at a time and drops pins as it goes. Expect ten to twenty minutes for the full pass. You can leave it running and come back.

## Make it open instantly (recommended before Friday)

Run the script once so the data is baked in:

    python3 fetch_museums.py

It writes `museums.js` beside `index.html`. From then on the map opens with every pin already loaded, no waiting, no internet needed for the pins (the imagery still streams).

If you have never run Python: on a Mac, open Terminal, type `cd ` (with a space), drag the folder onto the Terminal window, press Return, then paste the command above.

## Use it

* Search by museum or country in the top right.
* Click any pin for the name, website, and Wikidata page.
* **Tag as pilot candidate** stars the pin and keeps a list you can export as CSV. The list is saved in your browser.
* Satellite and Streets toggle the basemap.

## Put it online

Upload the folder (including `museums.js`) to GitHub Pages, Netlify, or any web host. It is plain files, no server needed. Then the link works on a phone at the advisor meeting.

## Coverage, honestly

Wikidata holds tens of thousands of museums with coordinates, strongest in Europe and North America. UNESCO estimates about 104,000 museums exist. The gap is the small ones nobody has entered yet, which is also the market. The status line under the search box reports the exact count after a load.

## Google satellite instead of Esri

Possible with a Google Maps Platform key (Google Cloud account with billing attached). The place to swap it in is marked at the top of the script in `index.html`. Esri imagery is free for this use and looks the same from orbit, so this is optional.
