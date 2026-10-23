"""Verificación reproducible sin conexión ni llamadas facturables a AWS.

Ejecuta desde la raíz: python -m unittest discover -s tests -v
Requiere únicamente las dependencias de requirements.txt.
"""

import importlib.util
import io
import json
import logging
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError, NoCredentialsError
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
SPEC = importlib.util.spec_from_file_location("aetheris_test_subject", APP_PATH)
APP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(APP)

EXPECTED_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
EXPECTED_PROMPT = (
    "Eres un astrofísico experto. Analiza estos datos de telemetría del telescopio. "
    "Identifica la anomalía evidente en los datos, explica brevemente por qué es "
    "anómalo y clasifícalo como posible Supernova o Basura Espacial. "
    "Sé conciso y dramático. Datos: "
)
FIRST_BLOCK = "Sector GTC-007: posible Supernova."
SECOND_BLOCK = "Pico luminoso y térmico extremo."
EXPECTED_ANALYSIS = FIRST_BLOCK + "\n" + SECOND_BLOCK
DEFAULT_RESPONSE = {
    "content": [
        {"type": "text", "text": FIRST_BLOCK},
        {"type": "text", "text": SECOND_BLOCK},
    ]
}


def make_client(payload=None, *, raw_body=None, error=None):
    """Cliente simulado: nunca construye un cliente AWS ni usa credenciales."""
    client = MagicMock()
    if error is not None:
        client.invoke_model.side_effect = error
    else:
        if raw_body is None:
            response = DEFAULT_RESPONSE if payload is None else payload
            raw_body = json.dumps(response, ensure_ascii=False).encode("utf-8")
        client.invoke_model.return_value = {"body": io.BytesIO(raw_body)}
    return client


def widget_by_label(widgets, label):
    return next(widget for widget in widgets if widget.label == label)


def click_analysis(app_test, *, local=False):
    label = (
        "Ejecutar ensayo local (sin AWS)"
        if local else "Analizar Sector con Amazon Bedrock"
    )
    widget_by_label(app_test.button, label).click().run()


def session_value(app_test, key, default=None):
    """Acceso público compatible con AppTest sin APIs internas de estado."""
    try:
        return app_test.session_state[key]
    except KeyError:
        return default


class DataTests(unittest.TestCase):
    def test_twenty_rows_five_columns_and_one_based_index(self):
        df = APP.generar_datos()
        self.assertEqual(df.shape, (20, 5))
        self.assertEqual(
            list(df.columns),
            ["Sector", "Ascensión Recta", "Declinación", "Luminosidad", "Variación térmica"],
        )
        self.assertEqual(list(df.index), list(range(1, 21)))
        self.assertFalse(df.isna().any().any())

    def test_seventh_row_is_the_extreme_anomaly(self):
        df = APP.generar_datos()
        normal = df.drop(index=df.index[6])
        self.assertEqual(df.iloc[6]["Sector"], "GTC-007")
        self.assertEqual(df["Luminosidad"].idxmax(), 7)
        self.assertEqual(df["Variación térmica"].idxmax(), 7)
        self.assertGreater(df.iloc[6]["Luminosidad"], normal["Luminosidad"].max() * 80)
        self.assertGreater(
            df.iloc[6]["Variación térmica"], normal["Variación térmica"].max() * 500
        )
        self.assertTrue(df["Ascensión Recta"].between(0, 24).all())
        self.assertTrue(df["Declinación"].between(-90, 90).all())

    def test_demo_is_reproducible(self):
        self.assertTrue(APP.generar_datos().equals(APP.generar_datos()))


