-- Esquema compatible con roles y permisos_roles usados por la aplicación.
-- Ejecutar una vez con una cuenta administrativa de MariaDB.
USE ferreteria_cerpint;

CREATE TABLE IF NOT EXISTS roles (
  id int NOT NULL AUTO_INCREMENT,
  nombre varchar(50) NOT NULL,
  descripcion text DEFAULT NULL,
  activo tinyint(1) DEFAULT 1,
  fecha_creacion timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_roles_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS permisos_roles (
  id int NOT NULL AUTO_INCREMENT,
  rol_id int NOT NULL,
  modulo varchar(50) NOT NULL,
  puede_ver tinyint(1) DEFAULT 0,
  puede_crear tinyint(1) DEFAULT 0,
  puede_editar tinyint(1) DEFAULT 0,
  puede_eliminar tinyint(1) DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_permisos_roles_modulo (rol_id, modulo),
  CONSTRAINT fk_permisos_roles_rol
    FOREIGN KEY (rol_id) REFERENCES roles (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO roles (nombre, descripcion, activo) VALUES
  ('administrador', 'Acceso total al sistema', 1),
  ('almacenista', 'Acceso de lectura a inventario y clientes', 1),
  ('consultor', 'Acceso solo a consultas y reportes', 1);

-- Permite que usuarios.rol use roles distintos de administrador/consultor.
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS chk_usuarios_rol;

GRANT SELECT, INSERT, UPDATE, DELETE
  ON ferreteria_cerpint.roles TO 'ferreteria_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE
  ON ferreteria_cerpint.permisos_roles TO 'ferreteria_app'@'localhost';
