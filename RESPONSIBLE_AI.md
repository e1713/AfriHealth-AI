# Responsible AI Framework: Sahara Healthcare Suite

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
* *Current language scope:* v1.0 targets Amharic-English code-switched conversations. Afaan Oromoo-English is Phase 2 and Tigrinya-English is Phase 3; neither is currently enabled or established as production-supported.
* *Evaluation limits:* The four-model report covers 15 simulated Amharic-English cases and uses normalized WER, alias-aware target-term recall, and M-WER. It does not report demographic-group fairness, hallucination rate, or streaming segment loss. The report must not be used to claim that disparities between demographic or language groups have been measured.
* *Low-resource deployment:* The browser includes offline-recovery features, but reliability across mobile devices and unstable networks has not been clinically or operationally validated; test the target devices and connectivity before deployment.

## 4. Operational limitations

Generated transcripts, extracted entities, triage labels, ICD-10 suggestions,
and prescriptions are suggestions for clinician review. They must not be
presented as a diagnosis or medication order without a qualified clinician
checking the source audio, transcript, patient context, allergies, and local
clinical guidelines. Benchmark scores should include the sample count, language
composition, data provenance, consent status, and known limitations; a small
fixture must not be generalized to a population claim.
