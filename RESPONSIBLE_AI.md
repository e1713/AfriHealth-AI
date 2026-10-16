# Responsible AI Framework: Sahara Healthcare Suite

## Production AI and language scope

Production speech and voice functionality uses the Intron API, with Intron
Sahara v2.5 as the primary ASR model and Intron STT/SST capabilities used where
required. Other AI providers are not application dependencies.

The current production language scope is Amharic-English code-switching.
Tigrinya-English and Oromo-English are future roadmap languages only; neither
is currently production-supported.

## 1. Safety & Clinical Oversight
* *Human-in-the-Loop:* All AI-generated SOAP notes and triage summaries require explicit clinician review and signature prior to EMR integration.
* *Non-Diagnostic Scope:* The system functions strictly as a administrative transcription and clinical decision-support tool, not an autonomous diagnostic agent.

## 2. Privacy & Data Governance
* *Audio handling:* The browser captures audio for streaming or explicit upload. Raw audio is not stored by the stream persistence tables; this does not imply that transcript data is not retained.
* *Transcript retention:* The live WebSocket path persists session metadata but does not currently write transcript text to `clinic_sessions` or `transcript_events`. Session metadata has no expiry or deletion policy. Do not send identifiable patient data until approved retention, access, and deletion controls are implemented and verified.
* *Limited redaction:* The clinical text-processing endpoint removes common email addresses and Ethiopian-format phone numbers before processing submitted text. This is not comprehensive de-identification and is not applied to live WebSocket transcript messages returned to the browser.
* *Consent:* Audio must be collected only after the patient or authorized participant has provided informed consent. Consent status and intended use should be recorded in dataset metadata.
* *Access control:* API keys remain server-side. The backend supports an optional trusted-proxy identity-header check; the repository does not provide clinician accounts or role-based access control. Authenticated clinical access, audit logging, and an approved retention policy are still required before EHR integration.
* *Medication safety limitation:* This repository does not implement a
  backend-enforced medication recommendation gate or verified viral/allergy
  blocker. Any medication information entered in the workflow must be treated
  as unverified draft content and reviewed by a qualified clinician; do not
  represent the current prototype as preventing unsafe medication suggestions.

## 3. Equity & Linguistic Accessibility
* *Current language scope:* Production scope is Amharic-English code-switched conversations. Tigrinya-English and Oromo-English are future roadmap languages only; neither is currently enabled or established as production-supported.
* *Evaluation limits:* The product has not established independent clinical safety, efficacy, or demographic-group fairness. Do not infer population-level performance or absence of harm from the prototype.
* *Low-resource deployment:* The browser includes offline-recovery features, but reliability across mobile devices and unstable networks has not been clinically or operationally validated; test the target devices and connectivity before deployment.

## 4. Operational limitations

Generated transcripts, extracted entities, triage labels, ICD-10 suggestions,
and prescriptions are suggestions for clinician review. They must not be
presented as a diagnosis or medication order without a qualified clinician
checking the source audio, transcript, patient context, allergies, and local
clinical guidelines. Product testing does not substitute for clinical
validation, and prototype behavior must not be generalized to a population
claim.
