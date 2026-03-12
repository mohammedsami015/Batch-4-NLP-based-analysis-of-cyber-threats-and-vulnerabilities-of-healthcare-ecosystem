**Run this codes in your sql workbench or command line**





CREATE DATABASE IF NOT EXISTS `har\_db`;





USE `har\_db`;







-- Create the users table

CREATE TABLE IF NOT EXISTS `users` (

&nbsp; `id` INT AUTO\_INCREMENT PRIMARY KEY,

&nbsp; `username` VARCHAR(100) NOT NULL UNIQUE,

&nbsp; `password` VARCHAR(255) NOT NULL,

&nbsp; `email` VARCHAR(100) NOT NULL UNIQUE,

&nbsp; `role` VARCHAR(20) NOT NULL DEFAULT 'user',

&nbsp; `created\_at` TIMESTAMP DEFAULT CURRENT\_TIMESTAMP

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