class BedrockTests(unittest.TestCase):
    def setUp(self):
        self.df = APP.generar_datos()
        self.factory_patch = patch("boto3.client")
        self.factory = self.factory_patch.start()
        self.addCleanup(self.factory_patch.stop)

    def test_request_contains_exact_prompt_and_visible_data(self):
        client = make_client()
        self.factory.return_value = client
        result = APP.analizar_con_bedrock(self.df, "us-east-1")

        self.assertEqual(result, EXPECTED_ANALYSIS)
        self.assertEqual(APP.MODEL_ID, EXPECTED_MODEL_ID)
        self.assertEqual(APP.PROMPT, EXPECTED_PROMPT)
        self.assertEqual(self.factory.call_args.args, ("bedrock-runtime",))
        self.assertEqual(self.factory.call_args.kwargs["region_name"], "us-east-1")
        client.invoke_model.assert_called_once()
        request = client.invoke_model.call_args.kwargs
        self.assertEqual(request["modelId"], EXPECTED_MODEL_ID)
        self.assertEqual(request["contentType"], "application/json")
        self.assertEqual(request["accept"], "application/json")
        body = json.loads(request["body"])
        self.assertEqual(body["anthropic_version"], "bedrock-2023-05-31")
        self.assertGreater(body["max_tokens"], 0)
        self.assertEqual(len(body["messages"]), 1)
        message = body["messages"][0]
        self.assertEqual(message["role"], "user")
        self.assertEqual(
            message["content"],
            [{"type": "text", "text": EXPECTED_PROMPT + self.df.to_json(
                orient="records", force_ascii=False
            )}],
        )
        self.assertTrue(client.invoke_model.return_value["body"].closed)
        client.close.assert_called_once()

    def test_non_text_blocks_are_ignored(self):
        self.factory.return_value = make_client({
            "content": [
                {"type": "text", "text": FIRST_BLOCK},
                {"type": "other", "value": "no es texto de análisis"},
                {"type": "text", "text": SECOND_BLOCK},
            ]
        })
        self.assertEqual(APP.analizar_con_bedrock(self.df, "us-east-1"), EXPECTED_ANALYSIS)

    def test_empty_responses_are_rejected(self):
        for payload in ({}, {"content": []}, {"content": [{"type": "text", "text": "  "}]}):
            with self.subTest(payload=payload):
                client = make_client(payload)
                self.factory.return_value = client
                with self.assertRaises(ValueError):
                    APP.analizar_con_bedrock(self.df, "us-east-1")
                self.assertTrue(client.invoke_model.return_value["body"].closed)
                client.close.assert_called_once()

    def test_malformed_json_closes_resources(self):
        client = make_client(raw_body=b"this is not JSON")
        self.factory.return_value = client
        with self.assertRaises(ValueError):
            APP.analizar_con_bedrock(self.df, "us-east-1")
        self.assertTrue(client.invoke_model.return_value["body"].closed)
        client.close.assert_called_once()

    def test_invalid_response_shape_is_rejected(self):
        for payload in ([], {"content": None}, {"content": [None]}):
            with self.subTest(payload=payload):
                self.factory.return_value = make_client(payload)
                with self.assertRaises((ValueError, TypeError, AttributeError)):
                    APP.analizar_con_bedrock(self.df, "us-east-1")

    def test_aws_error_is_propagated_and_client_closed(self):
        denied = ClientError({"Error": {"Code": "AccessDeniedException"}}, "InvokeModel")
        client = make_client(error=denied)
        self.factory.return_value = client
        with self.assertRaises(ClientError):
            APP.analizar_con_bedrock(self.df, "us-east-1")
        client.close.assert_called_once()


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        old_logging_level = logging.root.manager.disable
        logging.disable(logging.WARNING)
        self.addCleanup(logging.disable, old_logging_level)
        self.env_patch = patch.dict(os.environ, {"AWS_REGION": "us-east-1"})
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        self.factory_patch = patch("boto3.client")
        self.factory = self.factory_patch.start()
        self.addCleanup(self.factory_patch.stop)
        self.factory.return_value = make_client()
        self.ui = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        self.assertFalse(self.ui.exception)
        self.factory.assert_not_called()

    def assert_no_crash(self):
        self.assertFalse(self.ui.exception, str(self.ui.exception))

    def test_initial_load_does_not_invoke_aws(self):
        self.assertGreaterEqual(len(self.ui.metric), 3)
        self.assertEqual(
            widget_by_label(self.ui.button, "Analizar Sector con Amazon Bedrock").label,
            "Analizar Sector con Amazon Bedrock",
        )
        mode = widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis")
        self.assertEqual(mode.value, "Amazon Bedrock (real)")
        self.factory.assert_not_called()

    def test_live_analysis_persists_without_reinvoking_aws(self):
        original = self.ui.session_state["telemetria"].copy()
        click_analysis(self.ui)
        self.assert_no_crash()
        self.assertEqual(self.ui.session_state["analisis"], EXPECTED_ANALYSIS)
        self.assertTrue(any(item.value == EXPECTED_ANALYSIS for item in self.ui.error))
        self.assertTrue(original.equals(self.ui.session_state["telemetria"]))
        self.assertEqual(self.factory.return_value.invoke_model.call_count, 1)
        self.ui.run()
        self.assert_no_crash()
        self.assertTrue(any(item.value == EXPECTED_ANALYSIS for item in self.ui.error))
        self.assertEqual(self.factory.return_value.invoke_model.call_count, 1)

    def test_region_change_invalidates_old_analysis(self):
        click_analysis(self.ui)
        region = widget_by_label(self.ui.sidebar.text_input, "Región AWS para Bedrock")
        region.input("eu-west-2").run()
        self.assert_no_crash()
        self.assertFalse(any(item.value == EXPECTED_ANALYSIS for item in self.ui.error))
        self.assertEqual(self.factory.return_value.invoke_model.call_count, 1)

    def test_missing_credentials_and_denied_access_are_visible_errors(self):
        errors = [
            NoCredentialsError(),
            ClientError({"Error": {"Code": "AccessDeniedException"}}, "InvokeModel"),
        ]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                self.factory.return_value = make_client(error=error)
                click_analysis(self.ui)
                self.assert_no_crash()
                self.assertTrue(self.ui.error)
                self.assertFalse(any(
                    item.value == "🚨 ALERTA DE ANOMALÍA CRÍTICA"
                    for item in self.ui.subheader
                ))
                self.assertFalse(session_value(self.ui, "analisis"))

    def test_bad_response_is_visible_error(self):
        self.factory.return_value = make_client(raw_body=b"not JSON")
        click_analysis(self.ui)
        self.assert_no_crash()
        self.assertTrue(self.ui.error)
        self.assertFalse(session_value(self.ui, "analisis"))

    def test_empty_region_does_not_attempt_aws(self):
        region = widget_by_label(self.ui.sidebar.text_input, "Región AWS para Bedrock")
        region.input("").run()
        click_analysis(self.ui)
        self.assert_no_crash()
        self.factory.assert_not_called()
        self.assertTrue(self.ui.warning or self.ui.error)

    def test_local_rehearsal_is_explicit_and_never_calls_aws(self):
        mode = widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis")
        mode.select("Ensayo local (sin AWS)").run()
        click_analysis(self.ui, local=True)
        self.assert_no_crash()
        self.factory.assert_not_called()
        result = session_value(self.ui, "analisis", "")
        self.assertIn("GTC-007", result)
        visible_text = "\n".join(
            str(item.value)
            for collection in (
                self.ui.caption, self.ui.info, self.ui.warning,
                self.ui.error, self.ui.markdown, self.ui.subheader,
            )
            for item in collection
        ).lower()
        self.assertTrue("simulad" in visible_text or "ensayo local" in visible_text)

    def test_real_report_preserves_provenance_and_visible_telemetry(self):
        click_analysis(self.ui)
        self.assert_no_crash()
        report = self.ui.session_state["informe"]
        self.assertEqual(report["origen"], "bedrock")
        self.assertEqual(report["modelo"], EXPECTED_MODEL_ID)
        self.assertEqual(report["region"], "us-east-1")
        self.assertIs(report["telemetria_simulada"], True)
        self.assertEqual(report["analisis"], EXPECTED_ANALYSIS)
        self.assertEqual(len(report["datos"]), 20)
        self.assertEqual(
            report["datos"],
            json.loads(self.ui.session_state["telemetria"].to_json(
                orient="records", force_ascii=False
            )),
        )
        # El informe que recibe download_button debe ser JSON portable, sin objetos pandas.
        exported = json.loads(json.dumps(report, ensure_ascii=False, allow_nan=False))
        self.assertEqual(exported, report)
        self.assertEqual(exported["datos"][6]["Sector"], "GTC-007")

    def test_local_report_never_attributes_analysis_to_aws(self):
        widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis").select(
            "Ensayo local (sin AWS)"
        ).run()
        click_analysis(self.ui, local=True)
        self.assert_no_crash()
        self.factory.assert_not_called()
        report = self.ui.session_state["informe"]
        self.assertEqual(report["origen"], "ensayo_local")
        self.assertIsNone(report["modelo"])
        self.assertIsNone(report["region"])
        self.assertIs(report["telemetria_simulada"], True)
        self.assertEqual(len(report["datos"]), 20)
        self.assertEqual(report["analisis"], self.ui.session_state["analisis"])
        self.assertIn("SIMULADO", report["analisis"])
        self.assertEqual(
            report["datos"],
            json.loads(self.ui.session_state["telemetria"].to_json(
                orient="records", force_ascii=False
            )),
        )
        self.assertEqual(json.loads(json.dumps(report, allow_nan=False)), report)

    def test_switching_mode_invalidates_report_before_new_analysis(self):
        click_analysis(self.ui)
        self.assertEqual(self.ui.session_state["informe"]["origen"], "bedrock")
        widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis").select(
            "Ensayo local (sin AWS)"
        ).run()
        self.assert_no_crash()
        self.assertIsNone(session_value(self.ui, "informe"))
        self.assertFalse(session_value(self.ui, "analisis"))
        click_analysis(self.ui, local=True)
        self.assertEqual(self.ui.session_state["informe"]["origen"], "ensayo_local")
        widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis").select(
            "Amazon Bedrock (real)"
        ).run()
        self.assert_no_crash()
        self.assertIsNone(session_value(self.ui, "informe"))
        self.assertFalse(session_value(self.ui, "analisis"))
        self.assertEqual(self.factory.return_value.invoke_model.call_count, 1)


