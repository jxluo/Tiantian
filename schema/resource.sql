CREATE TABLE IF NOT EXISTS RenrenAccounts (
  username  CHAR(40) NOT NULL,
  password  CHAR(40) NOT NULL,
  is_using  BOOL NOT NULL DEFAULT 0,
  is_valid  BOOL NOT NULL DEFAULT 1,

  create_time  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_used_time  TIMESTAMP,

  come_from  CHAR(120) NOT NULL,
  login_count  INT NOT NULL DEFAULT 0,
  request_count  INT NOT NULL DEFAULT 0,

  become_invalid_time  TIMESTAMP,
  error_code  INT,
  error_info  CHAR(120),

  PRIMARY KEY (username, password)
);


CREATE TABLE IF NOT EXISTS RenrenAccountsLog (
  log_id  INT NOT NULL AUTO_INCREMENT,
  username  CHAR(40) NOT NULL,
  password  CHAR(40) NOT NULL,
  happen_time  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  event  INT NOT NULL,
  is_login  BOOL,
  request_count  INT,

  PRIMARY KEY (log_id)
);

CREATE TABLE IF NOT EXISTS Proxies (
  address CHAR(80) NOT NULL,
  port CHAR(20) NOT NULL,
  protocol CHAR(20) NOT NULL,

  info CHAR(200),
  source CHAR(200),

  test_count INT NOT NULL DEFAULT 0,
  success_count INT NOT NULL DEFAULT 0,
  average_time INT NOT NULL DEFAULT 999999,

  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (address, port)
);

