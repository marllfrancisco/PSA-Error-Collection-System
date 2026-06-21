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

--
-- Table structure for table `birth_certificate`
--
USE ecorrectdb;
DROP TABLE IF EXISTS `birth_certificate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `birth_certificate` (
  `registry_number` varchar(20) NOT NULL,
  `child_id` char(7) NOT NULL,
  `mother_id` char(7) NOT NULL,
  `father_id` char(7) DEFAULT NULL,
  `birth_order` tinyint unsigned NOT NULL,
  PRIMARY KEY (`registry_number`),
  KEY `child_id` (`child_id`),
  KEY `mother_id` (`mother_id`),
  KEY `father_id` (`father_id`),
  CONSTRAINT `birth_certificate_ibfk_1` FOREIGN KEY (`registry_number`) REFERENCES `certificate_owner` (`registry_number`),
  CONSTRAINT `birth_certificate_ibfk_2` FOREIGN KEY (`child_id`) REFERENCES `person_data` (`person_id`),
  CONSTRAINT `birth_certificate_ibfk_3` FOREIGN KEY (`mother_id`) REFERENCES `person_data` (`person_id`),
  CONSTRAINT `birth_certificate_ibfk_4` FOREIGN KEY (`father_id`) REFERENCES `person_data` (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `birth_certificate`
--

LOCK TABLES `birth_certificate` WRITE;
/*!40000 ALTER TABLE `birth_certificate` DISABLE KEYS */;
/*!40000 ALTER TABLE `birth_certificate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certificate_owner`
--

DROP TABLE IF EXISTS `certificate_owner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificate_owner` (
  `registry_number` varchar(20) NOT NULL,
  `person_id` char(7) NOT NULL,
  PRIMARY KEY (`registry_number`),
  KEY `person_id` (`person_id`),
  CONSTRAINT `certificate_owner_ibfk_1` FOREIGN KEY (`person_id`) REFERENCES `person_data` (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificate_owner`
--

LOCK TABLES `certificate_owner` WRITE;
/*!40000 ALTER TABLE `certificate_owner` DISABLE KEYS */;
/*!40000 ALTER TABLE `certificate_owner` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Table structure for table `death_certificate`
--

DROP TABLE IF EXISTS `death_certificate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `death_certificate` (
  `registry_number` varchar(20) NOT NULL,
  `deceased_id` char(7) NOT NULL,
  `death_date` date NOT NULL,
  `registration_date` date NOT NULL,
  `certification_date` date NOT NULL,
  PRIMARY KEY (`registry_number`),
  KEY `deceased_id` (`deceased_id`),
  CONSTRAINT `death_certificate_ibfk_1` FOREIGN KEY (`registry_number`) REFERENCES `certificate_owner` (`registry_number`),
  CONSTRAINT `death_certificate_ibfk_2` FOREIGN KEY (`deceased_id`) REFERENCES `person_data` (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `death_certificate`
--

LOCK TABLES `death_certificate` WRITE;
/*!40000 ALTER TABLE `death_certificate` DISABLE KEYS */;
/*!40000 ALTER TABLE `death_certificate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discrepancy_entries`
--

DROP TABLE IF EXISTS `discrepancy_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discrepancy_entries` (
  `report_id` varchar(20) NOT NULL,
  `person_name` varchar(50) DEFAULT NULL,
  `cert_type` enum('Birth Certificate','Death Certificate','Marriage Certificate') NOT NULL,
  `explanation` varchar(255) NOT NULL,
  `error_field` varchar(50) NOT NULL,
  `original_value` varchar(255) NOT NULL,
  `revised_value` varchar(255) NOT NULL,
  `modified_by` varchar(20) NOT NULL,
  `modified_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`),
  KEY `fk_report_entry` (`report_id`),
  CONSTRAINT `fk_discrepancy_entries_report` FOREIGN KEY (`report_id`) REFERENCES `discrepancy_report` (`report_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discrepancy_entries`
--

LOCK TABLES `discrepancy_entries` WRITE;
/*!40000 ALTER TABLE `discrepancy_entries` DISABLE KEYS */;
INSERT INTO `discrepancy_entries` VALUES ('26-06-00001',NULL,'Birth Certificate','wrong age','Age at Time of death','65','67','1','2026-06-17 19:42:50');
/*!40000 ALTER TABLE `discrepancy_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discrepancy_entries_audit`
--

DROP TABLE IF EXISTS `discrepancy_entries_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discrepancy_entries_audit` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `report_id` varchar(20) NOT NULL,
  `person_name` varchar(50) DEFAULT NULL,
  `cert_type` enum('Birth Certificate','Death Certificate','Marriage Certificate') NOT NULL,
  `explanation` varchar(255) NOT NULL,
  `error_field` varchar(50) NOT NULL,
  `original_value` varchar(255) NOT NULL,
  `revised_value` varchar(255) NOT NULL,
  `modified_by` varchar(20) NOT NULL,
  `modified_date` datetime NOT NULL,
  `audit_timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
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
  `cert_type` enum('Birth Certificate','Death Certificate','Marriage Certificate') NOT NULL,
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
INSERT INTO `discrepancy_report` VALUES ('26-06-00001','1','2023-7654321','Birth Certificate','PENDING','2026-06-17 19:42:50');
/*!40000 ALTER TABLE `discrepancy_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discrepancy_report_audit`
--

DROP TABLE IF EXISTS `discrepancy_report_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discrepancy_report_audit` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `report_id` varchar(20) NOT NULL,
  `employee_id` varchar(20) NOT NULL,
  `registry_number` varchar(20) NOT NULL,
  `cert_type` enum('Birth Certificate','Death Certificate','Marriage Certificate') NOT NULL,
  `status` enum('PENDING','RESOLVED') NOT NULL,
  `created_date` datetime NOT NULL,
  `audit_timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
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
-- Table structure for table `marriage_certificate`
--

DROP TABLE IF EXISTS `marriage_certificate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `marriage_certificate` (
  `registry_number` varchar(20) NOT NULL,
  `applicant_id` char(7) NOT NULL,
  `spouse_id` char(7) NOT NULL,
  `applicant_age` tinyint unsigned NOT NULL,
  `spouse_age` tinyint unsigned NOT NULL,
  PRIMARY KEY (`registry_number`),
  KEY `applicant_id` (`applicant_id`),
  KEY `spouse_id` (`spouse_id`),
  CONSTRAINT `marriage_certificate_ibfk_1` FOREIGN KEY (`registry_number`) REFERENCES `certificate_owner` (`registry_number`),
  CONSTRAINT `marriage_certificate_ibfk_2` FOREIGN KEY (`applicant_id`) REFERENCES `person_data` (`person_id`),
  CONSTRAINT `marriage_certificate_ibfk_3` FOREIGN KEY (`spouse_id`) REFERENCES `person_data` (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marriage_certificate`
--

LOCK TABLES `marriage_certificate` WRITE;
/*!40000 ALTER TABLE `marriage_certificate` DISABLE KEYS */;
/*!40000 ALTER TABLE `marriage_certificate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `person_data`
--

DROP TABLE IF EXISTS `person_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person_data` (
  `person_id` char(7) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  PRIMARY KEY (`person_id`),
  CONSTRAINT `person_data_chk_1` CHECK (regexp_like(`person_id`,_utf8mb4'^P-[0-9]{5}$'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person_data`
--

LOCK TABLES `person_data` WRITE;
/*!40000 ALTER TABLE `person_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `person_data` ENABLE KEYS */;
UNLOCK TABLES;

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

-- Dump completed on 2026-06-18 21:31:58
