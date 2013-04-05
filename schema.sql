CREATE TABLE IF NOT EXISTS Persons(
  id  CHAR(20) NOT NULL,
  status  INT NOT NULL,
  name  CHAR(20) NOT NULL,
  gender  INT,
  hometown  CHAR(40),
  residence  CHAR(40),
  birthday  CHAR(40),
  visitor_number  INT NOT NULL,
  friend_number  INT NOT NULL,
  recent_visitor_number  INT NOT NULL,
  home_page_friend_number  INT NOT NULL,
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
  id CHAR(20) NOT NULL,
  created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);
