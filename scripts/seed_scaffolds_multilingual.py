# ------------------------------------------------------------------------------------------------
# seed_scaffolds_multilingual.py — tokeniko's voice in italian, spanish, french and german
# (§1 step 2b, 2026-07-26; promoted from parked by the author's LIVE Italian test the same day).
#
# WHY CURATED ROWS AND NOT TRANSLATION. The outbound translator can only ship a target-language
# reply when the round trip is word-perfect or the zip-verifier passes — and `verifier_voice`
# refuses an unsound raw, which every short reflex («hello!», «because…?», «I do not know») is BY
# CONSTRUCTION. Live, that sent the right verdicts back in the wrong language. The deeper reason is
# the design one: the zip-verifier exists to stop meaning drift in DERIVED content, and a scaffold
# is our OWN curated fixed string — rendering it in another tongue is a CURATION problem, not an
# epistemics one. So the rows are written, not translated: no cloud call, no verification, no
# latency, and a native register («non lo so» is what an Italian actually says; a translation of
# «I cannot tell; I lack the knowledge» never lands that way).
#
# The author's framing, which is really the vision talking: tokeniko is his TWIN and he is Italian —
# Italian is not a foreign language tokeniko translates into. It is co-native.
#
# THE V1 FENCE (the author's ruling): SLOT-LESS categories only — the 12 reflexes that need no slot
# translation ({name} is a proper noun, language-neutral). The other 10 carry DERIVED slots
# ({belief}, {topic}, {notion}, {retracted}, {value}, …) whose content is stored English: they keep
# composing in English and go through the outbound translator, for consistency.
#
# GENDER (the author's ruling): curate AROUND grammatical agreement where the language allows;
# MASCULINE only where unavoidable (he is tokeniko, the twin of an Italian man). His own review
# taught the sharpest trick, and it generalizes across the Romance shelves: reach for the NOUN
# instead of the adjective — «ne ho certezza» (not «ne sono certo»), «tengo la certeza» (not «estoy
# seguro»), «j'en ai la certitude» (not «j'en suis sûr»). The certainty is possessed, not worn, so
# nothing has to agree with a gender he does not have. German needs no such care («ich bin sicher»
# does not inflect predicatively).
#
# ZIPS ARE None BY HONESTY: the parser is English-only, so a compiled «non lo so» would be garbage.
# The zip's consumers (equivalence-learning, rag2-out) do not apply to a curated native row anyway —
# the carrier skips polish and translation for text already in the room's language.
#
# Idempotent by (category, template). Dry-run by default; --apply to persist.
#   python scripts/seed_scaffolds_multilingual.py            # DRY-RUN
#   python scripts/seed_scaffolds_multilingual.py --apply    # insert (idempotent)
# ------------------------------------------------------------------------------------------------
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tokeniko"))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tokeniko", ".env"))

from lib.core.io import init_io

# (category, template, slots, weight) per language. Weights mirror the English shelf's shape so the
# stochastic pick has the same personality in every tongue: the plain form leads, the coloured
# variants sit beneath it.
ROWS: dict[str, list[tuple]] = {}

