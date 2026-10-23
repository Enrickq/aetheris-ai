"""Aetheris AI · MVP en un solo archivo.

Instalación: pip install --upgrade streamlit pandas boto3
Ejecución:   streamlit run app.py
AWS: configura credenciales mediante el mecanismo habitual de boto3
(perfil de AWS, variables de entorno o rol IAM) y permiso bedrock:InvokeModel.
La región seleccionada debe ofrecer acceso al modelo solicitado para tu cuenta.
"""

import json
import os
import random
import hashlib
import html
import time
from datetime import datetime, timezone

import boto3
import pandas as pd
import streamlit as st
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)


MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
VERSION = "1.1.0"
MODO_REAL = "Amazon Bedrock (real)"
MODO_LOCAL = "Ensayo local (sin AWS)"
PROMPT = (
    "Eres un astrofísico experto. Analiza estos datos de telemetría del telescopio. "
    "Identifica la anomalía evidente en los datos, explica brevemente por qué es "
    "anómalo y clasifícalo como posible Supernova o Basura Espacial. "
    "Sé conciso y dramático. Datos: "
)


def generar_datos():
    """Veinte mediciones reproducibles; la séptima fila es la anomalía."""
    rng = random.Random(2026)
    filas = [
        {
            "Sector": f"GTC-{i:03d}",
            "Ascensión Recta": round(rng.uniform(0, 24), 4),
            "Declinación": round(rng.uniform(-30, 70), 4),
            "Luminosidad": round(rng.uniform(90, 110), 2),
            "Variación térmica": round(rng.uniform(-2, 2), 2),
        }
        for i in range(1, 21)
    ]
    # Fila 7 contando desde 1, equivalente a iloc[6].
    filas[6]["Luminosidad"] = 9800.0
    filas[6]["Variación térmica"] = 1250.0
    df = pd.DataFrame(filas)
    df.index = pd.RangeIndex(1, len(df) + 1, name="Fila")
    return df


def generar_ensayo_local(df):
    """Respuesta determinista para ensayos; no invoca ni imita una llamada AWS."""
    candidato = df.loc[df["Luminosidad"].idxmax()]
    base = df.drop(index=candidato.name)["Luminosidad"].median()
    factor = candidato["Luminosidad"] / base
    return (
        "[RESULTADO SIMULADO · ENSAYO LOCAL]\n\n"
        f"¡Evento extremo en {candidato['Sector']}! Su luminosidad alcanza "
        f"{candidato['Luminosidad']:,.0f} u. a., aproximadamente {factor:.0f} veces "
        f"la mediana del resto, junto a una variación térmica de "
        f"{candidato['Variación térmica']:,.0f} K.\n\n"
        "Clasificación de ensayo: posible Supernova. El aumento simultáneo de "
        "brillo y temperatura motiva la alerta; requiere observaciones de "
        "seguimiento para descartar basura espacial u otras causas.\n\n"
        "Este texto procede de una regla local, no de Amazon Bedrock."
    )


def analizar_con_bedrock(df, region):
    """Envía exactamente los datos mostrados y devuelve el texto de Claude 3."""
    datos_json = df.to_json(orient="records", force_ascii=False)
    cuerpo = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 600,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": PROMPT + datos_json}],
            }
        ],
    }
    cliente = boto3.client(
        "bedrock-runtime",
        region_name=region,
        config=Config(
            connect_timeout=10,
            read_timeout=90,
            retries={"mode": "standard", "total_max_attempts": 1},
        ),
    )
    try:
        respuesta = cliente.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"),
        )
        flujo = respuesta["body"]
        try:
            resultado = json.loads(flujo.read())
        finally:
            flujo.close()
    finally:
        cliente.close()

    if not isinstance(resultado, dict) or not isinstance(resultado.get("content"), list):
        raise ValueError("Formato inesperado en la respuesta de Bedrock.")
    texto = "\n".join(
        bloque["text"]
        for bloque in resultado["content"]
        if isinstance(bloque, dict)
        and bloque.get("type") == "text"
        and isinstance(bloque.get("text"), str)
    ).strip()
    if not texto:
        raise ValueError("Bedrock devolvió una respuesta sin texto de análisis.")
    return texto


