--
-- PostgreSQL database dump
--

\restrict CxhSaRnhGLk2dbwfAEyTUEGoiVFA2P0olvamdYUDPln2R7qBDMtrmwS7vSWBK3z

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2025-09-23 17:26:12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 217 (class 1259 OID 16386)
-- Name: acl_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.acl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.acl_id_seq OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 16387)
-- Name: acl; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.acl (
    "ORDER_ID" integer NOT NULL,
    "SOURCE_IP_START" character varying(15) NOT NULL,
    "SOURCE_IP_END" character varying(15) NOT NULL,
    "ALLOW" character(1) NOT NULL,
    "ACL_ID" bigint DEFAULT nextval('public.acl_id_seq'::regclass) NOT NULL
);


ALTER TABLE public.acl OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16391)
-- Name: cdr_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cdr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cdr_id_seq OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16392)
-- Name: cdr; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cdr (
    "CDR_ID" bigint DEFAULT nextval('public.cdr_id_seq'::regclass) NOT NULL,
    "SETUP_TIME" timestamp without time zone,
    "DISCONNECT_TIME" timestamp without time zone,
    "CONNECT_TIME" timestamp without time zone,
    "CPN" character varying(256),
    "DNIS" character varying(256),
    "ROUTE" character varying(256),
    "ROUTE_PORT" smallint,
    "SESSION_TIME" integer,
    "DISCONNECT_CAUSE" integer,
    "CLOSING_LEG" character varying(5),
    "RECORD_TIME" timestamp without time zone
);


ALTER TABLE public.cdr OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16398)
-- Name: dtproperties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dtproperties (
    id integer NOT NULL,
    objectid integer,
    property character varying(64) NOT NULL,
    value character varying(255),
    uvalue character varying(255),
    lvalue bytea,
    version integer NOT NULL
);


ALTER TABLE public.dtproperties OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16403)
-- Name: location; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.location (
    "USERNAME" character varying(64) NOT NULL,
    "DOMAIN_NAME" character varying(128) NOT NULL,
    "CONTACT" character varying(255) NOT NULL,
    "EXPIRE" integer,
    "EXPIRE_TIME" timestamp without time zone,
    "CALL_ID" character varying(255),
    "CSEQ" integer,
    "LAST_MODIFIED" timestamp without time zone,
    "USER_AGENT" character varying(255),
    "LOCATION_ID" bigint NOT NULL,
    "BEHIND_NAT" character(1)
);


ALTER TABLE public.location OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16408)
-- Name: routing_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.routing_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.routing_id_seq OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16409)
-- Name: routing; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.routing (
    "ORDER_ID" integer NOT NULL,
    "CPN" character varying(256),
    "DNIS" character varying(256),
    "SOURCE_IP_START" character(15),
    "SOURCE_IP_END" character(15),
    "P_RULE" character varying(1024),
    "PROXY_IP" character(15),
    "PROXY_PORT" integer,
    "DOMAIN_NAME" character varying(128),
    "ROUTING_ID" bigint DEFAULT nextval('public.routing_id_seq'::regclass) NOT NULL
);


ALTER TABLE public.routing OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16415)
-- Name: subscriber; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriber (
    "USERNAME" character varying(64) NOT NULL,
    "DOMAIN_NAME" character varying(128) NOT NULL,
    "PASSWORD" character varying(25),
    "FIRST_NAME" character varying(25),
    "LAST_NAME" character varying(45),
    "PHONE" character varying(15),
    "EMAIL_ADDRESS" character varying(50),
    "DATETIME_CREATED" timestamp without time zone,
    "DATETIME_MODIFIED" timestamp without time zone,
    "CONFORMATION" character varying(64),
    "HA1" character varying(128),
    "HA1B" character varying(128),
    "SUBSCRIBER_ID" bigint NOT NULL
);


ALTER TABLE public.subscriber OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16420)
-- Name: web_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.web_config (
    "CONFIG_ID" bigint NOT NULL,
    "CONFIG_NAME" character varying(256) NOT NULL,
    "CONFIG_VALUE" character varying(256) NOT NULL
);


