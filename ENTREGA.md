# Aetheris AI — ficha de entrega

**Proyecto:** Aetheris AI 1.1.0  
**Pista preparada:** Alexa+ — experiencia web simulada  
**Tecnología AWS implementada:** Amazon Bedrock Runtime con Claude 3 Sonnet

**Devpost:** usuario autenticado y registrado; [borrador creado](https://devpost.com/software/aetheris-ai), ID `1257991-aetheris-ai`, **3/5 pasos completos**. Descripción inglesa, repositorio, cuatro etiquetas tecnológicas y tres capturas guardados. Información adicional de feedback, pruebas y friction log guardada. Pista Alexa+ simulada seleccionada; AWS Builder y Open Source no seleccionados. **Sin URL de vídeo, aceptación de términos finales ni envío final todavía.**

## Descripción breve para el formulario

Aetheris AI convierte un lote de telemetría astronómica en una alerta explicada. Una interfaz Streamlit inspirada en el Observatorio del Roque de los Muchachos visualiza 20 mediciones sintéticas, muestra un evento extremo y permite enviar los mismos datos a Claude 3 Sonnet en Amazon Bedrock para obtener una interpretación breve. El jurado puede revisar los datos y exportar el informe con su origen.

## Problema y propuesta

Un pico de telemetría necesita contexto para ser investigado. Este MVP demuestra cómo conectar una visualización de datos con una explicación generada bajo demanda: observación, interpretación y alerta en una sola pantalla. El objetivo de una evolución del proyecto sería ayudar a priorizar eventos para revisión humana; este prototipo no valida detección científica ni sustituye a un astrofísico.

## Demostración disponible

- Aplicación completa en un único `app.py`, sin base de datos ni servicios auxiliares.
- 20 filas reproducibles; la séptima contiene el evento inyectado `GTC-007`.
- Cliente `bedrock-runtime`, operación `invoke_model`, prompt y modelo exigidos.
- Modo de ensayo local explícito, útil cuando no hay acceso a AWS.
- CSV de telemetría e informe JSON que distingue `bedrock` y `ensayo_local`.
- Pruebas automatizadas y capturas de la ejecución local en `evidencias/`.
- Espacio **Alexa+ simulation**: escaneo, explicación, traza y seguimiento para revisión humana.
- Vídeo inglés actual de 138 s, con voz sintética, en `demo/Aetheris-AI-demo-en.mp4`.
- Guion `VOICEOVER_EN.md` para la voz del autor; el audio propio aún no se ha recibido ni montado.
- Textos del formulario y feedback en `SUBMISSION_EN.md` y `FEEDBACK_EN.md`.
- [Friction log público](https://github.com/Enrickq/aetheris-ai/blob/main/evidencias/FRICTION_LOG_EN.md) con dos observaciones locales de Streamlit.

## Estado que debe declararse al presentar

La aplicación y el ensayo local están verificados. El contrato de la llamada a AWS se comprueba con clientes simulados. **No se acredita una inferencia real de Bedrock**: el perfil local `aetheris-demo` tiene región, pero necesita autenticación y acceso al modelo. Las capturas y el informe de ejemplo son del ensayo local. No hay conexión real al telescopio ni adquisición continua.

El ID solicitado se conserva: `anthropic.claude-3-sonnet-20240229-v1:0`. Su disponibilidad depende de región/cuenta y del ciclo de vida documentado en `AWS_SETUP.md`.

## Cómo evaluar la entrega

1. Descomprime el paquete en una carpeta y ejecuta `./iniciar.ps1` en PowerShell.
2. Selecciona **Workspace → Alexa+ simulation** y **Ensayo local (sin AWS)**.
3. Pulsa **Scan the observatory**, **Explain the anomaly** y **Prepare follow-up**; revisa la traza y `pending_human_review`.
4. Descarga el JSON y comprueba su procedencia. En **Observatory** puedes revisar `GTC-007`, la gráfica y exportar el CSV.
5. Consulta `DEMO_EN.md` para la presentación inglesa, `VOICEOVER_EN.md` para la narración y `AWS_SETUP.md` para probar la ruta real.

## Antes de enviar al evento

Evento confirmado: Build, Ship, Shape: Amazon Developer Hackathon. Código, vídeo actual y evidencias están publicados en https://github.com/Enrickq/aetheris-ai con licencia MIT. El usuario preparará su grabación de voz; todavía no se ha recibido. Publicará el vídeo en YouTube/Vimeo y facilitará su URL. El borrador está guardado en Devpost, pero faltan el vídeo y el cierre final. Consulta `CIERRE.md` para el estado y `SUBMISSION_EN.md` para los textos del formulario.
