# Aetheris AI · Guion de presentación

Vídeo final: [Aetheris AI en YouTube](https://youtu.be/-5itenMafn0), **1 min 46 s**, con grabación inglesa aportada por el autor y subtítulos ingleses incrustados. El archivo final local es `entrega/Aetheris-AI-FINAL-subtitulado.mp4`; el vídeo de 138 s en `demo/` se conserva como respaldo con voz sintética. El montaje muestra el ensayo local de la aplicación; no una conexión real con Alexa ni una inferencia AWS.

[Envío a Devpost confirmado](https://devpost.com/software/aetheris-ai) el 23 de octubre de 2026, aproximadamente a las 18:28 UTC, antes del cierre. El estado de envío no constituye una evaluación del jurado.

## Pitch breve

> Aetheris AI convierte telemetría astronómica en una alerta que se puede entender. En este MVP simulamos 20 observaciones del Roque de los Muchachos, introducimos una anomalía evidente y enviamos exactamente esos datos a Claude 3 Sonnet mediante Amazon Bedrock. El observador ve el pico, recibe una explicación breve y puede descargar la evidencia. Todo funciona desde una aplicación Streamlit en un único archivo Python.

## Antes de presentar

1. Ejecuta `iniciar.ps1` y abre la URL de Streamlit.
2. Decide qué vas a demostrar: **Amazon Bedrock (real)** o **Ensayo local (sin AWS)**. Anuncia el modo elegido.
3. Para AWS real, completa `AWS_SETUP.md` y realiza una prueba con la misma cuenta y región antes del turno del jurado.
4. Comprueba que se muestran 20 filas y que la séptima es `GTC-007`.
5. Mantén accesible la terminal para ver problemas de arranque. Las credenciales no deben aparecer en la pantalla compartida ni en los archivos entregados.

## Demo de 90 segundos

| Tiempo | Acción en pantalla | Qué decir |
| --- | --- | --- |
| 0–15 s | Mostrar título y observatorio | «Aetheris AI explora cómo reducir el tiempo entre ver una señal extraña y entender por qué merece atención.» |
| 15–30 s | Señalar tabla y pico | «Estos datos son simulados. De 20 observaciones, la séptima tiene una luminosidad de 9800 y una variación térmica de 1250; el resto permanece cerca del nivel normal.» |
| 30–45 s | Mostrar el modo y pulsar analizar | AWS: «Convertimos la misma tabla a JSON y la enviamos con `invoke_model` a Claude 3 Sonnet en Bedrock». Ensayo: «Este es el ensayo sin AWS; el análisis siguiente está marcado como simulado». |
| 45–65 s | Leer la alerta cuando aparezca | «La explicación identifica el sector y relaciona el pico luminoso con el térmico. La clasificación es una hipótesis para la demo, no una confirmación científica.» |
| 65–80 s | Descargar CSV e informe JSON | «Podemos entregar las observaciones y el resultado indicando de dónde procede el análisis.» |
| 80–90 s | Cerrar con el siguiente paso | «El siguiente paso sería integrar telemetría real, validar con astrónomos y medir calidad y latencia antes de automatizar decisiones.» |

La llamada real puede tardar más que el tiempo asignado en este guion. Si aún está en curso, explica el flujo y espera su respuesta sin prometer una latencia. Si falla, muestra el error; cambia al ensayo de forma explícita y aclara que no es una respuesta de AWS.

## Preguntas previsibles

**¿Son datos reales del Gran Telescopio Canarias?**  
No. El contexto se inspira en el observatorio; las observaciones y la anomalía están generadas localmente.

**¿La IA descubre una supernova?**  
No se acredita un descubrimiento. La anomalía está insertada en la séptima fila. El MVP demuestra el envío de telemetría y una explicación; una clasificación científica exige más información y validación experta.

**¿Qué parte usa AWS?**  
El modo real crea un cliente `bedrock-runtime`, envía el prompt y los datos con `invoke_model` y muestra el texto devuelto por Claude. El ensayo local no llama a AWS.

**¿Por qué Claude 3 Sonnet?**  
Es el modelo fijado para este MVP. Su disponibilidad debe verificarse para la cuenta y región. Un producto posterior tendría que gestionar versiones y evaluar una migración antes del retiro anunciado.

**¿Ya está en producción o en un telescopio?**  
No. Esta entrega es una demo local. No incorpora ingesta continua, autenticación de usuarios, almacenamiento persistente ni validación observacional.

**¿Cuánto cuesta o cuánto tarda?**  
No afirmamos cifras sin medirlas. El ensayo no invoca Bedrock. El coste y la latencia reales dependen de la ejecución en AWS y deben medirse por separado.

## Texto breve para acompañar la entrega

**Proyecto:** Aetheris AI.  
**Problema:** explicar con rapidez anomalías visibles en telemetría astronómica.  
**MVP:** aplicación Streamlit de un archivo con 20 observaciones sintéticas, una anomalía inyectada y análisis bajo demanda con Amazon Bedrock.  
**Tecnologías:** Python, Streamlit, Pandas, boto3, Claude 3 Sonnet.  
**Entregables:** código, dependencias, iniciador, configuración AWS, guion y evidencias locales.  
**Límite declarado:** sin datos de un telescopio real ni inferencia real acreditada en la entrega; el ensayo está identificado como simulado.
