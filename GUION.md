# Guion de exposición · 6 minutos · Equipo 8

El dashboard es el único apoyo. Se avanza con **Siguiente →** o desde el recorrido del sidebar.

**Antes de empezar**, en el sidebar, en «Personaliza la vista»:
- Activen **Texto grande (proyector)** si la sala es grande.
- Dejen el nivel de detalle en **General**. **Técnico** sirve para las preguntas: muestra servicios, definiciones y las consultas SQL abiertas.

El guion dura unos 5:30 y deja 30 segundos de margen. El reparto de voces es una propuesta.

| Sección | Tiempo | Quién | Clic clave |
|---|---|---|---|
| 1 · De qué trata | 0:00 – 0:50 | Nicolás | Mover el control de minutos; «¿Qué es un proceso?» si hace falta |
| 2 · Por qué importa | 0:50 – 1:50 | José Alejandro | «¿Qué significa un solo oferente?» si hace falta; bajar a la matriz |
| 3 · Objetivo | 1:50 – 2:20 | José Alejandro | Ninguno (o un objetivo si preguntan) |
| 4 · Resultados | 2:20 – 3:20 | David | Recorrer las cuatro tarjetas; «¿Cómo lo medimos?» si preguntan |
| 5 · Arquitectura y metodología | 3:20 – 4:40 | Juan Diego → Jacobo | Etapas del diagrama: Oro, Modelo, Este dashboard |
| 6 · Conclusiones | 4:40 – 5:30 | Juan Diego | Recorrer problema → solución → resultado |

---

## 1 · De qué trata · Nicolás

> "El Estado colombiano compra de todo: medicamentos, obras, computadores. Casi todas esas compras se publican en SECOP II, y cada día hay unos **2.000 procesos abiertos**. Y cada año son más: los procesos publicados se duplicaron, de **44 mil en 2020 a 98 mil en 2025**."

👉 **Mover el control de minutos** (a la derecha) de 3 a 5:
> "Si una persona tarda 5 minutos en leer cada proceso, revisarlos todos le tomaría **más de 160 horas al día**. Una mipyme no puede."

👉 Señalar **«En resumen»**:
> "Muchas oportunidades se pierden y cada vez menos empresas compiten por cada contrato. Por eso construimos un *Netflix de contratos públicos*: cada mañana, **38.500 empresas** reciben dos listas, una según su historial y otra con oportunidades que normalmente no verían, cada proceso con su **probabilidad de ganar**."

👉 Si el público no conoce SECOP, abrir **«¿Qué es un proceso?»**: "un proceso es el anuncio con el que una entidad del Estado avisa que quiere comprar algo, como una oferta de trabajo pero para comprar". → **Siguiente**.

## 2 · Por qué importa · José Alejandro

> "¿Por qué importa? Porque cada vez compiten menos empresas. Un proceso tiene **un solo oferente** cuando solo una empresa se presentó, y entonces el Estado no tiene con qué comparar precios."

👉 Si el público no lo tiene claro, abrir **«¿Qué significa un solo oferente?»**.

> "Esta gráfica muestra ese porcentaje, y sube en las cinco modalidades. En mínima cuantía, la más usada, pasó del **27 % al 44 %**. En régimen especial ya va en **68 %**. Sumando todas, el **47 %** de los procesos de este año tuvo un solo oferente."

👉 Bajar a **«Dónde está el problema»**:
> "En la matriz el color se oscurece hacia la derecha en todas las modalidades. Y a la derecha, en números: de **60.702 procesos** que recibieron ofertas este año, **28.653** tuvieron un solo oferente. Solo en mínima cuantía, donde están las mipymes, son **16.629 de 38.208**."

👉 Opcional: pestaña **«Ofertas por proceso»**: "y cada proceso recibe menos ofertas, de 4,2 a 3,3 en mínima cuantía". → **Siguiente**.

## 3 · Objetivo · José Alejandro

> "Nuestro objetivo es recomendar a cada empresa, **todos los días y sin intervención manual**, los procesos donde tiene interés y opción de ganar. Lo dividimos en cuatro objetivos, uno por área del equipo, y cada uno muestra qué entregó."

👉 Señalar las cuatro tarjetas. → **Siguiente**.

## 4 · Resultados · David

> "¿Lo logramos? Antes de contarles cómo lo hicimos, revisamos cada parte del objetivo con datos reales."

👉 Recorrer las **cuatro tarjetas** de izquierda a derecha:
> "**A cada empresa:** el 17 de noviembre, **38.614 empresas** recibieron sus listas, con unos 9 procesos cada una. **Todos los días:** **7 de 7 días** con listas publicadas. **Donde tiene interés:** de **2.205 ofertas reales** que hicieron las empresas esa semana, **1.286** —6 de cada 10— eran procesos que ya les habíamos recomendado. **Y opción de ganar:** la probabilidad tiene un error promedio de **medio punto**: si dice 20 %, la empresa gana más o menos 2 de cada 10 veces."

👉 Señalar las **dos barras de la izquierda**:
> "Y en la vida real acierta igual que en la prueba: **58 %** frente a **57 %**. El modelo no empeoró al salir a producción."

