CREATE TABLE IF NOT EXISTS Persons(
  id  CHAR(20) NOT NULL,
  status  INT NOT NULL,
  name  CHAR(40) NOT NULL,
  gender  INT,
  hometown  CHAR(40),
  residence  CHAR(40),
  birthday  CHAR(40),
  visitor_number  INT NOT NULL,
  friend_number  INT NOT NULL,
  recent_visitor_number  INT NOT NULL,
  home_page_friend_number  INT NOT NULL,
  
  create_time TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
  last_modified_time TIMESTAMP NOT NULL
    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  reference_id CHAR(20),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS RecentVisitors(
  id  CHAR(20) NOT NULL,
  visitor  CHAR(20) NOT NULL,
  PRIMARY KEY (id, visitor)
);


CREATE TABLE IF NOT EXISTS HomePageFriends(
  id  CHAR(20) NOT NULL,
  friend  CHAR(20) NOT NULL,
  PRIMARY KEY (id, friend)
);


CREATE TABLE IF NOT EXISTS StartList(
  table_id INT NOT NULL AUTO_INCREMENT,
  id CHAR(20) NOT NULL,
  is_using BOOL NOT NULL DEFAULT 0,
  last_modified TIMESTAMP NOT NULL
    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (table_id),
  UNIQUE KEY (id)
);
