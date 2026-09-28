# Ferretería Cerpint

Sistema de escritorio para la gestión de una ferretería, desarrollado con Python, CustomTkinter y SQLite.

## Funcionalidades

- Acceso de usuarios.
- Gestión de clientes y productos.
- Registro de ventas y actualización de existencias.
- Notas a crédito, pagos, anulaciones y reposición de inventario.
- Consultas de ventas, clientes y productos.
- Generación de comprobantes PDF.

## Arquitectura

El proyecto sigue una organización MVC por módulo:

- `modulos/`: lógica de clientes, inventario, ventas y consultas.
- `componentes/`: controles reutilizables de interfaz.
- `database/`: conexión, esquema SQLite y reglas de integridad.
- `servicios/`: servicios transversales, como PDF y seguridad.
- `tests/`: pruebas automatizadas.

Todas las operaciones de negocio usan el mismo esquema SQLite: `clientes`, `productos`, `ventas`, `detalles_venta`, `pagos_cuentas_por_cobrar` y `usuarios`.

## Requisitos

- Python 3.12 o superior.
- Paquete `customtkinter`.

## Ejecución

```powershell
python main.py
```

Credenciales de demostración:

```text
Usuario: admin
Clave: 1234
```

La contraseña se almacena mediante PBKDF2-HMAC-SHA256. Las instalaciones que aún tengan la clave inicial en texto plano se actualizan automáticamente al iniciar sesión.

## Pruebas

```powershell
pytest -q
```

## Entrega académica

Antes de entregar, ejecute las pruebas, revise que el inicio de sesión funcione y cree un commit final con una descripción clara de la versión presentada.
