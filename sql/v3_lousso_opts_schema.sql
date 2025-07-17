--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5



SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
-- (removed) SELECT pg_catalog.set_config('search_path', '', false);
SET search_path = public;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 240 (class 1255 OID 19771)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$;


-- ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 19634)
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    customer_id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100),
    phone character varying(20),
    address text,
    city text,
    state text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    register_token character varying(64),
    password_hash text,
    registered_at timestamp without time zone,
    is_staff boolean DEFAULT false
);


-- ALTER TABLE public.customers OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 19633)
-- Name: customers_customer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_customer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.customers_customer_id_seq OWNER TO postgres;

--
-- TOC entry 4997 (class 0 OID 0)
-- Dependencies: 221
-- Name: customers_customer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_customer_id_seq OWNED BY public.customers.customer_id;


--
-- TOC entry 228 (class 1259 OID 19662)
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    employee_id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100),
    role character varying(50)
);


-- ALTER TABLE public.employees OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 19661)
-- Name: employees_employee_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_employee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.employees_employee_id_seq OWNER TO postgres;

--
-- TOC entry 4998 (class 0 OID 0)
-- Dependencies: 227
-- Name: employees_employee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_employee_id_seq OWNED BY public.employees.employee_id;


--
-- TOC entry 234 (class 1259 OID 19707)
-- Name: item_workflow; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.item_workflow (
    workflow_id integer NOT NULL,
    item_id integer,
    task_id integer,
    sequence integer,
    notes text
);


-- ALTER TABLE public.item_workflow OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 19706)
-- Name: item_workflow_workflow_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.item_workflow_workflow_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.item_workflow_workflow_id_seq OWNER TO postgres;

--
-- TOC entry 4999 (class 0 OID 0)
-- Dependencies: 233
-- Name: item_workflow_workflow_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.item_workflow_workflow_id_seq OWNED BY public.item_workflow.workflow_id;


--
-- TOC entry 232 (class 1259 OID 19685)
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    item_id integer NOT NULL,
    order_id integer,
    barcode character varying(50),
    description text,
    status character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    product_code character varying(50) NOT NULL
);


-- ALTER TABLE public.order_items OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 19684)
-- Name: order_items_item_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_items_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.order_items_item_id_seq OWNER TO postgres;

--
-- TOC entry 5000 (class 0 OID 0)
-- Dependencies: 231
-- Name: order_items_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

-- ALTER SEQUENCE public.order_items_item_id_seq OWNED BY public.order_items.item_id;


--
-- TOC entry 238 (class 1259 OID 19752)
-- Name: order_milestones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_milestones (
    milestone_id integer NOT NULL,
    order_id integer,
    milestone_name text NOT NULL,
    updated_by text,
    notes text,
    "timestamp" timestamp without time zone DEFAULT now(),
    is_client_action boolean DEFAULT false,
    is_approved boolean DEFAULT false,
    status character varying(32) DEFAULT 'Not Started'::character varying
);


-- ALTER TABLE public.order_milestones OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 19751)
-- Name: order_milestones_milestone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_milestones_milestone_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.order_milestones_milestone_id_seq OWNER TO postgres;

--
-- TOC entry 5001 (class 0 OID 0)
-- Dependencies: 237
-- Name: order_milestones_milestone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_milestones_milestone_id_seq OWNED BY public.order_milestones.milestone_id;


--
-- TOC entry 239 (class 1259 OID 19811)
-- Name: order_specs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_specs (
    order_id integer NOT NULL,
    quantity integer,
    repair_glue boolean,
    replace_springs boolean,
    fabric_specs text,
    back_style text,
    seat_style text,
    new_back_insert boolean,
    new_seat_insert boolean,
    back_insert_type text,
    seat_insert_type text,
    trim_style text,
    placement text,
    vendor_color text,
    frame_finish text,
    specs text,
    topcoat text,
    customer_initials text
);


-- ALTER TABLE public.order_specs OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 19669)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    customer_id integer,
    order_date date DEFAULT CURRENT_DATE,
    due_date date,
    status character varying(50) DEFAULT 'Pending'::character varying,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    qr_path text,
    pdf_path text,
    lousso_pdf_path text,
    client_pdf_path text,
    invoice_no character varying(50) DEFAULT ''::character varying NOT NULL
);


-- ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 19668)
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.orders_order_id_seq OWNER TO postgres;

--
-- TOC entry 5002 (class 0 OID 0)
-- Dependencies: 229
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- TOC entry 224 (class 1259 OID 19644)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text
);


-- ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 19643)
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.products_product_id_seq OWNER TO postgres;

--
-- TOC entry 5003 (class 0 OID 0)
-- Dependencies: 223
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- TOC entry 236 (class 1259 OID 19726)
-- Name: scan_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scan_events (
    scan_id integer NOT NULL,
    item_id integer,
    employee_id integer,
    scan_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(20) NOT NULL,
    notes text,
    milestone_id integer,
    CONSTRAINT scan_events_status_check CHECK (((status)::text = ANY ((ARRAY['Started'::character varying, 'Completed'::character varying])::text[])))
);


-- ALTER TABLE public.scan_events OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 19725)
-- Name: scan_events_scan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scan_events_scan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.scan_events_scan_id_seq OWNER TO postgres;

--
-- TOC entry 5004 (class 0 OID 0)
-- Dependencies: 235
-- Name: scan_events_scan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scan_events_scan_id_seq OWNED BY public.scan_events.scan_id;


