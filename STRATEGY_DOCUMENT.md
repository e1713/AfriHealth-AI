# AfriHealth AI Product Strategy

## Executive summary

AfriHealth AI is a clinician-reviewed voice documentation and decision-support
workflow for community health teams working across English and Amharic-English
conversations (active v1.0 scope). Afaan Oromoo-English is Phase 2 and
Tigrinya-English is Phase 3. The product is designed to reduce
documentation burden while keeping clinical decisions with qualified people.

## Product scope

### Frontline triage

The workflow captures reviewed audio, sends it through the server-side Intron
speech bridge, and presents a transcript with a review-oriented symptom and
urgency summary.

### Voice EHR intake

Reviewed speech can be organized into draft SOAP, coding, and handoff
artifacts. Vital signs, examination findings, diagnoses, medications, and
allergies require explicit human confirmation.

### Post-care follow-up

The prototype demonstrates follow-up conversation patterns and escalation
signals. It does not autonomously contact patients, diagnose complications, or
dispatch care.

## Evidence strategy

The project keeps four evidence layers separate:

1. **Fixture benchmark:** a reproducible software test using embedded
   hypotheses. It is not independent audio inference.
2. **15-case transcript comparison:** saved outputs from Intron Sahara v2.5,
   Whisper Tiny, English-only Wav2Vec2 Base 960h, and Gemini are scored against
   verified Amharic-English references using normalized WER, alias-aware
   target-term recall, and M-WER. See `BENCHMARK_RESULTS.md`; these simulated-set
   scores are not demographic fairness or population-performance evidence.
3. **AfriSwitch pilot:** real general-purpose Amharic/Oromo code-switched audio
   used for exploratory ASR evaluation, not clinical validation.
4. **Clinical review baseline:** 15 reviewed Amharic-English recordings with
   56.38% mean WER, 44.33% target-term recall, and critical-term misses in six
   cases. This is evidence for clinician review, not autonomous care.

Clinical validation materials are maintained as private evaluation and
governance artifacts. They are not presented as a patient-facing product
module or a claim of clinical approval.

## Safety and privacy

- Intron credentials remain on the backend.
- Audio is reviewed locally before an explicit upload.
- Private validation audio, transcripts, and provider artifacts remain outside
  Git.
- Medication safety is not enforced end to end in the current prototype. The
   repository does not contain a backend-enforced viral/allergy blocker; any
   medication information must be independently reviewed by a qualified
   clinician and must not be presented as a safe prescription recommendation.
- The interface labels content as draft material requiring review.

## Team and ownership

- **Project owner:** Ermias Amare
- **Clinical team:** Hiwot Shiwangezaw and Rahel Tamiru
- **AI and ML researcher:** Melaku Bayu

These roles describe project responsibilities and do not imply regulatory
approval or autonomous-care authorization.

## Delivery priorities

1. Keep the recording, playback, and explicit upload workflow reliable.
2. Replace fixture comparisons with independently generated model outputs before
   making performance claims.
3. Expand language-specific evaluation with consented, de-identified data.
4. Deploy the static frontend separately from the Python backend, with exact
   production CORS origins and server-side secrets.
5. Require clinical review and documented sign-off before operational use.
