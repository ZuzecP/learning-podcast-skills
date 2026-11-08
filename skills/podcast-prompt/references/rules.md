# Audio Overview instructions

Instruction box limit: 5000 characters (textarea maxlength, measured 2026-10-06)

## Assembly

`scripts/assemble.py` builds the block from this file: one line per section, label in capitals and a colon, in the order below, only where the table includes it. No greetings and no explanations of why. To change wording, edit the texts under "Section texts"; never edit a generated block by hand.

| Order | Label | Deep Dive, Critique, Debate | Brief |
|---|---|---|---|
| 1 | NAMES | optional locale rule: only when the config sets `names_rule` to true and a person named in the sources has a Czech name with special characters of the Czech alphabet | same |
| 2 | TONE | always | always |
| 3 | FACTS | always | always |
| 4 | BRIEF | never | always |
| 5 | DEPTH | always | never |
| 6 | LEVELS | always | never |
| 7 | ACTIONS | always | never |
| 8 | GAPS | always, full text | always, Brief text |
| 9 | STUDY FURTHER | first-time topics only | never |

Cut order when the block is longer than the limit, one section at a time, skipping sections the block doesn't have: STUDY FURTHER, ACTIONS, LEVELS, DEPTH, GAPS. Never cut NAMES, TONE or FACTS.

## Why each rule exists

These are the author's defaults. Copy this file to `rules.local.md` in your project folder and edit the copy to make them yours; the copy replaces this file as a whole.

- NAMES: hosts mispronounce names with Czech diacritics; asking for the simpler of first name or surname avoids it. Optional: off unless `names_rule` is true in the config.
- TONE: audio hosts drift toward hype and staged surprise; this keeps them calm and factual.
- FACTS: stops the hosts from inventing examples, numbers or quotes; inferences must be labelled.
- BRIEF: a Brief episode has no length setting, so pacing is steered with this line.
- DEPTH: fewer points covered thoroughly teach more than many points covered briefly.
- LEVELS: insights for three expertise levels make one episode useful to beginners and experts.
- ACTIONS: ends the episode with small steps the listener can start today.
- GAPS: names what the sources leave out, so the episode does not sound more certain than the evidence.
- STUDY FURTHER: for a first-time topic, points to where to learn more.

## Section texts

One line per text, read verbatim by `assemble.py`. `(brief)` replaces the plain text in Brief.

NAMES: The Czech names with special characters of the Czech alphabet are complicated to pronounce for a non-Czech speaker. Use either the first name or the surname, whichever does not have those special characters. If both have them, go with the simpler one.
TONE: Calm, understated and factual. No hype, exclamations or staged surprise; no invented disagreement. Where the sources genuinely differ, discuss it calmly and say which source says what.
FACTS: Say only what the sources support. Label every inference, generalisation or speculation as such ("this is an inference"). Do not invent examples, numbers or quotes.
BRIEF: Keep the pacing brisk. Cover only the key takeaways and the context needed to make decisions with them.
DEPTH: When you give a tip or an example, go deep: how it works, why it works, when it fails, and what it looks like in practice. Cover fewer points thoroughly rather than many points briefly.
LEVELS: For each level of expertise, junior (new to the topic), mid (practitioner) and senior (expert), point out the most interesting insights: one or two in a shorter episode, up to five in a long one. Say which level you are on.
ACTIONS: Close with 3 to 5 small, concrete actions the listener can start today that would improve their life or work a little. Explain each briefly.
GAPS: Name the gaps: what the sources leave out, where the evidence is thin, and what is disputed or unknown in the field.
GAPS (brief): Name the single most important gap in the sources or the topic.
STUDY FURTHER: The listener is new to this topic. End with 3 specific, high-impact places to study further (a book, course, researcher or organisation) and why each is worth the time.
