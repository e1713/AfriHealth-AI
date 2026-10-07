# Annotation Guidelines

## Roles and blinding

Annotators should be fluent in Amharic and English and familiar with clinical
terminology. Clinical entity and criticality decisions require qualified
clinical review. Annotators must freeze reference text, focus terms, and labels
before inspecting system hypotheses. Record annotator IDs as pseudonyms,
training, date, and adjudication outcome in restricted project records.

## Reference transcripts

1. Transcribe what is audible, preserving Amharic, English, code-switches,
   repetitions, negation, numbers, units, medication names, and clinically
   meaningful disfluencies.
2. Do not silently correct a speaker's grammar or replace an uncertain phrase
   with a likely diagnosis.
3. Mark unintelligible spans and uncertainty using a pre-agreed notation; do
   not invent missing words.
4. Keep a verbatim source transcript separate from any normalized scoring
   representation.
5. Obtain independent annotations and adjudicate disagreements before labeling
   a reference gold-standard. Preserve annotator count and provenance.
6. The canonical spreadsheet's `review_status=verified` supports the current
  normalized references for CS-01–CS-100. Preserve its source-row evidence.
  The older DOCX differs on 16 records and the PDF on 19; neither is canonical. Raw transcripts
  are blank in the sheet; do not reconstruct them from normalized text.

## WER tokenization and normalization

- Apply the frozen normalizer in `evaluator.py` to both reference and
  hypothesis; do not normalize one side differently.
- Case-fold text, replace punctuation with spaces while retaining Ethiopic
  characters, and split on whitespace. The current evaluator does not expand
  unit abbreviations or transliteration variants; any future changes require
  versioning and rescoring all models.
- Preserve digits, dosage, routes, frequency, negation, and word order.
- Do not translate Amharic to English, transliterate the reference, remove
  code-switch tokens, or treat clinically distinct terms as equivalent.
- Any additions to normalization or alias rules require versioning and
  rescoring all models.

WER is `(S + D + I) / N`, where `N` is the number of reference tokens.
Insertions, deletions, and substitutions are computed by minimum-edit-distance
alignment. See [EVALUATION_METRICS.md](EVALUATION_METRICS.md).

## Medical terms and clinical entities

- Annotate each target concept once per distinct mention under a documented
  counting policy. Preserve dosage/strength and route as separate attributes
  when they change meaning.
- Include exact surface form, character span, entity category, normalized
  concept, language/script, assertion (present/negated/uncertain), and
  temporality where available.
- A synonym or transliteration counts only when included in a clinician-reviewed
  alias table before scoring. No ad hoc matching after seeing model output.
- Do not equate a broad diagnosis with a symptom, or a related procedure with
  the intended procedure.
- The focus-term list is a source annotation, not automatically a validated
  entity gold set. Review category, mention boundaries, and clinical
  criticality before computing clinical metrics.

## Critical-term misses

Critical terms must be identified and adjudicated by clinical reviewers before
model scoring. A miss is a reference critical mention not correctly represented
in the hypothesis under the frozen alias, negation, and assertion rules.
Report both the number of missed mentions and the cases with at least one miss.
Do not infer criticality solely from inclusion in the general medical dictionary.

## Code-switch labeling

For human labels, assign each lexical token a language/script label from the
audio and context, including Amharic, English, borrowed/uncertain, or
non-lexical/number as defined by the annotation tool. Calculate accuracy only
on tokens with adjudicated labels. A switch boundary occurs between adjacent
lexical tokens whose language labels differ.

Manifest categories (`Mostly Amharic`, `Balanced Mix`, `Mostly English Clinical
Terms`) use a provisional 60% written-token script-share rule (Ethiopic vs
Latin) and must be confirmed by annotators. They are not audio-derived ground
truth, and Latin-token share does not prove that most tokens are clinical
terms.

## Domain, speaker, and adjudication

Assign medical domains only when supported by the case source and clinician
review. Assign speaker IDs only from a controlled, de-identified speaker
roster; IDs must not be guessed from ordering. Resolve disagreements with a
documented third-party adjudicator. Leave fields pending rather than inventing
labels.
