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

The project keeps evidence types separate:

1. **Fixture benchmark:** a reproducible software test using embedded
   hypotheses. It is not independent audio inference.
2. **Clinical benchmark pipeline:** the single active source is
   `benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx` and its manifest projection,
   with 100 source rows marked verified. The canonical normalized transcript
   differs from the older DOCX on 16 cases and the PDF on 19. Speaker assignments remain pending
   separate review, categories are provisional, and mock outputs are not
   accuracy evidence. No live model metrics or CEAS are available.
3. **AfriSwitch pilot:** general-purpose Amharic/Oromo code-switched audio
   used for exploratory ASR evaluation, not clinical validation.

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
