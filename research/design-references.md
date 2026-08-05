# Reporte: Referencias de diseño para landing de relación/aniversario

## 1. Direcciones visuales detectadas

**A. "Informe Anual de la Pareja" (Wrapped oscuro y festivo)** — Fondo dark con acento de color único, cada stat es una escena de pantalla completa con número gigante que hace count-up al entrar, tarjetas tipo bento para emojis/rachas, "fun facts" con tono juguetón y de celebración. Es el género "Spotify Wrapped aplicado a una relación": los datos son el espectáculo.
Ejemplo: [Spotify Wrapped](https://www.spotify.com/us/wrapped/).

**B. "Crónica Editorial en Capítulos" (magazine cálida)** — Tipografía editorial (sans display + serif de contraste), fondo papel cálido, secciones asimétricas estilo revista, grandes citas y titulares, fotos enmarcadas tipo polaroid. Cuenta la historia como un libro con capítulos; el dato aparece como infografía de revista.
Ejemplo: [The Pudding – "A love story"](https://pudding.cool/2026/06/love-story) (narra relaciones con capítulos, gráficos tipo línea y rejillas de iconos).

**C. "Dossier de Telemetría" (brutalismo industrial)** — Números en monoespaciada, tablas tipo telemetría, marcos ASCII, acento rojo único, fondo papel maquinilla o CRT oscuro, "unidades" de datos verificados ("CIFRA 04 // MENSAJES ENVIADOS"). Juego de "datos duros de la relación" con humor nerdy. Encaja perfecto con lo "infográfico-estadístico" que pide la sorpresa.
Ejemplo de patrón: [Dribbble – tag anniversary-website](https://dribbble.com/tags/anniversary-website) (dirección no-rosa, mecánica/gráfica).

**D. "Museo Premium de la Relación" (high-end agencia)** — Blanco/gris frío o negro OLED, doble-bezel en tarjetas, macro-espaciado, nav de píldora flotante, tipografía cara, micro-física en hover. Se siente caro y cuidado; el amor como pieza de colección.
Ejemplo genérico del lenguaje: sitios Awwwards-tier (referencia de la skill high-end-visual-design); secciones típicas en [YourLovePage](https://www.yourlovepage.com/anniversary-website).

**E. "Scrapbook Cariñoso" (polaroids sueltas, casual)** — Fotos rotadas tipo polaroid dispersas, notas manuscritas, collage cálido, poco grid, mucha personalidad. Es lo que más venden los builders de sitios de pareja.
Ejemplo: [YourLovePage](https://www.yourlovepage.com/anniversary-website) y [Wegic couple builder](https://wegic.ai/ai-website-builder/couple) (secciones típicas: timeline interactivo, countdown, carta de amor, retratos).

## 2. Patrones infográficos para stats

1. **Número gigante por escena con count-up** — Una métrica por pantalla, tipografía enorme (clamp), contador animado al entrar. La opción por defecto para "primer mensaje", "total de mensajes", "días juntos". Ejemplo: [Spotify Wrapped](https://www.spotify.com/us/wrapped/).
2. **Heatmap de intensidad (grid 7×24 o rejilla de días)** — Celdas con intensidad de color (verde→rojo o un solo matiz con opacidad) para horas favoritas y días con más conversación; el mismo patrón que la contribution graph de GitHub o "tu vida en semanas". Ejemplo de rejilla de momentos: [The Pudding – "happy map"](https://pudding.cool/2026/02/happy-map).
3. **Barras espejo él↔ella (como burbujas de chat)** — Dos columnas back-to-back estilo conversación de WhatsApp para comparar "quién escribe más"; en vez de burbujas, barras horizontales enfrentadas. Ejemplo de comparativas por grupo: [The Pudding – "A love story"](https://pudding.cool/2026/06/love-story) (barras "men vs women").
4. **Leaderboard de emojis** — Top 5 emojis como ranking con el glifo gigante (o el código unicode si vas brutalista) y conteo; el humor de "nuestro lenguaje secreto". Patrón típico de los "wrapped" de apps de mensajería (Discord Wrapped).
5. **Strip de rachas / calendario** — Tira de días consecutivos con puntos llenos/vacíos para streaks ("12 meses sin dejar de hablar"), derivado del mismo grid de intensidad. Ejemplo de calendario estadístico-momentos: [The Pudding – "happy map"](https://pudding.cool/2026/02/happy-map).

## 3. Marcos narrativos

1. **Capítulos tipo libro** — "Capítulo 1: El primer mensaje", "Capítulo 2: El 'te quiero' número 1000"... cada capítulo con su paleta de sección y su escena de dato. El arco del Pudding: "Once upon a time…" / "But a global pandemic is coming…" — historias con giros marcados por transiciones escena a escena. Ejemplo: [The Pudding – "A love story"](https://pudding.cool/2026/06/love-story) y el de dos perspectivas [The Pudding – "infertility journey"](https://pudding.cool/2026/03/ivf).
2. **Timeline scrollytelling de milestones** — Línea del tiempo que se recorre haciendo scroll; cada hito se pincha (pinned section) y se anima su fecha + detalle; el patrón canónico para "primer mensaje → primera cita → mudanza". Vocabulario técnico de escenas (graphic sequence, animated transition, sticky side-by-side) en la [referencia de scrollytelling de OpenAI](https://github.com/openai/plugins/blob/main/plugins/build-web-data-visualization/skills/scrollytelling-and-parallax-data-visualization/references/story-patterns-and-scene-contracts.md). Ejemplos editables: [scrollytelling.ai – timeline examples](https://scrollytelling.ai/timeline-examples/).
3. **Narración por acumulación de puntos** — "Cada punto es un mensaje": un grid que se va completando mientras cuentas la historia; el dato se vuelve personaje y la cifra total llega al final como punchline. Ejemplo (cada icono = una persona): [The Pudding – "A love story"](https://pudding.cool/2026/06/love-story).

## 4. Mapeo dirección → skill de taste

| Dirección | Skill | Por qué (una línea) |
|---|---|---|
| A. Wrapped oscuro/festivo | **gpt-taste** | Es la única que aporta GSAP con pinning/scrubbing + bento sin huecos, exactamente lo que pide cada stat como escena animada. |
| B. Crónica editorial en capítulos | **design-taste-frontend** | Disciplina tipográfica editorial, asimetría controlada y paleta bloqueada; anti-template por defecto. |
| C. Dossier de telemetría | **industrial-brutalist-ui** | Los números mono, grids de blueprint y marcos ASCII son literalmente su idioma; los stats son el diseño. |
| D. Museo premium | **high-end-visual-design** | Doble-bezel, macro-whitespace y sensación "cara" de agencia. |
| E. Scrapbook cariñoso | **imagegen-frontend-web** | Su arsenal (polaroid scatter, tiras giratorias, composiciones sueltas) genera los comps; el código puede apoyarse en design-taste. |

Complemento transversal: **imagegen-frontend-web** sirve en cualquier dirección para generar una imagen de referencia por sección antes de codificar (una imagen por sección, paleta única).

## 5. Fuentes consultadas

- The Pudding (home + 3 piezas): https://pudding.cool, https://pudding.cool/2026/06/love-story, https://pudding.cool/2026/05/kpop-generations, https://pudding.cool/2026/03/ivf, https://pudding.cool/2026/02/happy-map
- OpenAI plugins – scrollytelling story patterns & scene contracts: https://github.com/openai/plugins/blob/main/plugins/build-web-data-visualization/skills/scrollytelling-and-parallax-data-visualization/references/story-patterns-and-scene-contracts.md
- scrollytelling.ai – timeline examples: https://scrollytelling.ai/timeline-examples/
- YourLovePage – anniversary website: https://www.yourlovepage.com/anniversary-website
- Wegic – couple website builder: https://wegic.ai/ai-website-builder/couple
- Spotify Wrapped: https://www.spotify.com/us/wrapped/
- Dribbble – anniversary-website tag: https://dribbble.com/tags/anniversary-website
- Webflow – made-in-webflow/anniversary: https://webflow.com/made-in-webflow/anniversary
- Skills locales leídas: design-taste-frontend, imagegen-frontend-web, high-end-visual-design, gpt-taste, minimalist-ui, industrial-brutalist-ui (`~/.agents/skills/…/SKILL.md`)

## Recomendación final (shortlist de 3)

1. **"Informe Anual de la Pareja" (Wrapped festivo, dark)** → **gpt-taste** + imagegen-frontend-web para comps. Es el formato que la gente ya asocia con "estadísticas divertidas de una app", perfecto para WhatsApp stats.
2. **"Crónica Editorial en Capítulos"** → **design-taste-frontend**. El marco narrativo más emotivo (primer mensaje → hoy como libro), el que mejor envejece como regalo sorpresa.
3. **"Dossier de Telemetría" (brutalismo)** → **industrial-brutalist-ui**. La más original y con más carisma para una pareja que se toma el dato en broma; ningún template del mercado se parece a esto.
