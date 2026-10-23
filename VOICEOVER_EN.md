# Aetheris AI · Voiceover en inglés

Guion de **243 palabras**, pensado para una voz natural en unos **1:55–2:25**. Las marcas de tiempo orientan el montaje del vídeo local de 2:18; ajustaremos las pausas a la grabación real. No es una promesa de duración exacta ni de resultado en el concurso.

## Cómo grabarlo

- Graba con tu voz en **MP3, WAV o M4A**, en una habitación tranquila y con el micrófono a distancia constante.
- Lee solo los párrafos en inglés. No leas títulos ni marcas de tiempo.
- Deja **dos segundos de silencio entre bloques** para facilitar los cortes. Si te equivocas, pausa y repite la frase completa.
- Habla con claridad y a un ritmo cómodo; no fuerces un acento. Pronuncia los números despacio.
- Graba **sin música** y evita filtros agresivos, reducción de ruido que deforme la voz o compresión que la vuelva ruidosa. Conserva el archivo original.
- En pantalla debe verse el modo **Ensayo local (sin AWS)** y la etiqueta de simulación. La narración no representa una conexión real con Alexa ni una invocación AWS verificada.

Para leerlo: **GTC zero zero seven** se refiere a `GTC-007`; **pending human review** se refiere al estado `pending_human_review`; **ninety-six point three five** corresponde al ratio `96.35` de esta muestra.

## 1 · Valor y simulador · 0:00–0:25

An observer needs more than a red warning. They need to understand what changed and what to review next. Aetheris AI demonstrates that workflow through an Alexa+ web simulation. This recording uses synthetic data and local rehearsal, without a live Alexa or AWS connection.

## 2 · Observatorio y fila 7 · 0:25–0:46

Here, the Observatory workspace shows twenty measurements. Row seven, sector GTC zero zero seven, contains our deliberately injected event. The table and line chart expose the same data, so the warning can be checked against visible evidence.

## 3 · Scan the observatory · 0:46–1:07

Back in the simulator, I select Scan the observatory. The local tool inspects the current batch and identifies the candidate sector. Its trace records the operation, keeping the assistant's response connected to the measurements it actually used.

## 4 · Explain the anomaly · 1:07–1:31

Next, Explain the anomaly compares the event with the other sectors. Its luminosity is ninety-six point three five times their median, alongside an extreme thermal variation. That supports a review-worthy alert, but it does not confirm a supernova or rule out other causes.

## 5 · Prepare follow-up · 1:31–1:55

Prepare follow-up turns the finding into a structured draft. The JSON clearly says pending human review. It proposes checking calibration and obtaining authorized follow-up observations. No message is sent, and nothing is scheduled. The observer keeps control of the next step.

## 6 · Trazabilidad, pruebas y siguiente paso · 1:55–2:18

The trace and exported evidence make the workflow inspectable. Twenty-six local tests pass, including tests with mocked AWS responses. The Bedrock invocation path is implemented; our next milestone is an authorized cloud run, followed by evaluation with astronomers and representative observations.

## Comprobación antes del montaje

Escucha la toma completa: las palabras deben entenderse sin subir y bajar el volumen. Comprueba especialmente «ninety-six point three five», «pending human review» y la distinción entre local tests y authorized cloud run. Los 26 tests constan como correctos en `evidencias/pruebas.txt`; sus respuestas AWS simuladas no acreditan ejecución cloud. Si cambia la muestra o la suite, actualiza esas cifras antes de grabar.

El repositorio público ya existe: [Enrickq/aetheris-ai](https://github.com/Enrickq/aetheris-ai). La publicación del vídeo en YouTube queda a cargo del usuario; este archivo no afirma que se haya publicado.

