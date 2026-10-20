-- Borrado lógico para clientes y productos (MariaDB).
-- Idempotente: se puede ejecutar varias veces sin duplicar nada.
-- Ejecutar con una cuenta administrativa (root) sobre la base ya seleccionada
-- en phpMyAdmin o HeidiSQL (ferreteria_cerpint).

-- 1. Columna activo (1 = vigente, 0 = eliminado lógicamente).
ALTER TABLE clientes
  ADD COLUMN IF NOT EXISTS activo tinyint(1) NOT NULL DEFAULT 1;
ALTER TABLE productos
  ADD COLUMN IF NOT EXISTS activo tinyint(1) NOT NULL DEFAULT 1;

-- 2. Integridad histórica. ventas.cliente_documento y detalles_venta.producto_codigo
--    ya referencian clientes.documento y productos.codigo con ON DELETE RESTRICT,
--    por lo que una fila con historial nunca puede borrarse físicamente.
--    Estos triggers cubren además las filas sin historial: cualquier DELETE directo
--    se rechaza y debe hacerse con UPDATE activo = 0.
DROP TRIGGER IF EXISTS bd_clientes_borrado_logico;
CREATE TRIGGER bd_clientes_borrado_logico
BEFORE DELETE ON clientes
FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Los clientes no se borran: use UPDATE clientes SET activo = 0';

DROP TRIGGER IF EXISTS bd_productos_borrado_logico;
CREATE TRIGGER bd_productos_borrado_logico
BEFORE DELETE ON productos
FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Los productos no se borran: use UPDATE productos SET activo = 0';

-- 3. Consultas que reemplazan al DELETE (los parámetros ? los envía la aplicación).
--    Eliminar (borrado lógico):
--      UPDATE clientes  SET activo = 0 WHERE documento = ? AND activo = 1;
--      UPDATE productos SET activo = 0 WHERE codigo    = ? AND activo = 1;
--    Restaurar:
--      UPDATE clientes  SET activo = 1 WHERE documento = ? AND activo = 0;
--      UPDATE productos SET activo = 1 WHERE codigo    = ? AND activo = 0;
--    Listados operativos (solo vigentes):
--      SELECT * FROM clientes  WHERE activo = 1;
--      SELECT * FROM productos WHERE activo = 1;
--    Historial: NO filtrar por activo, para conservar el vínculo con registros inactivos:
--      SELECT v.id, v.fecha, c.nombre, c.activo
--      FROM ventas v JOIN clientes c ON c.documento = v.cliente_documento;
--      SELECT d.venta_id, p.codigo, p.nombre, p.activo, d.cantidad, d.subtotal
--      FROM detalles_venta d JOIN productos p ON p.codigo = d.producto_codigo;

-- 4. Índices (MariaDB; IF NOT EXISTS los hace idempotentes).
--    Ya existen y cubren las claves foráneas por prefijo izquierdo:
--    ventas.cliente_documento (idx_ventas_cliente_fecha), detalles_venta.venta_id (fk_detalles_venta),
--    pagos_cuentas_por_cobrar.venta_id (idx_pagos_venta_fecha) y permisos_roles.rol_id (rol_id).
CREATE INDEX IF NOT EXISTS idx_detalles_venta_producto ON detalles_venta (producto_codigo);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas (fecha);
CREATE INDEX IF NOT EXISTS idx_pagos_fecha ON pagos_cuentas_por_cobrar (fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_metodo_fecha ON ventas (metodo_pago, fecha);
CREATE INDEX IF NOT EXISTS idx_permisos_roles_rol_modulo ON permisos_roles (rol_id, modulo);

-- 5. Triggers de auditoría (crear, modificar, desactivar) en ventas, productos y clientes.
--    Usuario/rol: variables de sesión @app_usuario y @app_rol si la aplicación las define
--    (SET @app_usuario = 'admin', @app_rol = 'administrador'); si no, el usuario de MariaDB.
--    Ejecutar como root. Si usas el cliente mysql, mantén las líneas DELIMITER.
DELIMITER $$

DROP TRIGGER IF EXISTS ai_clientes_auditoria$$
CREATE TRIGGER ai_clientes_auditoria AFTER INSERT ON clientes FOR EACH ROW
BEGIN
  INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
  VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
          'TRG_CREAR', 'cliente', NEW.documento,
          LEFT(CONCAT('nombre=', NEW.nombre, '; telefono=', COALESCE(NEW.telefono, ''),
                      '; direccion=', COALESCE(NEW.direccion, '')), 2000));
