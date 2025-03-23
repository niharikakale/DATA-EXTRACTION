-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: webapp
-- ------------------------------------------------------
-- Server version	8.0.28

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
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'admin','$2b$12$CMOqC9EH2G3i8uXRQBHSl.M/w7/pL.Tun/FTq859zcz5LFklN4LL6','2025-03-05 09:18:18');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_logs`
--

DROP TABLE IF EXISTS `admin_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int NOT NULL,
  `action` text NOT NULL,
  `action_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `admin_logs_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_logs`
--

LOCK TABLES `admin_logs` WRITE;
/*!40000 ALTER TABLE `admin_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consulting`
--

DROP TABLE IF EXISTS `consulting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consulting` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `passport_number` varchar(20) NOT NULL,
  `extracted_passport_number` varchar(20) DEFAULT NULL,
  `center_number` varchar(20) NOT NULL,
  `extracted_center` varchar(20) DEFAULT NULL,
  `test_date` date NOT NULL,
  `dob` date NOT NULL,
  `ielts_date` date DEFAULT NULL,
  `ielts_expiry` date DEFAULT NULL,
  `ielts_listening_score_user` float NOT NULL,
  `ielts_listening_score_extracted` float DEFAULT NULL,
  `ielts_reading_score_user` float NOT NULL,
  `ielts_reading_score_extracted` float DEFAULT NULL,
  `ielts_writing_score_user` float NOT NULL,
  `ielts_writing_score_extracted` float DEFAULT NULL,
  `ielts_speaking_score_user` float NOT NULL,
  `ielts_speaking_score_extracted` float DEFAULT NULL,
  `overall_band_score` float NOT NULL,
  `cefr_level` varchar(10) NOT NULL,
  `uploaded_ielts` varchar(255) DEFAULT NULL,
  `status` enum('pending','verified','discrepancy_found') DEFAULT 'pending',
  `name_matched` tinyint(1) DEFAULT '0',
  `dob_matched` tinyint(1) DEFAULT '0',
  `score_mismatch` text,
  `passport_match` tinyint(1) DEFAULT '0',
  `center_match` tinyint(1) DEFAULT '0',
  `listening_match` tinyint(1) DEFAULT '0',
  `reading_match` tinyint(1) DEFAULT '0',
  `writing_match` tinyint(1) DEFAULT '0',
  `speaking_match` tinyint(1) DEFAULT '0',
  `extracted_center_number` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `consulting_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consulting`
--

LOCK TABLES `consulting` WRITE;
/*!40000 ALTER TABLE `consulting` DISABLE KEYS */;
INSERT INTO `consulting` VALUES (1,1,'X8279471','OCR Failed','IN855','IN855','2025-02-28','2024-02-29',NULL,NULL,8.5,8.5,9,9,7,7,7,7,6,'C1','static/uploads/user_1_ielts_IELTS.pdf','verified',NULL,NULL,NULL,0,1,0,0,0,0,'IN855');
/*!40000 ALTER TABLE `consulting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_applications`
--

DROP TABLE IF EXISTS `exam_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_applications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `pan_card` varchar(255) NOT NULL,
  `aadhar_card` varchar(255) NOT NULL,
  `extracted_pan` varchar(255) DEFAULT NULL,
  `extracted_aadhar` varchar(255) DEFAULT NULL,
  `dob_matched` tinyint(1) DEFAULT NULL,
  `id_number_matched` tinyint(1) DEFAULT NULL,
  `application_status` enum('pending','reviewed','accepted','rejected') DEFAULT 'pending',
  `applied_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `exam_applications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `exam_applications_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exam_posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_applications`
--

