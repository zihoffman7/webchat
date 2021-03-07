---- UNCOMMENT TO OVERRIDE ALL DATA ----
-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS rooms;
-- DROP TABLE IF EXISTS user_rooms;
---- END ----

-- All user data
CREATE TABLE IF NOT EXISTS users (
  username TEXT NOT NULL,   -- The user's chosen username
  email TEXT NOT NULL,      -- The user's email.  Only used for login
  password TEXT NOT NULL,   -- Hashed version of the user's password
  id TEXT NOT NULL          -- User id is created on account creation
);

-- All basic room data
CREATE TABLE IF NOT EXISTS rooms (
  name TEXT NOT NULL,       -- Name of room
  code TEXT NOT NULL,       -- Join code of room
  owner TEXT NOT NULL       -- User id of room creator
);

-- Which rooms the users are apart of
CREATE TABLE IF NOT EXISTS user_rooms (
  username TEXT NOT NULL,   -- The user's chosen username
  userID TEXT NOT NULL,     -- The user's id
  roomID TEXT NOT NULL,     -- The join code of room
  room TEXT NOT NULL        -- The name of the room
);