def resumir_anomalia(df):
    """Herramienta local: calcula evidencia, sin inferencia ni llamadas externas."""
    fila = df.loc[df["Luminosidad"].idxmax()]
    base = float(df.drop(index=fila.name)["Luminosidad"].median())
    return {
        "sector": str(fila["Sector"]),
        "row": int(fila.name),
        "luminosity": float(fila["Luminosidad"]),
        "baseline_median": base,
        "luminosity_ratio": round(float(fila["Luminosidad"]) / base, 2),
        "thermal_variation_k": float(fila["Variación térmica"]),
        "synthetic_telemetry": True,
    }


def crear_informe(df, region, modo, english=False):
    """Motor compartido por el observatorio y el simulador conversacional."""
    if modo == MODO_REAL and not region:
        raise ValueError("An AWS region is required for a Bedrock scan.")
    inicio = time.perf_counter()
    if modo == MODO_REAL:
        texto = analizar_con_bedrock(df, region)
    elif english:
        evidencia = resumir_anomalia(df)
        texto = (
            "[SIMULATED RESULT · LOCAL REHEARSAL]\n\n"
            f"Extreme event in {evidencia['sector']}: luminosity "
            f"{evidencia['luminosity']:,.0f} arbitrary units, about "
            f"{evidencia['luminosity_ratio']:.0f} times the other rows' median, "
            f"with a thermal variation of {evidencia['thermal_variation_k']:,.0f} K. "
            "Rehearsal classification: possible supernova. Follow-up observations "
            "are required to investigate alternatives, including space debris.\n\n"
            "This response is generated by a local rule, not by Alexa+ or Bedrock."
        )
    else:
        texto = generar_ensayo_local(df)
    return {
        "proyecto": "Aetheris AI",
        "version": VERSION,
        "origen": "bedrock" if modo == MODO_REAL else "ensayo_local",
        "telemetria_simulada": True,
        "modelo": MODEL_ID if modo == MODO_REAL else None,
        "region": region if modo == MODO_REAL else None,
        "analisis": texto,
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "duracion_segundos": round(time.perf_counter() - inicio, 3),
        "datos": json.loads(df.to_json(orient="records", force_ascii=False)),
    }


def crear_seguimiento(df, informe):
    """Crea un borrador descargable. No reserva observaciones ni envía mensajes."""
    registros = json.loads(df.to_json(orient="records", force_ascii=False))
    if informe.get("datos") != registros:
        raise ValueError("The scan does not match the current telemetry.")
    evidencia = resumir_anomalia(df)
    digest = hashlib.sha256(json.dumps(registros, sort_keys=True).encode()).hexdigest()[:10]
    return {
        "ticket_id": f"AET-{evidencia['sector']}-{digest}",
        "status": "pending_human_review",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "workspace": "alexa_plus_web_simulation",
        "analysis_origin": informe["origen"],
        "external_actions_executed": False,
        "evidence": evidencia,
        "proposed_checks": [
            "Review instrument calibration and compare adjacent observations.",
            "Request authorized multi-band and time-series follow-up for human review.",
            "Check satellite/debris trajectories before assigning a scientific class.",
        ],
        "scan_report": informe,
    }


def interpretar_solicitud(solicitud):
    """Router determinista del ensayo; no pretende ser el agente real de Alexa+."""
    texto = solicitud.casefold().strip()
    if any(word in texto for word in ("follow", "seguimiento", "next step")):
        return "followup"
    if any(word in texto for word in ("explain", "why", "explica", "critical")):
        return "explain"
    if any(word in texto for word in ("scan", "analiza", "observatory", "escanea")):
        return "scan"
    return None


