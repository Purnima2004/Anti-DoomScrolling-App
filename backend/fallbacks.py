"""Allowlisted feel-good sites and offline 9-card packs."""

SITES = [
    {
        "name": "WindowSwap",
        "url": "https://www.window-swap.com",
        "tags": ("burnt out", "numb", "anxious"),
    },
    {
        "name": "Radio Garden",
        "url": "https://radio.garden",
        "tags": ("restless", "bored", "numb"),
    },
    {
        "name": "Slow Roads",
        "url": "https://slowroads.io",
        "tags": ("restless", "anxious", "foggy"),
    },
    {
        "name": "Do Nothing for 2 Minutes",
        "url": "https://www.donothingfor2minutes.com",
        "tags": ("burnt out", "anxious", "foggy"),
    },
    {
        "name": "Pixel Thoughts",
        "url": "https://www.pixelthoughts.co",
        "tags": ("anxious", "burnt out"),
    },
    {
        "name": "NASA APOD",
        "url": "https://apod.nasa.gov",
        "tags": ("bored", "foggy", "numb"),
    },
    {
        "name": "Stellarium",
        "url": "https://stellarium-web.org",
        "tags": ("numb", "anxious", "bored"),
    },
    {
        "name": "Google Arts and Culture",
        "url": "https://artsandculture.google.com",
        "tags": ("bored", "burnt out", "foggy"),
    },
    {
        "name": "The Quiet Place",
        "url": "https://www.thequietplaceproject.com",
        "tags": ("anxious", "burnt out", "numb"),
    },
    {
        "name": "Silk",
        "url": "https://weavesilk.com",
        "tags": ("restless", "anxious", "foggy"),
    },
    {
        "name": "Neal.fun",
        "url": "https://neal.fun",
        "tags": ("bored", "restless"),
    },
    {
        "name": "Poetry Foundation",
        "url": "https://www.poetryfoundation.org",
        "tags": ("numb", "burnt out", "foggy"),
    },
    {
        "name": "Project Gutenberg",
        "url": "https://www.gutenberg.org",
        "tags": ("bored", "foggy"),
    },
    {
        "name": "Good News Network",
        "url": "https://www.goodnewsnetwork.org",
        "tags": ("numb", "anxious", "burnt out"),
    },
    {
        "name": "Duolingo",
        "url": "https://www.duolingo.com",
        "tags": ("foggy", "bored", "restless"),
    },
    {
        "name": "Khan Academy",
        "url": "https://www.khanacademy.org",
        "tags": ("foggy", "bored"),
    },
    {
        "name": "Lichess learn",
        "url": "https://lichess.org/learn",
        "tags": ("foggy", "restless"),
    },
    {
        "name": "Insight Timer",
        "url": "https://insighttimer.com",
        "tags": ("anxious", "burnt out"),
    },
    {
        "name": "FutureMe",
        "url": "https://www.futureme.org",
        "tags": ("numb", "burnt out", "foggy"),
    },
    {
        "name": "Atlas Obscura",
        "url": "https://www.atlasobscura.com",
        "tags": ("bored", "restless"),
    },
]

SITES_BY_URL = {s["url"].rstrip("/").lower(): s for s in SITES}
SITES_BY_NAME = {s["name"].lower(): s for s in SITES}

_MOOD_ALIASES = (
    (("burnt out", "burned out", "exhausted", "drained", "tired"), "burnt out"),
    (("restless", "antsy", "wired", "fidgety"), "restless"),
    (("bored", "meh", "blah", "uninspired"), "bored"),
    (("foggy", "unfocused", "scattered", "brain fog"), "foggy"),
    (("anxious", "worried", "on edge", "stressed"), "anxious"),
    (("numb", "empty", "flat", "nothing"), "numb"),
)


def mood_key(mood: str) -> str:
    text = (mood or "").lower().strip()
    for needles, key in _MOOD_ALIASES:
        if any(n in text for n in needles):
            return key
    return "bored"


def sites_for_prompt() -> str:
    return "\n".join(f"- {s['name']}: {s['url']}" for s in SITES)


def _site(name: str) -> dict:
    return SITES_BY_NAME[name.lower()]


