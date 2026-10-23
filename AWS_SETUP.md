# Conectar Aetheris AI con Amazon Bedrock

El modo **Amazon Bedrock (real)** envía telemetría sintética a la cuenta AWS configurada. El modo **Ensayo local (sin AWS)** no necesita credenciales y no verifica la integración cloud.

## 1. Confirmar cuenta, región y modelo

En la consola de Amazon Bedrock de tu cuenta, comprueba acceso al modelo:

```text
anthropic.claude-3-sonnet-20240229-v1:0
```

Usa en el panel lateral una región donde esa cuenta pueda invocarlo. El valor inicial procede de `AWS_REGION`, después de `AWS_DEFAULT_REGION` y, si ambas faltan, es `us-east-1`; ese valor inicial no garantiza disponibilidad. La región del portal SSO puede ser distinta de la región de inferencia.

Estado consultado el **23 de octubre de 2026**: AWS anuncia EOL el **13 de noviembre de 2026** en `ap-south-1`, `ap-southeast-1`, `eu-west-2`, `sa-east-1` y `ca-central-1`. La disponibilidad y las restricciones de Legacy varían por región y cuenta; no basta con que el identificador exista. El código conserva el ID exigido y no cambia a otro modelo cuando falla. [Ciclo de vida oficial de AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle-legacy.html).

## 2. Autenticar con un perfil

En el equipo de preparación se ha creado **`aetheris-demo`** en `~/.aws/config` con esta configuración:

```ini
[profile aetheris-demo]
region = us-east-1
output = json
```

**No contiene credenciales ni acredita acceso a AWS.** En otro equipo tendrás que configurar el perfil; el archivo personal `~/.aws/config` no se incluye en el paquete.

Boto3 admite perfiles locales, IAM Identity Center, variables de entorno y roles de AWS. La aplicación utiliza esa cadena estándar sin guardar claves. [Credenciales de boto3](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html).

Con AWS CLI v2 y un perfil de IAM Identity Center:

```powershell
aws configure sso --profile aetheris-demo
aws sso login --profile aetheris-demo
aws sts get-caller-identity --profile aetheris-demo
```

La configuración SSO necesita los datos de cuenta y organización que proporcione el evento o tu administrador. El perfil local preparado no permite deducirlos. Si ya tienes un perfil válido, selecciónalo mediante `-PerfilAWS` al iniciar o con `AWS_PROFILE`. Para un entorno AWS con rol de ejecución, asigna el permiso al rol y deja que boto3 obtenga las credenciales temporales.

No pegues claves en `app.py`, en el repositorio ni en el chat. Si tu organización usa variables de entorno con credenciales temporales, también necesita `AWS_SESSION_TOKEN` cuando corresponda.

## 3. Aplicar el permiso de inferencia

La llamada utilizada requiere **`bedrock:InvokeModel`**. El archivo `iam-policy.json` ya limita el recurso al modelo exacto en **`us-east-1`**:

```text
arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0
```

El administrador debe asociar la política a la identidad o al rol de la demo. Si eliges otra región, cambia también la región del ARN. No se necesitan permisos de base de datos. [Referencia de InvokeModel](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html).

La política de inferencia no sustituye el acceso al modelo ni los permisos administrativos que una cuenta pueda necesitar para habilitarlo por primera vez. Debe prepararlos el administrador de la cuenta.

## 4. Ejecutar la prueba real

Con el perfil autenticado:

```powershell
.\iniciar.ps1 -PerfilAWS aetheris-demo
```

El iniciador prepara `.venv` y selecciona el perfil solo para esta ejecución. También admite `-SoloPreparar`, `-PythonExe` y `-Puerto`. Para usar directamente `streamlit run app.py`, selecciona antes el perfil en esa terminal:

```powershell
$env:AWS_PROFILE = "aetheris-demo"
streamlit run app.py
```

1. Selecciona **Amazon Bedrock (real)**.
2. Escribe la región comprobada.
3. Pulsa **Analizar Sector con Amazon Bedrock**.
4. Confirma que llega una respuesta y que el resultado indica origen AWS.
5. Descarga el CSV y el JSON para documentar esa ejecución. La respuesta puede variar entre llamadas.

`aws sts get-caller-identity` comprueba la identidad, pero no prueba acceso a Bedrock. Solo una invocación satisfactoria valida la ruta completa. Las llamadas reales pueden generar cargos en la cuenta; el ensayo local no llama al servicio.

## Diagnóstico

| Síntoma | Qué revisar |
| --- | --- |
| Credenciales ausentes o incompletas | Perfil elegido, sesión SSO vigente o conjunto completo de credenciales temporales |
| `AccessDeniedException` | Permiso `bedrock:InvokeModel`, recurso/región de la política, acceso al modelo y restricciones de la cuenta |
| `ValidationException` o modelo no encontrado | ID exacto, disponibilidad regional, estado Legacy/EOL y tipo de invocación permitido |
| `ThrottlingException` | Cuota de la cuenta; espera antes de reintentar |
| Conexión o timeout | Red, proxy corporativo, región y conectividad con el endpoint de AWS |
| Respuesta sin texto | Formato devuelto; vuelve a intentar y conserva el error como evidencia operativa |

El cuerpo de la solicitud usa `anthropic_version="bedrock-2023-05-31"` y `messages` con un bloque de texto. El análisis se obtiene de los bloques de texto de `content`. [Formato Messages oficial](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html).

No uses el ensayo como prueba de inferencia real. Si no hay acceso al modelo solicitado, presenta el ensayo con su etiqueta y deja la validación de AWS como pendiente explícita.
