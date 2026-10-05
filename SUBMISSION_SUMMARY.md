# Sahara CodeSwitch Africa Challenge Submission

## Copy-and-paste submission

**Project:** AfriHealth AI — Sahara Healthcare Suite  
**Lead:** Ermias Amare  
**Repository:** https://github.com/sahara-healthcare-suite/sahara-healthcare-suite  
**Live prototype:** https://sahara-healthcare-suite.pages.dev/  
**Walkthrough:** https://youtu.be/47ldOyJxyPE?si=B4X5WVlztZzwGktZ
**Official documentation:** https://afri-health-ai.mintlify.site/

AfriHealth AI is a clinician-support prototype for voice-enabled clinical
documentation workflows focused on Amharic-English code-switched
conversations. It combines browser audio capture, transcription through a
backend gateway, reviewable clinical intake workflows, and FHIR-compatible
export paths with explicit review gates. It is designed to support clinicians,
not replace clinical judgment or independently diagnose, prescribe, or direct
care.

The project includes a resumable six-adapter inference pipeline, an evaluator,
visualization and reporting tools, benchmark governance documentation, and a
single 100-case master manifest covering CS-01 through CS-100. The latest mock
evaluation contains 100 outputs per adapter (600 case/model pairs total), but
these are pipeline fixtures, not model-performance measurements. The corpus
manifest currently contains source reference text and focus terms; it is not
yet a fully verified 100-recording gold-standard benchmark. Audio availability,
provenance and consent, audio-aligned reference verification, speaker
assignments, and confirmation of code-switch categories remain prerequisites
for a complete live benchmark.

We define a proposed Clinical Equity-Adjusted ASR Score (CEAS) to make
recognition accuracy, worst-speaker robustness, and consistency across
code-switch categories visible together. CEAS is a project-proposed metric,
conceptually inspired by fairness-adjusted ASR scoring work; it is not a
validated clinical score, an exact reproduction of a published method, or a
demographic fairness claim. It is not currently calculable because speaker
labels are missing and code-switch categories are provisional.

The current mock run validates pipeline data flow only. Mock transcripts and
simulated latency are not model-performance evidence; therefore, validated
WER, clinical-term recall, and CEAS results are not available at this stage.
We report these limitations explicitly rather than presenting synthetic
outputs as measured accuracy or clinical efficacy.

The application also includes a follow-up VoiceBot workflow simulation,
illustrative pilot-impact projections, and challenge-alignment documentation.
The VoiceBot demonstration does not call or contact patients, and impact
projections are not measured outcomes. The prototype is not ready for
identifiable-patient use; production authentication, role-based access,
auditability, retention/deletion controls, and deployment safeguards must be
implemented and verified first.

**Project resources**

- Official documentation: https://afri-health-ai.mintlify.site/
- Technical overview and setup: `README.md`
- Challenge requirement map: `CHALLENGE_ALIGNMENT.md`
- Benchmark protocol, dataset card, and limitations: `benchmark/`
- Current benchmark evidence status: `BENCHMARK_RESULTS.md`
- Six-slide presentation script: `benchmark/reporting/PRESENTATION_SLIDES.md`

We welcome evaluation of the working prototype and the transparency of its
benchmark design, safety boundaries, and evidence limitations.
