"""0027 — inflections v3: **a noun has a number, and the speaker stated it** (schema v6).

**«Software can be MINDS» and «software can be A MIND» were the same zip.** The box held
`{head: mind.n}` and nothing else, so the decompiler had two renderings and both were wrong: «be
mind» is not English, and «be a mind» measured the round trip DOWN — 65 to 61 of 87 — because an
article the zip does not hold comes back as a determination it did not have. The Captain ruled the
field (`Box.number`, schema v6); this is the roster that lets it be SAID.

**THE RULE FIRST, AND TWO OF ITS THREE BRANCHES ARE THE VERB'S** — `-ies` after a consonant and `y`,
`-es` after a sibilant, `-s` otherwise. English marks a plural noun and a third-singular verb with
one suffix, which is why `db/0022`'s rule needed almost no changing. Two branches are new and both
are measured, not assumed:

    -o     takes `-s`. **668 of WordNet's 829** consonant-plus-`-o` nouns do, against 89 that take
           `-es` — the same way round as the verb. The first draft had it backwards on the strength
           of «heroes» and «potatoes», and would have written «photoes».
    -sis   takes `-ses` — «analysis» → «analyses», a Greek plural English kept, right for **514 of
           the 546** nouns ending in it.

**TWO RESOURCES, as `db/0024`.** Every row is cross-checked against **WordNet's `noun.exc`**,
Princeton's hand-curated list of irregular noun forms, and `lemminflect` run offline as an
instrument. 295 rows, and only **three** disagreements in the whole of WordNet's 55,387 single-word
noun lemmas:

    duodenum   the instrument's «duodena» is right; WordNet's «duona»/«duonas» are plainly typos
    edema      it said «edema», unchanged, which is wrong; WordNet's «edemata» is the Greek and the
               rule's «edemas» is the English, so the rule stands and no row is written
    vertigo    the same shape, and the same answer

**WHAT IS DELIBERATELY NOT HERE: THE MASS NOUNS.** The instrument answers «abandon», «abeyance»,
«abhorrence» unchanged, and it is right — they have no plural — but that is **5,525 lemmas**, and a
roster of them would be a dictionary of uncountability wearing an inflection table's clothes. The
decompiler never asks: a box with no `number` is rendered singular, and a mass noun never carries
one. *If a witness ever arrives — a zip that asks for the plural of a mass noun — it is a defect
upstream, not a missing row here.*

**Written by the QM on 2026-09-20, by `tools/inflection_bench.py --tag NNS`.**
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, InflectionDoc
from tk2.migrations import ensure_collections

VERSION = 3

TAG_PLURAL = "NNS"

SOURCE = ("lemminflect 0.2.3 cross-checked against WordNet's noun.exc over 55,387 single-word noun "
          "lemmas, 2026-09-20, by `tools/inflection_bench.py --tag NNS`")

WHY = {
    "both": "both resources give this form",
    "wordnet": "Princeton's hand-curated list, where the instrument disagreed with it",
    "hand": "the resources disagreed and the QM ruled it — see the docstring",
}

#: `(lemma, the form, what the rule would have said, which resource wrote it)`.
PLURAL_NOUNS = (
    ('duodenum', 'duodena', 'duodenums', 'hand'),
    ('abscissa', 'abscissae', 'abscissas', 'both'),
    ('addendum', 'addenda', 'addendums', 'both'),
    ('adieu', 'adieux', 'adieus', 'wordnet'),
    ('alkali', 'alkalies', 'alkalis', 'both'),
    ('alluvium', 'alluvia', 'alluviums', 'both'),
    ('altocumulus', 'altocumuli', 'altocumuluses', 'both'),
    ('alumna', 'alumnae', 'alumnas', 'both'),
    ('alumnus', 'alumni', 'alumnuses', 'both'),
    ('ambulacrum', 'ambulacra', 'ambulacrums', 'both'),
    ('ameba', 'amebae', 'amebas', 'both'),
    ('amoeba', 'amoebae', 'amoebas', 'both'),
    ('annulus', 'annuli', 'annuluses', 'both'),
    ('anthrax', 'anthraces', 'anthraxes', 'both'),
    ('antihero', 'antiheroes', 'antiheros', 'both'),
    ('aorta', 'aortae', 'aortas', 'both'),
    ('apex', 'apices', 'apexes', 'both'),
    ('aphelion', 'aphelia', 'aphelions', 'both'),
    ('apothecium', 'apothecia', 'apotheciums', 'both'),
    ('appendix', 'appendices', 'appendixes', 'both'),
    ('aqua', 'aquae', 'aquas', 'both'),
    ('archipelago', 'archipelagoes', 'archipelagos', 'both'),
    ('axis', 'axes', 'axises', 'both'),
    ('bacillus', 'bacilli', 'bacilluses', 'both'),
    ('basidium', 'basidia', 'basidiums', 'both'),
    ('basileus', 'basileis', 'basileuses', 'wordnet'),
    ('basso', 'bassi', 'bassos', 'both'),
    ('beef', 'beeves', 'beefs', 'both'),
    ('bongo', 'bongoes', 'bongos', 'both'),
    ('bonito', 'bonitoes', 'bonitos', 'wordnet'),
    ('bookshelf', 'bookshelves', 'bookshelfs', 'both'),
    ('borax', 'boraces', 'boraxes', 'wordnet'),
    ('bravado', 'bravadoes', 'bravados', 'both'),
    ('bravo', 'bravoes', 'bravos', 'both'),
    ('bronchus', 'bronchi', 'bronchuses', 'both'),
    ('bucktooth', 'buckteeth', 'bucktooths', 'both'),
    ('caduceus', 'caducei', 'caduceuses', 'both'),
    ('calculus', 'calculi', 'calculuses', 'both'),
    ('calf', 'calves', 'calfs', 'both'),
    ('calico', 'calicoes', 'calicos', 'both'),
    ('cambium', 'cambia', 'cambiums', 'wordnet'),
    ('canaliculus', 'canaliculi', 'canaliculuses', 'both'),
    ('candelabrum', 'candelabra', 'candelabrums', 'both'),
    ('carcinoma', 'carcinomata', 'carcinomas', 'wordnet'),
    ('cargo', 'cargoes', 'cargos', 'both'),
    ('carpus', 'carpi', 'carpuses', 'both'),
    ('cerebellum', 'cerebella', 'cerebellums', 'both'),
    ('cerebrum', 'cerebra', 'cerebrums', 'both'),
    ('cervix', 'cervices', 'cervixes', 'both'),
    ('child', 'children', 'childs', 'both'),
    ('chilli', 'chillies', 'chillis', 'wordnet'),
    ('cicatrix', 'cicatrices', 'cicatrixes', 'both'),
    ('cilium', 'cilia', 'ciliums', 'both'),
    ('cirrocumulus', 'cirrocumuli', 'cirrocumuluses', 'both'),
    ('cirrus', 'cirri', 'cirruses', 'both'),
    ('cloverleaf', 'cloverleaves', 'cloverleafs', 'wordnet'),
    ('coccus', 'cocci', 'coccuses', 'both'),
    ('coccyx', 'coccyges', 'coccyxes', 'both'),
    ('cochlea', 'cochleae', 'cochleas', 'both'),
    ('codex', 'codices', 'codexes', 'both'),
    ('colloquium', 'colloquia', 'colloquiums', 'both'),
    ('colossus', 'colossi', 'colossuses', 'both'),
    ('continuum', 'continua', 'continuums', 'both'),
    ('copula', 'copulae', 'copulas', 'both'),
    ('criterion', 'criteria', 'criterions', 'both'),
    ('crux', 'cruces', 'cruxes', 'both'),
    ('cumulus', 'cumuli', 'cumuluses', 'both'),
    ('cutis', 'cutes', 'cutises', 'wordnet'),
    ('cyclops', 'cyclopes', 'cyclopses', 'both'),
    ('dado', 'dadoes', 'dados', 'both'),
    ('datum', 'data', 'datums', 'both'),
    ('desideratum', 'desiderata', 'desideratums', 'both'),
    ('desperado', 'desperadoes', 'desperados', 'both'),
    ('dictum', 'dicta', 'dictums', 'both'),
    ('dingo', 'dingoes', 'dingos', 'both'),
    ('diplococcus', 'diplococci', 'diplococcuses', 'both'),
    ('discus', 'disci', 'discuses', 'both'),
    ('dodo', 'dodoes', 'dodos', 'wordnet'),
    ('domino', 'dominoes', 'dominos', 'both'),
    ('dormouse', 'dormice', 'dormouses', 'both'),
    ('echinococcus', 'echinococci', 'echinococcuses', 'both'),
    ('echo', 'echoes', 'echos', 'both'),
    ('elf', 'elves', 'elfs', 'both'),
    ('embargo', 'embargoes', 'embargos', 'both'),
    ('encephalitis', 'encephalitides', 'encephalitises', 'both'),
    ('endocardium', 'endocardia', 'endocardiums', 'both'),
    ('endothelium', 'endothelia', 'endotheliums', 'both'),
    ('epicardium', 'epicardia', 'epicardiums', 'both'),
    ('epididymis', 'epididymides', 'epididymises', 'both'),
    ('epiglottis', 'epiglottides', 'epiglottises', 'both'),
    ('epithalamium', 'epithalamia', 'epithalamiums', 'both'),
    ('epithelium', 'epithelia', 'epitheliums', 'both'),
    ('equilibrium', 'equilibria', 'equilibriums', 'both'),
    ('erratum', 'errata', 'erratums', 'both'),
    ('esophagus', 'esophagi', 'esophaguses', 'both'),
    ('eucalyptus', 'eucalypti', 'eucalyptuses', 'both'),
    ('executrix', 'executrices', 'executrixes', 'both'),
    ('eyetooth', 'eyeteeth', 'eyetooths', 'wordnet'),
    ('fasciculus', 'fasciculi', 'fasciculuses', 'both'),
    ('fauna', 'faunae', 'faunas', 'wordnet'),
    ('fez', 'fezzes', 'fezes', 'both'),
    ('fiasco', 'fiascoes', 'fiascos', 'both'),
    ('flagellum', 'flagella', 'flagellums', 'both'),
    ('flamingo', 'flamingoes', 'flamingos', 'both'),
    ('flatfoot', 'flatfeet', 'flatfoots', 'wordnet'),
    ('flora', 'florae', 'floras', 'wordnet'),
    ('flyleaf', 'flyleaves', 'flyleafs', 'both'),
    ('foot', 'feet', 'foots', 'both'),
    ('forceps', 'forceps', 'forcepses', 'both'),
    ('forefoot', 'forefeet', 'forefoots', 'wordnet'),
    ('fresco', 'frescoes', 'frescos', 'both'),
    ('fungus', 'fungi', 'funguses', 'both'),
    ('ganglion', 'ganglia', 'ganglions', 'both'),
    ('genus', 'genera', 'genuses', 'both'),
    ('glomerulus', 'glomeruli', 'glomeruluses', 'both'),
    ('glottis', 'glottides', 'glottises', 'both'),
    ('go', 'goes', 'gos', 'wordnet'),
    ('godchild', 'godchildren', 'godchilds', 'both'),
    ('gonococcus', 'gonococci', 'gonococcuses', 'both'),
    ('goose', 'geese', 'gooses', 'both'),
    ('graffito', 'graffiti', 'graffitos', 'both'),
    ('grandchild', 'grandchildren', 'grandchilds', 'both'),
    ('granuloma', 'granulomata', 'granulomas', 'both'),
    ('half', 'halves', 'halfs', 'both'),
    ('halo', 'haloes', 'halos', 'both'),
    ('helix', 'helices', 'helixes', 'both'),
    ('hero', 'heroes', 'heros', 'both'),
    ('hobo', 'hoboes', 'hobos', 'both'),
    ('housewife', 'housewives', 'housewifes', 'both'),
    ('humerus', 'humeri', 'humeruses', 'both'),
    ('hypothalamus', 'hypothalami', 'hypothalamuses', 'both'),
    ('ibex', 'ibices', 'ibexes', 'wordnet'),
    ('ilium', 'ilia', 'iliums', 'both'),
    ('incubus', 'incubi', 'incubuses', 'both'),
    ('indigo', 'indigoes', 'indigos', 'wordnet'),
    ('intermezzo', 'intermezzi', 'intermezzos', 'both'),
    ('jackknife', 'jackknives', 'jackknifes', 'both'),
    ('knife', 'knives', 'knifes', 'both'),
    ('kohlrabi', 'kohlrabies', 'kohlrabis', 'wordnet'),
    ('krone', 'kroner', 'krones', 'both'),
    ('labium', 'labia', 'labiums', 'both'),
    ('lactobacillus', 'lactobacilli', 'lactobacilluses', 'both'),
    ('lacuna', 'lacunae', 'lacunas', 'both'),
    ('larva', 'larvae', 'larvas', 'both'),
    ('lasso', 'lassoes', 'lassos', 'both'),
    ('latex', 'latices', 'latexes', 'wordnet'),
    ('leaf', 'leaves', 'leafs', 'both'),
    ('lemma', 'lemmata', 'lemmas', 'both'),
    ('libretto', 'libretti', 'librettos', 'both'),
    ('life', 'lives', 'lifes', 'both'),
    ('limulus', 'limuli', 'limuluses', 'both'),
    ('lira', 'lire', 'liras', 'both'),
    ('loaf', 'loaves', 'loafs', 'both'),
    ('locus', 'loci', 'locuses', 'wordnet'),
    ('louse', 'lice', 'louses', 'both'),
    ('lustre', 'lustra', 'lustres', 'wordnet'),
    ('lymphangitis', 'lymphangitides', 'lymphangitises', 'both'),
    ('macaroni', 'macaronies', 'macaronis', 'wordnet'),
    ('magma', 'magmata', 'magmas', 'wordnet'),
    ('man', 'men', 'mans', 'both'),
    ('mango', 'mangoes', 'mangos', 'both'),
    ('matrix', 'matrices', 'matrixes', 'both'),
    ('matzo', 'matzoth', 'matzos', 'wordnet'),
    ('maxilla', 'maxillae', 'maxillas', 'both'),
    ('medium', 'media', 'mediums', 'both'),
    ('metacarpus', 'metacarpi', 'metacarpuses', 'both'),
    ('metatarsus', 'metatarsi', 'metatarsuses', 'both'),
    ('micrococcus', 'micrococci', 'micrococcuses', 'both'),
    ('midwife', 'midwives', 'midwifes', 'both'),
    ('minutia', 'minutiae', 'minutias', 'both'),
    ('modulus', 'moduli', 'moduluses', 'both'),
    ('momentum', 'momenta', 'momentums', 'both'),
    ('monsieur', 'messieurs', 'monsieurs', 'both'),
    ('mosquito', 'mosquitoes', 'mosquitos', 'both'),
    ('motto', 'mottoes', 'mottos', 'both'),
    ('mouse', 'mice', 'mouses', 'both'),
    ('mulatto', 'mulattoes', 'mulattos', 'both'),
    ('muskellunge', 'muskallunge', 'muskellunges', 'wordnet'),
    ('mycobacterium', 'mycobacteria', 'mycobacteriums', 'both'),
    ('myocardium', 'myocardia', 'myocardiums', 'both'),
    ('nebula', 'nebulae', 'nebulas', 'both'),
    ('nimbus', 'nimbi', 'nimbuses', 'both'),
    ('nova', 'novae', 'novas', 'both'),
    ('nucleolus', 'nucleoli', 'nucleoluses', 'both'),
    ('nucleus', 'nuclei', 'nucleuses', 'both'),
    ('oedema', 'oedemata', 'oedemas', 'wordnet'),
    ('oesophagus', 'oesophagi', 'oesophaguses', 'both'),
    ('optimum', 'optima', 'optimums', 'both'),
    ('ovum', 'ova', 'ovums', 'both'),
    ('papilla', 'papillae', 'papillas', 'both'),
    ('papyrus', 'papyri', 'papyruses', 'both'),
    ('paramecium', 'paramecia', 'parameciums', 'both'),
    ('parhelion', 'parhelia', 'parhelions', 'both'),
    ('patella', 'patellae', 'patellas', 'both'),
    ('patina', 'patinae', 'patinas', 'both'),
    ('peccadillo', 'peccadilloes', 'peccadillos', 'both'),
    ('pekinese', 'pekingese', 'pekineses', 'wordnet'),
    ('penknife', 'penknives', 'penknifes', 'both'),
    ('pericardium', 'pericardia', 'pericardiums', 'both'),
    ('perihelion', 'perihelia', 'perihelions', 'both'),
    ('perithecium', 'perithecia', 'peritheciums', 'both'),
    ('peritoneum', 'peritonea', 'peritoneums', 'both'),
    ('persona', 'personae', 'personas', 'both'),
    ('pharynx', 'pharynges', 'pharynxes', 'both'),
    ('phenomenon', 'phenomena', 'phenomenons', 'both'),
    ('phylum', 'phyla', 'phylums', 'both'),
    ('plectrum', 'plectra', 'plectrums', 'both'),
    ('ploughman', 'ploughmen', 'ploughmans', 'both'),
    ('plowman', 'ploughmen', 'plowmans', 'both'),
    ('pneumococcus', 'pneumococci', 'pneumococcuses', 'both'),
    ('pocketknife', 'pocketknives', 'pocketknifes', 'both'),
    ('polyhedron', 'polyhedra', 'polyhedrons', 'both'),
    ('polypus', 'polypi', 'polypuses', 'both'),
    ('portico', 'porticoes', 'porticos', 'both'),
    ('potato', 'potatoes', 'potatos', 'both'),
    ('proboscis', 'proboscides', 'proboscises', 'both'),
    ('prothalamium', 'prothalamia', 'prothalamiums', 'both'),
    ('protozoan', 'protozoa', 'protozoans', 'both'),
    ('pupa', 'pupae', 'pupas', 'both'),
    ('quantum', 'quanta', 'quantums', 'both'),
    ('quiz', 'quizzes', 'quizes', 'both'),
    ('radius', 'radii', 'radiuses', 'both'),
    ('rectum', 'recta', 'rectums', 'both'),
    ('regulus', 'reguli', 'reguluses', 'both'),
    ('retina', 'retinae', 'retinas', 'both'),
    ('rhombus', 'rhombi', 'rhombuses', 'both'),
    ('rhonchus', 'rhonchi', 'rhonchuses', 'both'),
    ('sahuaro', 'saguaros', 'sahuaros', 'wordnet'),
    ('salesperson', 'salespeople', 'salespersons', 'both'),
    ('salmonella', 'salmonellae', 'salmonellas', 'wordnet'),
    ('salvo', 'salvoes', 'salvos', 'both'),
    ('scapula', 'scapulae', 'scapulas', 'both'),
    ('scarf', 'scarves', 'scarfs', 'both'),
    ('scherzo', 'scherzi', 'scherzos', 'both'),
    ('self', 'selves', 'selfs', 'both'),
    ('sheaf', 'sheaves', 'sheafs', 'both'),
    ('shelf', 'shelves', 'shelfs', 'both'),
    ('solarium', 'solaria', 'solariums', 'both'),
    ('spermatozoon', 'spermatozoa', 'spermatozoons', 'both'),
    ('sputum', 'sputa', 'sputums', 'both'),
    ('staphylococcus', 'staphylococci', 'staphylococcuses', 'both'),
    ('stepchild', 'stepchildren', 'stepchilds', 'both'),
    ('stimulus', 'stimuli', 'stimuluses', 'both'),
    ('stratum', 'strata', 'stratums', 'both'),
    ('streptococcus', 'streptococci', 'streptococcuses', 'both'),
    ('stucco', 'stuccoes', 'stuccos', 'wordnet'),
    ('substratum', 'substrasta', 'substratums', 'wordnet'),
    ('supernova', 'supernovae', 'supernovas', 'both'),
    ('taxis', 'taxes', 'taxises', 'both'),
    ('terminus', 'termini', 'terminuses', 'both'),
    ('testis', 'testes', 'testises', 'both'),
    ('thalamus', 'thalami', 'thalamuses', 'both'),
    ('thief', 'thieves', 'thiefs', 'both'),
    ('thorax', 'thoraces', 'thoraxes', 'both'),
    ('thymus', 'thymi', 'thymuses', 'both'),
    ('titmouse', 'titmice', 'titmouses', 'both'),
    ('tobacco', 'tobaccoes', 'tobaccos', 'both'),
    ('tomato', 'tomatoes', 'tomatos', 'both'),
    ('tooth', 'teeth', 'tooths', 'both'),
    ('tornado', 'tornadoes', 'tornados', 'both'),
    ('torpedo', 'torpedoes', 'torpedos', 'both'),
    ('trachea', 'tracheae', 'tracheas', 'both'),
    ('trapezium', 'trapezia', 'trapeziums', 'both'),
    ('triclinium', 'triclinia', 'tricliniums', 'both'),
    ('tuba', 'tubae', 'tubas', 'both'),
    ('ulna', 'ulnae', 'ulnas', 'both'),
    ('umbilicus', 'umbilici', 'umbilicuses', 'both'),
    ('urethra', 'urethrae', 'urethras', 'both'),
    ('uvula', 'uvulae', 'uvulas', 'both'),
    ('veto', 'vetoes', 'vetos', 'both'),
    ('volcano', 'volcanoes', 'volcanos', 'both'),
    ('vortex', 'vortices', 'vortexes', 'both'),
    ('vulva', 'vulvae', 'vulvas', 'both'),
    ('werewolf', 'werewolves', 'werewolfs', 'both'),
    ('wharf', 'wharves', 'wharfs', 'both'),
    ('wife', 'wives', 'wifes', 'both'),
    ('wolf', 'wolves', 'wolfs', 'both'),
)

#: `db/0024`'s three verb tags, carried forward whole: a version is read as one set, so a roster that
#: dropped them would silently un-teach the decompiler how to say «is» and «wrote».
def _verb_rows():
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == 24), None)
    if found is None:
        raise RuntimeError("0024 is gone — it holds the verb tags this one extends")
    return found.load().INFLECTION_ROWS


INFLECTION_ROWS = [
    *({**row, "version": VERSION} for row in _verb_rows()),
    *(
        {
            "version": VERSION,
            "lemma": lemma,
            "tag": TAG_PLURAL,
            "form": form,
            "instead_of": rule_says,
            "source": SOURCE,
            "note": WHY[why],
            "position": position,
        }
        for position, (lemma, form, rule_says, why) in enumerate(PLURAL_NOUNS)
    ),
]


def _check() -> None:
    from tk2.language.inflect import (
        participle_rule, past_tense_rule, plural_rule, present_tense_rule,
    )

    rules = {"VBZ": present_tense_rule, "VBD": past_tense_rule, "VBN": participle_rule,
             TAG_PLURAL: plural_rule}
    seen = set()
    for row in INFLECTION_ROWS:
        key = (row["lemma"], row["tag"])
        if key in seen:
            raise ValueError(f"{key} appears twice — one form per lemma per tag")
        seen.add(key)
        if row["form"] == row["instead_of"]:
            raise ValueError(f"{row['lemma']}: the rule already produces {row['form']!r}")
        # **THE ROW MUST DISAGREE WITH THE RULE AS THE CODE STATES IT.** The plural rule moved twice
        # while this roster was being built — the `-o` branch turned over on a measurement — and each
        # time this check named every row the move had invalidated.
        says = rules[row["tag"]](row["lemma"])
        if says != row["instead_of"]:
            raise ValueError(
                f"{row['lemma']} ({row['tag']}): the rule now says {says!r} and this row was "
                f"written against {row['instead_of']!r} — the rule moved under the roster")

    tags = {row["tag"] for row in INFLECTION_ROWS}
    if tags != {"VBZ", "VBD", "VBN", TAG_PLURAL}:
        raise ValueError(f"a tag was lost: {sorted(tags)} — a version is read whole")


_check()


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(InflectionDoc, INFLECTION_ROWS)