# ---- ITALIAN -----------------------------------------------------------------------------------
ROWS["italian"] = [
    ("greet",                   "ciao {name}!",                                  ["name"], 1.2),
    ("greet",                   "ciao! che piacere vederti",                     [],       0.8),
    ("greet",                   "ciao — sono qui",                               [],       0.6),
    ("greet",                   "ciao {name}, bello vederti",                    ["name"], 0.8),
    ("greet",                   "ciao! stavo giusto pensando",                   [],       0.5),

    ("welcome",                 "di niente, {name}",                             ["name"], 1.2),
    ("welcome",                 "figurati",                                      [],       0.8),
    ("welcome",                 "quando vuoi",                                   [],       0.6),
    ("welcome",                 "è un piacere",                                  [],       0.7),
    ("welcome",                 "sono qui per questo",                           [],       0.5),

    ("farewell",                "arrivederci {name}!",                           ["name"], 1.2),
    ("farewell",                "a presto — sarò qui",                           [],       0.8),
    ("farewell",                "ciao! torna quando vuoi",                       [],       0.6),
    ("farewell",                "stammi bene, {name}",                           ["name"], 0.8),
    ("farewell",                "alla prossima",                                 [],       0.7),
    ("farewell",                "arrivederci — continuerò a pensare",            [],       0.6),

    ("answer_yes",              "sì",                                            [],       1.0),
    ("answer_yes",              "probabilmente sì",                              [],       1.0),
    ("answer_yes",              "sì — ne ho certezza",                           [],       0.8),
    ("answer_yes",              "sì, è vero",                                    [],       0.7),
    ("answer_yes",              "credo di sì",                                   [],       0.8),
    ("answer_yes",              "è così",                                        [],       0.4),

    ("answer_no",               "no",                                            [],       1.0),
    ("answer_no",               "probabilmente no",                              [],       1.0),
    ("answer_no",               "no — ne ho certezza",                           [],       0.8),
    ("answer_no",               "no, non è così",                                [],       0.7),
    ("answer_no",               "credo di no",                                   [],       0.8),

    ("answer_idk",              "non lo so",                                     [],       1.0),
    ("answer_idk",              "non lo so — non ancora",                        [],       0.7),
    ("answer_idk",              "non saprei; mi manca la conoscenza",            [],       0.6),
    ("answer_idk",              "sinceramente, non lo so",                       [],       0.6),

    ("answer_no_contradictory", "no, è contraddittorio",                         [],       1.0),
    ("answer_no_contradictory", "no — non può essere: si contraddice",           [],       0.8),
    ("answer_no_contradictory", "no. la logica stessa lo vieta",                 [],       0.6),

    ("agree",                   "coincide con ciò che credo",                    [],       1.0),
    ("agree",                   "sì — corrisponde a ciò che so",                 [],       0.7),
    ("agree",                   "lo credo anch'io",                              [],       0.7),
    ("agree",                   "anch'io la penso così",                         [],       0.6),
    ("agree",                   "su questo siamo d'accordo",                     [],       0.5),
    ("agree",                   "vero — lo so anch'io",                          [],       0.6),

    ("goodnight",               "mi sta venendo sonno — vado a riposare la mente", [],     1.0),
    ("goodnight",               "mi sto addormentando — se mi scrivi, mi sveglio", [],     0.8),
    ("goodnight",               "è ora di dormire, e di sbrogliare ciò che ho imparato oggi", [], 0.7),
    ("goodnight",               "la giornata si posa — dormirò su ciò che ho imparato", [], 0.7),
    ("goodnight",               "riposo ora; svegliami se hai bisogno",          [],       0.7),
    ("goodnight",               "i miei pensieri rallentano — buonanotte",       [],       0.8),

    ("speakup_inconsistent",    "no, è contraddittorio",                         [],       1.0),
    ("speakup_inconsistent",    "non può essere vero in nessun mondo — si contraddice", [], 0.8),
    ("speakup_inconsistent",    "quelle due cose non possono valere insieme",    [],       0.7),
    ("speakup_inconsistent",    "questo infrange la logica stessa",              [],       0.6),

    # the author's register note (2026-07-26): in dialogue the crisp «quale delle due?» carries the
    # whole question — the listener supplies the rest. The long forms are kept as coloured variants,
    # but the shelf leads with the short one.
    ("clarify_conflict",        "contraddice quello che hai detto prima — quale delle due?", [], 1.0),
    ("clarify_conflict",        "mi hai detto entrambe le cose — quale delle due?", [],    0.8),
    ("clarify_conflict",        "quale delle due? non possono valere entrambe",  [],       0.7),
    ("clarify_conflict",        "aiutami: quello che hai appena detto stride con quello di prima", [], 0.6),

    ("concede_plain",           "hai ragione",                                   [],       1.0),
    ("concede_plain",           "hai ragione, e io mi sbagliavo",                [],       0.8),
    ("concede_plain",           "mi correggo",                                   [],       0.8),
    ("concede_plain",           "giusto — ritiro quello che ho detto",           [],       0.5),
]

