/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.20-13.0.2-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: ferreteria_cerpint
-- ------------------------------------------------------
-- Server version	13.0.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `auditoria`
--

DROP TABLE IF EXISTS `auditoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditoria` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL DEFAULT current_timestamp(),
  `usuario` varchar(64) NOT NULL,
  `rol` varchar(32) NOT NULL,
  `accion` varchar(64) NOT NULL,
  `entidad` varchar(64) NOT NULL,
  `referencia` varchar(128) NOT NULL,
  `detalle` varchar(2000) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_auditoria_fecha` (`fecha`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditoria`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `auditoria` WRITE;
/*!40000 ALTER TABLE `auditoria` DISABLE KEYS */;
INSERT INTO `auditoria` VALUES
(1,'2026-09-28 09:55:11','admin','administrador','ACTUALIZAR','venta','31','Estado: A Credito'),
(2,'2026-09-29 20:27:21','Sistema','sistema','NORMALIZAR','producto','SOC-004','Eliminado soc-004 y renombrado SOC-004 a HIST-SOC-004; detalles históricos reasignados.'),
(3,'2026-10-19 00:29:58','admin','administrador','ACTIVAR','producto','AAAA-0005',''),
(4,'2026-10-19 00:30:08','admin','administrador','DESACTIVAR','producto','AAAA-0001',''),
(5,'2026-10-19 00:30:12','admin','administrador','DESACTIVAR','producto','AAAA-0000',''),
(6,'2026-10-19 00:30:19','admin','administrador','ACTIVAR','producto','AAAA-0001',''),
(7,'2026-10-19 00:30:22','admin','administrador','ACTIVAR','producto','AAAA-0000',''),
(8,'2026-10-19 00:30:37','admin','administrador','DESACTIVAR','cliente','J-409876541',''),
(9,'2026-10-19 00:44:35','admin','administrador','DESACTIVAR','cliente','V-19555666',''),
(10,'2026-10-19 00:44:48','admin','administrador','ACTIVAR','cliente','V-19555666',''),
(11,'2026-10-19 00:46:25','admin','administrador','CREAR','venta','32','Total: 74850 centavos'),
(12,'2026-10-19 10:19:53','admin','administrador','DESACTIVAR','producto','AAAA-0001',''),
(13,'2026-10-19 10:20:05','admin','administrador','DESACTIVAR','cliente','V-12345678',''),
(14,'2026-10-19 10:20:44','admin','administrador','CREAR','venta','33','Total: 1400 centavos'),
(15,'2026-10-19 12:04:30','admin','administrador','CREAR','venta','34','Total: 27650 centavos'),
(16,'2026-10-20 11:14:29','admin','administrador','CREAR','venta','35','Total: 1580 centavos'),
(17,'2026-10-20 12:18:39','admin','administrador','ACTIVAR','cliente','V-12345678',''),
(18,'2026-10-20 13:05:18','admin','administrador','ACTUALIZAR','producto','AAAA-0005','Taladro Percutor 1/2 Dewalt 800W'),
(19,'2026-10-20 13:06:58','admin','administrador','ACTUALIZAR','producto','AAAA-0003','Tubo PVC 1/2 pulgada Pavco 6m'),
(20,'2026-10-20 13:07:17','admin','administrador','ACTUALIZAR','producto','AAAA-0000','Martillo De Uña 16Oz Stanley'),
(21,'2026-10-20 13:08:26','admin','administrador','ACTUALIZAR','producto','AAAA-0000','Martillo De Uña 16Oz Stanley'),
(22,'2026-10-20 13:08:50','admin','administrador','ACTUALIZAR','producto','AAAA-0007','Llave Ajustable 10 pulgadas Pretul');
/*!40000 ALTER TABLE `auditoria` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `documento` varchar(64) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `telefono` varchar(64) DEFAULT NULL,
  `direccion` varchar(500) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `documento` (`documento`),
  CONSTRAINT `chk_clientes_datos` CHECK (char_length(trim(`documento`)) > 0 and char_length(trim(`nombre`)) > 0)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES
(1,'V-18564029-5','Yohan Manuel Moreno Molina','0414-7138030','Arjona',1),
(2,'V-12345678','Juan Pérez','0414-1234567','Av. Principal Nro 12',1),
(3,'V-87654321','María Delgado','0424-7654321','Calle 5 de Mayo #45',1),
(4,'J-301234560','Constructora Los Andes C.A.','0276-3334455','Zona Industrial San José',1),
(5,'V-19555666','Carlos Rodríguez','0412-5556677','Barrio Sucre Sector B',1),
(6,'J-409876541','Ferretería La Solución S.R.L.','0276-9998877','Centro Comercial Plaza',1);
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER ai_clientes_auditoria AFTER INSERT ON clientes FOR EACH ROW
BEGIN
  INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
  VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
          'TRG_CREAR', 'cliente', NEW.documento,
          LEFT(CONCAT('nombre=', NEW.nombre, '; telefono=', COALESCE(NEW.telefono, ''),
                      '; direccion=', COALESCE(NEW.direccion, '')), 2000));
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER au_clientes_auditoria AFTER UPDATE ON clientes FOR EACH ROW
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
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER bd_clientes_borrado_logico
BEFORE DELETE ON clientes
FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Los clientes no se borran: use UPDATE clientes SET activo = 0' 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `demo_seed_runs`
--

DROP TABLE IF EXISTS `demo_seed_runs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `demo_seed_runs` (
  `lote` varchar(128) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`lote`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `demo_seed_runs`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `demo_seed_runs` WRITE;
/*!40000 ALTER TABLE `demo_seed_runs` DISABLE KEYS */;
INSERT INTO `demo_seed_runs` VALUES
('consultas_notas_20_v1','2026-09-27 23:13:09');
/*!40000 ALTER TABLE `demo_seed_runs` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `detalles_venta`
--

DROP TABLE IF EXISTS `detalles_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalles_venta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `venta_id` int(11) NOT NULL,
  `producto_codigo` varchar(64) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(13,2) NOT NULL,
  `subtotal` decimal(13,2) NOT NULL,
  `precio_unitario_centavos` bigint(20) NOT NULL,
  `subtotal_centavos` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_detalles_venta` (`venta_id`),
  KEY `idx_detalles_producto_venta` (`producto_codigo`,`venta_id`),
  KEY `idx_detalles_venta_producto` (`producto_codigo`),
  CONSTRAINT `fk_detalles_producto` FOREIGN KEY (`producto_codigo`) REFERENCES `productos` (`codigo`),
  CONSTRAINT `fk_detalles_venta` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`),
  CONSTRAINT `chk_detalles_datos` CHECK (`cantidad` > 0 and `precio_unitario` >= 0 and `subtotal` >= 0 and `precio_unitario_centavos` >= 0 and `subtotal_centavos` >= 0 and `precio_unitario_centavos` = round(`precio_unitario` * 100,0) and `subtotal_centavos` = round(`subtotal` * 100,0) and `subtotal_centavos` = `cantidad` * `precio_unitario_centavos`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_venta`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `detalles_venta` WRITE;
/*!40000 ALTER TABLE `detalles_venta` DISABLE KEYS */;
INSERT INTO `detalles_venta` VALUES
(1,1,'AAAA-0005',2,85.00,170.00,8500,17000),
(2,2,'AAAA-0006',4,1.80,7.20,180,720),
(3,3,'AAAA-0005',4,85.00,340.00,8500,34000),
(4,4,'AAAA-0006',12,1.80,21.60,180,2160),
(5,5,'AAAA-0002',5,3.50,17.50,350,1750),
(6,5,'AAAA-0006',20,1.80,36.00,180,3600),
(7,6,'AAAA-0005',4,85.00,340.00,8500,34000),
(8,6,'AAAA-0006',2,1.80,3.60,180,360),
(9,7,'AAAA-0006',20,1.80,36.00,180,3600),
(10,7,'AAAA-0008',10,1.20,12.00,120,1200),
(11,8,'AAAA-0008',10,1.20,12.00,120,1200),
(12,8,'AAAA-0000',2,12.50,25.00,1250,2500),
(13,9,'AAAA-0006',2,1.80,3.60,180,360),
(14,10,'AAAA-0000',2,12.50,25.00,1250,2500),
(15,11,'AAAA-0006',1,1.80,1.80,180,180),
(16,12,'AAAA-0006',1,1.80,1.80,180,180),
(17,13,'AAAA-0006',1,1.80,1.80,180,180),
(18,14,'AAAA-0006',1,1.80,1.80,180,180),
(19,15,'AAAA-0006',1,1.80,1.80,180,180),
(20,16,'AAAA-0006',1,1.80,1.80,180,180),
(21,17,'AAAA-0006',1,1.80,1.80,180,180),
(22,18,'AAAA-0006',1,1.80,1.80,180,180),
(23,19,'AAAA-0006',1,1.80,1.80,180,180),
(24,20,'AAAA-0006',1,1.80,1.80,180,180),
(25,21,'AAAA-0006',1,1.80,1.80,180,180),
(26,22,'AAAA-0006',1,1.80,1.80,180,180),
(27,23,'AAAA-0006',1,1.80,1.80,180,180),
(28,24,'AAAA-0006',1,1.80,1.80,180,180),
(29,25,'AAAA-0006',1,1.80,1.80,180,180),
(30,26,'AAAA-0006',1,1.80,1.80,180,180),
(31,27,'AAAA-0006',1,1.80,1.80,180,180),
(32,28,'AAAA-0006',1,1.80,1.80,180,180),
(33,29,'AAAA-0006',1,1.80,1.80,180,180),
(34,30,'AAAA-0006',1,1.80,1.80,180,180),
(35,31,'AAAA-0004',5,9.50,47.50,950,4750),
(36,31,'AAAA-0006',2,1.80,3.60,180,360),
(37,31,'AAAA-0001',5,18.00,90.00,1800,9000),
(38,32,'AAAA-0001',2,18.00,36.00,1800,3600),
(39,32,'AAAA-0004',75,9.50,712.50,950,71250),
(40,33,'AAAA-0007',2,7.00,14.00,700,1400),
(41,34,'AAAA-0007',2,7.00,14.00,700,1400),
(42,34,'AAAA-0000',21,12.50,262.50,1250,26250),
(43,35,'AAAA-0006',1,1.80,1.80,180,180),
(44,35,'AAAA-0007',2,7.00,14.00,700,1400);
/*!40000 ALTER TABLE `detalles_venta` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `pagos_cuentas_por_cobrar`
--

DROP TABLE IF EXISTS `pagos_cuentas_por_cobrar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos_cuentas_por_cobrar` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `venta_id` int(11) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT current_timestamp(),
  `monto` decimal(13,2) NOT NULL,
  `metodo_pago` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_pagos_venta_fecha` (`venta_id`,`fecha`),
  KEY `idx_pagos_fecha` (`fecha`),
  CONSTRAINT `fk_pagos_venta` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`),
  CONSTRAINT `chk_pagos_monto` CHECK (`monto` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos_cuentas_por_cobrar`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `pagos_cuentas_por_cobrar` WRITE;
/*!40000 ALTER TABLE `pagos_cuentas_por_cobrar` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos_cuentas_por_cobrar` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `permisos_roles`
--

DROP TABLE IF EXISTS `permisos_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisos_roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rol_id` int(11) NOT NULL,
  `modulo` varchar(50) NOT NULL,
  `puede_ver` tinyint(1) DEFAULT 0,
  `puede_crear` tinyint(1) DEFAULT 0,
  `puede_editar` tinyint(1) DEFAULT 0,
  `puede_eliminar` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_permisos_roles_rol_modulo` (`rol_id`,`modulo`),
  CONSTRAINT `1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos_roles`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `permisos_roles` WRITE;
/*!40000 ALTER TABLE `permisos_roles` DISABLE KEYS */;
INSERT INTO `permisos_roles` VALUES
(13,2,'inventario',1,0,0,0),
(14,2,'clientes',1,0,0,0),
(15,2,'ventas',0,0,0,0),
(16,2,'consultas',0,0,0,0),
(33,6,'inventario',0,0,0,0),
(34,6,'clientes',1,0,0,0),
(35,6,'ventas',1,1,0,0),
(36,6,'consultas',0,0,0,0);
/*!40000 ALTER TABLE `permisos_roles` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(64) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `precio` decimal(13,2) NOT NULL,
  `precio_centavos` bigint(20) NOT NULL,
  `stock` int(11) NOT NULL,
  `stock_minimo` decimal(13,3) NOT NULL DEFAULT 0.000,
  `proveedor` varchar(255) DEFAULT NULL,
  `marca` varchar(255) DEFAULT NULL,
  `codigo_empresa` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  CONSTRAINT `chk_productos_datos` CHECK (char_length(trim(`codigo`)) > 0 and char_length(trim(`nombre`)) > 0 and `precio` >= 0 and `precio_centavos` >= 0 and `precio_centavos` = round(`precio` * 100,0) and `stock` >= 0 and `stock_minimo` >= 0),
  CONSTRAINT `chk_productos_codigo` CHECK (cast(`codigo` as char charset binary) regexp '^[A-Z]{4}-[0-9]{4}$')
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES
(2,'AAAA-0000','Martillo De Uña 16Oz Stanley',12.50,1250,2,0.000,'DA HAI','FONTOR','',1),
(3,'AAAA-0001','Juego De Alicates 3 Pzas Truper',18.00,1800,8,0.000,'DA HAI','FONTOR',NULL,0),
(4,'AAAA-0002','Destornillador de Estría 1/4x4',3.50,350,45,0.000,'DA HAI','FONTOR',NULL,1),
(5,'AAAA-0003','Tubo PVC 1/2 pulgada Pavco 6m',8.20,820,1000,0.000,'FERCOVEN','GRINACA','',1),
(6,'AAAA-0004','Saco de Cemento Portland 42.5kg',9.50,950,0,0.000,'EDIL','CATATUMBO',NULL,1),
(7,'AAAA-0005','Taladro Percutor 1/2 Dewalt 800W',85.00,8500,100,0.000,'TOLSEN','TOLSEN','',1),
(8,'AAAA-0006','Disco De Corte Para Metal 4-1/2',1.80,180,217,0.000,'MAXCAN','COVO',NULL,1),
(9,'AAAA-0007','Llave Ajustable 10 pulgadas Pretul',7.00,700,24,50.000,'LITANI','EXCEL','',1),
(10,'AAAA-0008','Socate',1.20,120,80,0.000,'LUMISTAR','LUMISTAR',NULL,1);
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `bi_productos_codigo_cerpint` BEFORE INSERT ON productos
                    FOR EACH ROW
                    BEGIN
                        IF BINARY NEW.codigo NOT REGEXP '^[A-Z]{4}-[0-9]{4}$' THEN
                            SIGNAL SQLSTATE '45000'
                                SET MESSAGE_TEXT = 'El código debe tener formato AAAA-0000';
                        END IF;
                    END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER ai_productos_auditoria AFTER INSERT ON productos FOR EACH ROW
BEGIN
  INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
  VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
          'TRG_CREAR', 'producto', NEW.codigo,
          LEFT(CONCAT('nombre=', NEW.nombre, '; precio_centavos=', NEW.precio_centavos,
                      '; stock=', NEW.stock, '; stock_minimo=', COALESCE(NEW.stock_minimo, ''),
                      '; proveedor=', COALESCE(NEW.proveedor, ''), '; marca=', COALESCE(NEW.marca, '')), 2000));
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `bu_productos_codigo_cerpint` BEFORE UPDATE ON productos
                    FOR EACH ROW
                    BEGIN
                        IF BINARY NEW.codigo NOT REGEXP '^[A-Z]{4}-[0-9]{4}$' THEN
                            SIGNAL SQLSTATE '45000'
                                SET MESSAGE_TEXT = 'El código debe tener formato AAAA-0000';
                        END IF;
                    END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER au_productos_auditoria AFTER UPDATE ON productos FOR EACH ROW
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
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER bd_productos_borrado_logico
BEFORE DELETE ON productos
FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Los productos no se borran: use UPDATE productos SET activo = 0' 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `fecha_creacion` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES
(1,'administrador','Acceso total al sistema',1,'2026-10-20 14:12:46'),
(2,'almacenista','Acceso de lectura a inventario y clientes',1,'2026-10-20 14:12:46'),
(3,'consultor','Acceso solo a consultas y reportes',1,'2026-10-20 14:12:46'),
(6,'vendedor','vendedor',1,'2026-10-20 14:48:28');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario` varchar(64) NOT NULL,
  `clave` varchar(255) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `rol` varchar(32) NOT NULL DEFAULT 'consultor',
  `correo` varchar(255) DEFAULT NULL,
  `codigo_recuperacion` varchar(255) DEFAULT NULL,
  `recuperacion_expira_en` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario` (`usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'admin','pbkdf2_sha256$600000$851e83bc74b1faf62c6c381fdf3d55a5$7d5a14a0368f6514029c16d284be0249dab62e9461d88c7565f6160dc13335b2','Administrador General','administrador','yohanm3@gmail.com',NULL,NULL),
(2,'consultor','pbkdf2_sha256$600000$3e29dad0b377fe801075ae3d51db45fe$bed09c8893cc29e7a2106f5548629d49d6b77e68243654fa8fb1c59251ae8886','Consultor','consultor','ym3test@gmail.com',NULL,NULL),
(3,'ven1','pbkdf2_sha256$600000$48cde770e998f82394b2b024ef3159cb$9231861bd123c5a98e3ceb62090cde5bed21ee72b7b9695d77b31c05232989ba','Pedro Perez','vendedor',NULL,NULL,NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL DEFAULT current_timestamp(),
  `cliente_documento` varchar(64) NOT NULL,
  `total` decimal(13,2) NOT NULL,
  `total_centavos` bigint(20) NOT NULL,
  `estado` varchar(32) NOT NULL DEFAULT 'Pagado',
  `metodo_pago` varchar(64) NOT NULL DEFAULT 'No especificado',
  `dias_credito` int(11) NOT NULL DEFAULT 0,
  `fecha_vencimiento` date DEFAULT NULL,
  `fecha_anulacion` datetime DEFAULT NULL,
  `motivo_anulacion` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ventas_cliente_fecha` (`cliente_documento`,`fecha`),
  KEY `idx_ventas_estado_fecha` (`estado`,`fecha`),
  KEY `idx_ventas_fecha` (`fecha`),
  KEY `idx_ventas_metodo_fecha` (`metodo_pago`,`fecha`),
  CONSTRAINT `fk_ventas_cliente` FOREIGN KEY (`cliente_documento`) REFERENCES `clientes` (`documento`),
  CONSTRAINT `chk_ventas_datos` CHECK (char_length(trim(`cliente_documento`)) > 0 and `total` >= 0 and `total_centavos` >= 0 and `total_centavos` = round(`total` * 100,0) and `dias_credito` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES
(1,'2026-09-26 21:26:44','V-18564029-5',170.00,17000,'Pagado','No especificado',0,NULL,NULL,NULL),
(2,'2026-09-26 23:26:06','V-18564029-5',7.20,720,'Pagado','No especificado',0,NULL,NULL,NULL),
(3,'2026-09-27 00:20:50','V-18564029-5',340.00,34000,'A Credito','No especificado',30,'2026-10-27',NULL,NULL),
(4,'2026-09-27 00:21:25','V-18564029-5',21.60,2160,'A Credito','No especificado',30,'2026-10-27',NULL,NULL),
(5,'2026-09-27 00:31:02','V-18564029-5',53.50,5350,'A Credito','No especificado',30,'2026-10-27',NULL,NULL),
(6,'2026-09-27 00:34:35','V-18564029-5',343.60,34360,'Pagado','No especificado',0,NULL,NULL,NULL),
(7,'2026-09-27 00:38:17','V-12345678',48.00,4800,'Pagado','No especificado',0,NULL,NULL,NULL),
(8,'2026-09-27 00:47:04','V-19555666',37.00,3700,'Pagado','No especificado',0,NULL,NULL,NULL),
(9,'2026-09-27 02:26:25','V-19555666',3.60,360,'Pagado','No especificado',0,NULL,NULL,NULL),
(10,'2026-09-27 22:30:55','V-87654321',25.00,2500,'A Credito','No especificado',30,'2026-10-27',NULL,NULL),
(11,'2026-09-27 12:00:00','J-301234560',1.80,180,'A Credito','No especificado',30,'2026-10-27',NULL,NULL),
(12,'2026-09-27 12:00:00','J-409876541',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(13,'2026-09-22 12:00:00','V-12345678',1.80,180,'A Credito','No especificado',30,'2026-10-22',NULL,NULL),
(14,'2026-09-22 12:00:00','V-18564029-5',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(15,'2026-09-17 12:00:00','V-19555666',1.80,180,'A Credito','No especificado',30,'2026-10-17',NULL,NULL),
(16,'2026-09-17 12:00:00','V-87654321',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(17,'2026-09-07 12:00:00','J-301234560',1.80,180,'A Credito','No especificado',30,'2026-10-07',NULL,NULL),
(18,'2026-09-07 12:00:00','J-409876541',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(19,'2026-08-23 12:00:00','V-12345678',1.80,180,'A Credito','No especificado',30,'2026-09-22',NULL,NULL),
(20,'2026-08-23 12:00:00','V-18564029-5',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(21,'2026-08-13 12:00:00','V-19555666',1.80,180,'A Credito','No especificado',30,'2026-09-12',NULL,NULL),
(22,'2026-08-13 12:00:00','V-87654321',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(23,'2026-08-08 12:00:00','J-301234560',1.80,180,'A Credito','No especificado',30,'2026-09-07',NULL,NULL),
(24,'2026-08-08 12:00:00','J-409876541',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(25,'2026-09-12 12:00:00','V-12345678',1.80,180,'A Credito','No especificado',30,'2026-10-12',NULL,NULL),
(26,'2026-09-12 12:00:00','V-18564029-5',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(27,'2026-09-02 12:00:00','V-19555666',1.80,180,'A Credito','No especificado',30,'2026-10-02',NULL,NULL),
(28,'2026-09-02 12:00:00','V-87654321',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(29,'2026-08-18 12:00:00','J-301234560',1.80,180,'Pagado','No especificado',0,NULL,NULL,NULL),
(30,'2026-08-18 12:00:00','J-409876541',1.80,180,'Pagado','Efectivo',0,NULL,NULL,NULL),
(31,'2026-09-28 09:12:05','V-19555666',141.10,14110,'A Credito','No especificado',30,'2026-09-27',NULL,NULL),
(32,'2026-10-19 00:46:25','V-12345678',748.50,74850,'A Credito','No especificado',30,'2026-11-18',NULL,NULL),
(33,'2026-10-19 10:20:44','J-301234560',14.00,1400,'A Credito','No especificado',30,'2026-11-18',NULL,NULL),
(34,'2026-10-19 12:04:30','J-409876541',276.50,27650,'A Credito','No especificado',15,'2026-11-03',NULL,NULL),
(35,'2026-10-20 11:14:29','V-19555666',15.80,1580,'A Credito','No especificado',30,'2026-11-19',NULL,NULL);
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER ai_ventas_auditoria AFTER INSERT ON ventas FOR EACH ROW
BEGIN
  INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
  VALUES (COALESCE(@app_usuario, SUBSTRING_INDEX(USER(), '@', 1)), COALESCE(@app_rol, 'bd'),
          'TRG_CREAR', 'venta', NEW.id,
          LEFT(CONCAT('cliente=', NEW.cliente_documento, '; total_centavos=', NEW.total_centavos,
                      '; estado=', COALESCE(NEW.estado, ''), '; metodo_pago=', COALESCE(NEW.metodo_pago, '')), 2000));
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER au_ventas_auditoria AFTER UPDATE ON ventas FOR EACH ROW
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
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-10-20 18:44:30
