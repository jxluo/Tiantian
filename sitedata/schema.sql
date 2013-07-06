DROP TABLE IF EXISTS GlobalInfo;
DROP TABLE IF EXISTS XingCharMap;
DROP TABLE IF EXISTS XingMap;
DROP TABLE IF EXISTS MingCharMap;
DROP TABLE IF EXISTS MingMap;
DROP TABLE IF EXISTS XingCharRank;
DROP TABLE IF EXISTS XingRank;
DROP TABLE IF EXISTS MingCharRank;
DROP TABLE IF EXISTS MingRank;


CREATE TABLE IF NOT EXISTS GlobalInfo(
  id INT NOT NULL,
  all_xing_char_count INT NOT NULL,
  all_xing_count INT NOT NULL,
  all_ming_char_count INT NOT NULL,
  all_ming_count INT NOT NULL,

  person_count INT NOT NULL,
  male_count INT NOT NULL,
  female_count INT NOT NULL,

  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS XingCharMap(
  id INT NOT NULL AUTO_INCREMENT,
  s_key CHAR(32) NOT NULL,
  value VARBINARY(1024) NOT NULL,
  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY (s_key)
) CHARACTER SET utf8
  COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS XingMap(
  id INT NOT NULL AUTO_INCREMENT,
  s_key CHAR(32) NOT NULL,
  value VARBINARY(1024) NOT NULL,
  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY (s_key)
) CHARACTER SET utf8
  COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS MingCharMap(
  id INT NOT NULL AUTO_INCREMENT,
  s_key CHAR(32) NOT NULL,
  value VARBINARY(1024) NOT NULL,
  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY (s_key)
) CHARACTER SET utf8
  COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS MingMap(
  id INT NOT NULL AUTO_INCREMENT,
  s_key CHAR(32) NOT NULL,
  value VARBINARY(1024) NOT NULL,
  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY (s_key)
) CHARACTER SET utf8
  COLLATE utf8_general_ci;


CREATE TABLE IF NOT EXISTS XingCharRank(
  id INT NOT NULL AUTO_INCREMENT,
  s_key CHAR(32) NOT NULL,
  rank INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (s_key, rank)
) CHARACTER SET utf8
  COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS XingRank(
  id INT NOT NULL AUTO_INCREMENT,
  s_key CHAR(32) NOT NULL,
  rank INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (s_key, rank)
) CHARACTER SET utf8
  COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS MingCharRank(
  id INT NOT NULL AUTO_INCREMENT,
  s_key CHAR(32) NOT NULL,
  rank INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (s_key, rank)
) CHARACTER SET utf8
  COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS MingRank(
  id INT NOT NULL AUTO_INCREMENT,
  s_key CHAR(32) NOT NULL,
  rank INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (s_key, rank)
) CHARACTER SET utf8
  COLLATE utf8_general_ci;