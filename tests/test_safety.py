import asyncio
import base64
import io
import json
import unittest
import wave
from xml.etree import ElementTree
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import parse_qs, urlsplit

import config
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient
from starlette.responses import PlainTextResponse
from starlette.requests import Request

import main


class SafetyTests(unittest.TestCase):
    def test_intron_sahara_key_is_supported_as_an_alias(self):
        with patch.dict("os.environ", {"INTRON_API_KEY": "", "INTRON_SAHARA_API_KEY": "sahara-key"}):
            self.assertEqual(config.get_intron_api_key(), "sahara-key")

    def test_intron_api_key_takes_precedence_over_alias(self):
        with patch.dict("os.environ", {"INTRON_API_KEY": "primary-key", "INTRON_SAHARA_API_KEY": "alias-key"}):
            self.assertEqual(config.get_intron_api_key(), "primary-key")

    def test_negated_maternal_symptom_does_not_escalate(self):
        result = main._classify_maternal_acuity("The patient reports no heavy bleeding.")
        self.assertEqual(result["level"], 5)
        self.assertFalse(result["is_emergency_trigger"])

    def test_positive_maternal_symptom_still_escalates(self):
        result = main._classify_maternal_acuity("The patient has heavy bleeding.")
        self.assertEqual(result["level"], 1)
        self.assertTrue(result["is_emergency_trigger"])

    def test_process_clinical_route_returns_manual_review_fallback_for_prose(self):
        result = asyncio.run(
            main.process_clinical_text(
                main.ClinicalProcessRequest(transcript="Patient reports headache and fever.")
            )
        )
        self.assertTrue(result.sign_off_required)
        self.assertTrue(result.soap.requires_manual_review)
        self.assertEqual(result.soap.icd10_codes, [])

    def test_clinical_process_rejects_transcripts_over_maximum_length(self):
        with self.assertRaises(ValueError):
            main.ClinicalProcessRequest(transcript="x" * 100_001)
        with self.assertRaises(ValueError):
            main.SOAPDraftPayload(transcript="x" * 100_001)
        with self.assertRaises(ValueError):
            main.PostCareAnalysisRequest(transcript="x" * 100_001)
        with self.assertRaises(ValueError):
            main.FHIRExportRequest(
                patient_id="synthetic",
                encounter_id="synthetic",
                chief_complaint="audit",
                medications=["x" * 1001],
            )

    def test_process_clinical_http_requires_sahara_api_key(self):
        with patch.dict("os.environ", {"SAHARA_API_KEY": "test-sahara-api-key"}):
            unauthenticated = TestClient(main.app).post(
                "/api/v1/process-clinical",
                json={"transcript": "Patient reports headache and fever."},
            )
            forged_header = TestClient(main.app).post(
                "/api/v1/process-clinical",
                headers={"x-authenticated-user": "clinician@example.org"},
                json={"transcript": "Patient reports headache and fever."},
            )
            invalid_key = TestClient(main.app).post(
                "/api/v1/process-clinical",
                headers={"Authorization": "Bearer invalid-key"},
                json={"transcript": "Patient reports headache and fever."},
            )
            fhir_export = TestClient(main.app).post(
                "/api/v1/fhir/export",
                json={"patient_id": "synthetic", "encounter_id": "synthetic", "chief_complaint": "audit"},
            )
            ehr_commit = TestClient(main.app).post(
                "/api/v1/ehr/commit",
                json={"patient_id": "synthetic", "encounter_id": "synthetic", "chief_complaint": "audit", "clinician_signed_off": True},
            )
            response = TestClient(main.app).post(
                "/api/v1/process-clinical",
                headers={"Authorization": "Bearer test-sahara-api-key"},
                json={"transcript": "Patient reports headache and fever."},
            )

        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(forged_header.status_code, 401)
        self.assertEqual(invalid_key.status_code, 401)
        self.assertEqual(fhir_export.status_code, 401)
        self.assertEqual(ehr_commit.status_code, 401)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["sign_off_required"])
        self.assertTrue(payload["soap"]["requires_manual_review"])
        self.assertEqual(payload["soap"]["icd10_codes"], [])
        self.assertEqual(payload["scrubbed_transcript"], "Patient reports headache and fever.")

    def test_sahara_api_key_uses_constant_time_comparison(self):
        with patch.dict("os.environ", {"SAHARA_API_KEY": "test-sahara-api-key"}):
            self.assertTrue(main._api_key_matches("test-sahara-api-key"))
            self.assertFalse(main._api_key_matches("incorrect-key"))
            self.assertFalse(main._api_key_matches(None))

            encoded_key = base64.urlsafe_b64encode(b"test-sahara-api-key").decode("ascii").rstrip("=")
            websocket = Mock()
            websocket.headers = {"sec-websocket-protocol": f"sahara-auth.{encoded_key}"}
            self.assertTrue(main._websocket_api_key_matches(websocket))

            websocket.headers = {"sec-websocket-protocol": "sahara-auth.invalid"}
            self.assertFalse(main._websocket_api_key_matches(websocket))
            websocket.headers = {}
            self.assertFalse(main._websocket_api_key_matches(websocket))

    def test_public_health_response_does_not_expose_configuration(self):
        self.assertEqual(asyncio.run(main.health_check()), {"status": "ok"})
        response = TestClient(main.app).get("/readyz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ready"})

    def test_intron_v1_stt_route_uses_backend_proxy(self):
        with (
            patch.dict("os.environ", {"SAHARA_API_KEY": "test-sahara-api-key"}),
            patch.object(main, "INTRON_API_KEY", "server-side-test-key"),
            patch.object(
                main,
                "_post_intron_sync_upload",
                new_callable=AsyncMock,
                return_value={"data": {"audio_transcript": "test transcript"}},
            ) as proxy,
        ):
            response = TestClient(main.app).post(
                "/api/v1/stt/intron",
                headers={"Authorization": "Bearer test-sahara-api-key"},
                files={"audio_file_blob": ("test.wav", b"audio", "audio/wav")},
                data={"audio_file_name": "test.wav", "use_language_asr_input": "am"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["audio_transcript"], "test transcript")
        proxy.assert_awaited_once()

    def test_later_positive_maternal_symptom_overrides_earlier_negation(self):
        result = main._classify_maternal_acuity(
            "Patient denies heavy bleeding, but has heavy bleeding now."
        )
        self.assertEqual(result["level"], 1)
        self.assertTrue(result["is_emergency_trigger"])

    def test_later_positive_recovery_symptom_overrides_earlier_negation(self):
        result = main._score_recovery_risk("No fever, but I have fever now.")
        self.assertIn("persistent_fever", result["indicators_detected"])
        self.assertEqual(result["risk_score"], 35)

    def test_missing_provider_key_fails_closed(self):
        original_key = main.INTRON_API_KEY
        try:
            main.INTRON_API_KEY = ""
            request = Mock()
            upload = UploadFile(file=io.BytesIO(b"audio"), filename="test.wav")
            with self.assertRaises(HTTPException) as context:
                asyncio.run(main.transcribe_audio(request, upload))
            self.assertEqual(context.exception.status_code, 503)
        finally:
            main.INTRON_API_KEY = original_key

    def test_gemini_api_key_is_sent_in_header_not_url(self):
        captured = {}

        class FakeResponse:
            status_code = 200

            def raise_for_status(self):
                return None

            def json(self):
                return {"candidates": [{"content": {"parts": [{"text": "transcript"}]}}]}

        class FakeAsyncClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return None

            async def post(self, url, *, headers=None, json=None):
                captured.update({"url": url, "headers": headers, "body": json})
                return FakeResponse()

        original_keys = (main.GEMINI_API_KEY, main.GEMINI_API_KEY_1, main.GEMINI_API_KEY_2)
        try:
            main.GEMINI_API_KEY = "test-gemini-key"
            main.GEMINI_API_KEY_1 = ""
            main.GEMINI_API_KEY_2 = ""
            with patch("main.httpx.AsyncClient", return_value=FakeAsyncClient()):
                transcript = asyncio.run(main._benchmark_gemini(b"audio", "audio/wav"))
        finally:
            main.GEMINI_API_KEY, main.GEMINI_API_KEY_1, main.GEMINI_API_KEY_2 = original_keys

        self.assertEqual(transcript, "transcript")
        self.assertNotIn("test-gemini-key", captured["url"])
        self.assertEqual(captured["headers"]["x-goog-api-key"], "test-gemini-key")

    def test_gemini_rotates_to_next_key_after_429(self):
        used_keys = []

        class FakeResponse:
            def __init__(self, status_code, transcript=""):
                self.status_code = status_code
                self.transcript = transcript

            def raise_for_status(self):
                if self.status_code >= 400:
                    request = main.httpx.Request("POST", "https://generativelanguage.googleapis.com")
                    response = main.httpx.Response(self.status_code, request=request)
                    raise main.httpx.HTTPStatusError("rate limited", request=request, response=response)

            def json(self):
                return {"candidates": [{"content": {"parts": [{"text": self.transcript}]}}]}

        class FakeAsyncClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return None

            async def post(self, url, *, headers=None, json=None):
                used_keys.append(headers["x-goog-api-key"])
                if len(used_keys) == 1:
                    return FakeResponse(429)
                return FakeResponse(200, "fallback transcript")

        original_keys = (main.GEMINI_API_KEY, main.GEMINI_API_KEY_1, main.GEMINI_API_KEY_2)
        try:
            main.GEMINI_API_KEY = "key-slot-one"
            main.GEMINI_API_KEY_1 = "key-slot-two"
            main.GEMINI_API_KEY_2 = ""
            with patch("main.httpx.AsyncClient", return_value=FakeAsyncClient()):
                transcript = asyncio.run(main._benchmark_gemini(b"audio", "audio/wav"))
        finally:
            main.GEMINI_API_KEY, main.GEMINI_API_KEY_1, main.GEMINI_API_KEY_2 = original_keys

        self.assertEqual(transcript, "fallback transcript")
        self.assertEqual(used_keys, ["key-slot-one", "key-slot-two"])

    def test_gemini_exhausted_key_pool_marks_429_non_retryable(self):
        class FakeResponse:
            status_code = 429

            def raise_for_status(self):
                request = main.httpx.Request("POST", "https://generativelanguage.googleapis.com")
                response = main.httpx.Response(429, request=request)
                raise main.httpx.HTTPStatusError("rate limited", request=request, response=response)

        class FakeAsyncClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return None

            async def post(self, url, *, headers=None, json=None):
                return FakeResponse()

        original_keys = (main.GEMINI_API_KEY, main.GEMINI_API_KEY_1, main.GEMINI_API_KEY_2)
        try:
            main.GEMINI_API_KEY = "key-slot-one"
            main.GEMINI_API_KEY_1 = "key-slot-two"
            main.GEMINI_API_KEY_2 = ""
            with patch("main.httpx.AsyncClient", return_value=FakeAsyncClient()):
                with self.assertRaises(main.GeminiKeysRateLimitedError) as context:
                    asyncio.run(main._benchmark_gemini(b"audio", "audio/wav"))
        finally:
            main.GEMINI_API_KEY, main.GEMINI_API_KEY_1, main.GEMINI_API_KEY_2 = original_keys

        self.assertEqual(context.exception.response.status_code, 429)
        self.assertTrue(context.exception.stop_retries)

    def test_upload_limit_is_enforced(self):
        upload = UploadFile(
            file=io.BytesIO(b"x" * (main.MAX_AUDIO_BYTES + 1)),
            filename="too-large.wav",
        )
        with self.assertRaises(HTTPException) as context:
            asyncio.run(main._read_limited_upload(upload))
        self.assertEqual(context.exception.status_code, 413)

    def test_wav_duration_limit_is_enforced(self):
        wav_data = io.BytesIO()
        with wave.open(wav_data, "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(1)
            audio.writeframes(b"\0\0" * 121)

        with self.assertRaises(HTTPException) as context:
            main._validate_wav_duration(wav_data.getvalue())
        self.assertEqual(context.exception.status_code, 413)

    def test_stt_stream_url_uses_documented_endpoint_and_configuration(self):
        url = main._build_intron_stt_stream_url({"use_language_asr_input": "en"})
        parsed = urlsplit(url)
        self.assertEqual(parsed.scheme, "wss")
        self.assertEqual(parsed.netloc, "infer.voice.intron.io")
        self.assertEqual(parsed.path, "/stt/v1/stream")
        self.assertEqual(
            parse_qs(parsed.query),
            {
                "sample_rate": ["16000"],
                "bit_rate": ["16"],
                "num_channels": ["1"],
                "use_language_asr_input": ["en"],
            },
        )

    def test_stt_stream_rejects_audio_config_not_supported_by_browser(self):
        with self.assertRaises(ValueError):
            main._build_intron_stt_stream_url({"sample_rate": "48000"})

    def test_stt_websocket_logs_disallowed_origin(self):
        async def exercise():
            browser = Mock()
            browser.headers = {"origin": "https://unexpected.example"}
            browser.query_params = {}
            browser.close = AsyncMock()
            with (
                patch.object(main, "ALLOWED_ORIGINS", ["https://sahara-healthcare-suite.pages.dev"]),
                patch.object(main.logger, "warning") as warning,
            ):
                await main.websocket_stream(browser)
            browser.close.assert_awaited_once_with(code=1008)
            warning.assert_called_once_with("Rejecting STT WebSocket: origin is not allowed")

        asyncio.run(exercise())

    def test_stt_websocket_rejects_missing_api_key(self):
        async def exercise():
            browser = Mock()
            browser.headers = {"origin": "https://sahara-healthcare-suite.pages.dev"}
            browser.query_params = {}
            browser.close = AsyncMock()
            with (
                patch.object(main, "ALLOWED_ORIGINS", ["https://sahara-healthcare-suite.pages.dev"]),
                patch.object(main.logger, "warning") as warning,
            ):
                await main.websocket_stream(browser)
            browser.close.assert_awaited_once_with(code=1008)
            warning.assert_called_once_with("Rejecting STT WebSocket: API key is missing or invalid")

        asyncio.run(exercise())

    def test_stt_websocket_logs_missing_intron_key(self):
        async def exercise():
            browser = Mock()
            encoded_key = base64.urlsafe_b64encode(b"test-sahara-api-key").decode("ascii").rstrip("=")
            browser.headers = {
                "origin": "https://sahara-healthcare-suite.pages.dev",
                "sec-websocket-protocol": f"sahara-auth.{encoded_key}",
            }
            browser.query_params = {}
            browser.close = AsyncMock()
            with (
                patch.object(main, "ALLOWED_ORIGINS", ["https://sahara-healthcare-suite.pages.dev"]),
                patch.dict("os.environ", {"SAHARA_API_KEY": "test-sahara-api-key"}),
                patch.object(main, "INTRON_API_KEY", ""),
                patch.object(main.logger, "error") as error,
            ):
                await main.websocket_stream(browser)
            browser.close.assert_awaited_once_with(code=1011)
            error.assert_called_once_with("Rejecting STT WebSocket: INTRON_API_KEY is not configured")

        asyncio.run(exercise())

    def test_stt_audio_chunks_meet_provider_size_limits(self):
        small_audio = bytearray(b"\x01\x00" * 300)
        self.assertIsNone(main._take_stt_audio_chunk(small_audio))
        padded_chunk = main._take_stt_audio_chunk(small_audio, final=True)
        self.assertEqual(len(padded_chunk), main.STT_STREAM_MIN_CHUNK_BYTES)
        self.assertEqual(padded_chunk[:600], b"\x01\x00" * 300)
        self.assertFalse(small_audio)

        large_audio = bytearray(main.STT_STREAM_MAX_CHUNK_BYTES + 2)
        first_chunk = main._take_stt_audio_chunk(large_audio)
        final_chunk = main._take_stt_audio_chunk(large_audio, final=True)
        self.assertEqual(len(first_chunk), main.STT_STREAM_MAX_CHUNK_BYTES)
        self.assertEqual(len(final_chunk), main.STT_STREAM_MIN_CHUNK_BYTES)

    def test_stt_websocket_translates_audio_ack_and_commit_messages(self):
        class BrowserSocket:
            def __init__(self):
                self.headers = {
                    "origin": "http://localhost:3000",
                    "sec-websocket-protocol": (
                        "sahara-auth."
                        + base64.urlsafe_b64encode(b"test-sahara-api-key").decode("ascii").rstrip("=")
                    ),
                }
                self.query_params = {"use_language_asr_input": "en"}
                self.incoming = asyncio.Queue()
                self.outgoing = []

            async def accept(self):
                pass

            async def receive(self):
                return await self.incoming.get()

            async def send_json(self, payload):
                self.outgoing.append(payload)

            async def close(self, code=1000, reason=None):
                pass

        class IntronSocket:
            def __init__(self):
                self.incoming = asyncio.Queue()
                self.sent = []

            async def __aenter__(self):
                await self.incoming.put(json.dumps({
                    "message_type": "SESSION_CREATED",
                    "session_id": "provider-session",
                }))
                return self

            async def __aexit__(self, exc_type, exc_value, traceback):
                return False

            async def send(self, raw_message):
                payload = json.loads(raw_message)
                self.sent.append(payload)
                if payload["message_type"] == "INPUT_AUDIO_CHUNK":
                    await self.incoming.put(json.dumps({
                        "message_type": "AUDIO_CHUNK_ACK",
                        "chunk_id": payload["ack_id"],
                    }))
                elif payload["message_type"] == "COMMIT":
                    await self.incoming.put(json.dumps({
                        "message_type": "COMMITTED_TRANSCRIPT",
                        "transcript_text": "test transcript",
                    }))

            def __aiter__(self):
                return self

            async def __anext__(self):
                return await self.incoming.get()

        async def exercise():
            browser = BrowserSocket()
            first_audio = b"\x01\x00" * 300
            second_audio = b"\x02\x00" * 212
            for event in (
                {"type": "websocket.receive", "text": json.dumps({"type": "audio_meta", "sequence": 1, "timestamp_ms": 1000})},
                {"type": "websocket.receive", "bytes": first_audio},
                {"type": "websocket.receive", "text": json.dumps({"type": "audio_meta", "sequence": 2, "timestamp_ms": 1100})},
                {"type": "websocket.receive", "bytes": second_audio},
                {"type": "websocket.receive", "text": json.dumps({"event": "stop"})},
            ):
                await browser.incoming.put(event)

            intron = IntronSocket()
            with (
                patch.object(main, "ALLOWED_ORIGINS", ["http://localhost:3000"]),
                patch.dict("os.environ", {"SAHARA_API_KEY": "test-sahara-api-key"}),
                patch.object(main, "INTRON_API_KEY", "test-key"),
                patch.object(main.persistence, "start_session", new_callable=AsyncMock, return_value="local-session"),
                patch.object(main.persistence, "record_transcript", new_callable=AsyncMock) as record_transcript,
                  patch.object(main.persistence, "end_session", new_callable=AsyncMock) as end_session,
                patch.object(main.websockets, "connect", return_value=intron),
            ):
                await main.websocket_stream(browser)

            audio_messages = [message for message in intron.sent if message["message_type"] == "INPUT_AUDIO_CHUNK"]
            self.assertEqual(len(audio_messages), 1)
            self.assertEqual(audio_messages[0]["ack_id"], 1)
            self.assertEqual(
                base64.b64decode(audio_messages[0]["audio_base_64"]),
                first_audio + second_audio,
            )
            self.assertEqual(intron.sent[-1], {"message_type": "COMMIT"})
            self.assertIn({"ack_sequence": 2}, browser.outgoing)
            self.assertIn(
                {"transcript": "test transcript", "session_id": "local-session"},
                browser.outgoing,
            )
            record_transcript.assert_not_awaited()
            end_session.assert_awaited_once_with("local-session")

        asyncio.run(exercise())

    def test_tts_text_limit_matches_documented_boundary(self):
        request = main.IntronTTSRequest(text="a" * 4096)
        self.assertEqual(len(request.text), 4096)
        with self.assertRaises(ValueError):
            main.IntronTTSRequest(text="a" * 4097)

    def test_tts_routes_use_documented_provider_urls(self):
        async def exercise():
            payload = main.IntronTTSRequest(text="Clinical reminder")
            for route, endpoint in (
                (main.intron_tts_generate, main.INTRON_TTS_ENDPOINT),
                (main.intron_tts_enqueue, main.INTRON_TTS_ENQUEUE_ENDPOINT),
            ):
                with patch.object(main, "_post_intron_json", new_callable=AsyncMock) as post:
                    post.return_value = {"status": "ok"}
                    result = await route(payload)
                    self.assertEqual(result, {"status": "ok"})
                    post.assert_awaited_once_with(endpoint, payload.model_dump())

        asyncio.run(exercise())

    def test_voicebot_workflow_uses_documented_provider_url(self):
        async def exercise():
            payload = {"name": "Reminder", "workflow_type": "ROBOCALL", "message": "Hello"}
            with patch.object(main, "_post_intron_json", new_callable=AsyncMock) as post:
                post.return_value = {"workflow_id": "workflow-1"}
                result = await main.create_intron_voicebot_workflow(payload)
                self.assertEqual(result, {"workflow_id": "workflow-1"})
                post.assert_awaited_once_with(main.INTRON_VOICEBOT_WORKFLOWS_ENDPOINT, payload)

        asyncio.run(exercise())

    def test_followup_session_pruning_removes_expired_sessions(self):
        original_sessions = main._followup_sessions.copy()
        try:
            main._followup_sessions.clear()
            main._followup_sessions["expired"] = {"last_access": 0}
            main._prune_followup_sessions()
            self.assertNotIn("expired", main._followup_sessions)
        finally:
            main._followup_sessions.clear()
            main._followup_sessions.update(original_sessions)

    def test_unconfigured_api_key_fails_closed_in_api_middleware(self):
        with patch.dict("os.environ", {"SAHARA_API_KEY": ""}):
            middleware = main.ClinicalIdentityMiddleware(main.app)
            request = Request({"type": "http", "method": "POST", "path": "/api/v1/post-care/analyze", "headers": []})
            response = asyncio.run(middleware.dispatch(request, lambda _: PlainTextResponse("ok")))
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.headers["www-authenticate"], "Bearer")

    def test_fhir_export_contains_patient_and_encounter_references(self):
        payload = main.FHIRExportRequest(
            patient_id="patient-1",
            encounter_id="encounter-1",
            chief_complaint="Chest pain",
            diagnosis_code="R07.9",
            diagnosis_display="Chest pain, unspecified",
        )
        bundle = asyncio.run(main.export_fhir(payload))
        resources = [entry["resource"] for entry in bundle["entry"]]
        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertEqual(bundle["type"], "transaction")
        self.assertEqual(resources[1]["subject"]["reference"], bundle["entry"][0]["fullUrl"])
        self.assertTrue(all(entry["fullUrl"].startswith("urn:uuid:") for entry in bundle["entry"]))
        self.assertEqual(len({entry["fullUrl"] for entry in bundle["entry"]}), len(bundle["entry"]))
        self.assertTrue(all(
            entry["request"] == {"method": "POST", "url": entry["resource"]["resourceType"]}
            for entry in bundle["entry"]
        ))
        self.assertEqual(resources[-1]["code"]["coding"][0]["code"], "R07.9")

    def test_fhir_export_keeps_soap_composition_preliminary(self):
        payload = main.FHIRExportRequest(
            patient_id="patient-1",
            encounter_id="encounter-1",
            chief_complaint="Chest pain",
            soap=main.SOAPDraftPayload(
                transcript="Chest pain for two days.",
                subjective="Chest pain for two days.",
                objective="BP 140/90.",
                assessment="R07.9 - Chest pain, unspecified.",
                plan="Clinician review and follow-up.",
            ),
        )
        bundle = asyncio.run(main.export_fhir(payload))
        compositions = [
            entry["resource"]
            for entry in bundle["entry"]
            if entry["resource"]["resourceType"] == "Composition"
        ]
        self.assertEqual(len(compositions), 1)
        composition = compositions[0]
        self.assertEqual(composition["status"], "preliminary")
        self.assertEqual(composition["subject"]["reference"], bundle["entry"][0]["fullUrl"])
        self.assertEqual(composition["encounter"]["reference"], bundle["entry"][1]["fullUrl"])
        self.assertTrue(composition["identifier"]["value"].startswith("urn:uuid:"))
        self.assertTrue(composition["date"].endswith("Z"))
        self.assertTrue(composition["author"])
        self.assertTrue(composition["title"])
        narrative = ElementTree.fromstring(composition["section"][0]["text"]["div"])
        self.assertEqual(narrative.tag, "{http://www.w3.org/1999/xhtml}div")
        self.assertEqual(narrative.text, "Chest pain for two days.")

    def test_verified_commit_builder_marks_composition_final(self):
        payload = main.EHRCommitRequest(
            patient_id="patient-1",
            encounter_id="encounter-1",
            chief_complaint="Chest pain",
            clinician_id="clinician@example.org",
            clinician_signed_off=True,
            soap=main.SOAPDraftPayload(assessment="Clinician reviewed."),
        )
        bundle = main._build_fhir_bundle(payload, signed_off=True)
        composition = next(
            entry["resource"]
            for entry in bundle["entry"]
            if entry["resource"]["resourceType"] == "Composition"
        )
        self.assertEqual(composition["status"], "final")
        self.assertEqual(
            composition["author"][0]["display"],
            "Clinician sign-off recorded (identity not verified)",
        )

    def test_ehr_commit_requires_explicit_signoff(self):
        request = Mock()
        request.state = Mock(auth_method="api_key")
        payload = main.EHRCommitRequest(
            patient_id="patient-1",
            encounter_id="encounter-1",
            chief_complaint="Chest pain",
        )
        with self.assertRaises(HTTPException) as context:
            asyncio.run(main.commit_to_ehr(payload, request))
        self.assertEqual(context.exception.status_code, 400)

    def test_ehr_commit_requires_api_key_authentication(self):
        request = Mock()
        request.state = Mock(auth_method="legacy_token")
        payload = main.EHRCommitRequest(
            patient_id="patient-1",
            encounter_id="encounter-1",
            chief_complaint="Chest pain",
            clinician_signed_off=True,
        )
        with self.assertRaises(HTTPException) as context:
            asyncio.run(main.commit_to_ehr(payload, request))
        self.assertEqual(context.exception.status_code, 401)

    def test_live_benchmark_reports_unconfigured_providers(self):
        upload = UploadFile(file=io.BytesIO(b"audio"), filename="sample.wav")
        with patch.object(main, "INTRON_API_KEY", ""):
            result = asyncio.run(
                main.live_benchmark(
                    upload,
                    "Patient has fever and cough.",
                    "am-ET",
                    "intron",
                    "verified",
                )
            )
        self.assertEqual(result["benchmark_type"], "live_provider_comparison")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["model"], "Intron Sahara v2.5")
        self.assertEqual(result["results"][0]["status"], "unavailable")

    def test_live_benchmark_allows_transcript_only_mode(self):
        upload = UploadFile(file=io.BytesIO(b"audio"), filename="sample.wav")
        with patch.object(main, "INTRON_API_KEY", ""):
            result = asyncio.run(main.live_benchmark(upload, "", "am-ET", "intron", "verified"))
        self.assertEqual(result["scoring_status"], "transcript_only")

    def test_ehr_commit_fails_closed_without_endpoint(self):
        request = Mock()
        request.state = Mock(auth_method="api_key")
        payload = main.EHRCommitRequest(
            patient_id="patient-1",
            encounter_id="encounter-1",
            chief_complaint="Chest pain",
            clinician_signed_off=True,
        )
        original_endpoint = main.EHR_FHIR_ENDPOINT
        try:
            main.EHR_FHIR_ENDPOINT = ""
            with self.assertRaises(HTTPException) as context:
                asyncio.run(main.commit_to_ehr(payload, request))
            self.assertEqual(context.exception.status_code, 503)
        finally:
            main.EHR_FHIR_ENDPOINT = original_endpoint


if __name__ == "__main__":
    unittest.main()