END$$

DROP TRIGGER IF EXISTS au_clientes_auditoria$$
CREATE TRIGGER au_clientes_auditoria AFTER UPDATE ON clientes FOR EACH ROW
BEGIN
  DECLARE v_accion VARCHAR(64);
  DECLARE v_detalle VARCHAR(2000) DEFAULT '';
  IF NOT (OLD.activo <=> NEW.activo) THEN
    SET v_accion = IF(NEW.activo = 0, 'TRG_DESACTIVAR', 'TRG_REACTIVAR');
  ELSE
    SET v_accion = 'TRG_MODIFICAR';
  END IF;
  IF NOT (OLD.nombre <=> NEW.nombre) THEN
    SET v_detalle = CONCAT(v_detalle, 'nombre: ', COALESCE(OLD.nombre, ''), ' -> ', COALESCE(NEW.nombre, ''), '; ');
  END IF;
  IF NOT (OLD.telefono <=> NEW.telefono) THEN
    SET v_detalle = CONCAT(v_detalle, 'telefono: ', COALESCE(OLD.telefono, ''), ' -> ', COALESCE(NEW.telefono, ''), '; ');
  END IF;
  IF NOT (OLD.direccion <=> NEW.direccion) THEN
    SET v_detalle = CONCAT(v_detalle, 'direccion: ', COALESCE(OLD.direccion, ''), ' -> ', COALESCE(NEW.direccion, ''), '; ');
  END IF;
  IF NOT (OLD.activo <=> NEW.activo) THEN
    SET v_detalle = CONCAT(v_detalle, 'activo: ', COALESCE(OLD.activo, ''), ' -> ', COALESCE(NEW.activo, ''), '; ');
  END IF;
  IF v_detalle <> '' THEN
    INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
    VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
            v_accion, 'cliente', NEW.documento, LEFT(v_detalle, 2000));
  END IF;
END$$

DROP TRIGGER IF EXISTS ai_productos_auditoria$$
CREATE TRIGGER ai_productos_auditoria AFTER INSERT ON productos FOR EACH ROW
BEGIN
  INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
  VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
          'TRG_CREAR', 'producto', NEW.codigo,
          LEFT(CONCAT('nombre=', NEW.nombre, '; precio_centavos=', NEW.precio_centavos,
                      '; stock=', NEW.stock, '; stock_minimo=', COALESCE(NEW.stock_minimo, ''),
                      '; proveedor=', COALESCE(NEW.proveedor, ''), '; marca=', COALESCE(NEW.marca, '')), 2000));
END$$

DROP TRIGGER IF EXISTS au_productos_auditoria$$
CREATE TRIGGER au_productos_auditoria AFTER UPDATE ON productos FOR EACH ROW
BEGIN
  DECLARE v_accion VARCHAR(64);
  DECLARE v_detalle VARCHAR(2000) DEFAULT '';
  IF NOT (OLD.activo <=> NEW.activo) THEN
    SET v_accion = IF(NEW.activo = 0, 'TRG_DESACTIVAR', 'TRG_REACTIVAR');
  ELSE
    SET v_accion = 'TRG_MODIFICAR';
  END IF;
  IF NOT (OLD.nombre <=> NEW.nombre) THEN
    SET v_detalle = CONCAT(v_detalle, 'nombre: ', COALESCE(OLD.nombre, ''), ' -> ', COALESCE(NEW.nombre, ''), '; ');
  END IF;
  IF NOT (OLD.precio_centavos <=> NEW.precio_centavos) THEN
    SET v_detalle = CONCAT(v_detalle, 'precio_centavos: ', COALESCE(OLD.precio_centavos, ''), ' -> ', COALESCE(NEW.precio_centavos, ''), '; ');
  END IF;
  IF NOT (OLD.stock <=> NEW.stock) THEN
    SET v_detalle = CONCAT(v_detalle, 'stock: ', COALESCE(OLD.stock, ''), ' -> ', COALESCE(NEW.stock, ''), '; ');
  END IF;
  IF NOT (OLD.stock_minimo <=> NEW.stock_minimo) THEN
    SET v_detalle = CONCAT(v_detalle, 'stock_minimo: ', COALESCE(OLD.stock_minimo, ''), ' -> ', COALESCE(NEW.stock_minimo, ''), '; ');
  END IF;
  IF NOT (OLD.proveedor <=> NEW.proveedor) THEN
    SET v_detalle = CONCAT(v_detalle, 'proveedor: ', COALESCE(OLD.proveedor, ''), ' -> ', COALESCE(NEW.proveedor, ''), '; ');
  END IF;
  IF NOT (OLD.marca <=> NEW.marca) THEN
    SET v_detalle = CONCAT(v_detalle, 'marca: ', COALESCE(OLD.marca, ''), ' -> ', COALESCE(NEW.marca, ''), '; ');
  END IF;
  IF NOT (OLD.codigo_empresa <=> NEW.codigo_empresa) THEN
    SET v_detalle = CONCAT(v_detalle, 'codigo_empresa: ', COALESCE(OLD.codigo_empresa, ''), ' -> ', COALESCE(NEW.codigo_empresa, ''), '; ');
  END IF;
  IF NOT (OLD.activo <=> NEW.activo) THEN
    SET v_detalle = CONCAT(v_detalle, 'activo: ', COALESCE(OLD.activo, ''), ' -> ', COALESCE(NEW.activo, ''), '; ');
  END IF;
  IF v_detalle <> '' THEN
    INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
    VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
            v_accion, 'producto', NEW.codigo, LEFT(v_detalle, 2000));
  END IF;
