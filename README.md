# Sistema de Inventario y Ventas (Python + SQLite)

# Estudiante: Andrés Felipe Mancilla Santiago

## Parte 1: Analisis y Diseno: Entidades y Atributos

* **Producto**:
  * `id` (INTEGER, Clave Primaria, Autoincremental)
  * `nombre` (TEXT, No nulo)
  * `precio` (REAL, No nulo)
  * `cantidad` (INTEGER, No nulo)

* **Venta**:
  * `id` (INTEGER, Clave Primaria, Autoincremental)
  * `producto_id` (INTEGER, Clave Foranea referenciando a `Producto(id)`)
  * `cantidad` (INTEGER, No nulo)
  * `fecha` (TEXT, Valor por defecto TIMESTAMP actual)

## Descripcion del Software
Es una aplicacion en consola para la gestion de productos y registro de ventas utilizando transacciones relacionales ACID en SQLite para prevenir inconsistencias en el inventario.

## Modelo de Datos (DDL)
- **productos** (`id`, `nombre`, `precio`, `cantidad`)
- **ventas** (`id`, `producto_id`, `cantidad`, `fecha`)

## Funcionamiento de la Transaccion y Rollback
Cuando se registra una venta:
1. Se valida la existencia del producto y la disponibilidad de stock.
2. Se inserta el registro en la tabla `ventas`.
3. Se actualiza el stock en la tabla `productos`.
4. Si ambas operaciones son exitosas, se ejecuta `commit()`.
5. Si ocurre cualquier fallo o interrupcion intermedia, la excepcion ejecuta `rollback()`, dejando los datos intactos.

## Instrucciones de Ejecucion
1. Clonar el repositorio:
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd <NOMBRE_DEL_REPOSITORIO>