--
-- TOC entry 226 (class 1259 OID 19653)
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    task_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    sequence integer,
    estimated_time_minutes integer
);


-- ALTER TABLE public.tasks OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 19652)
-- Name: tasks_task_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_task_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE public.tasks_task_id_seq OWNER TO postgres;

--
-- TOC entry 5005 (class 0 OID 0)
-- Dependencies: 225
-- Name: tasks_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_task_id_seq OWNED BY public.tasks.task_id;


--
-- TOC entry 4791 (class 2604 OID 19637)
-- Name: customers customer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN customer_id SET DEFAULT nextval('public.customers_customer_id_seq'::regclass);


--
-- TOC entry 4796 (class 2604 OID 19665)
-- Name: employees employee_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN employee_id SET DEFAULT nextval('public.employees_employee_id_seq'::regclass);


--
-- TOC entry 4805 (class 2604 OID 19710)
-- Name: item_workflow workflow_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_workflow ALTER COLUMN workflow_id SET DEFAULT nextval('public.item_workflow_workflow_id_seq'::regclass);


--
-- TOC entry 4803 (class 2604 OID 19688)
-- Name: order_items item_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items ALTER COLUMN item_id SET DEFAULT nextval('public.order_items_item_id_seq'::regclass);


--
-- TOC entry 4808 (class 2604 OID 19755)
-- Name: order_milestones milestone_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_milestones ALTER COLUMN milestone_id SET DEFAULT nextval('public.order_milestones_milestone_id_seq'::regclass);


--
-- TOC entry 4797 (class 2604 OID 19672)
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- TOC entry 4794 (class 2604 OID 19647)
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- TOC entry 4806 (class 2604 OID 19729)
-- Name: scan_events scan_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scan_events ALTER COLUMN scan_id SET DEFAULT nextval('public.scan_events_scan_id_seq'::regclass);


--
-- TOC entry 4795 (class 2604 OID 19656)
-- Name: tasks task_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN task_id SET DEFAULT nextval('public.tasks_task_id_seq'::regclass);


--
-- TOC entry 4815 (class 2606 OID 19642)
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customer_id);


--
-- TOC entry 4821 (class 2606 OID 19667)
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (employee_id);


--
-- TOC entry 4829 (class 2606 OID 19714)
-- Name: item_workflow item_workflow_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_workflow
    ADD CONSTRAINT item_workflow_pkey PRIMARY KEY (workflow_id);


--
-- TOC entry 4825 (class 2606 OID 19695)
-- Name: order_items order_items_barcode_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_barcode_key UNIQUE (barcode);


--
-- TOC entry 4827 (class 2606 OID 19693)
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (item_id);


--
-- TOC entry 4833 (class 2606 OID 19762)
-- Name: order_milestones order_milestones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_milestones
    ADD CONSTRAINT order_milestones_pkey PRIMARY KEY (milestone_id);


--
-- TOC entry 4835 (class 2606 OID 19817)
-- Name: order_specs order_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_specs
    ADD CONSTRAINT order_specs_pkey PRIMARY KEY (order_id);


--
-- TOC entry 4823 (class 2606 OID 19678)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- TOC entry 4817 (class 2606 OID 19651)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- TOC entry 4831 (class 2606 OID 19735)
-- Name: scan_events scan_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scan_events
    ADD CONSTRAINT scan_events_pkey PRIMARY KEY (scan_id);


--
-- TOC entry 4819 (class 2606 OID 19660)
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (task_id);


--
-- TOC entry 4846 (class 2620 OID 19773)
-- Name: order_items trg_order_items_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_order_items_updated_at BEFORE UPDATE ON public.order_items FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4845 (class 2620 OID 19772)
-- Name: orders trg_orders_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_orders_updated_at BEFORE UPDATE ON public.orders FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4838 (class 2606 OID 19715)
-- Name: item_workflow item_workflow_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_workflow
    ADD CONSTRAINT item_workflow_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.order_items(item_id);


--
-- TOC entry 4839 (class 2606 OID 19720)
-- Name: item_workflow item_workflow_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_workflow
    ADD CONSTRAINT item_workflow_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id);


--
-- TOC entry 4837 (class 2606 OID 19696)
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id);


--
-- TOC entry 4843 (class 2606 OID 19763)
-- Name: order_milestones order_milestones_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_milestones
    ADD CONSTRAINT order_milestones_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- TOC entry 4844 (class 2606 OID 19818)
-- Name: order_specs order_specs_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_specs
    ADD CONSTRAINT order_specs_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id);


--
-- TOC entry 4836 (class 2606 OID 19679)
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id);


--
-- TOC entry 4840 (class 2606 OID 28040)
-- Name: scan_events scan_events_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scan_events
    ADD CONSTRAINT scan_events_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.customers(customer_id);


--
-- TOC entry 4841 (class 2606 OID 19736)
-- Name: scan_events scan_events_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scan_events
    ADD CONSTRAINT scan_events_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.order_items(item_id);


--
-- TOC entry 4842 (class 2606 OID 28035)
-- Name: scan_events scan_events_milestone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scan_events
    ADD CONSTRAINT scan_events_milestone_id_fkey FOREIGN KEY (milestone_id) REFERENCES public.order_milestones(milestone_id);


-- Completed on 2025-07-16 22:07:26

--
-- PostgreSQL database dump complete
--

