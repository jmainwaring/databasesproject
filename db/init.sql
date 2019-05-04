CREATE DATABASE mydb;
USE mydb; 
CREATE TABLE counties (county_id BIGINT, name VARCHAR(255), PRIMARY KEY (county_id));
CREATE TABLE precincts (precinct_abbrv VARCHAR(255), precinct_desc VARCHAR(255), county_id BIGINT, PRIMARY KEY (county_id, precinct_abbrv));
CREATE TABLE wards (ward_abbrv VARCHAR(255), ward_desc VARCHAR(255), county_id BIGINT, PRIMARY KEY (county_id, ward_abbrv));
CREATE TABLE municipalities (muni_abbrv VARCHAR(255), muni_desc VARCHAR(255), county_id BIGINT, PRIMARY KEY (county_id, muni_abbrv));
CREATE TABLE voters (ncid VARCHAR(255), voter_status_desc VARCHAR(255), voter_status_reason_desc VARCHAR(255), 
                       res_street_address VARCHAR(255), res_city_desc VARCHAR(255), zip_code VARCHAR(255), first_name VARCHAR(255), 
                       last_name VARCHAR(255), middle_name VARCHAR(255), birth_year BIGINT, gender_code VARCHAR(255),
                       race_code VARCHAR(255), registr_dt DATETIME, ward_abbrv VARCHAR(255), precinct_abbrv VARCHAR(255), 
                       muni_abbrv VARCHAR(255), county_id BIGINT, PRIMARY KEY (ncid));
CREATE TABLE parties (voted_party_cd VARCHAR(255), voted_party_desc VARCHAR(255), PRIMARY KEY (voted_party_cd));
CREATE TABLE vhist (ncid VARCHAR(255), election_year BIGINT, voting_method VARCHAR(255), voted_party_cd VARCHAR(255), PRIMARY KEY (ncid));

LOAD DATA INFILE '/Users/Tim/Desktop/MIMS/final_semester/databases/databasesproject/db/counties.csv' 
INTO TABLE counties
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n';

LOAD DATA INFILE '/Users/Tim/Desktop/MIMS/final_semester/databases/databasesproject/db/wards.csv' 
INTO TABLE wards
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n';

LOAD DATA INFILE '/Users/Tim/Desktop/MIMS/final_semester/databases/databasesproject/db/municipalities.csv' 
INTO TABLE municipalities
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n';

LOAD DATA INFILE '/Users/Tim/Desktop/MIMS/final_semester/databases/databasesproject/db/precincts.csv' 
INTO TABLE precincts
FIELDS TERMINATED BY '\t' 
LINES TERMINATED BY '\n';

LOAD DATA INFILE '/Users/Tim/Desktop/MIMS/final_semester/databases/databasesproject/db/voters.csv' 
INTO TABLE voters
FIELDS TERMINATED BY '\t' 
LINES TERMINATED BY '\n';

LOAD DATA INFILE '/Users/Tim/Desktop/MIMS/final_semester/databases/databasesproject/db/parties.csv' 
INTO TABLE parties
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n';

LOAD DATA INFILE '/Users/Tim/Desktop/MIMS/final_semester/databases/databasesproject/db/vhist.csv' 
INTO TABLE vhist
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n';

-- mysql -uroot -pNEWPASS
-- mysqldump -uroot -pNEWPASS mydb > /Users/Tim/Desktop/MIMS/final_semester/databases/databasesproject/db/initialize.sql