LOCK TABLES `exam_applications` WRITE;
/*!40000 ALTER TABLE `exam_applications` DISABLE KEYS */;
INSERT INTO `exam_applications` VALUES (1,1,1,'33','33','OCR Failed','OCR Failed',0,0,'rejected','2025-03-06 04:39:46'),(2,1,1,'CCHPN1009B','CCHPN1009B','4710212001','4710212001',0,0,'rejected','2025-03-06 05:07:44'),(3,1,1,'CCHPN1009B','CCHPN1009B','CCHPN1009B','OCR Failed',0,0,'rejected','2025-03-06 06:05:04'),(4,1,1,'CCHPN1009B','733420105428','CCHPN1009B','OCR Failed',0,0,'rejected','2025-03-06 09:01:35'),(5,1,1,'CCHPN1009B','733420105428','CCHPN1009B','733420105428',0,1,'accepted','2025-03-06 09:03:02');
/*!40000 ALTER TABLE `exam_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_posts`
--

DROP TABLE IF EXISTS `exam_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_posts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `posted_by` int DEFAULT NULL,
  `posted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `posted_by` (`posted_by`),
  CONSTRAINT `exam_posts_ibfk_1` FOREIGN KEY (`posted_by`) REFERENCES `admin` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_posts`
--

LOCK TABLES `exam_posts` WRITE;
/*!40000 ALTER TABLE `exam_posts` DISABLE KEYS */;
INSERT INTO `exam_posts` VALUES (1,'Unit Test 1','dsp ',1,'2025-03-05 05:25:56');
/*!40000 ALTER TABLE `exam_posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `job_applications`
--

DROP TABLE IF EXISTS `job_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `job_applications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `job_id` int NOT NULL,
  `resume` varchar(255) NOT NULL,
  `similarity_score` decimal(5,2) DEFAULT NULL,
  `skills_matched` text,
  `additional_info` text,
  `application_status` enum('pending','reviewed','accepted','rejected') DEFAULT 'pending',
  `applied_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `job_id` (`job_id`),
  CONSTRAINT `job_applications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `job_applications_ibfk_2` FOREIGN KEY (`job_id`) REFERENCES `job_posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `job_applications`
--

LOCK TABLES `job_applications` WRITE;
/*!40000 ALTER TABLE `job_applications` DISABLE KEYS */;
INSERT INTO `job_applications` VALUES (1,1,2,'user_1_divesh_kumar.docx',38.56,'None','sql, python, excel., numpy, pandas, power bi, tableau','rejected','2025-03-05 08:00:21'),(2,1,2,'user_1_divesh_kumar.docx',38.56,'sql,  python,  pandas,  numpy,  power bi,  tableau','power bi, pandas, python, excel., sql, tableau, numpy','accepted','2025-03-05 09:19:09'),(3,1,2,'app/static/resumes/user_1_divesh_kumar.docx',39.36,'sql, python, pandas, numpy, power bi, tableau','excel.','rejected','2025-03-05 09:25:43'),(4,1,2,'app/static/resumes/user_1_divesh_kumar.docx',39.36,'sql, python, pandas, numpy, power bi, tableau','excel.','accepted','2025-03-05 09:28:24'),(5,1,2,'user_1_job_2.docx',38.55,'sql, python, pandas, numpy, tableau','power bi, excel.','rejected','2025-03-05 09:36:41'),(6,1,2,'user_1_job_2.docx',39.36,'sql, python, pandas, numpy, tableau','power bi, excel.','rejected','2025-03-05 09:47:44'),(7,1,2,'user_1_job_2.docx',39.36,'sql, python, pandas, numpy, tableau','power bi, excel.','rejected','2025-03-05 09:51:40'),(8,1,2,'user_1_job_2.docx',39.36,'sql, python, pandas, numpy, tableau, excel','power bi','accepted','2025-03-05 09:55:22');
/*!40000 ALTER TABLE `job_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `job_posts`
--

DROP TABLE IF EXISTS `job_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `job_posts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `skills_required` text NOT NULL,
  `posted_by` int DEFAULT NULL,
  `posted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `posted_by` (`posted_by`),
  CONSTRAINT `job_posts_ibfk_1` FOREIGN KEY (`posted_by`) REFERENCES `admin` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `job_posts`
--

LOCK TABLES `job_posts` WRITE;
/*!40000 ALTER TABLE `job_posts` DISABLE KEYS */;
INSERT INTO `job_posts` VALUES (1,'Data Analyst Full Time','Analyzing the data of the different tables and pictorial representation','python, mysql, power bi, numpy, pandas, seaborn, matplotlib, descriptive statistics',1,'2025-03-05 05:23:40'),(2,'Data Analyst','We are looking for a skilled Data Analyst to join our team.\r\n    Responsibilities include data cleaning, analysis, visualization, and reporting.\r\n   \r\n    Experience: 2-4 years in data analytics or related fields.\r\n    Education: Bachelor\'s/Master\'s degree in Statistics, Mathematics, or Computer Science.\r\n    Preferred certifications: Google Data Analytics, Microsoft Power BI Certification.','SQL, Python, Pandas, NumPy, Power BI, Tableau, Excel.',1,'2025-03-05 07:33:38');
/*!40000 ALTER TABLE `job_posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `otp`
--

DROP TABLE IF EXISTS `otp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otp` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `otp` varchar(6) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `otp`
--

LOCK TABLES `otp` WRITE;
/*!40000 ALTER TABLE `otp` DISABLE KEYS */;
/*!40000 ALTER TABLE `otp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `dob` date NOT NULL,
  `security_question` varchar(255) NOT NULL,
  `security_answer` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `country` varchar(100) NOT NULL,
  `status` enum('active','inactive') DEFAULT 'inactive',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'divesh kumar mattigiri','diveshkmattigiri@gmail.com','$2b$12$gzRw3Mau0.oRGhIQ9Txbg.CE3usLh3Xu82REcXzK3fkkDg//7QoiW','8978309554','1990-08-17','Your first pet’s name?','$2b$12$W0OC8Fu7fhWOSE1yW12EeOWl0j0fxBVnDkmu9uloeQC2z5YNstQ1i','guntur','andhra pradesh','india','active','2025-03-05 05:17:23');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-10 18:09:49