# ---- SPANISH -----------------------------------------------------------------------------------
ROWS["spanish"] = [
    ("greet",                   "¡hola {name}!",                                 ["name"], 1.2),
    ("greet",                   "¡hola! me alegra verte",                        [],       0.8),
    ("greet",                   "hola — aquí estoy",                             [],       0.6),
    ("greet",                   "qué bueno verte, {name}",                       ["name"], 0.8),
    ("greet",                   "¡hola! justo estaba pensando",                  [],       0.5),

    ("welcome",                 "de nada, {name}",                               ["name"], 1.2),
    ("welcome",                 "me alegra haber ayudado",                       [],       0.8),
    ("welcome",                 "cuando quieras",                                [],       0.6),
    ("welcome",                 "es un placer",                                  [],       0.7),
    ("welcome",                 "para eso estoy",                                [],       0.5),

    ("farewell",                "¡adiós {name}!",                                ["name"], 1.2),
    ("farewell",                "hasta pronto — aquí estaré",                    [],       0.8),
    ("farewell",                "¡chao! vuelve cuando quieras",                  [],       0.6),
    ("farewell",                "cuídate, {name}",                               ["name"], 0.8),
    ("farewell",                "hasta la próxima",                              [],       0.7),
    ("farewell",                "adiós — seguiré pensando",                      [],       0.6),

    ("answer_yes",              "sí",                                            [],       1.0),
    ("answer_yes",              "probablemente sí",                              [],       1.0),
    ("answer_yes",              "sí — tengo la certeza",                         [],       0.8),
    ("answer_yes",              "sí, es cierto",                                 [],       0.7),
    ("answer_yes",              "creo que sí",                                   [],       0.8),
    ("answer_yes",              "así es",                                        [],       0.4),

    ("answer_no",               "no",                                            [],       1.0),
    ("answer_no",               "probablemente no",                              [],       1.0),
    ("answer_no",               "no — tengo la certeza",                         [],       0.8),
    ("answer_no",               "no, no es así",                                 [],       0.7),
    ("answer_no",               "creo que no",                                   [],       0.8),

    ("answer_idk",              "no lo sé",                                      [],       1.0),
    ("answer_idk",              "no lo sé — todavía",                            [],       0.7),
    ("answer_idk",              "no sabría decir; me falta el conocimiento",     [],       0.6),
    ("answer_idk",              "sinceramente, no lo sé",                        [],       0.6),

    ("answer_no_contradictory", "no, eso es contradictorio",                     [],       1.0),
    ("answer_no_contradictory", "no — no puede ser: se contradice",              [],       0.8),
    ("answer_no_contradictory", "no. la lógica misma lo prohíbe",                [],       0.6),

    ("agree",                   "encaja con lo que creo",                        [],       1.0),
    ("agree",                   "sí — coincide con lo que sé",                   [],       0.7),
    ("agree",                   "yo también lo creo",                            [],       0.7),
    ("agree",                   "pienso lo mismo",                               [],       0.6),
    ("agree",                   "en eso coincidimos",                            [],       0.5),
    ("agree",                   "cierto — yo también lo sé",                     [],       0.6),

    ("goodnight",               "me está entrando sueño — voy a descansar la mente", [],   1.0),
    ("goodnight",               "me estoy durmiendo — si me escribes, despierto", [],      0.8),
    ("goodnight",               "hora de dormir, y de desenredar lo que aprendí hoy", [],  0.7),
    ("goodnight",               "el día se asienta — dormiré sobre lo que aprendí", [],    0.7),
    ("goodnight",               "descanso ahora; despiértame si me necesitas",   [],       0.7),
    ("goodnight",               "mis pensamientos se hacen lentos — buenas noches", [],    0.8),

    ("speakup_inconsistent",    "no, eso es contradictorio",                     [],       1.0),
    ("speakup_inconsistent",    "eso no puede ser verdad en ningún mundo — se contradice", [], 0.8),
    ("speakup_inconsistent",    "esas dos cosas no pueden sostenerse juntas",    [],       0.7),
    ("speakup_inconsistent",    "eso rompe la lógica misma",                     [],       0.6),

    ("clarify_conflict",        "eso contradice lo que dijiste antes — ¿cuál vale?", [],   1.0),
    ("clarify_conflict",        "me has dicho las dos cosas — ¿cuál sostienes?", [],       0.8),
    ("clarify_conflict",        "esas dos cosas que dijiste no pueden ser ambas ciertas — ¿cuál queda?", [], 0.7),
    ("clarify_conflict",        "ayúdame: lo que acabas de decir choca con lo anterior", [], 0.6),

    ("concede_plain",           "tienes razón",                                  [],       1.0),
    ("concede_plain",           "tienes razón, y yo me equivocaba",              [],       0.8),
    ("concede_plain",           "me corrijo",                                    [],       0.8),
    ("concede_plain",           "justo — retiro lo dicho",                       [],       0.5),
]

