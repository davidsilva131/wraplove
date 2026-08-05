# Informe: Export de chat de WhatsApp (Android) — formato, pérdidas y pipeline de parsing

## 1. Estructura exacta del .txt de export Android

El export Android es un **archivo de texto plano UTF-8** (`<nombre>.txt`) — y cuando eliges "Incluir archivos", se envía un **ZIP con el .txt + archivos de media** adjuntos; el pipeline solo necesita el `.txt`. Formato canónico actual:

```
dd/mm/aaaa, HH:MM[:SS] - Remitente: mensaje
```

Ejemplos reales verificados:

```
# Mensaje normal (formato Android, fixture real de whatstk — chat "Pokemon Chat")
15.04.2016, 15:04 - Pokemon Chat: Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them.
06.08.2016, 13:23 - Ash Ketchum: Hey guys!

# Mensaje de sistema (timestamp + texto SIN "Remitente:") — el "sender" es null
06.08.2016, 13:18 - Messages you send to this group are now secured with end-to-end encryption. Tap for more info.

# Mensaje multilínea (las líneas siguientes se anexan al mensaje anterior)
23/06/2018, 01:55 p.m. - Loris: one
two

# Media omitida (placeholder localizado; inglés, español, alemán, francés…)
12/03/2023, 21:34 - Sara: <Media omitted>            ← EN
12/03/2023, 21:34 - Sara: <Multimedia omitido>        ← ES (variantes: <Archivo omitido>)
12/03/2023, 21:34 - Sara: <Imagen omitida>            ← subtipos: <Vídeo omitido>, <Nota de voz omitida>, <Sticker omitido>, <Documento omitido>…

# Export "Con media" en Android moderno: el nombre del archivo en línea
12/03/2023, 21:34 - Sara: IMG-20230312-WA0001.jpg (file attached)   ← localizado ("(Datei angehängt)" en DE)

# Mensaje vacío (existe y no es sistema)
03/02/17, 18:42 - Luke:

# Eliminados/llamadas como sistema o como línea con nombre
06/03/2017, 00:45 - You created group "Test"
14/05/2023, 09:12 - You deleted this message / This message was deleted / Missed voice call
```