def renderizar_alexa(df, modo, region):
    """Experiencia web simulada con herramientas locales y estado verificable."""
    st.markdown('<div class="mission-tag">AETHERIS AI / CONVERSATIONAL OBSERVATORY</div>', unsafe_allow_html=True)
    st.title("Alexa+ experience simulator")
    st.warning("SIMULATION — no connection to Alexa+; synthetic telescope data.")
    st.caption(
        "Local rehearsal: no AWS calls. The assistant uses deterministic local tools."
        if modo == MODO_LOCAL else
        "Bedrock analysis enabled. Alexa+ remains simulated; only Scan can call AWS."
    )
    st.session_state.setdefault("alexa_history", [])
    st.session_state.setdefault("alexa_trace", [])
    st.caption("Ask for a scan, inspect its evidence, then prepare a follow-up for human review.")
    a, b, c = st.columns(3)
    action = None
    request = ""
    if a.button("Scan the observatory", width="stretch"):
        action, request = "scan", "Scan the observatory"
    if b.button("Explain the anomaly", width="stretch"):
        action, request = "explain", "Explain the anomaly"
    if c.button("Prepare follow-up", width="stretch"):
        action, request = "followup", "Prepare follow-up"
    with st.form("alexa_request_form", clear_on_submit=True):
        user_request = st.text_input("Ask the observatory assistant", placeholder="Why is this critical?")
        sent = st.form_submit_button("Send request")
    if sent and user_request.strip():
        request = user_request.strip()
        action = interpretar_solicitud(request) or "unsupported"

    if action:
        st.session_state.alexa_history.append({"role": "user", "content": request})
        reply = ""
        if action == "scan":
            for key in ("analisis", "informe", "alexa_followup"):
                st.session_state.pop(key, None)
            try:
                with st.spinner("Scanning the 20 observations…"):
                    informe = crear_informe(df, region, modo, english=True)
                st.session_state.informe = informe
                st.session_state.analisis = informe["analisis"]
                reply = informe["analisis"]
                st.session_state.alexa_trace.append({
                    "tool": "scan_observatory",
                    "arguments": {"rows": len(df), "analysis_mode": modo},
                    "result": {"origin": informe["origen"], "evidence": resumir_anomalia(df)},
                })
            except (BotoCoreError, ClientError, ValueError, KeyError, TypeError, AttributeError):
                reply = "Scan failed. Check AWS credentials, region and model access, or select local rehearsal. No analysis or follow-up was created."
                st.session_state.alexa_trace.append({"tool": "scan_observatory", "status": "failed"})
        elif action in ("explain", "followup") and not st.session_state.get("informe"):
            reply = "Scan the observatory first. I need a successful scan of the current telemetry before this action."
        elif action == "explain":
            evidence = resumir_anomalia(df)
            reply = (
                f"{evidence['sector']} is row {evidence['row']}. Its luminosity is "
                f"{evidence['luminosity']:,.0f}, compared with a baseline median of "
                f"{evidence['baseline_median']:.2f}: a {evidence['luminosity_ratio']:.2f}× spike. "
                f"Thermal variation is {evidence['thermal_variation_k']:,.0f} K. "
                "These are measurements from synthetic data, not evidence of a discovery. "
                "This explanation is computed locally; it does not make another model call."
            )
            st.session_state.alexa_trace.append({"tool": "explain_anomaly", "arguments": {"rows": len(df)}, "result": evidence})
        elif action == "followup":
            ticket = crear_seguimiento(df, st.session_state.informe)
            st.session_state.alexa_followup = ticket
            reply = (
                f"Follow-up draft {ticket['ticket_id']} created for {ticket['evidence']['sector']}. "
                "Status: pending_human_review. Review calibration, obtain authorized follow-up "
                "and check debris trajectories. Nothing was sent or scheduled."
            )
            st.session_state.alexa_trace.append({
                "tool": "prepare_follow_up", "arguments": {"sector": ticket["evidence"]["sector"]},
                "result": {"ticket_id": ticket["ticket_id"], "status": ticket["status"], "external_actions_executed": False},
            })
        else:
            reply = "Supported requests: Scan the observatory, Explain the anomaly, or Prepare follow-up. No action was executed."
        st.session_state.alexa_history.append({"role": "assistant", "content": reply})

    st.subheader("Conversation")
    if not st.session_state.alexa_history:
        st.info("Ready. Start with Scan the observatory.")
    for message in st.session_state.alexa_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if st.session_state.get("alexa_followup"):
        st.success("Follow-up prepared · pending_human_review · no external action")
        st.download_button("Download follow-up JSON", json.dumps(st.session_state.alexa_followup, ensure_ascii=False, indent=2), file_name="aetheris_followup.json", mime="application/json", on_click="ignore")
    if st.session_state.get("informe"):
        st.download_button("Download scan report JSON", json.dumps(st.session_state.informe, ensure_ascii=False, indent=2), file_name="aetheris_scan_report.json", mime="application/json", on_click="ignore")
    with st.expander("Tool execution trace", expanded=True):
        st.markdown('<pre class="tool-trace">' + html.escape(json.dumps(st.session_state.alexa_trace, ensure_ascii=False, indent=2)) + '</pre>', unsafe_allow_html=True)
    st.caption("A working web simulation, not an Alexa Skill, MCP server or connected Alexa device. Classification requires scientific review.")


