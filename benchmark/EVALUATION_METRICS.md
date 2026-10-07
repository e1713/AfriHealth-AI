# Evaluation Metrics

Freeze the dataset version, normalization, alias table, target terms, and model
outputs before scoring. Report per-model coverage and paired sample count.
Unless stated otherwise, aggregate by the unweighted mean across eligible
cases and also publish numerator/denominator counts.

## Word Error Rate (WER)

After the frozen tokenization and text normalization, let `S`, `D`, and `I` be
the minimum edit-alignment substitutions, deletions, and insertions, and let
`N` be the number of reference tokens:

`WER = (S + D + I) / N`

Report as a fraction or percent consistently. WER can exceed 1.0 because
insertions are unbounded. Define empty-reference handling before scoring; do
not hide those cases in aggregate results. The repository normalizer is
described in [ANNOTATION_GUIDELINES.md](ANNOTATION_GUIDELINES.md).

## Medical-Term Recall

Let `T_i` be the reviewed, unique focus terms present in reference case `i`,
and let `M_i` be those terms correctly matched in the hypothesis using the
pre-approved alias list:

`MedicalTermRecall_i = |M_i| / |T_i|`

Macro recall is the mean over cases with at least one valid target term.
Publish total matched terms and total eligible terms as well. Terms absent
from the reference are excluded only after documented adjudication.

## Critical-Term Miss Rate

Let `C` be the set of adjudicated critical-term mentions in all eligible
references and `Missed(c)` indicate a mention absent or clinically incorrect
in the hypothesis:

`CriticalTermMissRate = sum(Missed(c)) / |C|`

Also report `cases_with_one_or_more_critical_misses / eligible_cases` and
absolute miss counts. A wrong medication strength, negated condition turned
positive, or wrong laterality may be a miss even if a related word appears.
The result is an error indicator, not a clinical risk probability.

## Clinical Entity Recall

With adjudicated entity spans/concepts, let `TP` be correctly captured
reference entities and `FN` be reference entities not correctly captured:

`EntityRecall = TP / (TP + FN)`

Match policy must specify category, normalized concept, span tolerance,
assertion/negation, temporality, and dose attributes. Report entity precision
and F1 as companions; recall alone does not penalize hallucinated entities.
This is distinct from focus-term recall when the focus list is not a complete
entity annotation.

## Code-Switch Accuracy

For `N_labeled` adjudicated lexical tokens with gold language labels, and
`CorrectLanguageLabels` labels matching the reference:

`CodeSwitchAccuracy = CorrectLanguageLabels / N_labeled`

Publish macro per-language accuracy and switch-boundary precision, recall, and
F1 where possible. Exclude ambiguous/unlabeled tokens and disclose their
count. Text-script estimates in the manifest cannot be used as gold labels.

## Latency

For each successful request, measure monotonic wall-clock time from request
submission to receipt of the complete transcript:

`Latency_seconds = completion_timestamp - submission_timestamp`

Report median, p90/p95, sample count, failures/timeouts, and whether queueing,
network, preprocessing, retries, or cold start are included. Also report
real-time factor:

`RTF = inference_wall_time / audio_duration`

Do not compare hosted and local latency without disclosing hardware, region,
network, batching, and endpoint conditions. Failed requests are not zero-latency
observations.

## Clinical Equity-Adjusted ASR Score (CEAS)

CEAS is a **proposed, project-specific summary metric** conceptually inspired
by the fairness-adjusted ASR score framework attributed to Rai et al.,
Interspeech 2025. It is not an exact reproduction, validated clinical metric,
or demographic fairness measure. The weighting below is an explicit project
choice and must be frozen before comparative scoring.

For each eligible case, define bounded recognition accuracy as:

`A_i = max(0, 1 - min(WER_i, 1))`

Let `A_overall` be the unweighted mean of `A_i` across eligible cases.
For speaker group `s`, let `A_s` be its unweighted mean; for adjudicated
code-switch category `c`, let `A_c` be its unweighted mean. The robustness
components are the lowest subgroup accuracies:

`A_speaker_robustness = min_s(A_s)`

`A_codeswitch_consistency = min_c(A_c)`

The proposed score is:

`CEAS = 100 * (0.50 * A_overall + 0.25 * A_speaker_robustness + 0.25 * A_codeswitch_consistency)`

The score ranges from 0 to 100. Report the three component values, subgroup
case counts, and each subgroup's WER alongside CEAS; the composite must not
hide a weak or missing subgroup. Do not impute missing subgroup results or
silently drop failures. Compare models on the same eligible cases and frozen
normalization. The weights may be changed only before scoring and must be
versioned with the protocol.

**Availability gate:** Do not calculate or publish a numeric CEAS until
speaker assignments and code-switch categories have been independently
adjudicated, each required group has sufficient eligible cases under a
predeclared minimum, and references have been audio-verified. The current
manifest has no case-level speaker assignments and labels its switch
categories provisional, so CEAS is currently unavailable. Even when computed,
this score measures robustness across the benchmark's annotated speakers and
linguistic categories only; it does not establish demographic fairness,
clinical safety, or population-level generalization.

## Existing implementation distinction

audio-verified. It does not currently implement adjudicated clinical
The current evaluation engine implements normalized token WER, focus-term
recall, critical-term miss counts/rates, and latency from the verified source
references and model outputs. The canonical source marks all 100 normalized
references verified, but no live paired model outputs are available, and
clinical target-term/entity criticality has not been independently
re-adjudicated. It does not currently implement adjudicated clinical
entity-span metrics, token-level code-switch accuracy, or CEAS. Do not imply
otherwise.