class AlexaSimulationTests(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.WARNING)
        self.addCleanup(logging.disable, logging.NOTSET)
        self.factory_patch = patch("boto3.client")
        self.factory = self.factory_patch.start()
        self.addCleanup(self.factory_patch.stop)
        self.factory.return_value = make_client()
        self.ui = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        widget_by_label(self.ui.sidebar.selectbox, "Workspace").select("Alexa+ simulation").run()
        widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis").select(APP.MODO_LOCAL).run()
        self.assertFalse(self.ui.exception)

    def click(self, label):
        widget_by_label(self.ui.button, label).click().run()
        self.assertFalse(self.ui.exception, str(self.ui.exception))

    def test_local_scan_explanation_and_followup_execute_tools(self):
        self.click("Scan the observatory")
        report = self.ui.session_state["informe"]
        self.assertEqual(report["origen"], "ensayo_local")
        self.assertIn("SIMULATED RESULT", report["analisis"])
        self.click("Explain the anomaly")
        self.click("Prepare follow-up")
        ticket = self.ui.session_state["alexa_followup"]
        self.assertEqual(ticket["status"], "pending_human_review")
        self.assertIs(ticket["external_actions_executed"], False)
        self.assertEqual(ticket["evidence"]["sector"], "GTC-007")
        self.assertEqual(ticket["scan_report"], report)
        self.assertEqual([t["tool"] for t in self.ui.session_state["alexa_trace"]],
                         ["scan_observatory", "explain_anomaly", "prepare_follow_up"])
        json.dumps(ticket, allow_nan=False)
        self.factory.assert_not_called()

    def test_explain_and_followup_require_a_successful_scan(self):
        for label in ("Explain the anomaly", "Prepare follow-up"):
            self.click(label)
            self.assertIn("Scan the observatory first", self.ui.session_state["alexa_history"][-1]["content"])
            self.assertFalse(session_value(self.ui, "alexa_followup"))
            self.assertFalse(session_value(self.ui, "informe"))
        self.factory.assert_not_called()

    def test_mode_change_discards_old_ticket_and_conversation(self):
        self.click("Scan the observatory")
        self.click("Prepare follow-up")
        widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis").select(APP.MODO_REAL).run()
        self.assertFalse(self.ui.exception)
        self.assertFalse(session_value(self.ui, "alexa_followup"))
        self.assertFalse(session_value(self.ui, "informe"))
        self.assertFalse(self.ui.session_state["alexa_history"])
        self.assertFalse(self.ui.session_state["alexa_trace"])
        self.factory.assert_not_called()

    def test_bedrock_scan_is_the_only_step_that_invokes_aws(self):
        widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis").select(APP.MODO_REAL).run()
        self.click("Scan the observatory")
        self.assertEqual(self.ui.session_state["informe"]["origen"], "bedrock")
        self.click("Explain the anomaly")
        self.click("Prepare follow-up")
        self.factory.return_value.invoke_model.assert_called_once()
        self.assertEqual(self.ui.session_state["alexa_followup"]["analysis_origin"], "bedrock")

    def test_failed_scan_does_not_create_an_analysis_or_ticket(self):
        self.factory.return_value = make_client(error=NoCredentialsError())
        widget_by_label(self.ui.sidebar.selectbox, "Modo de análisis").select(APP.MODO_REAL).run()
        self.click("Scan the observatory")
        self.assertFalse(session_value(self.ui, "informe"))
        self.assertFalse(session_value(self.ui, "alexa_followup"))
        self.assertEqual(self.ui.session_state["alexa_trace"][-1]["status"], "failed")

    def test_followup_rejects_a_report_for_different_telemetry(self):
        df = APP.generar_datos()
        report = APP.crear_informe(df, "", APP.MODO_LOCAL, english=True)
        changed = df.copy()
        changed.loc[7, "Luminosidad"] = 9000
        with self.assertRaises(ValueError):
            APP.crear_seguimiento(changed, report)
        self.factory.assert_not_called()

    def test_request_router_does_not_execute_unknown_commands(self):
        self.assertEqual(APP.interpretar_solicitud("Why is this critical?"), "explain")
        self.assertEqual(APP.interpretar_solicitud("Prepare follow-up"), "followup")
        self.assertEqual(APP.interpretar_solicitud("Scan the observatory"), "scan")
        self.assertIsNone(APP.interpretar_solicitud("Delete all my files"))


if __name__ == "__main__":
    logging.getLogger("streamlit").setLevel(logging.ERROR)
    unittest.main(verbosity=2)