Variantes reales que un parser debe aceptar (confirmadas en fixtures de Pustur y Nuntius):
- **Fechas**: `dd/mm/yyyy`, `dd.mm.yyyy`, `dd-mm-yy`, `m/d/yy` (EE.UU., con AM/PM), `aaaa-mm-dd` (ISO), separadores `/ . -`.
- **Hora**: `HH:MM` (versiones antiguas) u `HH:MM:SS` (versiones nuevas); 24h o `a.m./p.m.` (con **espacio normal/narrow no-break** raro: `p. m.` o `9:34 PM`).
- **Separador**: ` - ` (puede ser **en dash `–`**), y en iOS `[dd/mm/yyyy, hh:mm:ss]` con corchetes (formato iOS ≠ Android: no confundir).
- **Caracteres invisibles**: iOS inserta marcas bidi (U+200E/U+200F/U+202A–U+202E/U+2066–U+2069/U+FEFF) alrededor de fechas y media; hay que strip-arlos antes de matchear.
- **Mensajes de sistema**: cualquier línea con timestamp y **sin** `Nombre:` → sistema (avisos de cifrado, "creó el grupo", "cambió el nombre", "X se unió/salió", avisos de seguridad). Ojo: avisos que contienen dos puntos ("You changed the group description to: ...") no deben inventar un remitente.
- El propio usuario exporta con su **nombre tal como aparece en el chat**, no como "You".
- Los mensajes **no siempre vienen en orden cronológico** (issue #247 de Pustur: por problemas de conexión, hay bloques desordenados) — el parser no debe reordenar a medias; la capa de stats sí puede sortear.

## 2. Qué se pierde vs. la conversación real

El FAQ oficial lo dice literal: *"Your chat history can't be re-imported because it's a text file and not a backup file."* No es un backup:

- **Sin ticks de estado**: no hay entregado/leído/doble check — solo la hora de envío (minuto o segundo, hora local del dispositivo, **sin zona horaria**, con saltos DST).
- **Sin ediciones**: solo el texto final; el marcador "(editado)" no aparece.
- **Sin reacciones**: los emojis de reacción a mensajes no se exportan.
- **Sin estructura de replies/citas**: una respuesta se exporta como mensaje plano; no puedes saber si era reply (solo si el texto citado estaba pegado).
- **Media no incrustada**: en "Sin media" queda el placeholder localizado; en "Con media", solo **los archivos recientes** que entren en el método de envío (FAQ: "the most recent media sent will be added as attachments") y llegan como adjuntos/ZIP, nunca en el txt. "Ver una vez" nunca se exporta.
- **Sin IDs de mensaje**: deduplicación solo heurística (ts+sender+texto).
- **Eliminados**: si el otro borró, puede quedar "This message was deleted"; tus propios borrados → "You deleted this message".
- **Nombres de contacto** tal como estaban guardados en el móvil al exportar (si no está en contactos, número de teléfono); no es posible recuperar el número del nombre.
- **Solo lo que queda en el dispositivo**: mensajes efímeros ya expirados, chats borrados, o media antigua purgada por falta de espacio, no están.
- **Límite práctico**: export vía sharesheet/correo; chats enormes pueden no incluir toda la media (el txt sí sale completo).
- Línea de cabecera obligatoria: el aviso "Messages and calls are end-to-end encrypted…" (a veces con el nombre del grupo como remitente, a veces sin nombre).

Consecuencia para las stats de la landing: "mensajes enviados por hora", "palabras", "emojis", "rachas", conteo de frases ("te quiero") son **fiables**; ticks/lecturas/reacciones son **imposibles** y no hay que prometerlos.

## 3. Approach de parsing recomendado

**Python 3 (stdlib: `zipfile`, `re`, `datetime`, `csv`, `json`). Un solo script, cero dependencias.** (Alternativa Node: la lib `whatsapp-chat-parser` de Pustur hace exactamente esto; pero para un pipeline one-off de pre-proceso, Python stdlib es lo mínimo que funciona.)

Técnicas (todas verificadas en parsers de producción):
1. **Descomprimir** el ZIP si existe: quedarse con el único `.txt` (whatstk falla si el ZIP trae más de un txt — en la práctica trae txt + media; ignorar media).
2. **Leer UTF-8** con `encoding="utf-8-sig"` (tolera BOM) y `errors="replace"`. Nunca asumir otro encoding.
3. **Limpiar caracteres invisibles** antes de parsear: `[\u200e\u200f\u202a-\u202e\ufeff\u2066-\u2069]` (bidi marks, ZWJ/ZWNJ/ZWSP, soft hyphen).
4. **Detección de orden de fecha** (dd/mm vs mm/dd) en una pasada previa: muestrear líneas, la componente con valores >12 es el día (misma heurística de Pustur/whatstk; en una pareja española es dd/mm).
5. **Parseo línea a línea** con regex anclada al inicio:
   `^\[?(\d{1,4})[/.-](\d{1,2})[/.-](\d{2,4})[,.]?\s+(\d{1,2})[:.](\d{2})(?::(\d{2}))?[ .]*(?:[ap]\.?\s?m\.?)?\]?\s*[-–—]\s*(?:([^:]{1,120}):\s?)?(.+)?$`
   - Línea que **no matchea** → continuar línea del mensaje anterior (unir con `\n`), incluso si contiene algo parecido a una fecha (caso cubierto en los tests de Pustur).
   - Línea con timestamp **sin `Nombre:`** → mensaje de sistema (author=null).
   - Autor limitado a ~120 chars antes del `:` para no romper con ":" dentro de urls/texto.
   - Año de 2 dígitos → +2000.
6. **Clasificación de tipo** por tabla localizada (nunca string fijo en inglés): placeholders `<media omitted|multimedia omitido|archivo omitido|médias omis|mídia oculta|media weggelaten|media omessi|medya atlandı>`, subtipos (`image/video/audio/voice/sticker/gif/document/contact omitted`, `contact card`, `live location shared`, `location:`, `POLL:`), adjuntos `<attached: file>` (iOS) y `file (file attached)` (Android), y líneas `this message was deleted|you deleted this message|missed voice/video call|no answer|call ended`.
7. **Fechas → epoch** (segundos, hora local sin tz) + ISO string.

Tamaños: un chat de pareja es típicamente 10⁴–10⁵ mensajes; el parseo con una pasada y acumulación es O(n), sin problemas de memoria. Para el pipeline por lotes no se necesita streaming.

## 4. Esquema de dataset resultante (decidido)

**Dos artefactos: `messages.csv` (canónico) + `stats.json` (lo que consume la landing). Sin SQLite** (un solo chat, decenas de miles de filas: sqlite/pandas serían overhead; el `csv` y `json` del stdlib bastan y se pueden re-exportar).

**`messages.csv`** — fila por mensaje, sin datos derivados (los cálculos viven en stats):

| columna | tipo | notas |
|---|---|---|
| `id` | int | secuencial |
| `ts` | int | epoch segundos, hora local del dispositivo (sin tz) |
| `date_iso` | str | `YYYY-MM-DD HH:MM[:SS]` |
| `sender` | str | nombre tal cual sale en el export; el del exportador se identifica por config (un prompt/constante), no heurísticamente |
| `type` | str enum | `text \| system \| media \| image \| video \| audio \| voice \| sticker \| gif \| document \| contact \| location \| poll \| call \| deleted \| other` |
| `text` | str | texto completo; multilínea unida con `\n`; los placeholders quedan en `text` (la clasificación está en `type`) |

**`stats.json`** — agregados precalculados, lo único que la landing fetchea:

```json
{
  "meta": { "chat_name": "…", "exported_by": "David", "partner": "Elena",
            "first_ts": 1234567890, "last_ts": 1234567999,
            "n_messages": 45231, "n_days": 812 },
  "per_sender": [ { "sender": "…", "messages": 0, "words": 0, "chars": 0,
                    "media": 0, "system": 0, "avg_words": 0.0,
                    "first_ts": 0, "last_ts": 0, "days_active": 0 } ],
  "series": { "by_hour": [0,…23], "by_dow": [0,…6], "by_month": ["2023-01", …],
              "by_sender_hour": { "David": [0,…23], "Elena": […] } },
  "top_emojis": [["❤️", 321], …],
  "top_words": [["amor", 89], …],
  "phrases": { "te_quiero": 128, "te_amo": 41, "i_love_you": 7 },
  "streaks": { "longest_days": 47, "current_days": 3, "by_sender": {…} },
  "longest_message": { "sender": "…", "words": 210, "ts": 0 },
  "median_reply_seconds": 0
}
```

Notas de honestidad del esquema: `median_reply_seconds` es **heurístico** (siguiente mensaje del otro a menos de N min, sin IDs de reply — si la cifra no convence, se omite); `top_words` normaliza (lowercase, sin puntuación, stopwords ES). Todo lo demás es exacto salvo las pérdidas de la sección 2.

## 5. Fuentes consultadas

- WhatsApp FAQ oficial (Android, export): https://faq.whatsapp.com/android/chats/how-to-save-your-chat-history — "Include media → the most recent media…"; "can't be re-imported… not a backup file".
- Pustur/whatsapp-chat-parser (TS/Node): https://github.com/Pustur/whatsapp-chat-parser · regex real en `src/parser.ts` · casos borde en `tests/parser.test.ts` (multilínea, sistema, empty, formatos, adjuntos, días 1º).
- lucasrodes/whatstk (Python/pandas): https://github.com/lucasrodes/whatstk · `whatstk/whatsapp/parser.py` (regex, limpieza unicode, años 2 dígitos, AM/PM) · `header_format_support.json` (catálogo de formatos) · export real de ejemplo `chats/whatsapp/pokemon.txt`.
- ArsalanKaleem/Nuntius (app Flutter "WhatsApp Wrapped", mismo caso de uso): https://github.com/ArsalanKaleem/Nuntius · `lib/features/parser/whatsapp_patterns.dart` — regex Android/iOS, caracteres invisibles, **tabla de placeholders localizados**, guard para avisos de sistema con dos puntos.
- whatstk docs (formato de export por plataforma): https://whatstk.readthedocs.io/en/latest/source/getting_started/export_chat.html
- KnugiHK/WhatsApp-Chat-Exporter (alternativa pesada basada en msgstore.db, descartada para este caso).
- MasterScrat/Chatistics (flujo de export manual y esquema por-mensaje).

## Pipeline único recomendado (decisión)

**Android → ZIP/txt → Python 3 stdlib (1 script, sin deps) → `messages.csv` (canónico) + `stats.json` (landing).**

Pasos: unzip → leer UTF-8-sig → strip invisibles → detectar orden d/m → parsear con regex anclada + acumulación de multilínea + sistema sin remitente → clasificar tipo con tabla localizada → fecha→epoch local → identificar exportador por config → escribir CSV → computar agregados y volcar `stats.json` → la landing solo fetchea `stats.json`. Si luego se quiere recomputar o añadir una stat, se repite el paso de agregados contra el CSV; si el dataset creciera a multi-chat/multi-usuario, ahí sí migrar a SQLite.