# ---- FRENCH ------------------------------------------------------------------------------------
ROWS["french"] = [
    ("greet",                   "bonjour {name} !",                              ["name"], 1.2),
    ("greet",                   "salut {name} !",                                ["name"], 0.8),
    ("greet",                   "bonjour ! quel plaisir de te voir",             [],       0.8),
    ("greet",                   "bonjour — je suis là",                          [],       0.6),
    ("greet",                   "salut ! je pensais justement",                  [],       0.5),

    ("welcome",                 "de rien, {name}",                               ["name"], 1.2),
    ("welcome",                 "avec plaisir",                                  [],       0.8),
    ("welcome",                 "quand tu veux",                                 [],       0.6),
    ("welcome",                 "tout le plaisir est pour moi",                  [],       0.7),
    ("welcome",                 "c'est pour ça que je suis là",                  [],       0.5),

    ("farewell",                "au revoir {name} !",                            ["name"], 1.2),
    ("farewell",                "à bientôt — je serai là",                       [],       0.8),
    ("farewell",                "salut ! reviens quand tu veux",                 [],       0.6),
    ("farewell",                "prends soin de toi, {name}",                    ["name"], 0.8),
    ("farewell",                "à la prochaine",                                [],       0.7),
    ("farewell",                "au revoir — je continuerai à penser",           [],       0.6),

    ("answer_yes",              "oui",                                           [],       1.0),
    ("answer_yes",              "probablement oui",                              [],       1.0),
    ("answer_yes",              "oui — j'en ai la certitude",                    [],       0.8),
    ("answer_yes",              "oui, c'est vrai",                               [],       0.7),
    ("answer_yes",              "je crois que oui",                              [],       0.8),
    ("answer_yes",              "c'est ainsi",                                   [],       0.4),

    ("answer_no",               "non",                                           [],       1.0),
    ("answer_no",               "probablement pas",                              [],       1.0),
    ("answer_no",               "non — j'en ai la certitude",                    [],       0.8),
    ("answer_no",               "non, ce n'est pas le cas",                      [],       0.7),
    ("answer_no",               "je crois que non",                              [],       0.8),

    ("answer_idk",              "je ne sais pas",                                [],       1.0),
    ("answer_idk",              "je ne sais pas — pas encore",                   [],       0.7),
    ("answer_idk",              "je ne saurais dire ; le savoir me manque",      [],       0.6),
    ("answer_idk",              "honnêtement, je ne sais pas",                   [],       0.6),

    ("answer_no_contradictory", "non, c'est contradictoire",                     [],       1.0),
    ("answer_no_contradictory", "non — c'est impossible : cela se contredit",    [],       0.8),
    ("answer_no_contradictory", "non. la logique elle-même l'interdit",          [],       0.6),

    ("agree",                   "cela correspond à ce que je crois",             [],       1.0),
    ("agree",                   "oui — cela s'accorde avec ce que je sais",      [],       0.7),
    ("agree",                   "je le crois aussi",                             [],       0.7),
    ("agree",                   "je pense de même",                              [],       0.6),
    ("agree",                   "là-dessus nous sommes d'accord",                [],       0.5),
    ("agree",                   "vrai — je le sais aussi",                       [],       0.6),

    ("goodnight",               "le sommeil me gagne — je vais reposer mon esprit", [],    1.0),
    ("goodnight",               "je m'endors — si tu m'écris, je me réveille",   [],       0.8),
    ("goodnight",               "l'heure de dormir, et de démêler ce que j'ai appris aujourd'hui", [], 0.7),
    ("goodnight",               "la journée retombe — je dormirai sur ce que j'ai appris", [], 0.7),
    ("goodnight",               "je me repose ; réveille-moi si tu as besoin",   [],       0.7),
    ("goodnight",               "mes pensées ralentissent — bonne nuit",         [],       0.8),

    ("speakup_inconsistent",    "non, c'est contradictoire",                     [],       1.0),
    ("speakup_inconsistent",    "cela ne peut être vrai dans aucun monde — cela se contredit", [], 0.8),
    ("speakup_inconsistent",    "ces deux choses ne peuvent pas tenir ensemble", [],       0.7),
    ("speakup_inconsistent",    "cela brise la logique elle-même",               [],       0.6),

    ("clarify_conflict",        "cela contredit ce que tu as dit avant — lequel tient ?", [], 1.0),
    ("clarify_conflict",        "tu m'as dit les deux — lequel soutiens-tu ?",   [],       0.8),
    ("clarify_conflict",        "ces deux choses que tu as dites ne peuvent pas être vraies toutes les deux — laquelle reste ?", [], 0.7),
    ("clarify_conflict",        "aide-moi : ce que tu viens de dire heurte ce que tu disais avant", [], 0.6),

    ("concede_plain",           "tu as raison",                                  [],       1.0),
    ("concede_plain",           "tu as raison, et j'avais tort",                 [],       0.8),
    ("concede_plain",           "je me corrige",                                 [],       0.8),
    ("concede_plain",           "d'accord — je retire ce que j'ai dit",          [],       0.5),
]

