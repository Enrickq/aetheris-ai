# Verificación de la entrega · 23 de octubre de 2026

Estado: **demo local verificada; inferencia real de AWS pendiente de autenticación y acceso al modelo**.

| Comprobación | Resultado |
| --- | --- |
| Instalación desde `requirements.txt` en `.venv` | Correcta con `iniciar.ps1 -SoloPreparar` |
| Dependencias | Streamlit 1.66.1, Pandas 3.1.0, boto3 1.43.118; `pip check` sin conflictos |
| Iniciador Windows | Sintaxis correcta y arranque comprobado con el perfil `aetheris-demo` |
| Salud HTTP de Streamlit | `http://127.0.0.1:8501/_stcore/health` devuelve `ok` |
| Pruebas automatizadas | 26 ejecutadas; todas correctas; ver `pruebas.txt` |
| Navegador | Carga, selector de modos, controles oscuros, tabla, gráfico y alerta revisados |
| CSV descargado desde la UI | 20 filas; coincide con el DataFrame de la aplicación |
| JSON descargado desde la UI | 20 registros coincidentes; origen `ensayo_local`, modelo y región `null` |
| Cliente Bedrock real | Contrato probado con mocks; no se ha realizado una inferencia AWS |
| Simulador Alexa+ | Escaneo, pregunta escrita, explicación y seguimiento comprobados en navegador |
| Vídeo inglés | 138,43 s; H.264/AAC, 1920×1080, decodificación completa y audio comprobados |

## Evidencias

- `01-panel.png`: interfaz del MVP con el modo de ensayo seleccionado, tabla y pico de luminosidad.
- `02-alerta-ensayo.png`: resultado local marcado expresamente como simulado.
- `telemetria_simulada.csv`: exportación realizada desde el navegador.
- `informe_ensayo.json`: informe descargado desde el navegador; conserva origen y fecha UTC.
- `pruebas.txt`: salida de la suite ejecutada en el entorno de la entrega.
- `03-alexa-ready.png` a `07-alexa-trace.png`: ejecución del simulador 1.1.0.
- `scan_report_ensayo.json` y `followup_ensayo.json`: descargas del flujo conversacional; estado `pending_human_review`, ninguna acción externa.
- `video_verification.json`: formato, duración, decodificación y audio del vídeo.

La duración del informe corresponde al ensayo local. No es una medida de latencia de Bedrock ni una prueba de acceso al servicio. La anomalía está inyectada en los datos; no se ha medido precisión astronómica ni detección con datos reales.

El perfil `aetheris-demo` se preparó en la configuración AWS del equipo con región `us-east-1`; no contiene claves. Esta configuración personal queda fuera del ZIP. La política IAM incluida es una plantilla y no se ha aplicado a ninguna cuenta.

Para repetir las pruebas:

```powershell
.\iniciar.ps1 -SoloPreparar
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Para validar AWS real, sigue `AWS_SETUP.md` y guarda un informe nuevo con origen `bedrock` tras una llamada satisfactoria.