ALTER TABLE public.web_config OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16425)
-- Name: web_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.web_permission (
    "PERMISSION_ID" bigint NOT NULL,
    "PERMISSION_TYPE" character varying(256) NOT NULL,
    "PERMISSION_OBJECT" character varying(256) NOT NULL,
    "PERMISSION_RIGHT" character varying(256) NOT NULL,
    "PERMISSION_DESCRIPTION" character varying(256) NOT NULL
);


ALTER TABLE public.web_permission OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16430)
-- Name: web_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.web_role (
    "ROLE_ID" bigint NOT NULL,
    "ROLE_NAME" character varying(32) NOT NULL,
    "ROLE_DESCRIPTION" character varying(256) NOT NULL
);


ALTER TABLE public.web_role OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16433)
-- Name: web_role_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.web_role_permission (
    "ROLE_ID" bigint NOT NULL,
    "PERMISSION_ID" bigint NOT NULL
);


ALTER TABLE public.web_role_permission OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16436)
-- Name: web_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.web_user (
    "USER_ID" bigint NOT NULL,
    "USERNAME" character varying(256) NOT NULL,
    "PWD" character varying(256) NOT NULL,
    "FIRST_NAME" character varying(256) NOT NULL,
    "LAST_NAME" character varying(256) NOT NULL,
    "LAST_PWD_CHANGE_DATE" timestamp without time zone,
    "LAST_LOGIN_DATE" timestamp without time zone,
    "IS_ACTIVE" character varying(1) NOT NULL,
    "CREATED" timestamp without time zone NOT NULL
);


ALTER TABLE public.web_user OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16441)
-- Name: web_user_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.web_user_role (
    "USER_ID" bigint NOT NULL,
    "ROLE_ID" bigint NOT NULL
);


ALTER TABLE public.web_user_role OWNER TO postgres;

--
-- TOC entry 4947 (class 0 OID 16387)
-- Dependencies: 218
-- Data for Name: acl; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.acl ("ORDER_ID", "SOURCE_IP_START", "SOURCE_IP_END", "ALLOW", "ACL_ID") FROM stdin;
1	192.168.1.50	192.168.1.60	1	1
3	192.168.1.70	192.168.1.80	0	2
\.


--
-- TOC entry 4949 (class 0 OID 16392)
-- Dependencies: 220
-- Data for Name: cdr; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cdr ("CDR_ID", "SETUP_TIME", "DISCONNECT_TIME", "CONNECT_TIME", "CPN", "DNIS", "ROUTE", "ROUTE_PORT", "SESSION_TIME", "DISCONNECT_CAUSE", "CLOSING_LEG", "RECORD_TIME") FROM stdin;
\.


--
-- TOC entry 4950 (class 0 OID 16398)
-- Dependencies: 221
-- Data for Name: dtproperties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dtproperties (id, objectid, property, value, uvalue, lvalue, version) FROM stdin;
\.


--
-- TOC entry 4951 (class 0 OID 16403)
-- Dependencies: 222
-- Data for Name: location; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.location ("USERNAME", "DOMAIN_NAME", "CONTACT", "EXPIRE", "EXPIRE_TIME", "CALL_ID", "CSEQ", "LAST_MODIFIED", "USER_AGENT", "LOCATION_ID", "BEHIND_NAT") FROM stdin;
\.


--
-- TOC entry 4953 (class 0 OID 16409)
-- Dependencies: 224
-- Data for Name: routing; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.routing ("ORDER_ID", "CPN", "DNIS", "SOURCE_IP_START", "SOURCE_IP_END", "P_RULE", "PROXY_IP", "PROXY_PORT", "DOMAIN_NAME", "ROUTING_ID") FROM stdin;
1	*	0000*	               	               	1111=	192.168.1.3    	6000		1
7	33333	55555	               	               		192.168.1.10   	6000		9
13	*	90*	\N	\N	\N	192.168.1.40   	6000	\N	20
6	1111	5555	               	               		192.168.1.3    	5080		8
2	02161234567	902121234567	               	               		192.168.1.4    	6000		2
4	90*	22222	               	               		192.168.1.6    	7000		4
5	*	888	               	               	888=118	192.168.1.10   	5060	sip.creacode.net	5
11	8723281075	0090*	\N	\N	\N	192.168.1.10   	5060	\N	15
8	08111234567	902161234567	\N	\N	\N	192.168.1.40   	6000	\N	11
9	08111234567	902121234567	\N	\N	\N	192.168.1.41   	6000	\N	12
10	11111	902161234567	\N	\N	\N	192.168.1.3    	5060	\N	13
12	908501234567	0000*	\N	\N	0000=9	192.168.1.8    	5060	\N	19
\.