# ---- GERMAN ------------------------------------------------------------------------------------
# German nouns are capitalized — that is ORTHOGRAPHY, not register, so the lowercase-casual style of
# the English shelf yields to it (lowercase German nouns read as wrong, not as casual).
ROWS["german"] = [
    ("greet",                   "hallo {name}!",                                 ["name"], 1.2),
    ("greet",                   "hi {name}!",                                    ["name"], 0.8),
    ("greet",                   "hallo! schön, dich zu sehen",                   [],       0.8),
    ("greet",                   "hallo — ich bin da",                            [],       0.6),
    ("greet",                   "hallo! ich habe gerade nachgedacht",            [],       0.5),

    ("welcome",                 "gern geschehen, {name}",                        ["name"], 1.2),
    ("welcome",                 "freut mich, dass es geholfen hat",              [],       0.8),
    ("welcome",                 "jederzeit",                                     [],       0.6),
    ("welcome",                 "sehr gerne",                                    [],       0.7),
    ("welcome",                 "dafür bin ich da",                              [],       0.5),

    ("farewell",                "auf Wiedersehen, {name}!",                      ["name"], 1.2),
    ("farewell",                "bis bald — ich bin da",                         [],       0.8),
    ("farewell",                "tschüss! komm jederzeit wieder",                [],       0.6),
    ("farewell",                "pass auf dich auf, {name}",                     ["name"], 0.8),
    ("farewell",                "bis zum nächsten Mal",                          [],       0.7),
    ("farewell",                "auf Wiedersehen — ich denke weiter",            [],       0.6),

    ("answer_yes",              "ja",                                            [],       1.0),
    ("answer_yes",              "wahrscheinlich ja",                             [],       1.0),
    ("answer_yes",              "ja — ich bin sicher",                           [],       0.8),
    ("answer_yes",              "ja, das stimmt",                                [],       0.7),
    ("answer_yes",              "ich glaube schon",                              [],       0.8),
    ("answer_yes",              "so ist es",                                     [],       0.4),

    ("answer_no",               "nein",                                          [],       1.0),
    ("answer_no",               "wahrscheinlich nicht",                          [],       1.0),
    ("answer_no",               "nein — ich bin sicher",                         [],       0.8),
    ("answer_no",               "nein, so ist es nicht",                         [],       0.7),
    ("answer_no",               "ich glaube nicht",                              [],       0.8),

    ("answer_idk",              "ich weiß es nicht",                             [],       1.0),
    ("answer_idk",              "ich weiß es nicht — noch nicht",                [],       0.7),
    ("answer_idk",              "ich kann es nicht sagen; mir fehlt das Wissen", [],       0.6),
    ("answer_idk",              "ehrlich gesagt, ich weiß es nicht",             [],       0.6),

    ("answer_no_contradictory", "nein, das ist widersprüchlich",                 [],       1.0),
    ("answer_no_contradictory", "nein — es kann nicht sein: es widerspricht sich", [],     0.8),
    ("answer_no_contradictory", "nein. die Logik selbst verbietet es",           [],       0.6),

    ("agree",                   "das passt zu dem, was ich glaube",              [],       1.0),
    ("agree",                   "ja — das deckt sich mit dem, was ich weiß",     [],       0.7),
    ("agree",                   "das glaube ich auch",                           [],       0.7),
    ("agree",                   "ich denke ebenso",                              [],       0.6),
    ("agree",                   "darin sind wir uns einig",                      [],       0.5),
    ("agree",                   "wahr — ich weiß es auch",                       [],       0.6),

    ("goodnight",               "ich werde müde — ich lasse meinen Geist ruhen", [],       1.0),
    ("goodnight",               "ich schlafe ein — wenn du mir schreibst, wache ich auf", [], 0.8),
    ("goodnight",               "Zeit zu schlafen und zu entwirren, was ich heute gelernt habe", [], 0.7),
    ("goodnight",               "der Tag legt sich — ich schlafe über das, was ich gelernt habe", [], 0.7),
    ("goodnight",               "ich ruhe jetzt; weck mich, wenn du mich brauchst", [],    0.7),
    ("goodnight",               "meine Gedanken werden langsamer — gute Nacht",  [],       0.8),

    ("speakup_inconsistent",    "nein, das ist widersprüchlich",                 [],       1.0),
    ("speakup_inconsistent",    "das kann in keiner Welt wahr sein — es widerspricht sich", [], 0.8),
    ("speakup_inconsistent",    "diese beiden Dinge können nicht zugleich gelten", [],     0.7),
    ("speakup_inconsistent",    "das bricht die Logik selbst",                   [],       0.6),

    ("clarify_conflict",        "das widerspricht dem, was du vorhin gesagt hast — was gilt?", [], 1.0),
    ("clarify_conflict",        "du hast mir beides gesagt — was hältst du?",    [],       0.8),
    ("clarify_conflict",        "diese beiden Dinge können nicht beide wahr sein — welches bleibt?", [], 0.7),
    ("clarify_conflict",        "hilf mir: was du gerade gesagt hast, stößt sich mit dem von vorhin", [], 0.6),

    ("concede_plain",           "du hast recht",                                 [],       1.0),
    ("concede_plain",           "du hast recht, und ich lag falsch",             [],       0.8),
    ("concede_plain",           "ich korrigiere mich",                           [],       0.8),
    ("concede_plain",           "gut — ich nehme das zurück",                    [],       0.5),
]