👉 Señalar la **gráfica de la derecha**:
> "Además, el modelo vale la pena: encuentra **11 procesos más de cada 100** que un filtro simple."

👉 Bajar a **«¿Cuánto tiempo le ahorra a una empresa?»**:
> "En la práctica: si leer un proceso toma 3 minutos, revisar los 2.000 procesos abiertos serían **100 horas al día**. Con el recomendador, la empresa lee sus **18 procesos** en **menos de una hora**, y ahí ya están 6 de cada 10 a los que termina presentándose. Es una estimación con ese supuesto, no una medición de uso."

👉 Si preguntan cómo se midió, abrir **«¿Cómo lo medimos?»**. → **Siguiente**.

## 5 · Arquitectura y metodología · Juan Diego → Jacobo

**Juan Diego (≈ 40 s)**, con el diagrama en «Todo»:
> "¿Cómo logramos esto? Esta es la arquitectura en AWS. Los datos entran arriba a la izquierda desde datos.gov.co y las recomendaciones salen abajo a la izquierda hacia las empresas."

👉 **Clic en la etapa «Oro»**:
> "Leímos **10,6 millones de filas** y quedaron **625.625 procesos únicos**, porque SECOP publica cada proceso una vez por versión. Bronce guarda los datos como llegan, plata los limpia y oro deja tablas listas para el modelo y la analítica, sobre Iceberg, con versiones."

👉 **Clic en «Este dashboard»**:
> "Y este mismo dashboard se construyó consultando esas tablas de oro con Athena."

**Jacobo (≈ 40 s)**, 👉 **clic en «Modelo»** y luego en **«Publicación»**:
> "Recomendar no es puntuar todo: serían **97 millones de parejas al día**. Primero recuperamos **150 candidatos por empresa** y luego un modelo los ordena. Todo corre solo a las 7:30, termina en **59 minutos** y cuesta **USD 1,6 por noche**. Si algo falla, no se publica nada y llega una alerta."

> Tip: también se puede hacer clic directamente sobre un servicio del diagrama.

→ **Siguiente**.

## 6 · Conclusiones · Juan Diego

> "Para cerrar, el proyecto en tres pasos."

👉 Recorrer las tres columnas de izquierda a derecha:
> "**El problema:** los procesos con un solo oferente pasaron del **28 % al 47 %**; cada vez compiten menos empresas. **La solución:** en vez de revisar **2.000 procesos** al día, cada empresa recibe sus **18**. **El resultado:** **6 de cada 10** ofertas reales ya estaban en esas listas."

👉 Señalar la frase amarilla y las tres tarjetas de **«Lo que logramos»**:
> "Construimos un sistema que ya funciona y atiende a **38.614 empresas** cada mañana, hecho solo con datos abiertos que cualquiera puede verificar. Si más empresas encuentran los procesos que les sirven, hay más competencia y el Estado compra mejor. Gracias."

👉 Terminar en esta pantalla y abrir preguntas. Si preguntan por dificultades, abrir **«Retos de los datos que superamos»**; por limitaciones, **«Limitaciones y trabajo futuro»**.

---

## Preguntas probables

Para responderlas, cambien el sidebar a **Técnico**.

- **¿De dónde salen las gráficas?** De tablas de la capa oro (`mercado_mensual`, `desempeno_recomendaciones` y `calidad_fuente`), consultadas con Athena. En modo técnico, la sección 5 muestra las consultas y una muestra de los datos.
- **¿Se rechazaron 10 millones de filas?** No. La mayoría son versiones repetidas del mismo proceso; plata deja una fila por proceso. Los rechazos por errores son pocos y quedan registrados con su motivo.
- **¿Qué es el «filtro simple»?** La primera etapa del sistema, que escoge 150 candidatos parecidos sin ordenarlos con el modelo. En lenguaje técnico es la referencia «solo recuperación».
- **¿Por qué solo una semana?** El sistema empezó a correr en producción el 11 de noviembre. En modo Técnico la gráfica muestra el detalle día a día.
- **¿El ahorro de tiempo es medido?** No: es una estimación. Supone el mismo tiempo de lectura por proceso con y sin el sistema. Los 18 procesos por empresa sí salen de los datos (unos 9 en cada lista).
- **¿Y Precision, Recall y NDCG?** Cambien a modo Técnico y abran «¿Cómo lo medimos?»: ahí está la tabla con las métricas.
- **¿Por qué no usan el precio ofertado?** SECOP no lo publica. Es la principal limitación.
- **¿Cómo evitan la fuga de información?** Cada variable se calcula solo con lo que se sabía antes de la fecha de corte.
- **¿Por qué solo muestran la lista 1 en producción?** La lista 2 casi no coincide con las ofertas reales (alrededor del 1 %), y eso es lo esperado: muestra procesos que la empresa normalmente no vería.
- **¿Está calibrada P(gana) en producción?** En la prueba sí (error de 0,0053). En producción todavía hay muy pocos procesos adjudicados para medirlo. El 12 de noviembre esperábamos 2,2 victorias y hubo 2.
- **¿Por qué esos colores?** Son los azules institucionales del KIT UI de GOV.CO, el sistema de diseño de los portales del Estado, como datos.gov.co.
