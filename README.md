# Stockflow

## Prueba de concurrencia y condición de carrera

La sección crítica comprende la consulta del stock, la comprobación de las unidades disponibles y la actualización del inventario. Estas operaciones no están protegidas, por lo que varias cajas pueden tomar decisiones basadas en información que deja de ser válida.

Se ejecuta la aplicación varias veces y se comprueba el stock final. Si varias cajas aceptan pedidos basándose en las mismas existencias iniciales, pueden venderse más unidades de las disponibles y el inventario puede quedar en negativo.

Este comportamiento constituye una condición de carrera, ya que el resultado depende de cómo se intercalan las operaciones de los distintos hilos.