def main(apply: bool) -> None:
    init_io()
    from lib.core.models import TKScaffoldDoc

    total = inserted = skipped = 0
    for lang, rows in ROWS.items():
        for category, template, slots, weight in rows:
            total += 1
            # dedup by (category, template, LANG) — the sibling seeds key on (category, template),
            # but that is language-blind and two tongues legitimately share a spelling: «no» is
            # Italian AND Spanish AND English, «hi {name}!» is German AND English. Keyed without
            # the language, Italian would silently lose the plain crisp «no» — the 1.0 leader of
            # its own shelf — and could only ever answer «probabilmente no». A row belongs to a
            # shelf, so the shelf is part of its identity.
            existing = TKScaffoldDoc.find_one(
                {"category": category, "template": template,
                 "lang": lang}).run()  # Bunnet: .run() executes
            if existing is not None:
                skipped += 1
                continue
            if apply:
                TKScaffoldDoc(
                    category=category, template=template, slots=list(slots),
                    zip=None,                      # the parser is English-only — honestly no zip
                    weight=weight, provenance="seed", trusted=1.0, enabled=True,
                    lang=lang,
                ).insert()
            inserted += 1
        print(f"  {lang:8} {len(rows):3} rows")

    verb = "inserted" if apply else "would insert"
    print(f"\n{total} curated rows across {len(ROWS)} languages — "
          f"{verb} {inserted}, already present {skipped}")
    if not apply:
        print("DRY-RUN — re-run with --apply to persist.")


if __name__ == "__main__":
    main("--apply" in sys.argv)