END$$

DROP TRIGGER IF EXISTS ai_ventas_auditoria$$
CREATE TRIGGER ai_ventas_auditoria AFTER INSERT ON ventas FOR EACH ROW
BEGIN
  INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
  VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
          'TRG_CREAR', 'venta', NEW.id,
          LEFT(CONCAT('cliente=', NEW.cliente_documento, '; total_centavos=', NEW.total_centavos,
                      '; estado=', COALESCE(NEW.estado, ''), '; metodo_pago=', COALESCE(NEW.metodo_pago, '')), 2000));
END$$

-- En ventas, "desactivar" equivale a anular (fecha_anulacion / estado).
DROP TRIGGER IF EXISTS au_ventas_auditoria$$
CREATE TRIGGER au_ventas_auditoria AFTER UPDATE ON ventas FOR EACH ROW
BEGIN
  DECLARE v_accion VARCHAR(64);
  DECLARE v_detalle VARCHAR(2000) DEFAULT '';
  IF OLD.fecha_anulacion IS NULL AND NEW.fecha_anulacion IS NOT NULL THEN
    SET v_accion = 'TRG_ANULAR';
  ELSE
    SET v_accion = 'TRG_MODIFICAR';
  END IF;
  IF NOT (OLD.estado <=> NEW.estado) THEN
    SET v_detalle = CONCAT(v_detalle, 'estado: ', COALESCE(OLD.estado, ''), ' -> ', COALESCE(NEW.estado, ''), '; ');
  END IF;
  IF NOT (OLD.total_centavos <=> NEW.total_centavos) THEN
    SET v_detalle = CONCAT(v_detalle, 'total_centavos: ', COALESCE(OLD.total_centavos, ''), ' -> ', COALESCE(NEW.total_centavos, ''), '; ');
  END IF;
  IF NOT (OLD.metodo_pago <=> NEW.metodo_pago) THEN
    SET v_detalle = CONCAT(v_detalle, 'metodo_pago: ', COALESCE(OLD.metodo_pago, ''), ' -> ', COALESCE(NEW.metodo_pago, ''), '; ');
  END IF;
  IF NOT (OLD.fecha_vencimiento <=> NEW.fecha_vencimiento) THEN
    SET v_detalle = CONCAT(v_detalle, 'fecha_vencimiento: ', COALESCE(OLD.fecha_vencimiento, ''), ' -> ', COALESCE(NEW.fecha_vencimiento, ''), '; ');
  END IF;
  IF NOT (OLD.fecha_anulacion <=> NEW.fecha_anulacion) THEN
    SET v_detalle = CONCAT(v_detalle, 'fecha_anulacion: ', COALESCE(OLD.fecha_anulacion, ''), ' -> ', COALESCE(NEW.fecha_anulacion, ''),
                           '; motivo=', COALESCE(NEW.motivo_anulacion, ''), '; ');
  END IF;
  IF v_detalle <> '' THEN
    INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
    VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
            v_accion, 'venta', NEW.id, LEFT(v_detalle, 2000));
  END IF;
END$$

DELIMITER ;
