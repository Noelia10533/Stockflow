# Stockflow

## 1. Prueba de concurrencia y condición de carrera

La sección crítica comprende la consulta del stock, la comprobación de las unidades disponibles y la actualización del inventario. Estas operaciones no están protegidas, por lo que varias cajas pueden tomar decisiones basadas en información que deja de ser válida.

Se ejecuta la aplicación varias veces y se comprueba el stock final. Si varias cajas aceptan pedidos basándose en las mismas existencias iniciales, pueden venderse más unidades de las disponibles y el inventario puede quedar en negativo.

Este comportamiento constituye una condición de carrera, ya que el resultado depende de cómo se intercalan las operaciones de los distintos hilos.

## 2. Corrección de la condición de carrera mediante Lock

Se ha utilizado threading.Lock() para proteger el acceso al inventario compartido. El bloqueo se crea una sola vez y es utilizado por todas las cajas.

El uso de Lock evita que varias cajas comprueben simultáneamente el mismo stock y acepten pedidos que no pueden satisfacerse. De esta forma, se mantiene la coherencia del inventario compartido.

## 3. Control de concurrencia con Lock y Semaphore

La utilización de Lock y Semaphore permite controlar el acceso a los recursos compartidos y organizar el procesamiento concurrente de los pedidos. El bloqueo evita condiciones de carrera en el inventario, mientras que el semáforo limita el uso simultáneo de las terminales.

## 4. Gestión de reposiciones del almacén con Condition

La utilización de Condition permite coordinar las cajas y el almacén de forma eficiente, evitando la espera activa. Las cajas permanecen bloqueadas mientras no hay suficientes unidades y vuelven a comprobar el inventario cuando reciben una notificación. De esta forma, se mejora la sincronización entre los hilos y se gestiona correctamente el stock compartido.