--
-- TOC entry 4954 (class 0 OID 16415)
-- Dependencies: 225
-- Data for Name: subscriber; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscriber ("USERNAME", "DOMAIN_NAME", "PASSWORD", "FIRST_NAME", "LAST_NAME", "PHONE", "EMAIL_ADDRESS", "DATETIME_CREATED", "DATETIME_MODIFIED", "CONFORMATION", "HA1", "HA1B", "SUBSCRIBER_ID") FROM stdin;
11111	sip.creacode.net	1234	CallerTest	\N	03627654321	\N	\N	\N	\N	\N	\N	10
22222	sip.creacode.net	1234	CalleeTest	\N	03627654321	\N	\N	\N	\N	\N	\N	11
\.


--
-- TOC entry 4955 (class 0 OID 16420)
-- Dependencies: 226
-- Data for Name: web_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.web_config ("CONFIG_ID", "CONFIG_NAME", "CONFIG_VALUE") FROM stdin;
\.


--
-- TOC entry 4956 (class 0 OID 16425)
-- Dependencies: 227
-- Data for Name: web_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.web_permission ("PERMISSION_ID", "PERMISSION_TYPE", "PERMISSION_OBJECT", "PERMISSION_RIGHT", "PERMISSION_DESCRIPTION") FROM stdin;
\.


--
-- TOC entry 4957 (class 0 OID 16430)
-- Dependencies: 228
-- Data for Name: web_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.web_role ("ROLE_ID", "ROLE_NAME", "ROLE_DESCRIPTION") FROM stdin;
\.


--
-- TOC entry 4958 (class 0 OID 16433)
-- Dependencies: 229
-- Data for Name: web_role_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.web_role_permission ("ROLE_ID", "PERMISSION_ID") FROM stdin;
\.


--
-- TOC entry 4959 (class 0 OID 16436)
-- Dependencies: 230
-- Data for Name: web_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.web_user ("USER_ID", "USERNAME", "PWD", "FIRST_NAME", "LAST_NAME", "LAST_PWD_CHANGE_DATE", "LAST_LOGIN_DATE", "IS_ACTIVE", "CREATED") FROM stdin;
\.


--
-- TOC entry 4960 (class 0 OID 16441)
-- Dependencies: 231
-- Data for Name: web_user_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.web_user_role ("USER_ID", "ROLE_ID") FROM stdin;
\.


--
-- TOC entry 4967 (class 0 OID 0)
-- Dependencies: 217
-- Name: acl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.acl_id_seq', 5, true);


--
-- TOC entry 4968 (class 0 OID 0)
-- Dependencies: 219
-- Name: cdr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cdr_id_seq', 1958, true);


--
-- TOC entry 4969 (class 0 OID 0)
-- Dependencies: 223
-- Name: routing_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.routing_id_seq', 20, true);


--
-- TOC entry 4792 (class 2606 OID 16445)
-- Name: acl acl_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.acl
    ADD CONSTRAINT acl_pkey PRIMARY KEY ("ORDER_ID");


--
-- TOC entry 4794 (class 2606 OID 16447)
-- Name: cdr cdr_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cdr
    ADD CONSTRAINT cdr_pkey PRIMARY KEY ("CDR_ID");


--
-- TOC entry 4796 (class 2606 OID 16449)
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY ("USERNAME");


--
-- TOC entry 4798 (class 2606 OID 16451)
-- Name: routing routing_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routing
    ADD CONSTRAINT routing_pkey PRIMARY KEY ("ORDER_ID");


--
-- TOC entry 4800 (class 2606 OID 16453)
-- Name: subscriber subscriber_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber
    ADD CONSTRAINT subscriber_pkey PRIMARY KEY ("USERNAME");


--
-- TOC entry 4966 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2025-09-23 17:26:12

--
-- PostgreSQL database dump complete
--

\unrestrict CxhSaRnhGLk2dbwfAEyTUEGoiVFA2P0olvamdYUDPln2R7qBDMtrmwS7vSWBK3z

