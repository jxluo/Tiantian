CREATE TABLE IF NOT EXISTS Persons(
  id  CHAR(20) NOT NULL,
  name  CHAR(20) NOT NULL,
  status  INT NOT NULL,
  gender  INT,
  hometown  CHAR(40),
  residence  CHAR(40),
  birthday  CHAR(40),
  visitor_number  INT NOT NULL,
  friend_number  INT NOT NULL,
  visitor_list_number  INT NOT NULL,
  friend_list_number  INT NOT NULL,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS RecentVisitors(
  id  CHAR(20) NOT NULL,
  visitor  CHAR(20) NOT NULL,
  PRIMARY KEY (id, visitor)
);


CREATE TABLE IF NOT EXISTS SomeFriends(
  id  CHAR(20) NOT NULL,
  friend  CHAR(20) NOT NULL,
  PRIMARY KEY (id, friend)
);
