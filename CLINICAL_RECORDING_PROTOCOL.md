# Clinical validation recording protocol

This protocol prepares audio corresponding to cases CS-01–CS-100 in the
authoritative benchmark manifest for reproducible speech-model evaluation.
Use simulated or de-identified clinical content only.

## Pilot target

The project aims to cover five pseudonymous speakers. Record the true
case-to-speaker mapping in the manifest only after it is verified; do not
fabricate speaker assignments or demographics. Expand accent and recording
condition coverage after consent and quality checks pass.

## Recording settings

- WAV, mono, 16-bit PCM, 16 kHz.
- One case per file; do not combine cases.
- Record in a quiet room without patient identifiers or other voices.
- Read the case naturally, preserving Amharic script, English terms, numbers,
  units, abbreviations, and dosage instructions.
- Do not improvise patient names, medical record numbers, or personal history.

## Consent and de-identification

Use staff volunteers or simulated cases. Before recording, obtain written
consent for speech recognition evaluation, storage, and challenge benchmarking.
Record the consent reference in the metadata; never place a person's name in an
audio filename. Stop and delete a take if identifiable information is spoken.

## File naming

```text
<case_id>_<speaker_id>_<language_pair>_<take>.wav
```

Examples:

```text
CS-01_CLINICIAN-01_AM-EN_01.wav
CS-07_CLINICIAN-02_AM-EN_01.wav
CS-15_CLINICIAN-03_AM-EN_02.wav
```

Use stable pseudonymous speaker IDs. Keep the mapping between a speaker ID and
their identity outside the repository.

## Recording checklist

For every file, confirm:

- [ ] Consent reference exists.
- [ ] Audio is simulated or de-identified.
- [ ] Case ID matches the spoken script.
- [ ] No names, phone numbers, IDs, or unrelated voices are present.
- [ ] Audio is intelligible and contains one complete take.
- [ ] Reference transcript is unchanged from the approved manifest.
- [ ] A second reviewer checked the case and language label.

## Evaluation handoff

Put recordings and metadata in a private working folder. Do not commit audio
or consent records to the public repository. Share only approved,
de-identified artifacts with the evaluation owner.
