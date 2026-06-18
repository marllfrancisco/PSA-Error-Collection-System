-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: ecorrectdb
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE ecorrectdb;
USE ecorrectdb;
--
-- Table structure for table `certificate_type`
--

DROP TABLE IF EXISTS `certificate_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificate_type` (
  `cert_id` int NOT NULL,
  `cert_type` varchar(20) NOT NULL,
  PRIMARY KEY (`cert_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificate_type`
--

LOCK TABLES `certificate_type` WRITE;
/*!40000 ALTER TABLE `certificate_type` DISABLE KEYS */;
INSERT INTO `certificate_type` VALUES (1,'Birth Certificate'),(2,'Marriage Certificate'),(3,'Death Certificate');
/*!40000 ALTER TABLE `certificate_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discrepancy_entries`
--

DROP TABLE IF EXISTS `discrepancy_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discrepancy_entries` (
  `discrepancy_id` varchar(20) NOT NULL,
  `report_id` varchar(20) NOT NULL,
  `cert_type` int NOT NULL,
  `explanation` varchar(255) NOT NULL,
  `error_field` varchar(50) NOT NULL,
  `original_value` varchar(255) NOT NULL,
  `revised_value` varchar(255) NOT NULL,
  `modified_by` varchar(20) NOT NULL,
  `modified_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`discrepancy_id`),
  KEY `fk_report_entry` (`report_id`),
  CONSTRAINT `fk_report_entry` FOREIGN KEY (`report_id`) REFERENCES `discrepancy_report` (`report_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `discrepancy_entries_chk_1` CHECK ((`cert_type` in (1,2,3)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discrepancy_entries`
--

LOCK TABLES `discrepancy_entries` WRITE;
/*!40000 ALTER TABLE `discrepancy_entries` DISABLE KEYS */;
/*!40000 ALTER TABLE `discrepancy_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discrepancy_entries_audit`
--

DROP TABLE IF EXISTS `discrepancy_entries_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discrepancy_entries_audit` (
  `audit_id` int NOT NULL AUTO_INCREMENT,
  `report_id` varchar(20) NOT NULL,
  `discrepancy_id` varchar(20) NOT NULL,
  `cert_type` int NOT NULL,
  `explanation` varchar(255) NOT NULL,
  `error_field` varchar(50) NOT NULL,
  `original_value` varchar(255) NOT NULL,
  `revised_value` varchar(255) NOT NULL,
  `modified_by` varchar(20) NOT NULL,
  `modified_date` datetime NOT NULL,
  `audit_timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`audit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discrepancy_entries_audit`
--

LOCK TABLES `discrepancy_entries_audit` WRITE;
/*!40000 ALTER TABLE `discrepancy_entries_audit` DISABLE KEYS */;
/*!40000 ALTER TABLE `discrepancy_entries_audit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discrepancy_report`
--

DROP TABLE IF EXISTS `discrepancy_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discrepancy_report` (
  `report_id` varchar(20) NOT NULL,
  `employee_id` varchar(20) NOT NULL,
  `registry_number` varchar(20) NOT NULL,
  `status` enum('PENDING','RESOLVED') DEFAULT 'PENDING',
  `created_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discrepancy_report`
--

LOCK TABLES `discrepancy_report` WRITE;
/*!40000 ALTER TABLE `discrepancy_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `discrepancy_report` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tr_discrepancy_report_audit` BEFORE UPDATE ON `discrepancy_report` FOR EACH ROW BEGIN

    INSERT INTO discrepancy_report_audit (
        report_id,
        employee_id,
        registry_number,
        status,
        created_date
    )
    VALUES (
        OLD.report_id,
        OLD.employee_id,
        OLD.registry_number,
        OLD.status,
        OLD.created_date
    );

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `discrepancy_report_audit`
--

DROP TABLE IF EXISTS `discrepancy_report_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discrepancy_report_audit` (
  `audit_id` int NOT NULL AUTO_INCREMENT,
  `report_id` varchar(20) NOT NULL,
  `employee_id` varchar(20) NOT NULL,
  `registry_number` varchar(20) NOT NULL,
  `status` enum('PENDING','RESOLVED') NOT NULL,
  `created_date` datetime NOT NULL,
  `audit_timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`audit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discrepancy_report_audit`
--

LOCK TABLES `discrepancy_report_audit` WRITE;
/*!40000 ALTER TABLE `discrepancy_report_audit` DISABLE KEYS */;
/*!40000 ALTER TABLE `discrepancy_report_audit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `employee_id` varchar(20) NOT NULL,
  `emp_last_name` varchar(50) NOT NULL,
  `emp_middle_name` varchar(50) DEFAULT NULL,
  `emp_first_name` varchar(50) NOT NULL,
  PRIMARY KEY (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'ecorrectdb'
--

--
-- Dumping routines for database 'ecorrectdb'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-17 11:37:53