def main():
    st.set_page_config(
        page_title="Aetheris AI | Roque de los Muchachos",
        page_icon="🔭",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # Tema visual oscuro sin config.toml ni APIs privadas de Streamlit.
    st.markdown(
        """
        <style>
        .stApp {background: radial-gradient(ellipse at top, #152440, #080e1b 65%);
                color: #edf3ff; color-scheme: dark;}
        [data-testid="stHeader"] {background: #080e1b;}
        [data-testid="stSidebar"] {background: #0c1526; color: #edf3ff;}
        [data-testid="stAppViewContainer"] h1 {color: #f4f7ff;
                font-size: clamp(1.8rem, 3vw, 3rem); letter-spacing: -.04em;}
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stSidebar"] *, [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"], [data-testid="stCaptionContainer"],
        [data-testid="stWidgetLabel"] {color: #dbe7ff;}
        [data-baseweb="input"], [data-baseweb="input"] input,
        [data-baseweb="select"] > div {background: #17243b; color: #edf3ff;}
        [data-testid="stMetric"] {background: #101c30; border: 1px solid #263956;
                border-radius: 14px; padding: 18px;}
        [data-testid="stMainBlockContainer"] {padding: 2.5rem 2.2rem 3rem;}
        .react-aria-ComboBox [role="group"],
        [data-testid="stTextInputRootElement"] {background: #17243b !important;
                border-color: #334766 !important;}
        .react-aria-ComboBox input, [data-testid="stTextInputField"] {
                background: transparent !important; color: #dbe7ff !important;
                -webkit-text-fill-color: #dbe7ff !important;}
        .react-aria-ComboBox input:disabled, [data-testid="stTextInputField"]:disabled {
                -webkit-text-fill-color: #a8b9d2 !important; opacity: 1;}
        [role="listbox"], [role="option"] {background: #17243b !important;
                color: #dbe7ff !important;}
        [role="option"][data-focused] {background: #263b5b !important;}
        .mission-tag {color: #7dd3fc; font-size: .78rem; font-weight: 700;
                letter-spacing: .2em; margin-bottom: 1rem;}
        [data-testid="stAlert"] {border-radius: 12px;}
        [data-testid="stAlert"] p, [data-testid="stAlert"] li {
                color: #f6e9ed !important;}
        [data-testid="stExpander"] details,
        [data-testid="stExpander"] summary {background: #101c30 !important;
                color: #dbe7ff !important; border-color: #263956;}
        [data-testid="stFormSubmitButton"] button {background: #17243b;
                color: #dbe7ff; border-color: #334766;}
        [data-testid="stFormSubmitButton"] button p {color: #dbe7ff !important;}
        [data-testid="stChatMessage"] {background: #101c30; color: #dbe7ff;}
        [data-testid="stChatMessage"] p {color: #dbe7ff;}
        .tool-trace {background: #101c30; color: #b9d9ee; border: 1px solid #263956;
                padding: 16px; font-size: .78rem; max-height: 320px;
                overflow: auto; white-space: pre-wrap;}
        button[kind="secondary"] {background: #17243b; color: #dbe7ff;
                border-color: #334766; border-radius: 9px;}
        button[kind="primary"] {background: #dc2626 !important;
                color: white !important; border: 1px solid #ff6262 !important;
                min-height: 4.3rem; border-radius: 12px;}
        button[kind="primary"] p {font-size: 1.15rem; font-weight: 750;}
        button[kind="primary"]:hover {background: #b91c1c !important;}
        button[kind="primary"]:focus-visible {outline: 3px solid #ffaaaa;}
        .telemetria {overflow: auto; max-height: 410px; border-radius: 12px;
                border: 1px solid #263956; background: #101c30;}
        .telemetria table {width: 100%; border-collapse: collapse;
                color: #dbe7ff; font-size: .78rem; table-layout: fixed;}
        .telemetria th, .telemetria td {padding: 9px 6px; text-align: right;
                border-bottom: 1px solid #24324a;}
        .telemetria td {white-space: nowrap;}
        .telemetria th {white-space: normal; line-height: 1.3; font-size: .68rem;
                overflow-wrap: normal; word-break: normal;}
        .telemetria th:first-child, .telemetria td:first-child {width: 2.3rem;}
        .telemetria thead th {position: sticky; top: 0; background: #172740;}
        .telemetria tbody tr:nth-child(7) {background: #4a1824;
                color: #ffd1d9; font-weight: bold;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("🛰️ Control de misión")
        st.caption("AETHERIS AI · AMAZON HACKATHON 2026")
        st.selectbox("Telescopio (simulado)", ["Gran Telescopio Canarias"], disabled=True)
        st.selectbox("Espectro (simulado)", ["Infrarrojo"], disabled=True)
        st.selectbox("Estación (simulada)", ["Roque de los Muchachos · La Palma"], disabled=True)
        st.divider()
        workspace = st.selectbox("Workspace", ["Observatory", "Alexa+ simulation"])
        modo = st.selectbox("Modo de análisis", [MODO_REAL, MODO_LOCAL])
        region = st.text_input(
            "Región AWS para Bedrock",
            value=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1",
            help="Usa una región donde tu cuenta tenga acceso a Claude 3 Sonnet.",
            disabled=modo == MODO_LOCAL,
        ).strip()
        st.caption(f"Modelo: {MODEL_ID}")
        st.caption("Credenciales: perfil, variables de entorno o rol IAM de AWS.")
        perfil = os.getenv("AWS_PROFILE")
        if perfil:
            st.caption(f"Perfil AWS activo: {perfil}")
        st.caption(f"MVP {VERSION} · 20 mediciones por lote")

    if "telemetria" not in st.session_state:
        st.session_state.telemetria = generar_datos()
    df = st.session_state.telemetria
    huella = hashlib.sha256(df.to_json(orient="records").encode("utf-8")).hexdigest()
    contexto = (modo, region if modo == MODO_REAL else None, huella, perfil)
    if st.session_state.get("contexto_analisis") != contexto:
        st.session_state.pop("analisis", None)
        st.session_state.pop("informe", None)
        for key in ("alexa_history", "alexa_trace", "alexa_followup"):
            st.session_state.pop(key, None)
        st.session_state.contexto_analisis = contexto

    if workspace == "Alexa+ simulation":
        renderizar_alexa(df, modo, region)
        return

    st.markdown('<div class="mission-tag">AETHERIS / OBSERVACIÓN → INTERPRETACIÓN → ALERTA</div>', unsafe_allow_html=True)
    st.title("🔭 Aetheris AI: Observatorio Roque de los Muchachos - AWS Bedrock Data Feed")
    st.caption("Telemetría sintética inspirada en un observatorio canario · No es una conexión al telescopio real.")

    uno, dos, tres = st.columns(3)
    uno.metric("Sectores observados", len(df))
    dos.metric("Luminosidad máxima (u. a.)", f"{df['Luminosidad'].max():,.0f}")
    tres.metric("Variación térmica máxima (K)", f"{df['Variación térmica'].max():,.0f}")

    tabla, grafico = st.columns([1.35, 1], gap="large")
    with tabla:
        st.subheader("📡 Telemetría del telescopio")
        st.caption("Ascensión recta: horas · Declinación: grados · Luminosidad: u. a. · Variación térmica: K")
        # HTML generado solo a partir del DataFrame local, con escape activado.
        st.markdown(
            '<div class="telemetria">' + df.reset_index().to_html(index=False, escape=True, border=0) + "</div>",
            unsafe_allow_html=True,
        )
    with grafico:
        st.subheader("⚡ Firma de luminosidad")
        st.vega_lite_chart(
            df.reset_index(),
            {
                "background": "#101c30",
                "height": 310,
                "mark": {"type": "line", "color": "#53d6ff", "point": True},
                "encoding": {
                    "x": {"field": "Fila", "type": "quantitative", "title": "Medición",
                          "axis": {"tickMinStep": 1}},
                    "y": {"field": "Luminosidad", "type": "quantitative", "title": "Luminosidad (u. a.)"},
                    "tooltip": [{"field": "Sector", "type": "nominal"},
                                {"field": "Luminosidad", "type": "quantitative"},
                                {"field": "Variación térmica", "type": "quantitative"}],
                },
                "config": {
                    "axis": {"labelColor": "#dbe7ff", "titleColor": "#dbe7ff", "gridColor": "#263956"},
                    "view": {"stroke": "#263956"},
                },
            },
            width="stretch",
            theme=None,
        )
        st.caption("La séptima medición contiene el evento de prueba inyectado.")
        st.download_button(
            "Descargar telemetría CSV",
            data=df.to_csv(index=True).encode("utf-8-sig"),
            file_name="aetheris_telemetria_simulada.csv",
            mime="text/csv",
            on_click="ignore",
            width="stretch",
        )

    st.divider()
    if modo == MODO_LOCAL:
        st.warning("ENSAYO LOCAL · resultado simulado; no se ha llamado a Amazon Bedrock.")
    else:
        st.caption("MODO BEDROCK · El botón envía este lote a AWS; la inferencia puede generar consumo en tu cuenta.")
    etiqueta = "Analizar Sector con Amazon Bedrock" if modo == MODO_REAL else "Ejecutar ensayo local (sin AWS)"
    if st.button(etiqueta, type="primary", width="stretch"):
        st.session_state.pop("analisis", None)
        st.session_state.pop("informe", None)
        for key in ("alexa_history", "alexa_trace", "alexa_followup"):
            st.session_state.pop(key, None)
        if modo == MODO_REAL and not region:
            st.warning("Indica una región AWS en el panel lateral para iniciar el análisis.")
        else:
            mensaje = "Amazon Bedrock está analizando las 20 mediciones…" if modo == MODO_REAL else "Preparando el ensayo local…"
            with st.spinner(mensaje):
                try:
                    inicio = time.perf_counter()
                    texto = analizar_con_bedrock(df, region) if modo == MODO_REAL else generar_ensayo_local(df)
                    duracion = round(time.perf_counter() - inicio, 3)
                    st.session_state.analisis = texto
                    st.session_state.contexto_analisis = contexto
                    st.session_state.informe = {
                        "proyecto": "Aetheris AI",
                        "version": VERSION,
                        "origen": "bedrock" if modo == MODO_REAL else "ensayo_local",
                        "telemetria_simulada": True,
                        "modelo": MODEL_ID if modo == MODO_REAL else None,
                        "region": region if modo == MODO_REAL else None,
                        "analisis": texto,
                        "fecha_utc": datetime.now(timezone.utc).isoformat(),
                        "duracion_segundos": duracion,
                        "datos": json.loads(df.to_json(orient="records", force_ascii=False)),
                    }
                except (NoCredentialsError, PartialCredentialsError):
                    st.error("Faltan credenciales AWS válidas. Autentica tu perfil local y vuelve a intentarlo.")
                    st.info("Para presentar sin AWS, selecciona «Ensayo local (sin AWS)» en el panel lateral.")
                except ClientError as exc:
                    codigo = exc.response.get("Error", {}).get("Code", "ErrorAWS")
                    st.error(f"No se pudo completar el análisis en AWS ({codigo}).")
                    st.info("Comprueba credenciales, permiso bedrock:InvokeModel y disponibilidad/acceso al modelo en la región seleccionada.")
                except BotoCoreError:
                    st.error("No se pudo conectar o autenticar con Bedrock. Revisa credenciales AWS, región y conexión; puedes volver a intentarlo.")
                except (ValueError, KeyError, TypeError, AttributeError):
                    st.error("Bedrock devolvió una respuesta vacía o con formato inesperado. Vuelve a intentar el análisis.")

    if st.session_state.get("analisis"):
        st.subheader("🚨 ALERTA DE ANOMALÍA CRÍTICA")
        st.error(st.session_state.analisis)
        informe = st.session_state.informe
        origen = "Claude 3 Sonnet en Amazon Bedrock" if informe["origen"] == "bedrock" else "Resultado simulado por una regla local; sin invocación AWS"
        st.caption(f"{origen} · {informe['duracion_segundos']:.3f} s · Clasificación orientativa para la demo.")
        st.download_button(
            "Descargar informe JSON",
            data=json.dumps(informe, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="aetheris_informe.json",
            mime="application/json",
            on_click="ignore",
        )
    else:
        st.caption("Pulsa el botón para analizar las 20 mediciones con el modo seleccionado.")


if __name__ == "__main__":
    main()