# Nine distinct cards per known mood. Image prompts stay text-free.
FALLBACK_PACKS = {
    "burnt out": [
        {
            "title": "A window that isn't yours",
            "micro_action": "Stand up, face a real window for 90 seconds, then open a stranger's view.",
            "why": "A distant, quiet scene pulls your brain out of the loop it was chewing on.",
            "image_prompt": "warm painterly illustration of a sunlit apartment window overlooking terracotta rooftops, houseplant on the sill, no text",
            "site_name": "WindowSwap",
            "site_why": "Borrow someone else's afternoon light for two minutes.",
        },
        {
            "title": "Do literally nothing",
            "micro_action": "Sit still until the two-minute timer ends. No phone in your hands.",
            "why": "Stopping on purpose is a different signal than collapsing into a feed.",
            "image_prompt": "soft illustration of an empty wooden chair in late-afternoon light, dust motes, quiet room, no text",
            "site_name": "Do Nothing for 2 Minutes",
            "site_why": "A tiny page that only asks you to stay.",
        },
        {
            "title": "One painting, then leave",
            "micro_action": "Open one artwork, look for two minutes, close the tab.",
            "why": "Beauty without a next-button gives your attention somewhere kind to land.",
            "image_prompt": "vibrant museum gallery with one glowing painting, warm lamps, empty bench, no text",
            "site_name": "Google Arts and Culture",
            "site_why": "Walk into a museum without leaving the chair.",
        },
        {
            "title": "Let the worry drift",
            "micro_action": "Type one tired thought, watch it float, then stand up and stretch.",
            "why": "Putting a thought down is lighter than refreshing to escape it.",
            "image_prompt": "gentle illustration of a paper lantern floating over a still pond at dusk, no text",
            "site_name": "Pixel Thoughts",
            "site_why": "A two-minute ritual for setting something down.",
        },
        {
            "title": "A room with no feed",
            "micro_action": "Read one short prompt. Answer in a single sentence. Close it.",
            "why": "A finished line is a kinder landing than another tab.",
            "image_prompt": "quiet cabin desk with an open notebook and rain on the window, warm lamp, no text",
            "site_name": "The Quiet Place",
            "site_why": "A still page that asks almost nothing.",
        },
        {
            "title": "Two minutes of quiet audio",
            "micro_action": "Start one short sit. Stop when the bell would have been enough.",
            "why": "Guided stillness is a different muscle than zoning out.",
            "image_prompt": "illustration of headphones on a linen cushion in morning light, plants, no text",
            "site_name": "Insight Timer",
            "site_why": "One short sit, then you are allowed to leave.",
        },
        {
            "title": "One poem, out loud",
            "micro_action": "Read a single poem once, slowly, then put the screen down.",
            "why": "A complete piece of language fills the hole a feed never will.",
            "image_prompt": "painterly still life of an open poetry book and a peach on a wooden table, no text",
            "site_name": "Poetry Foundation",
            "site_why": "One finished poem. No next-up rail.",
        },
        {
            "title": "Write to later-you",
            "micro_action": "Send three kind sentences to a date six months out.",
            "why": "A future mailbox is a better hook than another headline.",
            "image_prompt": "illustration of a sealed cream envelope on a sunlit stoop, wildflowers, no text",
            "site_name": "FutureMe",
            "site_why": "A letter that waits. You do not have to keep checking.",
        },
        {
            "title": "One kind headline",
            "micro_action": "Read a single good-news story. Do not open a second.",
            "why": "A finished kind story is a safer spark than a doom pile.",
            "image_prompt": "bright illustration of neighbors sharing oranges on a sunny stoop, no text",
            "site_name": "Good News Network",
            "site_why": "Human news that ends when the article ends.",
        },
    ],
    "restless": [
        {
            "title": "Drive nowhere slowly",
            "micro_action": "Steer a quiet road for two minutes. No destination.",
            "why": "Motion without a goal burns the fidget without asking for more content.",
            "image_prompt": "cinematic illustration of an empty coastal highway at golden hour, long shadows, no cars, no text",
            "site_name": "Slow Roads",
            "site_why": "A calm drive that never turns into a feed.",
        },
        {
            "title": "Draw one silk line",
            "micro_action": "Make one slow shape with your finger or mouse, then stop.",
            "why": "A single sensory loop is enough; you do not need a streak.",
            "image_prompt": "abstract glowing silk threads in teal and copper on dark paper, elegant curves, no text",
            "site_name": "Silk",
            "site_why": "Pretty motion you control, then walk away from.",
        },
        {
            "title": "Tune a faraway city",
            "micro_action": "Spin the globe, land on one radio station, listen for two minutes.",
            "why": "Someone else's ordinary afternoon is more grounding than another short.",
            "image_prompt": "illustration of a glowing globe with tiny radio waves, night desk, warm lamp, no text",
            "site_name": "Radio Garden",
            "site_why": "Live radio from a street you will never scroll.",
        },
        {
            "title": "A weird little toy",
            "micro_action": "Pick one experiment, play it once, close the tab.",
            "why": "Curiosity that ends is healthier than a feed that pretends to be curiosity.",
            "image_prompt": "playful colorful illustration of curious gadgets on a sunny desk, paper planes, no text",
            "site_name": "Neal.fun",
            "site_why": "One clever toy, not an infinite pile.",
        },
        {
            "title": "A place that shouldn't exist",
            "micro_action": "Read one odd place, imagine being there, stop.",
            "why": "Wonder about the real world beats recycling the same outrage.",
            "image_prompt": "adventure illustration of a hidden canyon library carved in rock, lantern light, no text",
            "site_name": "Atlas Obscura",
            "site_why": "Strange real places, one article at a time.",
        },
        {
            "title": "Five restless words",
            "micro_action": "Finish one short language lesson, then stand and shake out your hands.",
            "why": "A tiny closed loop gives the fidget somewhere to go.",
            "image_prompt": "cheerful illustration of language flashcards fanned on a kitchen table, no text",
            "site_name": "Duolingo",
            "site_why": "Two minutes of a language, then leave.",
        },
        {
            "title": "One chess idea",
            "micro_action": "Do a single lesson step. Stop when it clicks once.",
            "why": "One rule is easier to hold than a tab full of half-swipes.",
            "image_prompt": "clean illustration of a single white chess knight on a sunlit wooden table, no text",
            "site_name": "Lichess learn",
            "site_why": "One clear move. No timeline underneath it.",
        },
        {
            "title": "Spin the real sky",
            "micro_action": "Find tonight's brightest star. Name it. Close the tab.",
            "why": "Looking up is motion for the mind without another notification.",
            "image_prompt": "rich night-sky illustration over a quiet hill, warm camp light, no text",
            "site_name": "Stellarium",
            "site_why": "The actual sky, not a highlight reel.",
        },
        {
            "title": "Borrow a window",
            "micro_action": "Watch one live view until something moves, then walk to your own window.",
            "why": "A real scene gives restless eyes a place to land.",
            "image_prompt": "sunlit foreign apartment window with laundry on a line, painterly, no text",
            "site_name": "WindowSwap",
            "site_why": "Someone else's weather, then yours.",
        },
    ],
    "bored": [
        {
            "title": "A weird little toy",
            "micro_action": "Pick one experiment on the page, play it once, close it.",
            "why": "Curiosity that ends is healthier than a feed that pretends to be curiosity.",
            "image_prompt": "playful colorful illustration of curious gadgets on a sunny desk, paper planes, no text",
            "site_name": "Neal.fun",
            "site_why": "One clever toy, not an infinite pile.",
        },
        {
            "title": "Today's sky",
            "micro_action": "Read the photo caption, look at the image, that's the whole visit.",
            "why": "A single astonishing picture is a full meal for a bored brain.",
            "image_prompt": "vivid illustration of a telescope on a rooftop under a nebula-colored night sky, no text",
            "site_name": "NASA APOD",
            "site_why": "One new universe picture a day. Then you're done.",
        },
        {
            "title": "A place that shouldn't exist",
            "micro_action": "Read one odd place, imagine being there, stop.",
            "why": "Wonder about the real world beats recycling the same outrage.",
            "image_prompt": "adventure illustration of a hidden canyon library carved in rock, lantern light, no text",
            "site_name": "Atlas Obscura",
            "site_why": "Strange real places, one article at a time.",
        },
        {
            "title": "One painting, then leave",
            "micro_action": "Open one artwork, look for two minutes, close the tab.",
            "why": "Beauty without a next-button gives boredom somewhere rich to sit.",
            "image_prompt": "vibrant museum gallery with one glowing painting, warm lamps, empty bench, no text",
            "site_name": "Google Arts and Culture",
            "site_why": "A museum visit that can actually end.",
        },
        {
            "title": "Two pages of a free book",
            "micro_action": "Open a public-domain book, read two pages, bookmark nothing.",
            "why": "A paragraph with an ending beats a feed with none.",
            "image_prompt": "illustration of a worn clothbound book and reading glasses on a sunny sill, no text",
            "site_name": "Project Gutenberg",
            "site_why": "A real chapter. You can stop mid-page on purpose.",
        },
        {
            "title": "One tiny lesson",
            "micro_action": "Watch or do the first two minutes of any topic that is not your job.",
            "why": "Learning one small thing is a cleaner hit than another meme.",
            "image_prompt": "friendly illustration of a chalkboard with a single simple diagram, plants, no text",
            "site_name": "Khan Academy",
            "site_why": "One concept. Then you are done for now.",
        },
        {
            "title": "Radio from nowhere",
            "micro_action": "Land on one station. Listen until one song ends.",
            "why": "A song that finishes is a better unit than a clip that doesn't.",
            "image_prompt": "illustration of a vintage radio on a balcony overlooking a night city, no text",
            "site_name": "Radio Garden",
            "site_why": "Live radio, one city, then off.",
        },
        {
            "title": "Name a constellation",
            "micro_action": "Find one shape in the sky map. That's the visit.",
            "why": "A named pattern is a complete thought.",
            "image_prompt": "illustration of a star map spread on a wooden table with a brass compass, no text",
            "site_name": "Stellarium",
            "site_why": "Tonight's sky, not tonight's timeline.",
        },
        {
            "title": "A poem you did not expect",
            "micro_action": "Open a random poem, read it once, leave.",
            "why": "Surprise without a comment section is still surprise.",
            "image_prompt": "illustration of typewritten pages pinned to a cork wall in warm light, no text",
            "site_name": "Poetry Foundation",
            "site_why": "One poem. No infinite related.",
        },
    ],
    "foggy": [
        {
            "title": "One chess idea",
            "micro_action": "Do a single lesson step. Stop when it clicks once.",
            "why": "A tiny rule is easier to hold than a tab full of half-thoughts.",
            "image_prompt": "clean illustration of a single white chess knight on a sunlit wooden table, no text",
            "site_name": "Lichess learn",
            "site_why": "One clear move. No timeline underneath it.",
        },
        {
            "title": "Five new words",
            "micro_action": "Finish one short lesson, then put the phone face down.",
            "why": "A small closed loop gives fog a start and a finish.",
            "image_prompt": "cheerful illustration of colorful language flashcards on a kitchen table, tea cup, no text",
            "site_name": "Duolingo",
            "site_why": "Two minutes of a language, then you are allowed to leave.",
        },
        {
            "title": "Cruise an empty road",
            "micro_action": "Hold a gentle line on the road until your shoulders drop.",
            "why": "Simple tracking wakes attention without asking it to decide.",
            "image_prompt": "soft foggy pine forest road at dawn, headlights, calm, no text",
            "site_name": "Slow Roads",
            "site_why": "Something to follow when thinking feels thick.",
        },
        {
            "title": "One tiny lesson",
            "micro_action": "Do the first exercise of a topic you already half-know.",
            "why": "Familiar + small is kinder than starting a new rabbit hole.",
            "image_prompt": "illustration of a single math problem on graph paper with a sharp pencil, no text",
            "site_name": "Khan Academy",
            "site_why": "One concept, then stop.",
        },
        {
            "title": "Two clear pages",
            "micro_action": "Read two pages of a simple public-domain story. Stop mid-chapter if you want.",
            "why": "Linear words are a lantern in fog.",
            "image_prompt": "illustration of a lamp-lit page with large readable type, cozy chair, no text",
            "site_name": "Project Gutenberg",
            "site_why": "A page that only goes forward.",
        },
        {
            "title": "Look at one artwork",
            "micro_action": "Zoom into one painting. Name three colors. Leave.",
            "why": "Naming what you see is a small way to come back online.",
            "image_prompt": "close illustration of a person looking at one large colorful canvas, no text",
            "site_name": "Google Arts and Culture",
            "site_why": "One image to hold, not a grid to graze.",
        },
        {
            "title": "Today's one photo",
            "micro_action": "Look at the astronomy picture. Read the first paragraph only.",
            "why": "One caption is a complete unit when your head is soup.",
            "image_prompt": "illustration of a single polaroid of a nebula pinned to a corkboard, no text",
            "site_name": "NASA APOD",
            "site_why": "One sky picture. That's the assignment.",
        },
        {
            "title": "One slow silk shape",
            "micro_action": "Draw one line. Watch it glow. Stop.",
            "why": "A single gesture is enough when decisions feel heavy.",
            "image_prompt": "soft abstract silk swirl in fog-blue and gold, dark paper, no text",
            "site_name": "Silk",
            "site_why": "Motion without a menu.",
        },
        {
            "title": "Sit until the timer ends",
            "micro_action": "Do nothing for two minutes. Fog can stay. You do not have to fix it.",
            "why": "Forcing clarity often makes the fog thicker.",
            "image_prompt": "minimal illustration of a mug and an empty chair in pale morning fog, no text",
            "site_name": "Do Nothing for 2 Minutes",
            "site_why": "Permission to not figure it out yet.",
        },
    ],
    "anxious": [
        {
            "title": "Let a thought float",
            "micro_action": "Type the worry, watch it drift, breathe until the page is quiet.",
            "why": "Seeing a thought leave is different from arguing with it in a comments thread.",
            "image_prompt": "gentle illustration of a paper boat floating away on a still lake at dusk, no text",
            "site_name": "Pixel Thoughts",
            "site_why": "A two-minute ritual for putting a thought down.",
        },
        {
            "title": "Two quiet minutes",
            "micro_action": "Stay with the waves. If you reach for another tab, come back.",
            "why": "Anxiety wants more input; this page refuses to give it.",
            "image_prompt": "minimal illustration of ocean waves and a bare wooden deck, overcast calm, no text",
            "site_name": "Do Nothing for 2 Minutes",
            "site_why": "Nothing to optimize. That's the point.",
        },
        {
            "title": "A room that writes back",
            "micro_action": "Read one short prompt and answer in one sentence.",
            "why": "A single honest line is a better landing than refreshing for relief.",
            "image_prompt": "quiet illustration of a small cabin desk, open notebook, rain on the window, no text",
            "site_name": "The Quiet Place",
            "site_why": "A still page that asks almost nothing of you.",
        },
        {
            "title": "A short sit",
            "micro_action": "Play one brief guided minute. Hands off the other apps.",
            "why": "A voice that stays in one place is safer than a feed that jumps.",
            "image_prompt": "illustration of a cushion by a window with soft curtains, morning, no text",
            "site_name": "Insight Timer",
            "site_why": "One sit. You do not need a streak.",
        },
        {
            "title": "A road with no traffic",
            "micro_action": "Drive slowly until your jaw unclenches. Then stop the tab.",
            "why": "Predictable motion gives anxiety something boring to hold.",
            "image_prompt": "illustration of an empty misty country road, golden grass, no cars, no text",
            "site_name": "Slow Roads",
            "site_why": "Forward motion without a decision tree.",
        },
        {
            "title": "Draw the edge off",
            "micro_action": "Make one slow looping line. Breathe on the way back.",
            "why": "Your hands can finish a shape the mind cannot finish a worry.",
            "image_prompt": "calming silk loops in deep blue and warm amber, no text",
            "site_name": "Silk",
            "site_why": "A loop you control, then drop.",
        },
        {
            "title": "A bigger sky",
            "micro_action": "Open the night map. Find one planet. Close it.",
            "why": "Scale that is not a crisis can shrink a spiked thought.",
            "image_prompt": "illustration of a person sitting on a roof looking at a huge calm sky, no text",
            "site_name": "Stellarium",
            "site_why": "The sky does not need you to reply.",
        },
        {
            "title": "Someone else's quiet window",
            "micro_action": "Watch a still view until you count three ordinary details.",
            "why": "Ordinary life elsewhere is an antidote to emergency-brain.",
            "image_prompt": "soft illustration of a rainy European courtyard seen from a high window, no text",
            "site_name": "WindowSwap",
            "site_why": "Proof the world can be uneventful.",
        },
        {
            "title": "One good thing",
            "micro_action": "Read a single kind story. Stop before the next one.",
            "why": "A finished gentle article is safer than scanning for threat.",
            "image_prompt": "illustration of a kettle and two cups on a sunny table, hopeful colors, no text",
            "site_name": "Good News Network",
            "site_why": "One story that is allowed to end.",
        },
    ],
    "numb": [
        {
            "title": "Someone else's weather",
            "micro_action": "Watch a real window until you notice one moving thing.",
            "why": "A live, ordinary view is a soft way back into the senses.",
            "image_prompt": "tender illustration of rain on a foreign city window, tea steam, cozy interior, no text",
            "site_name": "WindowSwap",
            "site_why": "Proof the world is still going, gently.",
        },
        {
            "title": "Look up",
            "micro_action": "Spin the sky to tonight's stars. Name one thing you can see.",
            "why": "Scale that isn't a crisis can thaw a flat mood without drama.",
            "image_prompt": "rich night-sky illustration, constellations over a quiet hill, warm camp light, no text",
            "site_name": "Stellarium",
            "site_why": "The actual sky, not a highlight reel.",
        },
        {
            "title": "One good thing that happened",
            "micro_action": "Read a single good-news story. Do not open a second.",
            "why": "A finished kind story is a safer spark than a doom pile.",
            "image_prompt": "bright illustration of people sharing oranges on a sunny stoop, hopeful colors, no text",
            "site_name": "Good News Network",
            "site_why": "Human news that ends when the article ends.",
        },
        {
            "title": "A voice from another street",
            "micro_action": "Land on one radio station. Listen until you catch a laugh or a song.",
            "why": "Other people's ordinary noise can thaw a mute day.",
            "image_prompt": "illustration of a small radio on a kitchen counter with morning light, no text",
            "site_name": "Radio Garden",
            "site_why": "Live human sound, not a highlight clip.",
        },
        {
            "title": "One poem in the body",
            "micro_action": "Read a short poem out loud, even if it feels silly.",
            "why": "Your voice is a sense. Numbness often forgets that.",
            "image_prompt": "illustration of a person reading at a sunlit kitchen table, steam from a mug, no text",
            "site_name": "Poetry Foundation",
            "site_why": "Words meant to be finished, not refreshed.",
        },
        {
            "title": "A note to a future morning",
            "micro_action": "Write three true sentences to yourself in six months.",
            "why": "A sealed note is a tiny future that does not need a feed.",
            "image_prompt": "illustration of a handwritten letter and a dried flower on linen, no text",
            "site_name": "FutureMe",
            "site_why": "You can put the feeling somewhere and walk away.",
        },
        {
            "title": "A quiet prompt",
            "micro_action": "Answer one question in one line. That is the whole visit.",
            "why": "A small honest sentence is a pulse.",
            "image_prompt": "illustration of a blank notebook and a single pencil in a dim cozy room, no text",
            "site_name": "The Quiet Place",
            "site_why": "Almost nothing is asked of you.",
        },
        {
            "title": "Today's one sky",
            "micro_action": "Look at the photo until you notice a color you like.",
            "why": "One beautiful fact can enter a flat day without demanding joy.",
            "image_prompt": "illustration of a huge space photograph taped above a tidy desk, no text",
            "site_name": "NASA APOD",
            "site_why": "One picture. No comments required.",
        },
        {
            "title": "Stand in front of one artwork",
            "micro_action": "Pick one piece. Stay for two minutes. Leave the museum.",
            "why": "Color and shape can reach you before words do.",
            "image_prompt": "illustration of a lone bench in front of a vivid abstract painting, no text",
            "site_name": "Google Arts and Culture",
            "site_why": "A gallery visit that can actually end.",
        },
    ],
}


def fallback_cards(mood: str) -> list[dict]:
    key = mood_key(mood)
    pack = FALLBACK_PACKS[key]
    cards = []
    for raw in pack:
        site = _site(raw["site_name"])
        cards.append({**raw, "site_url": site["url"]})
    return cards


def resolve_site(site_url: str, site_name: str, used_urls: set[str], mood: str) -> dict:
    """Map a model guess onto the allowlist. Never invent a domain."""
    url_key = (site_url or "").rstrip("/").lower()
    name_key = (site_name or "").strip().lower()
    hit = SITES_BY_URL.get(url_key) or SITES_BY_NAME.get(name_key)
    if hit and hit["url"] not in used_urls:
        return hit

    key = mood_key(mood)
    tagged = [s for s in SITES if key in s["tags"] and s["url"] not in used_urls]
    pool = tagged or [s for s in SITES if s["url"] not in used_urls] or SITES
    return pool[0]
