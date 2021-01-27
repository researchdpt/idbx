-- phpMyAdmin SQL Dump
-- version 4.9.5
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jul 16, 2020 at 07:19 PM
-- Server version: 10.3.22-MariaDB
-- PHP Version: 7.3.18

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `identibooru`
--
CREATE DATABASE IF NOT EXISTS `identibooru` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `identibooru`;

-- --------------------------------------------------------

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
CREATE TABLE IF NOT EXISTS `tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `tag` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `username` longtext NOT NULL,
  `password` longtext NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `user_opts`
--

DROP TABLE IF EXISTS `user_opts`;
CREATE TABLE IF NOT EXISTS `user_opts` (
  `uid` int(11) NOT NULL,
  `options` longtext NOT NULL,
  `bio` longtext NOT NULL,
  UNIQUE KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
COMMIT;

ALTER TABLE `user_opts` ADD `views` INT NOT NULL DEFAULT '0' AFTER `bio`, ADD `avatar` INT NOT NULL DEFAULT '0' AFTER `views`, ADD `map` INT NOT NULL DEFAULT '0' AFTER `avatar`, ADD `tracking` INT NOT NULL DEFAULT '0' AFTER `map`, ADD `rank` INT NOT NULL DEFAULT '0' AFTER `tracking`;
ALTER TABLE `user_opts` ADD `adult` INT NOT NULL DEFAULT '0' AFTER `rank`; 
ALTER TABLE `user_opts` ADD `sharing` INT NOT NULL DEFAULT '0' AFTER `tracking`; 
ALTER TABLE `user_opts` DROP `options`;

