# Clinical team handoff checklist

## Before recording

- [ ] Read [CLINICAL_RECORDING_PROTOCOL.md](./CLINICAL_RECORDING_PROTOCOL.md).
- [ ] Assign pseudonymous speaker IDs.
- [ ] Confirm consent and simulated/de-identified content.
- [ ] Create a private folder for audio and consent records.
- [ ] Verify each recorded script against the reference in
      [BENCHMARK_MANIFEST.csv](./benchmark/metadata/BENCHMARK_MANIFEST.csv);
      update the manifest review status only after audio review/adjudication.

## During recording

- [ ] Record one complete take per case.
- [ ] Keep the case ID and language label unchanged.
- [ ] Use the required WAV format where possible.
- [ ] Re-record unclear audio rather than editing the speech.
- [ ] Complete metadata immediately after each take.

## During clinical audit

- [ ] Run each recording through the app.
- [ ] Complete terminology review for each benchmark case.
- [ ] Complete the three safety scenarios.
- [ ] Score the SOAP output.
- [ ] Complete the Responsible AI sign-off.
- [ ] Export the audit JSON.

## Handoff to the research team

- [ ] Provide only approved de-identified audio.
- [ ] Provide the completed metadata CSV.
- [ ] Provide exported audit JSON files.
- [ ] Record model name, version, date, and settings for each run.
- [ ] Keep consent documents and identity mappings out of the public repository.
