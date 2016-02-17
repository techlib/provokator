--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: message_state; Type: TYPE; Schema: public; Owner: sms
--

CREATE TYPE message_state AS ENUM (
    'incoming',
    'outgoing',
    'checked',
    'failed',
    'sent'
);


ALTER TYPE message_state OWNER TO sms;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: message; Type: TABLE; Schema: public; Owner: sms; Tablespace: 
--

CREATE TABLE message (
    id character varying NOT NULL,
    ts timestamp without time zone DEFAULT now() NOT NULL,
    msg json NOT NULL,
    state message_state NOT NULL
);


ALTER TABLE message OWNER TO sms;

--
-- Name: daily_stats; Type: VIEW; Schema: public; Owner: sms
--

CREATE VIEW daily_stats AS
 SELECT (date_part('year'::text, message.ts))::integer AS year,
    (date_part('month'::text, message.ts))::integer AS month,
    (date_part('day'::text, message.ts))::integer AS day,
    (sum(
        CASE
            WHEN (message.state = 'incoming'::message_state) THEN 1
            ELSE 0
        END))::integer AS incoming,
    (sum(
        CASE
            WHEN (message.state = 'outgoing'::message_state) THEN 1
            ELSE 0
        END))::integer AS outgoing,
    (sum(
        CASE
            WHEN (message.state = 'checked'::message_state) THEN 1
            ELSE 0
        END))::integer AS checked,
    (sum(
        CASE
            WHEN (message.state = 'sent'::message_state) THEN 1
            ELSE 0
        END))::integer AS sent,
    (sum(
        CASE
            WHEN (message.state = 'failed'::message_state) THEN 1
            ELSE 0
        END))::integer AS failed
   FROM message
  GROUP BY (date_part('year'::text, message.ts))::integer, (date_part('month'::text, message.ts))::integer, (date_part('day'::text, message.ts))::integer
  ORDER BY (date_part('year'::text, message.ts))::integer DESC, (date_part('month'::text, message.ts))::integer DESC, (date_part('day'::text, message.ts))::integer DESC;


ALTER TABLE daily_stats OWNER TO sms;

--
-- Name: dated_messages; Type: VIEW; Schema: public; Owner: sms
--

CREATE VIEW dated_messages AS
 SELECT message.id,
    message.ts,
    message.msg,
    message.state,
    (date_part('year'::text, message.ts))::integer AS year,
    (date_part('month'::text, message.ts))::integer AS month,
    (date_part('day'::text, message.ts))::integer AS day
   FROM message
  ORDER BY message.ts DESC;


ALTER TABLE dated_messages OWNER TO sms;

--
-- Name: monthly_counts; Type: VIEW; Schema: public; Owner: sms
--

CREATE VIEW monthly_counts AS
 SELECT (date_part('year'::text, message.ts))::integer AS year,
    (date_part('month'::text, message.ts))::integer AS month,
    count(message.id) AS count
   FROM message
  GROUP BY date_part('year'::text, message.ts), date_part('month'::text, message.ts)
  ORDER BY date_part('year'::text, message.ts) DESC, date_part('month'::text, message.ts) DESC;


ALTER TABLE monthly_counts OWNER TO sms;

--
-- Name: message_pkey; Type: CONSTRAINT; Schema: public; Owner: sms; Tablespace: 
--

ALTER TABLE ONLY message
    ADD CONSTRAINT message_pkey PRIMARY KEY (id);


--
-- Name: message_ts_idx; Type: INDEX; Schema: public; Owner: sms; Tablespace: 
--

CREATE INDEX message_ts_idx ON message USING btree (ts);


--
-- Name: public; Type: ACL; Schema: -; Owner: sms
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM sms;
GRANT ALL ON SCHEMA public TO sms;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

