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

## Product verification

Product verification focuses on preserving the clinical application
workflows: audio capture and transcription, triage, EHR intake, FHIR export,
post-care follow-up, persistence, and deployment. Automated tests and manual
workflow checks verify software behavior; they do not establish clinical
safety, efficacy, or regulatory approval.

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
2. Expand focused regression coverage across the product APIs and frontend.
3. Verify PWA behavior and offline recovery on target browsers and devices.
4. Deploy the static frontend separately from the Python backend, with exact
   production CORS origins and server-side secrets.
5. Require clinical review and documented sign-off before operational use.
