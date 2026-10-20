import sqlite3

DatabaseName = "inventario.db"

def ObtenerConexion():
    conexion = sqlite3.connect(DatabaseName)
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def InicializarBaseDatos():
    conexion = ObtenerConexion()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
        )
    """)
    conexion.commit()
    conexion.close()

def RegistrarProducto():
    print("\n--- Registrar Producto ---")
    NombreProducto = input("Nombre del producto: ").strip()
    try:
        PrecioProducto = float(input("Precio: "))
        CantidadProducto = int(input("Cantidad disponible: "))
        if PrecioProducto < 0 or CantidadProducto < 0:
            print("El precio y la cantidad deben ser valores no negativos.")
            return
    except ValueError:
        print("Entrada invalida. Ingrese valores numericos correctos.")
        return

    ConexionDB = ObtenerConexion()
    CursorDB = ConexionDB.cursor()
    CursorDB.execute(
        "INSERT INTO productos (nombre, precio, cantidad) VALUES (?, ?, ?)",
        (NombreProducto, PrecioProducto, CantidadProducto)
    )
    ConexionDB.commit()
    ConexionDB.close()
    print(f"Producto '{NombreProducto}' registrado exitosamente.")

def ConsultarProductos():
    print("\n--- Listado de Productos ---")
    ConexionDB = ObtenerConexion()
    CursorDB = ConexionDB.cursor()
    CursorDB.execute("SELECT id, nombre, precio, cantidad FROM productos")
    ListaProductos = CursorDB.fetchall()
    ConexionDB.close()

    if not ListaProductos:
        print("No hay productos registrados.")
        return

    print(f"{'ID':<5} | {'Nombre':<25} | {'Precio':<10} | {'Stock':<8}")
    print("-" * 55)
    for Prod in ListaProductos:
        print(f"{Prod[0]:<5} | {Prod[1]:<25} | ${Prod[2]:<9.2f} | {Prod[3]:<8}")

def ActualizarProducto():
    print("\n--- Actualizar Producto ---")
    try:
        ProductoId = int(input("ID del producto a actualizar: "))
    except ValueError:
        print("ID invalido.")
        return

    ConexionDB = ObtenerConexion()
    CursorDB = ConexionDB.cursor()
    CursorDB.execute("SELECT nombre, precio, cantidad FROM productos WHERE id = ?", (ProductoId,))
    ProductoEncontrado = CursorDB.fetchone()

    if not ProductoEncontrado:
        print("Producto no encontrado.")
        ConexionDB.close()
        return

    print(f"Producto seleccionado: {ProductoEncontrado[0]} (Precio: ${ProductoEncontrado[1]}, Stock: {ProductoEncontrado[2]})")
    try:
        NuevoPrecioStr = input("Nuevo precio (dejar en blanco para mantener): ").strip()
        NuevaCantidadStr = input("Nueva cantidad (dejar en blanco para mantener): ").strip()

        PrecioVal = float(NuevoPrecioStr) if NuevoPrecioStr else ProductoEncontrado[1]
        CantidadVal = int(NuevaCantidadStr) if NuevaCantidadStr else ProductoEncontrado[2]

        CursorDB.execute(
            "UPDATE productos SET precio = ?, cantidad = ? WHERE id = ?",
            (PrecioVal, CantidadVal, ProductoId)
        )
        ConexionDB.commit()
        print("Producto actualizado correctamente.")
    except ValueError:
        print("Error en los datos ingresados.")
    finally:
        ConexionDB.close()

def EliminarProducto():
    print("\n--- Eliminar Producto ---")
    try:
        ProductoId = int(input("ID del producto a eliminar: "))
    except ValueError:
        print("ID invalido.")
        return

    ConexionDB = ObtenerConexion()
    CursorDB = ConexionDB.cursor()
    try:
        CursorDB.execute("DELETE FROM productos WHERE id = ?", (ProductoId,))
        if CursorDB.rowcount > 0:
            ConexionDB.commit()
            print("Producto eliminado correctamente.")
        else:
            print("No se encontro un producto con ese ID.")
    except sqlite3.IntegrityError:
        print("No se puede eliminar el producto porque tiene ventas asociadas.")
    finally:
        ConexionDB.close()

def RegistrarVenta(ForzarError=False):
    print("\n--- Registrar Venta ---")
    try:
        ProductoId = int(input("ID del producto: "))
        CantidadVenta = int(input("Cantidad a vender: "))
        if CantidadVenta <= 0:
            print("La cantidad a vender debe ser mayor a cero.")
            return
    except ValueError:
        print("Entrada invalida.")
        return

    ConexionDB = ObtenerConexion()
    CursorDB = ConexionDB.cursor()

    try:
        CursorDB.execute("SELECT nombre, cantidad FROM productos WHERE id = ?", (ProductoId,))
        ProductoData = CursorDB.fetchone()

        if not ProductoData:
            print("Error: El producto no existe.")
            return

        NombreProd, StockActual = ProductoData

        if StockActual < CantidadVenta:
            print(f"Error: Stock insuficiente. Stock actual: {StockActual}")
            return

        CursorDB.execute(
            "INSERT INTO ventas (producto_id, cantidad) VALUES (?, ?)",
            (ProductoId, CantidadVenta)
        )

        if ForzarError:
            raise Exception("Simulacion de fallo en el sistema antes de actualizar inventario.")

        NuevoStock = StockActual - CantidadVenta
        CursorDB.execute(
            "UPDATE productos SET cantidad = ? WHERE id = ?",
            (NuevoStock, ProductoId)
        )

        ConexionDB.commit()
        print(f"Venta registrada exitosamente. Se vendieron {CantidadVenta} unidades de '{NombreProd}'.")

    except Exception as ExcepcionError:
        ConexionDB.rollback()
        print(f"Transaccion cancelada (ROLLBACK ejecutado). Causa del error: {ExcepcionError}")
    finally:
        ConexionDB.close()

def MostrarHistorialVentas():
    print("\n--- Historial de Ventas ---")
    ConexionDB = ObtenerConexion()
    CursorDB = ConexionDB.cursor()
    QuerySql = """
        SELECT v.id, p.nombre, v.cantidad, v.fecha
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        ORDER BY v.fecha DESC
    """
    CursorDB.execute(QuerySql)
    ListaVentas = CursorDB.fetchall()
    ConexionDB.close()

    if not ListaVentas:
        print("No hay ventas registradas.")
        return

    print(f"{'ID Venta':<10} | {'Producto':<25} | {'Cantidad':<10} | {'Fecha/Hora':<20}")
    print("-" * 72)
    for VentaItem in ListaVentas:
        print(f"{VentaItem[0]:<10} | {VentaItem[1]:<25} | {VentaItem[2]:<10} | {VentaItem[3]:<20}")

def MenuPrincipal():
    InicializarBaseDatos()
    while True:
        print("\n- - - - - - - - - - - - - - - - - -")
        print("   Sistema de Inventario y Ventas")
        print("- - - - - - - - - - - - - - - - - -")
        print("1. Registrar Producto")
        print("2. Consultar Productos")
        print("3. Actualizar Producto")
        print("4. Eliminar Producto")
        print("5. Registrar Venta")
        print("6. Mostrar Historial de Ventas")
        print("7. Rollback")
        print("8. Salir")
        
        OpcionMenu = input("Seleccione una opcion (1-8): ").strip()

        if OpcionMenu == "1":
            RegistrarProducto()
        elif OpcionMenu == "2":
            ConsultarProductos()
        elif OpcionMenu == "3":
            ActualizarProducto()
        elif OpcionMenu == "4":
            EliminarProducto()
        elif OpcionMenu == "5":
            RegistrarVenta(ForzarError=False)
        elif OpcionMenu == "6":
            MostrarHistorialVentas()
        elif OpcionMenu == "7":
            RegistrarVenta(ForzarError=True)
        elif OpcionMenu == "8":
            print("Saliendo del programa...")
            break
        else:
            print("Opcion invalida. Intente de nuevo.")

if __name__ == "__main__":
    MenuPrincipal()