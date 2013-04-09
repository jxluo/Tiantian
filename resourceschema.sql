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

  became_invalid_time  TIMESTAMP,
  error_info  CHAR(120),
  error_code  INT,

  PRIMARY KEY (username, password)
);
