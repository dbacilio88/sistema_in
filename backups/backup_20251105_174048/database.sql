--
-- PostgreSQL database dump
--

\restrict r4QjZIlLQRTUcHt0EeRCfKH0vGSJqECEv9XQheO9OmXGQn19Va2Xo1QUFOWnE92

-- Dumped from database version 16.10
-- Dumped by pg_dump version 16.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.vehicles_vehicleownership DROP CONSTRAINT IF EXISTS vehicles_vehicleowne_vehicle_id_69ab1291_fk_vehicles_;
ALTER TABLE IF EXISTS ONLY public.vehicles_vehicleownership DROP CONSTRAINT IF EXISTS vehicles_vehicleowne_driver_id_55a24c8f_fk_vehicles_;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_user_id_92473840_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissio_permission_id_6d08dcd2_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_user_id_f500bee5_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_group_id_2f3517aa_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_outstandingtoken DROP CONSTRAINT IF EXISTS token_blacklist_outstandingtoken_user_id_83bc629a_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_blacklistedtoken DROP CONSTRAINT IF EXISTS token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk;
ALTER TABLE IF EXISTS ONLY public.notifications_notification DROP CONSTRAINT IF EXISTS notifications_notification_user_id_b5e8c0ff_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.ml_models_mlprediction DROP CONSTRAINT IF EXISTS ml_models_mlprediction_driver_id_e3b1005b_fk_vehicles_driver_id;
ALTER TABLE IF EXISTS ONLY public.ml_models_mlprediction DROP CONSTRAINT IF EXISTS ml_models_mlpredicti_model_id_938225b6_fk_ml_models;
ALTER TABLE IF EXISTS ONLY public.ml_models_mlprediction DROP CONSTRAINT IF EXISTS ml_models_mlpredicti_infraction_id_bd10a47a_fk_infractio;
ALTER TABLE IF EXISTS ONLY public.ml_models_mlmodel DROP CONSTRAINT IF EXISTS ml_models_mlmodel_deployed_by_id_ba48cf24_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.ml_models_mlmodel DROP CONSTRAINT IF EXISTS ml_models_mlmodel_created_by_id_f196f145_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.login_history DROP CONSTRAINT IF EXISTS login_history_user_id_0eeaebb8_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.infractions_vehicledetection DROP CONSTRAINT IF EXISTS infractions_vehicled_zone_id_9fbd9c83_fk_devices_z;
ALTER TABLE IF EXISTS ONLY public.infractions_vehicledetection DROP CONSTRAINT IF EXISTS infractions_vehicled_vehicle_id_ab143c31_fk_vehicles_;
ALTER TABLE IF EXISTS ONLY public.infractions_vehicledetection DROP CONSTRAINT IF EXISTS infractions_vehicled_infraction_id_37ea5a19_fk_infractio;
ALTER TABLE IF EXISTS ONLY public.infractions_vehicledetection DROP CONSTRAINT IF EXISTS infractions_vehicled_device_id_8b59ab3f_fk_devices_d;
ALTER TABLE IF EXISTS ONLY public.infractions_infractionevent DROP CONSTRAINT IF EXISTS infractions_infractionevent_user_id_b557494f_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.infractions_infraction DROP CONSTRAINT IF EXISTS infractions_infraction_zone_id_1456fb12_fk_devices_zone_id;
ALTER TABLE IF EXISTS ONLY public.infractions_infraction DROP CONSTRAINT IF EXISTS infractions_infraction_reviewed_by_id_afcad296_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.infractions_infraction DROP CONSTRAINT IF EXISTS infractions_infraction_driver_id_774bc88d_fk_vehicles_driver_id;
ALTER TABLE IF EXISTS ONLY public.infractions_infraction DROP CONSTRAINT IF EXISTS infractions_infraction_device_id_4291d43e_fk_devices_device_id;
ALTER TABLE IF EXISTS ONLY public.infractions_infraction DROP CONSTRAINT IF EXISTS infractions_infracti_vehicle_id_302a304c_fk_vehicles_;
ALTER TABLE IF EXISTS ONLY public.infractions_infractionevent DROP CONSTRAINT IF EXISTS infractions_infracti_infraction_id_a0f5a29d_fk_infractio;
ALTER TABLE IF EXISTS ONLY public.infractions_detectionstatistics DROP CONSTRAINT IF EXISTS infractions_detectio_zone_id_949f69d4_fk_devices_z;
ALTER TABLE IF EXISTS ONLY public.infractions_detectionstatistics DROP CONSTRAINT IF EXISTS infractions_detectio_device_id_fed00d97_fk_devices_d;
ALTER TABLE IF EXISTS ONLY public.infractions_appeal DROP CONSTRAINT IF EXISTS infractions_appeal_reviewed_by_id_49a1d0f8_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.infractions_appeal DROP CONSTRAINT IF EXISTS infractions_appeal_infraction_id_75273a24_fk_infractio;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_periodictask DROP CONSTRAINT IF EXISTS django_celery_beat_p_solar_id_a87ce72c_fk_django_ce;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_periodictask DROP CONSTRAINT IF EXISTS django_celery_beat_p_interval_id_a8ca27da_fk_django_ce;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_periodictask DROP CONSTRAINT IF EXISTS django_celery_beat_p_crontab_id_d3cba168_fk_django_ce;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_periodictask DROP CONSTRAINT IF EXISTS django_celery_beat_p_clocked_id_47a69f82_fk_django_ce;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.devices_deviceevent DROP CONSTRAINT IF EXISTS devices_deviceevent_device_id_5294ea65_fk_devices_device_id;
ALTER TABLE IF EXISTS ONLY public.devices_device DROP CONSTRAINT IF EXISTS devices_device_zone_id_a6931c33_fk_devices_zone_id;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
DROP INDEX IF EXISTS public.vehicles_vehicleownership_vehicle_id_69ab1291;
DROP INDEX IF EXISTS public.vehicles_vehicleownership_driver_id_55a24c8f;
DROP INDEX IF EXISTS public.vehicles_vehicle_license_plate_9d0c162b_like;
DROP INDEX IF EXISTS public.vehicles_ve_vehicle_a3bb7e_idx;
DROP INDEX IF EXISTS public.vehicles_ve_owner_d_b3eb80_idx;
DROP INDEX IF EXISTS public.vehicles_ve_license_907c55_idx;
DROP INDEX IF EXISTS public.vehicles_ve_is_want_b9a47b_idx;
DROP INDEX IF EXISTS public.vehicles_ve_is_stol_f22ded_idx;
DROP INDEX IF EXISTS public.vehicles_ve_is_prim_afe9c0_idx;
DROP INDEX IF EXISTS public.vehicles_ve_driver__d1090b_idx;
DROP INDEX IF EXISTS public.vehicles_driver_document_number_92b72614_like;
DROP INDEX IF EXISTS public.vehicles_dr_license_de2c16_idx;
DROP INDEX IF EXISTS public.vehicles_dr_is_susp_92ae1a_idx;
DROP INDEX IF EXISTS public.vehicles_dr_documen_45aca3_idx;
DROP INDEX IF EXISTS public.users_username_e8658fc8_like;
DROP INDEX IF EXISTS public.users_usernam_b4c624_idx;
DROP INDEX IF EXISTS public.users_user_permissions_user_id_92473840;
DROP INDEX IF EXISTS public.users_user_permissions_permission_id_6d08dcd2;
DROP INDEX IF EXISTS public.users_role_f0571928_like;
DROP INDEX IF EXISTS public.users_role_f0571928;
DROP INDEX IF EXISTS public.users_role_a8f2ba_idx;
DROP INDEX IF EXISTS public.users_groups_user_id_f500bee5;
DROP INDEX IF EXISTS public.users_groups_group_id_2f3517aa;
DROP INDEX IF EXISTS public.users_email_a7cfd1_idx;
DROP INDEX IF EXISTS public.users_email_0ea73cca_like;
DROP INDEX IF EXISTS public.users_dni_b6cb98d3_like;
DROP INDEX IF EXISTS public.token_blacklist_outstandingtoken_user_id_83bc629a;
DROP INDEX IF EXISTS public.token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_like;
DROP INDEX IF EXISTS public.notifications_notification_user_id_b5e8c0ff;
DROP INDEX IF EXISTS public.notificatio_user_id_427e4b_idx;
DROP INDEX IF EXISTS public.notificatio_created_ae6ed6_idx;
DROP INDEX IF EXISTS public.ml_models_mlprediction_predicted_at_c74fbb03;
DROP INDEX IF EXISTS public.ml_models_mlprediction_model_id_938225b6;
DROP INDEX IF EXISTS public.ml_models_mlprediction_infraction_id_bd10a47a;
DROP INDEX IF EXISTS public.ml_models_mlprediction_driver_id_e3b1005b;
DROP INDEX IF EXISTS public.ml_models_mlmodel_deployed_by_id_ba48cf24;
DROP INDEX IF EXISTS public.ml_models_mlmodel_created_by_id_f196f145;
DROP INDEX IF EXISTS public.ml_models_m_predict_472780_idx;
DROP INDEX IF EXISTS public.ml_models_m_model_n_f508f2_idx;
DROP INDEX IF EXISTS public.ml_models_m_model_i_23f478_idx;
DROP INDEX IF EXISTS public.ml_models_m_last_pr_205647_idx;
DROP INDEX IF EXISTS public.ml_models_m_is_acti_afbf29_idx;
DROP INDEX IF EXISTS public.ml_models_m_infract_ed1726_idx;
DROP INDEX IF EXISTS public.ml_models_m_driver__5f0e92_idx;
DROP INDEX IF EXISTS public.ml_models_m_deploym_14de3d_idx;
DROP INDEX IF EXISTS public.login_history_user_id_0eeaebb8;
DROP INDEX IF EXISTS public.login_history_login_at_5d8b3f90;
DROP INDEX IF EXISTS public.login_histo_user_id_7d22b5_idx;
DROP INDEX IF EXISTS public.login_histo_ip_addr_9672e0_idx;
DROP INDEX IF EXISTS public.infractions_zone_id_e4f2de_idx;
DROP INDEX IF EXISTS public.infractions_zone_id_4187a0_idx;
DROP INDEX IF EXISTS public.infractions_vehicledetection_zone_id_9fbd9c83;
DROP INDEX IF EXISTS public.infractions_vehicledetection_vehicle_id_ab143c31;
DROP INDEX IF EXISTS public.infractions_vehicledetection_infraction_id_37ea5a19;
DROP INDEX IF EXISTS public.infractions_vehicledetection_device_id_8b59ab3f;
DROP INDEX IF EXISTS public.infractions_vehicledetection_detected_at_1274a0a9;
DROP INDEX IF EXISTS public.infractions_vehicle_dbbc65_idx;
DROP INDEX IF EXISTS public.infractions_vehicle_bb01cf_idx;
DROP INDEX IF EXISTS public.infractions_status_f3736a_idx;
DROP INDEX IF EXISTS public.infractions_status_325877_idx;
DROP INDEX IF EXISTS public.infractions_source_035e58_idx;
DROP INDEX IF EXISTS public.infractions_period__e5d1df_idx;
DROP INDEX IF EXISTS public.infractions_license_cd67b1_idx;
DROP INDEX IF EXISTS public.infractions_license_4e6e5c_idx;
DROP INDEX IF EXISTS public.infractions_infractionevent_user_id_b557494f;
DROP INDEX IF EXISTS public.infractions_infractionevent_timestamp_529a1bc7;
DROP INDEX IF EXISTS public.infractions_infractionevent_infraction_id_a0f5a29d;
DROP INDEX IF EXISTS public.infractions_infraction_zone_id_1456fb12;
DROP INDEX IF EXISTS public.infractions_infraction_vehicle_id_302a304c;
DROP INDEX IF EXISTS public.infractions_infraction_reviewed_by_id_afcad296;
DROP INDEX IF EXISTS public.infractions_infraction_infraction_code_291ce723_like;
DROP INDEX IF EXISTS public.infractions_infraction_driver_id_774bc88d;
DROP INDEX IF EXISTS public.infractions_infraction_device_id_4291d43e;
DROP INDEX IF EXISTS public.infractions_infraction_detected_at_cf8801f5;
DROP INDEX IF EXISTS public.infractions_infract_ee0e51_idx;
DROP INDEX IF EXISTS public.infractions_infract_83f8da_idx;
DROP INDEX IF EXISTS public.infractions_infract_679c79_idx;
DROP INDEX IF EXISTS public.infractions_infract_089142_idx;
DROP INDEX IF EXISTS public.infractions_has_inf_2b770c_idx;
DROP INDEX IF EXISTS public.infractions_event_t_728a74_idx;
DROP INDEX IF EXISTS public.infractions_device__fe5c84_idx;
DROP INDEX IF EXISTS public.infractions_device__b22ab8_idx;
DROP INDEX IF EXISTS public.infractions_device__696240_idx;
DROP INDEX IF EXISTS public.infractions_detectionstatistics_zone_id_949f69d4;
DROP INDEX IF EXISTS public.infractions_detectionstatistics_period_start_d3e34774;
DROP INDEX IF EXISTS public.infractions_detectionstatistics_device_id_fed00d97;
DROP INDEX IF EXISTS public.infractions_appella_1bcf2c_idx;
DROP INDEX IF EXISTS public.infractions_appeal_reviewed_by_id_49a1d0f8;
DROP INDEX IF EXISTS public.django_session_session_key_c0390e0f_like;
DROP INDEX IF EXISTS public.django_session_expire_date_a5c62663;
DROP INDEX IF EXISTS public.django_celery_beat_periodictask_solar_id_a87ce72c;
DROP INDEX IF EXISTS public.django_celery_beat_periodictask_name_265a36b7_like;
DROP INDEX IF EXISTS public.django_celery_beat_periodictask_interval_id_a8ca27da;
DROP INDEX IF EXISTS public.django_celery_beat_periodictask_crontab_id_d3cba168;
DROP INDEX IF EXISTS public.django_celery_beat_periodictask_clocked_id_47a69f82;
DROP INDEX IF EXISTS public.django_admin_log_user_id_c564eba6;
DROP INDEX IF EXISTS public.django_admin_log_content_type_id_c4bce8eb;
DROP INDEX IF EXISTS public.devices_zone_name_66174faa_like;
DROP INDEX IF EXISTS public.devices_zone_code_f2c56271_like;
DROP INDEX IF EXISTS public.devices_zon_is_acti_e5a7fc_idx;
DROP INDEX IF EXISTS public.devices_zon_code_729a87_idx;
DROP INDEX IF EXISTS public.devices_deviceevent_timestamp_21194ee8;
DROP INDEX IF EXISTS public.devices_deviceevent_device_id_5294ea65;
DROP INDEX IF EXISTS public.devices_device_zone_id_a6931c33;
DROP INDEX IF EXISTS public.devices_device_code_09976111_like;
DROP INDEX IF EXISTS public.devices_dev_zone_id_926c7c_idx;
DROP INDEX IF EXISTS public.devices_dev_status_bbf58f_idx;
DROP INDEX IF EXISTS public.devices_dev_event_t_6d20f2_idx;
DROP INDEX IF EXISTS public.devices_dev_device__5b0de9_idx;
DROP INDEX IF EXISTS public.devices_dev_device__0d8d82_idx;
DROP INDEX IF EXISTS public.devices_dev_code_767230_idx;
DROP INDEX IF EXISTS public.auth_permission_content_type_id_2f476e4b;
DROP INDEX IF EXISTS public.auth_group_permissions_permission_id_84c5c92e;
DROP INDEX IF EXISTS public.auth_group_permissions_group_id_b120cbf9;
DROP INDEX IF EXISTS public.auth_group_name_a6ea08ec_like;
ALTER TABLE IF EXISTS ONLY public.vehicles_vehicleownership DROP CONSTRAINT IF EXISTS vehicles_vehicleownership_pkey;
ALTER TABLE IF EXISTS ONLY public.vehicles_vehicle DROP CONSTRAINT IF EXISTS vehicles_vehicle_pkey;
ALTER TABLE IF EXISTS ONLY public.vehicles_vehicle DROP CONSTRAINT IF EXISTS vehicles_vehicle_license_plate_key;
ALTER TABLE IF EXISTS ONLY public.vehicles_driver DROP CONSTRAINT IF EXISTS vehicles_driver_pkey;
ALTER TABLE IF EXISTS ONLY public.vehicles_driver DROP CONSTRAINT IF EXISTS vehicles_driver_document_number_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_username_key;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_user_id_permission_id_3b86cbdf_uniq;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_user_id_group_id_fc7788e8_uniq;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_email_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_dni_key;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_outstandingtoken DROP CONSTRAINT IF EXISTS token_blacklist_outstandingtoken_pkey;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_outstandingtoken DROP CONSTRAINT IF EXISTS token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_blacklistedtoken DROP CONSTRAINT IF EXISTS token_blacklist_blacklistedtoken_token_id_key;
ALTER TABLE IF EXISTS ONLY public.token_blacklist_blacklistedtoken DROP CONSTRAINT IF EXISTS token_blacklist_blacklistedtoken_pkey;
ALTER TABLE IF EXISTS ONLY public.notifications_notification DROP CONSTRAINT IF EXISTS notifications_notification_pkey;
ALTER TABLE IF EXISTS ONLY public.ml_models_mlprediction DROP CONSTRAINT IF EXISTS ml_models_mlprediction_pkey;
ALTER TABLE IF EXISTS ONLY public.ml_models_mlmodel DROP CONSTRAINT IF EXISTS ml_models_mlmodel_pkey;
ALTER TABLE IF EXISTS ONLY public.ml_models_mlmodel DROP CONSTRAINT IF EXISTS ml_models_mlmodel_model_name_version_c1172b3a_uniq;
ALTER TABLE IF EXISTS ONLY public.login_history DROP CONSTRAINT IF EXISTS login_history_pkey;
ALTER TABLE IF EXISTS ONLY public.infractions_vehicledetection DROP CONSTRAINT IF EXISTS infractions_vehicledetection_pkey;
ALTER TABLE IF EXISTS ONLY public.infractions_infractionevent DROP CONSTRAINT IF EXISTS infractions_infractionevent_pkey;
ALTER TABLE IF EXISTS ONLY public.infractions_infraction DROP CONSTRAINT IF EXISTS infractions_infraction_pkey;
ALTER TABLE IF EXISTS ONLY public.infractions_infraction DROP CONSTRAINT IF EXISTS infractions_infraction_infraction_code_key;
ALTER TABLE IF EXISTS ONLY public.infractions_detectionstatistics DROP CONSTRAINT IF EXISTS infractions_detectionstatistics_pkey;
ALTER TABLE IF EXISTS ONLY public.infractions_detectionstatistics DROP CONSTRAINT IF EXISTS infractions_detectionsta_period_type_period_start_b6708d69_uniq;
ALTER TABLE IF EXISTS ONLY public.infractions_appeal DROP CONSTRAINT IF EXISTS infractions_appeal_pkey;
ALTER TABLE IF EXISTS ONLY public.infractions_appeal DROP CONSTRAINT IF EXISTS infractions_appeal_infraction_id_key;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_solarschedule DROP CONSTRAINT IF EXISTS django_celery_beat_solarschedule_pkey;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_solarschedule DROP CONSTRAINT IF EXISTS django_celery_beat_solar_event_latitude_longitude_ba64999a_uniq;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_periodictasks DROP CONSTRAINT IF EXISTS django_celery_beat_periodictasks_pkey;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_periodictask DROP CONSTRAINT IF EXISTS django_celery_beat_periodictask_pkey;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_periodictask DROP CONSTRAINT IF EXISTS django_celery_beat_periodictask_name_key;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_intervalschedule DROP CONSTRAINT IF EXISTS django_celery_beat_intervalschedule_pkey;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_crontabschedule DROP CONSTRAINT IF EXISTS django_celery_beat_crontabschedule_pkey;
ALTER TABLE IF EXISTS ONLY public.django_celery_beat_clockedschedule DROP CONSTRAINT IF EXISTS django_celery_beat_clockedschedule_pkey;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.devices_zone DROP CONSTRAINT IF EXISTS devices_zone_pkey;
ALTER TABLE IF EXISTS ONLY public.devices_zone DROP CONSTRAINT IF EXISTS devices_zone_name_key;
ALTER TABLE IF EXISTS ONLY public.devices_zone DROP CONSTRAINT IF EXISTS devices_zone_code_key;
ALTER TABLE IF EXISTS ONLY public.devices_deviceevent DROP CONSTRAINT IF EXISTS devices_deviceevent_pkey;
ALTER TABLE IF EXISTS ONLY public.devices_device DROP CONSTRAINT IF EXISTS devices_device_pkey;
ALTER TABLE IF EXISTS ONLY public.devices_device DROP CONSTRAINT IF EXISTS devices_device_code_key;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
DROP TABLE IF EXISTS public.vehicles_vehicleownership;
DROP TABLE IF EXISTS public.vehicles_vehicle;
DROP TABLE IF EXISTS public.vehicles_driver;
DROP TABLE IF EXISTS public.users_user_permissions;
DROP TABLE IF EXISTS public.users_groups;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.token_blacklist_outstandingtoken;
DROP TABLE IF EXISTS public.token_blacklist_blacklistedtoken;
DROP TABLE IF EXISTS public.notifications_notification;
DROP TABLE IF EXISTS public.ml_models_mlprediction;
DROP TABLE IF EXISTS public.ml_models_mlmodel;
DROP TABLE IF EXISTS public.login_history;
DROP TABLE IF EXISTS public.infractions_vehicledetection;
DROP TABLE IF EXISTS public.infractions_infractionevent;
DROP TABLE IF EXISTS public.infractions_infraction;
DROP TABLE IF EXISTS public.infractions_detectionstatistics;
DROP TABLE IF EXISTS public.infractions_appeal;
DROP SEQUENCE IF EXISTS public.infraction_code_seq;
DROP TABLE IF EXISTS public.django_session;
DROP TABLE IF EXISTS public.django_migrations;
DROP TABLE IF EXISTS public.django_content_type;
DROP TABLE IF EXISTS public.django_celery_beat_solarschedule;
DROP TABLE IF EXISTS public.django_celery_beat_periodictasks;
DROP TABLE IF EXISTS public.django_celery_beat_periodictask;
DROP TABLE IF EXISTS public.django_celery_beat_intervalschedule;
DROP TABLE IF EXISTS public.django_celery_beat_crontabschedule;
DROP TABLE IF EXISTS public.django_celery_beat_clockedschedule;
DROP TABLE IF EXISTS public.django_admin_log;
DROP TABLE IF EXISTS public.devices_zone;
DROP TABLE IF EXISTS public.devices_deviceevent;
DROP TABLE IF EXISTS public.devices_device;
DROP TABLE IF EXISTS public.auth_permission;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP TABLE IF EXISTS public.auth_group;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: devices_device; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.devices_device (
    id uuid NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    device_type character varying(20) NOT NULL,
    location_lat numeric(9,6),
    location_lon numeric(9,6),
    address character varying(255) NOT NULL,
    ip_address inet NOT NULL,
    rtsp_url character varying(255) NOT NULL,
    rtsp_username character varying(50) NOT NULL,
    rtsp_password character varying(100) NOT NULL,
    model character varying(100) NOT NULL,
    manufacturer character varying(100) NOT NULL,
    firmware_version character varying(50) NOT NULL,
    resolution character varying(20) NOT NULL,
    fps integer NOT NULL,
    calibration_matrix jsonb,
    status character varying(20) NOT NULL,
    last_seen timestamp with time zone,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    zone_id uuid NOT NULL
);


--
-- Name: devices_deviceevent; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.devices_deviceevent (
    id uuid NOT NULL,
    event_type character varying(20) NOT NULL,
    message text NOT NULL,
    metadata jsonb NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    device_id uuid NOT NULL
);


--
-- Name: devices_zone; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.devices_zone (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    description text NOT NULL,
    boundary jsonb,
    center_point_lat numeric(9,6),
    center_point_lon numeric(9,6),
    speed_limit integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id uuid NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_celery_beat_clockedschedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_celery_beat_clockedschedule (
    id integer NOT NULL,
    clocked_time timestamp with time zone NOT NULL
);


--
-- Name: django_celery_beat_clockedschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_celery_beat_clockedschedule ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_celery_beat_clockedschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_celery_beat_crontabschedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_celery_beat_crontabschedule (
    id integer NOT NULL,
    minute character varying(240) NOT NULL,
    hour character varying(96) NOT NULL,
    day_of_week character varying(64) NOT NULL,
    day_of_month character varying(124) NOT NULL,
    month_of_year character varying(64) NOT NULL,
    timezone character varying(63) NOT NULL
);


--
-- Name: django_celery_beat_crontabschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_celery_beat_crontabschedule ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_celery_beat_crontabschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_celery_beat_intervalschedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_celery_beat_intervalschedule (
    id integer NOT NULL,
    every integer NOT NULL,
    period character varying(24) NOT NULL
);


--
-- Name: django_celery_beat_intervalschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_celery_beat_intervalschedule ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_celery_beat_intervalschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_celery_beat_periodictask; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_celery_beat_periodictask (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    task character varying(200) NOT NULL,
    args text NOT NULL,
    kwargs text NOT NULL,
    queue character varying(200),
    exchange character varying(200),
    routing_key character varying(200),
    expires timestamp with time zone,
    enabled boolean NOT NULL,
    last_run_at timestamp with time zone,
    total_run_count integer NOT NULL,
    date_changed timestamp with time zone NOT NULL,
    description text NOT NULL,
    crontab_id integer,
    interval_id integer,
    solar_id integer,
    one_off boolean NOT NULL,
    start_time timestamp with time zone,
    priority integer,
    headers text NOT NULL,
    clocked_id integer,
    expire_seconds integer,
    CONSTRAINT django_celery_beat_periodictask_expire_seconds_check CHECK ((expire_seconds >= 0)),
    CONSTRAINT django_celery_beat_periodictask_priority_check CHECK ((priority >= 0)),
    CONSTRAINT django_celery_beat_periodictask_total_run_count_check CHECK ((total_run_count >= 0))
);


--
-- Name: django_celery_beat_periodictask_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_celery_beat_periodictask ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_celery_beat_periodictask_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_celery_beat_periodictasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_celery_beat_periodictasks (
    ident smallint NOT NULL,
    last_update timestamp with time zone NOT NULL
);


--
-- Name: django_celery_beat_solarschedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_celery_beat_solarschedule (
    id integer NOT NULL,
    event character varying(24) NOT NULL,
    latitude numeric(9,6) NOT NULL,
    longitude numeric(9,6) NOT NULL
);


--
-- Name: django_celery_beat_solarschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_celery_beat_solarschedule ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_celery_beat_solarschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: infraction_code_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.infraction_code_seq
    START WITH 1000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: infractions_appeal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.infractions_appeal (
    id uuid NOT NULL,
    reason text NOT NULL,
    evidence_description text NOT NULL,
    supporting_documents jsonb NOT NULL,
    appellant_name character varying(200) NOT NULL,
    appellant_dni character varying(20) NOT NULL,
    appellant_phone character varying(20) NOT NULL,
    appellant_email character varying(254) NOT NULL,
    status character varying(20) NOT NULL,
    review_decision text NOT NULL,
    reviewed_at timestamp with time zone,
    submitted_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    infraction_id uuid NOT NULL,
    reviewed_by_id uuid
);


--
-- Name: infractions_detectionstatistics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.infractions_detectionstatistics (
    id uuid NOT NULL,
    period_type character varying(20) NOT NULL,
    period_start timestamp with time zone NOT NULL,
    period_end timestamp with time zone NOT NULL,
    car_count integer NOT NULL,
    truck_count integer NOT NULL,
    bus_count integer NOT NULL,
    motorcycle_count integer NOT NULL,
    bicycle_count integer NOT NULL,
    person_count integer NOT NULL,
    other_count integer NOT NULL,
    total_detections integer NOT NULL,
    total_with_plate integer NOT NULL,
    total_infractions integer NOT NULL,
    avg_confidence double precision NOT NULL,
    avg_speed double precision,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    device_id uuid,
    zone_id uuid
);


--
-- Name: infractions_infraction; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.infractions_infraction (
    id uuid NOT NULL,
    infraction_code character varying(20) NOT NULL,
    infraction_type character varying(20) NOT NULL,
    severity character varying(10) NOT NULL,
    location_lat numeric(9,6),
    location_lon numeric(9,6),
    license_plate_detected character varying(10) NOT NULL,
    license_plate_confidence double precision NOT NULL,
    detected_speed double precision,
    speed_limit integer,
    snapshot_url character varying(200) NOT NULL,
    video_url character varying(200) NOT NULL,
    evidence_metadata jsonb NOT NULL,
    status character varying(20) NOT NULL,
    reviewed_at timestamp with time zone,
    review_notes text NOT NULL,
    fine_amount numeric(10,2),
    fine_due_date date,
    payment_date timestamp with time zone,
    detected_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    device_id uuid NOT NULL,
    driver_id uuid,
    reviewed_by_id uuid,
    vehicle_id uuid,
    zone_id uuid NOT NULL,
    accident_risk double precision,
    recidivism_risk double precision,
    risk_factors jsonb NOT NULL,
    ml_prediction_time_ms double precision,
    processing_time_seconds double precision
);


--
-- Name: infractions_infractionevent; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.infractions_infractionevent (
    id uuid NOT NULL,
    event_type character varying(20) NOT NULL,
    notes text NOT NULL,
    metadata jsonb NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    infraction_id uuid NOT NULL,
    user_id uuid
);


--
-- Name: infractions_vehicledetection; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.infractions_vehicledetection (
    id uuid NOT NULL,
    vehicle_type character varying(20) NOT NULL,
    confidence double precision NOT NULL,
    license_plate_detected character varying(10) NOT NULL,
    license_plate_confidence double precision NOT NULL,
    bbox_x1 double precision NOT NULL,
    bbox_y1 double precision NOT NULL,
    bbox_x2 double precision NOT NULL,
    bbox_y2 double precision NOT NULL,
    estimated_speed double precision,
    has_infraction boolean NOT NULL,
    metadata jsonb NOT NULL,
    source character varying(50) NOT NULL,
    detected_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL,
    device_id uuid NOT NULL,
    infraction_id uuid,
    vehicle_id uuid,
    zone_id uuid
);


--
-- Name: login_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.login_history (
    id uuid NOT NULL,
    login_at timestamp with time zone NOT NULL,
    logout_at timestamp with time zone,
    ip_address inet NOT NULL,
    user_agent text NOT NULL,
    success boolean NOT NULL,
    failure_reason character varying(255) NOT NULL,
    user_id uuid NOT NULL
);


--
-- Name: ml_models_mlmodel; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ml_models_mlmodel (
    id uuid NOT NULL,
    model_name character varying(100) NOT NULL,
    version character varying(50) NOT NULL,
    model_type character varying(50) NOT NULL,
    framework character varying(50) NOT NULL,
    framework_version character varying(50) NOT NULL,
    model_path text NOT NULL,
    model_size_mb double precision,
    mlflow_run_id character varying(100) NOT NULL,
    mlflow_experiment_id character varying(100) NOT NULL,
    mlflow_model_uri text NOT NULL,
    metrics jsonb NOT NULL,
    hyperparameters jsonb NOT NULL,
    training_dataset_path text NOT NULL,
    training_dataset_size integer,
    validation_dataset_path text NOT NULL,
    test_dataset_path text NOT NULL,
    feature_names jsonb NOT NULL,
    feature_importance jsonb NOT NULL,
    is_active boolean NOT NULL,
    deployed_at timestamp with time zone,
    deployment_environment character varying(50) NOT NULL,
    prediction_count bigint NOT NULL,
    avg_prediction_time_ms double precision,
    last_prediction_at timestamp with time zone,
    data_drift_detected boolean NOT NULL,
    concept_drift_detected boolean NOT NULL,
    drift_check_at timestamp with time zone,
    description text NOT NULL,
    notes text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    metadata jsonb NOT NULL,
    created_by_id uuid,
    deployed_by_id uuid
);


--
-- Name: ml_models_mlprediction; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ml_models_mlprediction (
    id bigint NOT NULL,
    prediction_type character varying(50) NOT NULL,
    prediction_value double precision NOT NULL,
    prediction_class character varying(50) NOT NULL,
    prediction_confidence double precision,
    features jsonb NOT NULL,
    actual_value double precision,
    actual_class character varying(50) NOT NULL,
    prediction_time_ms double precision,
    predicted_at timestamp with time zone NOT NULL,
    metadata jsonb NOT NULL,
    driver_id uuid,
    infraction_id uuid,
    model_id uuid NOT NULL
);


--
-- Name: ml_models_mlprediction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.ml_models_mlprediction ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ml_models_mlprediction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: notifications_notification; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications_notification (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    message text NOT NULL,
    notification_type character varying(20) NOT NULL,
    link character varying(500),
    is_read boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    read_at timestamp with time zone,
    user_id uuid NOT NULL
);


--
-- Name: notifications_notification_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.notifications_notification ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.notifications_notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: token_blacklist_blacklistedtoken; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.token_blacklist_blacklistedtoken (
    id bigint NOT NULL,
    blacklisted_at timestamp with time zone NOT NULL,
    token_id bigint NOT NULL
);


--
-- Name: token_blacklist_blacklistedtoken_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.token_blacklist_blacklistedtoken ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.token_blacklist_blacklistedtoken_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: token_blacklist_outstandingtoken; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.token_blacklist_outstandingtoken (
    id bigint NOT NULL,
    token text NOT NULL,
    created_at timestamp with time zone,
    expires_at timestamp with time zone NOT NULL,
    user_id uuid,
    jti character varying(255) NOT NULL
);


--
-- Name: token_blacklist_outstandingtoken_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.token_blacklist_outstandingtoken ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.token_blacklist_outstandingtoken_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    password character varying(128) NOT NULL,
    id uuid NOT NULL,
    username character varying(150) NOT NULL,
    email character varying(255) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    role character varying(20) NOT NULL,
    is_active boolean NOT NULL,
    is_staff boolean NOT NULL,
    is_superuser boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    last_login timestamp with time zone,
    updated_at timestamp with time zone NOT NULL,
    phone character varying(20),
    dni character varying(8),
    profile_image character varying(100),
    failed_login_attempts integer NOT NULL,
    account_locked_until timestamp with time zone,
    password_changed_at timestamp with time zone NOT NULL,
    must_change_password boolean NOT NULL
);


--
-- Name: users_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users_groups (
    id bigint NOT NULL,
    user_id uuid NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: users_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users_user_permissions (
    id bigint NOT NULL,
    user_id uuid NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: users_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: vehicles_driver; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicles_driver (
    id uuid NOT NULL,
    document_type character varying(20) NOT NULL,
    document_number character varying(20) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    birth_date date,
    phone character varying(20) NOT NULL,
    email character varying(254) NOT NULL,
    address text NOT NULL,
    license_number character varying(20) NOT NULL,
    license_class character varying(10) NOT NULL,
    license_expiry date,
    is_suspended boolean NOT NULL,
    suspension_reason text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    risk_category character varying(20) NOT NULL,
    risk_score double precision NOT NULL,
    risk_updated_at timestamp with time zone
);


--
-- Name: vehicles_vehicle; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicles_vehicle (
    id uuid NOT NULL,
    license_plate character varying(10) NOT NULL,
    make character varying(50) NOT NULL,
    model character varying(50) NOT NULL,
    year integer,
    color character varying(30) NOT NULL,
    vehicle_type character varying(20) NOT NULL,
    owner_name character varying(200) NOT NULL,
    owner_dni character varying(20) NOT NULL,
    owner_address text NOT NULL,
    registration_date date,
    is_stolen boolean NOT NULL,
    is_wanted boolean NOT NULL,
    notes text NOT NULL,
    sunarp_last_updated timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: vehicles_vehicleownership; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicles_vehicleownership (
    id uuid NOT NULL,
    is_primary_owner boolean NOT NULL,
    ownership_percentage numeric(5,2) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    driver_id uuid NOT NULL,
    vehicle_id uuid NOT NULL
);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add blacklisted token	6	add_blacklistedtoken
22	Can change blacklisted token	6	change_blacklistedtoken
23	Can delete blacklisted token	6	delete_blacklistedtoken
24	Can view blacklisted token	6	view_blacklistedtoken
25	Can add outstanding token	7	add_outstandingtoken
26	Can change outstanding token	7	change_outstandingtoken
27	Can delete outstanding token	7	delete_outstandingtoken
28	Can view outstanding token	7	view_outstandingtoken
29	Can add crontab	8	add_crontabschedule
30	Can change crontab	8	change_crontabschedule
31	Can delete crontab	8	delete_crontabschedule
32	Can view crontab	8	view_crontabschedule
33	Can add interval	9	add_intervalschedule
34	Can change interval	9	change_intervalschedule
35	Can delete interval	9	delete_intervalschedule
36	Can view interval	9	view_intervalschedule
37	Can add periodic task	10	add_periodictask
38	Can change periodic task	10	change_periodictask
39	Can delete periodic task	10	delete_periodictask
40	Can view periodic task	10	view_periodictask
41	Can add periodic tasks	11	add_periodictasks
42	Can change periodic tasks	11	change_periodictasks
43	Can delete periodic tasks	11	delete_periodictasks
44	Can view periodic tasks	11	view_periodictasks
45	Can add solar event	12	add_solarschedule
46	Can change solar event	12	change_solarschedule
47	Can delete solar event	12	delete_solarschedule
48	Can view solar event	12	view_solarschedule
49	Can add clocked	13	add_clockedschedule
50	Can change clocked	13	change_clockedschedule
51	Can delete clocked	13	delete_clockedschedule
52	Can view clocked	13	view_clockedschedule
53	Can add User	14	add_user
54	Can change User	14	change_user
55	Can delete User	14	delete_user
56	Can view User	14	view_user
57	Can add Login History	15	add_loginhistory
58	Can change Login History	15	change_loginhistory
59	Can delete Login History	15	delete_loginhistory
60	Can view Login History	15	view_loginhistory
61	Can add zone	16	add_zone
62	Can change zone	16	change_zone
63	Can delete zone	16	delete_zone
64	Can view zone	16	view_zone
65	Can add device	17	add_device
66	Can change device	17	change_device
67	Can delete device	17	delete_device
68	Can view device	17	view_device
69	Can add device event	18	add_deviceevent
70	Can change device event	18	change_deviceevent
71	Can delete device event	18	delete_deviceevent
72	Can view device event	18	view_deviceevent
73	Can add infraction	19	add_infraction
74	Can change infraction	19	change_infraction
75	Can delete infraction	19	delete_infraction
76	Can view infraction	19	view_infraction
77	Can add appeal	20	add_appeal
78	Can change appeal	20	change_appeal
79	Can delete appeal	20	delete_appeal
80	Can view appeal	20	view_appeal
81	Can add infraction event	21	add_infractionevent
82	Can change infraction event	21	change_infractionevent
83	Can delete infraction event	21	delete_infractionevent
84	Can view infraction event	21	view_infractionevent
85	Can add Vehicle Detection	22	add_vehicledetection
86	Can change Vehicle Detection	22	change_vehicledetection
87	Can delete Vehicle Detection	22	delete_vehicledetection
88	Can view Vehicle Detection	22	view_vehicledetection
89	Can add Detection Statistics	23	add_detectionstatistics
90	Can change Detection Statistics	23	change_detectionstatistics
91	Can delete Detection Statistics	23	delete_detectionstatistics
92	Can view Detection Statistics	23	view_detectionstatistics
93	Can add driver	24	add_driver
94	Can change driver	24	change_driver
95	Can delete driver	24	delete_driver
96	Can view driver	24	view_driver
97	Can add vehicle	25	add_vehicle
98	Can change vehicle	25	change_vehicle
99	Can delete vehicle	25	delete_vehicle
100	Can view vehicle	25	view_vehicle
101	Can add vehicle ownership	26	add_vehicleownership
102	Can change vehicle ownership	26	change_vehicleownership
103	Can delete vehicle ownership	26	delete_vehicleownership
104	Can view vehicle ownership	26	view_vehicleownership
105	Can add Notificación	27	add_notification
106	Can change Notificación	27	change_notification
107	Can delete Notificación	27	delete_notification
108	Can view Notificación	27	view_notification
109	Can add ml model	28	add_mlmodel
110	Can change ml model	28	change_mlmodel
111	Can delete ml model	28	delete_mlmodel
112	Can view ml model	28	view_mlmodel
113	Can add ml prediction	29	add_mlprediction
114	Can change ml prediction	29	change_mlprediction
115	Can delete ml prediction	29	delete_mlprediction
116	Can view ml prediction	29	view_mlprediction
\.


--
-- Data for Name: devices_device; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.devices_device (id, code, name, device_type, location_lat, location_lon, address, ip_address, rtsp_url, rtsp_username, rtsp_password, model, manufacturer, firmware_version, resolution, fps, calibration_matrix, status, last_seen, is_active, created_at, updated_at, zone_id) FROM stdin;
eac7b607-2de4-4ed7-bcaf-d582d09c8086	CAM-001	Cámara Principal	camera	-12.046400	-77.042800	Av. Arequipa 1234, Lima	192.168.1.100	rtsp://localhost:8554/stream						1920x1080	30	\N	inactive	\N	t	2025-11-05 04:26:30.126139+00	2025-11-05 04:26:30.126191+00	5d989090-6cf9-4062-ba86-b7603f793659
ccf41599-6242-49f2-bd98-2bf965687177	CAM002	EZVIZ	camera	0.000005	0.000005	Av 200 Rimac	192.168.1.34	rtsp://admin:NXLTPJ@192.168.1.34:554/h264_stream	admin	NXLTPJ	H6C PRO	ezviz	1.0	2304x1296	30	\N	active	\N	t	2025-11-05 17:56:38.961972+00	2025-11-05 17:56:38.961987+00	5d989090-6cf9-4062-ba86-b7603f793659
f0c56a7b-8508-4988-9848-ab997e873c3b		Test Camera	camera	\N	\N		192.168.1.100							1920x1080	30	\N	active	\N	t	2025-11-05 18:10:19.563623+00	2025-11-05 18:10:19.563636+00	59bfe8d5-ac43-4605-8d73-23990290b0ad
b4dcec4c-9c9c-46a5-85a9-235643cd788a	CAM-DEFAULT-001	Cámara Web por Defecto	webcam	-12.046374	-77.042793		127.0.0.1							1920x1080	30	\N	active	\N	t	2025-11-05 20:20:19.232261+00	2025-11-05 20:20:19.23228+00	11d66be1-db41-42b4-8f1f-608469ab365a
\.


--
-- Data for Name: devices_deviceevent; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.devices_deviceevent (id, event_type, message, metadata, "timestamp", device_id) FROM stdin;
\.


--
-- Data for Name: devices_zone; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.devices_zone (id, name, code, description, boundary, center_point_lat, center_point_lon, speed_limit, is_active, created_at, updated_at) FROM stdin;
5d989090-6cf9-4062-ba86-b7603f793659	Centro de Lima	ZONE-001	Zona central de monitoreo	\N	\N	\N	60	t	2025-11-05 04:26:30.094481+00	2025-11-05 04:26:30.094529+00
59bfe8d5-ac43-4605-8d73-23990290b0ad	Test Zone	ZN-TEST	Test zone for ML predictions	\N	\N	\N	60	t	2025-11-05 18:10:19.550079+00	2025-11-05 18:10:19.550099+00
11d66be1-db41-42b4-8f1f-608469ab365a	Zona por Defecto	ZONE-DEFAULT	Zona para pruebas	\N	\N	\N	60	t	2025-11-05 20:20:09.088721+00	2025-11-05 20:20:09.088738+00
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2025-11-05 17:56:38.966777+00	ccf41599-6242-49f2-bd98-2bf965687177	CAM002 - EZVIZ	1	[{"added": {}}]	17	614dda88-105d-4865-bdef-53a10ffcbfa9
\.


--
-- Data for Name: django_celery_beat_clockedschedule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_celery_beat_clockedschedule (id, clocked_time) FROM stdin;
\.


--
-- Data for Name: django_celery_beat_crontabschedule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_celery_beat_crontabschedule (id, minute, hour, day_of_week, day_of_month, month_of_year, timezone) FROM stdin;
1	0	4	*	*	*	America/Lima
2	0	2	*	*	*	America/Lima
3	0	3	*	*	*	America/Lima
4	30	23	*	*	*	America/Lima
5	*/15	*	*	*	*	America/Lima
\.


--
-- Data for Name: django_celery_beat_intervalschedule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_celery_beat_intervalschedule (id, every, period) FROM stdin;
\.


--
-- Data for Name: django_celery_beat_periodictask; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) FROM stdin;
4	generate-daily-report	infractions.tasks.generate_daily_report	[]	{}	\N	\N	\N	\N	t	2025-11-05 04:30:00.00066+00	1	2025-11-05 04:30:42.810951+00		4	\N	\N	f	\N	\N	{}	\N	\N
2	sync-sunarp-data	vehicles.tasks.sync_sunarp_data	[]	{}	\N	\N	\N	\N	t	2025-11-05 07:00:00.00065+00	1	2025-11-05 07:01:43.276002+00		2	\N	\N	f	\N	\N	{}	\N	\N
3	cleanup-old-videos	infractions.tasks.cleanup_old_videos	[]	{}	\N	\N	\N	\N	t	2025-11-05 08:00:00.000542+00	1	2025-11-05 08:00:47.785927+00		3	\N	\N	f	\N	\N	{}	\N	\N
5	check-device-health	devices.tasks.check_device_health	[]	{}	\N	\N	\N	\N	t	2025-11-05 22:30:00.000261+00	65	2025-11-05 22:31:17.148371+00		5	\N	\N	f	\N	\N	{}	\N	\N
1	celery.backend_cleanup	celery.backend_cleanup	[]	{}	\N	\N	\N	\N	t	2025-11-05 09:00:00.001814+00	1	2025-11-05 09:03:08.78627+00		1	\N	\N	f	\N	\N	{}	\N	43200
\.


--
-- Data for Name: django_celery_beat_periodictasks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_celery_beat_periodictasks (ident, last_update) FROM stdin;
1	2025-11-05 03:01:54.775417+00
\.


--
-- Data for Name: django_celery_beat_solarschedule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_celery_beat_solarschedule (id, event, latitude, longitude) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	token_blacklist	blacklistedtoken
7	token_blacklist	outstandingtoken
8	django_celery_beat	crontabschedule
9	django_celery_beat	intervalschedule
10	django_celery_beat	periodictask
11	django_celery_beat	periodictasks
12	django_celery_beat	solarschedule
13	django_celery_beat	clockedschedule
14	authentication	user
15	authentication	loginhistory
16	devices	zone
17	devices	device
18	devices	deviceevent
19	infractions	infraction
20	infractions	appeal
21	infractions	infractionevent
22	infractions	vehicledetection
23	infractions	detectionstatistics
24	vehicles	driver
25	vehicles	vehicle
26	vehicles	vehicleownership
27	notifications	notification
28	ml_models	mlmodel
29	ml_models	mlprediction
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2025-11-05 03:01:51.12756+00
2	contenttypes	0002_remove_content_type_name	2025-11-05 03:01:51.138455+00
3	auth	0001_initial	2025-11-05 03:01:51.199627+00
4	auth	0002_alter_permission_name_max_length	2025-11-05 03:01:51.208501+00
5	auth	0003_alter_user_email_max_length	2025-11-05 03:01:51.216111+00
6	auth	0004_alter_user_username_opts	2025-11-05 03:01:51.222467+00
7	auth	0005_alter_user_last_login_null	2025-11-05 03:01:51.228625+00
8	auth	0006_require_contenttypes_0002	2025-11-05 03:01:51.231705+00
9	auth	0007_alter_validators_add_error_messages	2025-11-05 03:01:51.238345+00
10	auth	0008_alter_user_username_max_length	2025-11-05 03:01:51.283156+00
11	auth	0009_alter_user_last_name_max_length	2025-11-05 03:01:51.292194+00
12	auth	0010_alter_group_name_max_length	2025-11-05 03:01:51.302046+00
13	auth	0011_update_proxy_permissions	2025-11-05 03:01:51.310359+00
14	auth	0012_alter_user_first_name_max_length	2025-11-05 03:01:51.318245+00
15	authentication	0001_initial	2025-11-05 03:01:51.461295+00
16	admin	0001_initial	2025-11-05 03:01:51.491853+00
17	admin	0002_logentry_remove_auto_add	2025-11-05 03:01:51.500507+00
18	admin	0003_logentry_add_action_flag_choices	2025-11-05 03:01:51.511858+00
19	devices	0001_initial	2025-11-05 03:01:51.607184+00
20	django_celery_beat	0001_initial	2025-11-05 03:01:51.647522+00
21	django_celery_beat	0002_auto_20161118_0346	2025-11-05 03:01:51.661093+00
22	django_celery_beat	0003_auto_20161209_0049	2025-11-05 03:01:51.672644+00
23	django_celery_beat	0004_auto_20170221_0000	2025-11-05 03:01:51.677403+00
24	django_celery_beat	0005_add_solarschedule_events_choices	2025-11-05 03:01:51.682472+00
25	django_celery_beat	0006_auto_20180322_0932	2025-11-05 03:01:51.711888+00
26	django_celery_beat	0007_auto_20180521_0826	2025-11-05 03:01:51.72517+00
27	django_celery_beat	0008_auto_20180914_1922	2025-11-05 03:01:51.743092+00
28	django_celery_beat	0006_auto_20180210_1226	2025-11-05 03:01:51.755662+00
29	django_celery_beat	0006_periodictask_priority	2025-11-05 03:01:51.763961+00
30	django_celery_beat	0009_periodictask_headers	2025-11-05 03:01:51.773744+00
31	django_celery_beat	0010_auto_20190429_0326	2025-11-05 03:01:51.901869+00
32	django_celery_beat	0011_auto_20190508_0153	2025-11-05 03:01:51.932188+00
33	django_celery_beat	0012_periodictask_expire_seconds	2025-11-05 03:01:51.942122+00
34	django_celery_beat	0013_auto_20200609_0727	2025-11-05 03:01:51.951862+00
35	django_celery_beat	0014_remove_clockedschedule_enabled	2025-11-05 03:01:51.959769+00
36	django_celery_beat	0015_edit_solarschedule_events_choices	2025-11-05 03:01:51.965393+00
37	django_celery_beat	0016_alter_crontabschedule_timezone	2025-11-05 03:01:51.978265+00
38	django_celery_beat	0017_alter_crontabschedule_month_of_year	2025-11-05 03:01:51.989573+00
39	django_celery_beat	0018_improve_crontab_helptext	2025-11-05 03:01:52.000133+00
40	vehicles	0001_initial	2025-11-05 03:01:52.110753+00
41	infractions	0001_initial	2025-11-05 03:01:52.435525+00
42	infractions	0002_vehicledetection_detectionstatistics	2025-11-05 03:01:52.551126+00
43	notifications	0001_initial	2025-11-05 03:01:52.585453+00
44	sessions	0001_initial	2025-11-05 03:01:52.603503+00
45	token_blacklist	0001_initial	2025-11-05 03:01:52.671155+00
46	token_blacklist	0002_outstandingtoken_jti_hex	2025-11-05 03:01:52.688457+00
47	token_blacklist	0003_auto_20171017_2007	2025-11-05 03:01:52.719277+00
48	token_blacklist	0004_auto_20171017_2013	2025-11-05 03:01:52.742775+00
49	token_blacklist	0005_remove_outstandingtoken_jti	2025-11-05 03:01:52.75735+00
50	token_blacklist	0006_auto_20171017_2113	2025-11-05 03:01:52.770417+00
51	token_blacklist	0007_auto_20171017_2214	2025-11-05 03:01:52.815125+00
52	token_blacklist	0008_migrate_to_bigautofield	2025-11-05 03:01:52.897266+00
53	token_blacklist	0010_fix_migrate_to_bigautofield	2025-11-05 03:01:52.924046+00
54	token_blacklist	0011_linearizes_history	2025-11-05 03:01:52.92866+00
55	token_blacklist	0012_alter_outstandingtoken_user	2025-11-05 03:01:52.949052+00
56	devices	0002_alter_device_rtsp_url	2025-11-05 17:55:45.542753+00
57	infractions	0003_infraction_accident_risk_infraction_recidivism_risk_and_more	2025-11-05 18:04:57.012482+00
58	vehicles	0002_driver_risk_category_driver_risk_score_and_more	2025-11-05 18:04:57.033058+00
59	ml_models	0001_initial	2025-11-05 18:04:57.213152+00
60	infractions	0004_infraction_ml_prediction_time_ms_and_more	2025-11-05 18:24:28.606111+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: infractions_appeal; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.infractions_appeal (id, reason, evidence_description, supporting_documents, appellant_name, appellant_dni, appellant_phone, appellant_email, status, review_decision, reviewed_at, submitted_at, updated_at, infraction_id, reviewed_by_id) FROM stdin;
\.


--
-- Data for Name: infractions_detectionstatistics; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.infractions_detectionstatistics (id, period_type, period_start, period_end, car_count, truck_count, bus_count, motorcycle_count, bicycle_count, person_count, other_count, total_detections, total_with_plate, total_infractions, avg_confidence, avg_speed, created_at, updated_at, device_id, zone_id) FROM stdin;
\.


--
-- Data for Name: infractions_infraction; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.infractions_infraction (id, infraction_code, infraction_type, severity, location_lat, location_lon, license_plate_detected, license_plate_confidence, detected_speed, speed_limit, snapshot_url, video_url, evidence_metadata, status, reviewed_at, review_notes, fine_amount, fine_due_date, payment_date, detected_at, created_at, updated_at, device_id, driver_id, reviewed_by_id, vehicle_id, zone_id, accident_risk, recidivism_risk, risk_factors, ml_prediction_time_ms, processing_time_seconds) FROM stdin;
754e9992-4c95-43cc-be98-633af64b8b43	INF001080	speed	high	\N	\N		0.95	85	60			{}	validated	\N		\N	\N	\N	2025-11-03 18:18:08.402394+00	2025-11-05 18:18:08.403859+00	2025-11-05 18:18:08.40387+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b6ec9886-68fd-4c7b-83c3-3007249fcdf0	INF001081	red_light	medium	\N	\N		0.95	\N	\N			{}	validated	\N		\N	\N	\N	2025-10-31 18:18:08.409347+00	2025-11-05 18:18:08.410116+00	2025-11-05 18:18:08.410123+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8e211e7d-af3f-4ff1-a363-47e339e26c15	INF001082	speed	medium	\N	\N		0.95	78	60			{}	validated	\N		\N	\N	\N	2025-10-28 18:18:08.413226+00	2025-11-05 18:18:08.414311+00	2025-11-05 18:18:08.414316+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ee6d2498-e305-4191-96f7-5adbe29445fe	INF001083	lane_invasion	medium	\N	\N		0.95	\N	\N			{}	validated	\N		\N	\N	\N	2025-10-01 18:18:08.418176+00	2025-11-05 18:18:08.420742+00	2025-11-05 18:18:08.420748+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
975e4389-6b6b-4d83-b0b0-0bd00c038fc6	INF001084	speed	medium	\N	\N		0.95	75	60			{}	validated	\N		\N	\N	\N	2025-09-24 18:18:08.423104+00	2025-11-05 18:18:08.423774+00	2025-11-05 18:18:08.423778+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a22ad2e3-3725-46c5-9008-a7dc9848b2cf	INF001085	red_light	medium	\N	\N		0.95	\N	\N			{}	validated	\N		\N	\N	\N	2025-08-02 18:18:08.425362+00	2025-11-05 18:18:08.425737+00	2025-11-05 18:18:08.42574+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
27e62f72-ca22-4b55-b391-eee84097b8c0	INF001086	speed	high	\N	\N		0.95	82	60			{}	validated	\N		\N	\N	\N	2025-07-08 18:18:08.427498+00	2025-11-05 18:18:08.428228+00	2025-11-05 18:18:08.428232+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
233dd61f-ddaa-466a-a6bb-9edae166658b	INF001087	no_helmet	medium	\N	\N		0.95	\N	\N			{}	validated	\N		\N	\N	\N	2025-05-09 18:18:08.43068+00	2025-11-05 18:18:08.431328+00	2025-11-05 18:18:08.431332+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2404346f-4707-496d-9bc0-219e2943de24	INF001088	speed	high	\N	\N		0.95	90	60			{}	validated	\N		\N	\N	\N	2025-10-26 18:18:08.433808+00	2025-11-05 18:18:08.434511+00	2025-11-05 18:18:08.434515+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
02165ec8-1110-49b9-8e33-db3b9e3bb473	INF001089	red_light	medium	\N	\N		0.95	\N	\N			{}	validated	\N		\N	\N	\N	2025-10-11 18:18:08.437056+00	2025-11-05 18:18:08.438086+00	2025-11-05 18:18:08.438092+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	53e33d52-0e27-4fe8-982f-fe4b68c84239	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7e0a495b-2665-4793-9499-d5198618dd50	INF-WRO-132041-53	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [170.48776245117188, 122.03153228759766, 296.6170349121094, 227.39352416992188], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.051516", "confidence": 0.9108952879905701, "detection_id": "4-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.058945+00	2025-11-05 18:20:41.099932+00	2025-11-05 18:20:41.099938+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0f0eaa46-a568-4bbd-9e52-1dad71f7fd7c	INF-WRO-132041-72	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [256.28369140625, 108.56558990478516, 282.1596984863281, 126.61699676513672], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.053232", "confidence": 0.7495339512825012, "detection_id": "4-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.059157+00	2025-11-05 18:20:41.134032+00	2025-11-05 18:20:41.134039+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
02e9f0bf-0c37-4d84-89c5-a84019178319	INF-WRO-132041-52	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [170.2183837890625, 121.56427001953125, 295.8871765136719, 229.79238891601562], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.194700", "confidence": 0.8865254521369934, "detection_id": "6-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.206878+00	2025-11-05 18:20:41.234249+00	2025-11-05 18:20:41.234254+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
430cc1e3-1f94-4e6f-89f3-0ea8eee87a01	INF-WRO-132041-55	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [259.7793884277344, 108.85707092285156, 292.5948181152344, 132.00938415527344], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.196265", "confidence": 0.783237099647522, "detection_id": "6-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.20709+00	2025-11-05 18:20:41.268624+00	2025-11-05 18:20:41.26863+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4b038b86-2755-433f-8733-48fae33855ba	INF-WRO-132041-80	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [62.30784225463867, 80.88316345214844, 87.83338165283203, 93.66014862060547], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.197622", "confidence": 0.3198182284832001, "detection_id": "6-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.207278+00	2025-11-05 18:20:41.295482+00	2025-11-05 18:20:41.295488+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f600a763-25f9-4fd7-a4f3-9257a901f0e3	INF-WRO-132041-75	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [308.4520568847656, 107.15801239013672, 327.5328369140625, 118.51013946533203], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.198688", "confidence": 0.26091593503952026, "detection_id": "6-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.207503+00	2025-11-05 18:20:41.333686+00	2025-11-05 18:20:41.333693+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e85ed34d-44e6-452f-8d56-426adc0a20b8	INF-WRO-132041-36	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [169.60601806640625, 121.78557586669922, 296.0430908203125, 231.02430725097656], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.368253", "confidence": 0.904047966003418, "detection_id": "8-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.378745+00	2025-11-05 18:20:41.400883+00	2025-11-05 18:20:41.400889+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
86a7a9fc-cc02-43c3-aec3-6c6af42386ef	INF-WRO-132041-77	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [269.1148986816406, 110.68583679199219, 301.39666748046875, 137.73577880859375], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.369719", "confidence": 0.6921011209487915, "detection_id": "8-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.37896+00	2025-11-05 18:20:41.439238+00	2025-11-05 18:20:41.439244+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3c7c6d16-6ce2-4233-b235-ccc226b18026	INF-WRO-132041-66	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [51.83857727050781, 80.75255584716797, 81.45262145996094, 94.30552673339844], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.370798", "confidence": 0.37018537521362305, "detection_id": "8-2", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.37912+00	2025-11-05 18:20:41.473639+00	2025-11-05 18:20:41.47365+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e8c25441-ceed-4e82-af3e-cd3d5b4efcfd	INF-WRO-132041-51	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [300.040771484375, 107.32232666015625, 331.4139709472656, 130.60015869140625], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.371792", "confidence": 0.2788057029247284, "detection_id": "8-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.37927+00	2025-11-05 18:20:41.523389+00	2025-11-05 18:20:41.523395+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a361c044-7476-4a36-9128-bd8da63ba534	INF-WRO-132041-46	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [168.29444885253906, 121.8021240234375, 296.2335205078125, 232.2787628173828], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.514680", "confidence": 0.8843366503715515, "detection_id": "10-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.524252+00	2025-11-05 18:20:41.558757+00	2025-11-05 18:20:41.558763+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d9463566-bbf4-467f-8117-c3bba73e27f9	INF-WRO-132041-60	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [51.985862731933594, 82.43177032470703, 71.06719207763672, 94.02804565429688], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.373108", "confidence": 0.261699914932251, "detection_id": "8-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.379409+00	2025-11-05 18:20:41.559615+00	2025-11-05 18:20:41.559619+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
10541163-dab8-44e3-b193-b6b3ae8eed43	INF-WRO-132041-24	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [266.7334899902344, 110.13876342773438, 311.76910400390625, 143.11016845703125], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.516108", "confidence": 0.8005258440971375, "detection_id": "10-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.524513+00	2025-11-05 18:20:41.588936+00	2025-11-05 18:20:41.588943+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4a37c129-40ba-4a7b-8b9a-1efa2d360e15	INF-WRO-132041-76	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [44.41455078125, 79.8634033203125, 75.0323257446289, 94.39225006103516], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.517645", "confidence": 0.652963399887085, "detection_id": "10-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.524721+00	2025-11-05 18:20:41.61607+00	2025-11-05 18:20:41.616076+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1c1333e9-7b4f-4513-90fe-32b091a3c5d4	INF-WRO-132041-23	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [168.6362762451172, 121.58818817138672, 294.9868469238281, 232.6233367919922], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.687097", "confidence": 0.9052727818489075, "detection_id": "12-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.699177+00	2025-11-05 18:20:41.725038+00	2025-11-05 18:20:41.725043+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3d2f1ab5-4d79-4bd6-bec4-0aea125822cb	INF-WRO-132041-58	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [272.85662841796875, 112.1954116821289, 328.4268493652344, 154.25421142578125], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.689233", "confidence": 0.8049871921539307, "detection_id": "12-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.69934+00	2025-11-05 18:20:41.757674+00	2025-11-05 18:20:41.757681+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ade9e0bf-fe31-4209-9763-6bc0fb30370b	INF-WRO-132041-31	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [168.70834350585938, 121.40673065185547, 295.18505859375, 230.48130798339844], "source": "webcam_local", "timestamp": "2025-11-05T18:20:41.842616", "confidence": 0.9108906388282776, "detection_id": "14-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:41.849476+00	2025-11-05 18:20:41.87195+00	2025-11-05 18:20:41.871956+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5f786b3e-4a9e-4670-b9fd-cb8a4ff274fe	INF-WRO-132042-33	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [170.9088134765625, 122.18989562988281, 295.4306945800781, 225.8675537109375], "source": "webcam_local", "timestamp": "2025-11-05T18:20:42.187039", "confidence": 0.9100610613822937, "detection_id": "18-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:42.195848+00	2025-11-05 18:20:42.219317+00	2025-11-05 18:20:42.219323+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a06edac4-07ae-4767-b5bf-7616fae15436	INF-WRO-132042-14	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [0.23136520385742188, 160.7263641357422, 148.5121612548828, 268.95074462890625], "source": "webcam_local", "timestamp": "2025-11-05T18:20:42.188816", "confidence": 0.8202692866325378, "detection_id": "18-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:42.196012+00	2025-11-05 18:20:42.257987+00	2025-11-05 18:20:42.257994+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fdafdc95-318a-445a-9e75-8433add9dd05	INF-WRO-132042-28	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [171.58335876464844, 123.09196472167969, 296.8199157714844, 226.55517578125], "source": "webcam_local", "timestamp": "2025-11-05T18:20:42.341985", "confidence": 0.8449888229370117, "detection_id": "20-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:42.347456+00	2025-11-05 18:20:42.37027+00	2025-11-05 18:20:42.370277+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
da3c50b3-1026-4e27-8ff9-d522c4263cd2	INF-WRO-132042-44	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [172.66439819335938, 122.39151763916016, 298.45135498046875, 228.86752319335938], "source": "webcam_local", "timestamp": "2025-11-05T18:20:42.504881", "confidence": 0.7450999617576599, "detection_id": "22-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:42.512402+00	2025-11-05 18:20:42.538365+00	2025-11-05 18:20:42.53837+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
dfbb94fd-8bdd-4e7d-bdb4-d6d882a72c0a	INF-WRO-132042-91	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [172.21888732910156, 121.27922058105469, 297.6432800292969, 227.95701599121094], "source": "webcam_local", "timestamp": "2025-11-05T18:20:42.632058", "confidence": 0.8247719407081604, "detection_id": "24-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:42.640553+00	2025-11-05 18:20:42.664633+00	2025-11-05 18:20:42.664641+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
236d769e-3101-439e-8482-e2fa16af9fcd	INF-WRO-132042-38	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [172.2927703857422, 119.9966812133789, 298.0285339355469, 226.84835815429688], "source": "webcam_local", "timestamp": "2025-11-05T18:20:42.811051", "confidence": 0.8724002242088318, "detection_id": "26-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:42.819098+00	2025-11-05 18:20:42.843594+00	2025-11-05 18:20:42.843599+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f7d1aa10-3467-40aa-85f8-9f37e4df0a05	INF-WRO-132043-85	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [175.479736328125, 119.59501647949219, 302.6766052246094, 228.147216796875], "source": "webcam_local", "timestamp": "2025-11-05T18:20:43.502722", "confidence": 0.924049973487854, "detection_id": "34-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:43.511068+00	2025-11-05 18:20:43.534957+00	2025-11-05 18:20:43.534963+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b7d1a675-9900-446b-98f9-f7f90a813ce0	INF-WRO-132043-38	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [115.37722778320312, 116.00739288330078, 201.21157836914062, 170.507080078125], "source": "webcam_local", "timestamp": "2025-11-05T18:20:43.504807", "confidence": 0.873659610748291, "detection_id": "34-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:43.511447+00	2025-11-05 18:20:43.567395+00	2025-11-05 18:20:43.567403+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1faa61b2-259c-40c6-9901-c19176b0030c	INF-WRO-132044-34	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [176.57089233398438, 122.22711181640625, 302.4877014160156, 228.41624450683594], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.010890", "confidence": 0.9157218933105469, "detection_id": "40-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.021649+00	2025-11-05 18:20:44.054676+00	2025-11-05 18:20:44.054682+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b6f4d655-de00-4b6a-bc3c-d419754020d5	INF-WRO-132044-33	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [148.32666015625, 112.87003326416016, 208.55833435058594, 148.89932250976562], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.012930", "confidence": 0.8017560839653015, "detection_id": "40-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.021876+00	2025-11-05 18:20:44.088158+00	2025-11-05 18:20:44.088164+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0f97a2fc-8004-4d24-80d5-c73768f41c8b	INF-WRO-132044-44	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [176.40455627441406, 122.40872955322266, 302.1931457519531, 227.0148162841797], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.170925", "confidence": 0.9194379448890686, "detection_id": "42-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.180485+00	2025-11-05 18:20:44.205439+00	2025-11-05 18:20:44.205444+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6f77a774-3f77-49db-84a4-76ee03f51a1a	INF-WRO-132044-36	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [158.24342346191406, 111.32221984863281, 214.5056915283203, 144.0256805419922], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.172903", "confidence": 0.7567082643508911, "detection_id": "42-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.180746+00	2025-11-05 18:20:44.232921+00	2025-11-05 18:20:44.232928+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6a3f3407-0244-46b1-9883-5c0f459c58c2	INF-WRO-132044-92	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [176.05032348632812, 120.8576889038086, 301.8409423828125, 229.7877960205078], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.337588", "confidence": 0.9315667748451233, "detection_id": "44-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.349201+00	2025-11-05 18:20:44.37344+00	2025-11-05 18:20:44.373445+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
25461119-6fa3-4933-a9f3-eaac40de32bd	INF-WRO-132044-22	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [165.31907653808594, 110.0057144165039, 217.4075927734375, 139.06088256835938], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.339870", "confidence": 0.7321114540100098, "detection_id": "44-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.349576+00	2025-11-05 18:20:44.404727+00	2025-11-05 18:20:44.404733+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
59ef6bc7-89d7-4ef1-9916-a8015642403d	INF-WRO-132044-96	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [176.26397705078125, 120.28152465820312, 301.9804382324219, 228.23941040039062], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.513502", "confidence": 0.927294135093689, "detection_id": "46-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.522171+00	2025-11-05 18:20:44.547825+00	2025-11-05 18:20:44.547831+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0651f5b9-d08e-4227-8332-364510869063	INF-WRO-132044-46	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [172.34933471679688, 109.91777801513672, 219.04884338378906, 135.88734436035156], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.514905", "confidence": 0.6161342859268188, "detection_id": "46-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.522473+00	2025-11-05 18:20:44.582886+00	2025-11-05 18:20:44.582893+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1868c4b1-32f3-406b-8174-e964e6149e76	INF-WRO-132044-57	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [174.94692993164062, 121.08970642089844, 301.3018798828125, 228.57583618164062], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.684896", "confidence": 0.9114015102386475, "detection_id": "48-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.697885+00	2025-11-05 18:20:44.725276+00	2025-11-05 18:20:44.725283+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
850d8db1-79fd-4759-bade-365ec9c77fa9	INF-WRO-132044-94	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [180.39431762695312, 109.12825012207031, 209.9692840576172, 133.5740203857422], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.686245", "confidence": 0.5645730495452881, "detection_id": "48-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.698167+00	2025-11-05 18:20:44.762897+00	2025-11-05 18:20:44.762904+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
935109b2-347f-4447-b5df-ed7cb4d7f87a	INF-WRO-132044-31	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [320.45111083984375, 111.44133758544922, 334.9429016113281, 119.73857879638672], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.687583", "confidence": 0.41714388132095337, "detection_id": "48-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.698459+00	2025-11-05 18:20:44.824378+00	2025-11-05 18:20:44.824385+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e03cfa37-91cc-4e6d-8010-042fdd94e926	INF-WRO-132044-15	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [270.1270446777344, 115.9443588256836, 298.5757751464844, 137.06399536132812], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.690325", "confidence": 0.2136634886264801, "detection_id": "48-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.699121+00	2025-11-05 18:20:44.859481+00	2025-11-05 18:20:44.859492+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
249d0c31-a9b8-4518-aa12-4b94811341b9	INF-WRO-132044-97	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [174.43106079101562, 121.71807861328125, 300.96380615234375, 229.04042053222656], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.884080", "confidence": 0.9206854104995728, "detection_id": "50-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.890976+00	2025-11-05 18:20:44.915785+00	2025-11-05 18:20:44.915791+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e106ba9a-e7c5-4e63-a7b8-689ced328f51	INF-WRO-132045-39	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [174.66659545898438, 121.54042053222656, 301.57470703125, 231.2034912109375], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.016782", "confidence": 0.9300359487533569, "detection_id": "52-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.028429+00	2025-11-05 18:20:45.058388+00	2025-11-05 18:20:45.058393+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
32ad49fa-3810-4ba1-852e-ca1879e24295	INF-WRO-132045-52	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [185.82882690429688, 108.00068664550781, 224.6587371826172, 131.9952850341797], "source": "webcam_local", "timestamp": "2025-11-05T18:20:44.885931", "confidence": 0.5149057507514954, "detection_id": "50-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:44.891245+00	2025-11-05 18:20:45.059437+00	2025-11-05 18:20:45.059442+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d44ff901-83fa-4f44-8681-1667392431d1	INF-WRO-132045-20	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [189.1622772216797, 108.1871337890625, 217.638427734375, 129.87393188476562], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.018190", "confidence": 0.6348394751548767, "detection_id": "52-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.028669+00	2025-11-05 18:20:45.092976+00	2025-11-05 18:20:45.092982+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a71dea06-f3d1-4346-9fbc-483bf87a62be	INF-WRO-132045-57	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [258.30120849609375, 112.24298858642578, 289.6333923339844, 137.38478088378906], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.021061", "confidence": 0.41366931796073914, "detection_id": "52-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.028847+00	2025-11-05 18:20:45.138511+00	2025-11-05 18:20:45.138521+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c11aaf5e-bae4-43e6-9e63-924b19430c41	INF-WRO-132045-79	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [175.22207641601562, 121.94075775146484, 301.73944091796875, 230.8028106689453], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.149178", "confidence": 0.9245265126228333, "detection_id": "54-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.156154+00	2025-11-05 18:20:45.180242+00	2025-11-05 18:20:45.180248+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
bd360293-bbc0-4b2c-8290-25b1d1e28cbb	INF-WRO-132045-38	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [192.82498168945312, 107.41685485839844, 225.74102783203125, 129.78094482421875], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.150071", "confidence": 0.6257191896438599, "detection_id": "54-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.156332+00	2025-11-05 18:20:45.216549+00	2025-11-05 18:20:45.216556+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6e73a9d7-4b5f-41f3-aed9-70b354a9ea93	INF-WRO-132045-72	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [257.6230163574219, 112.50780487060547, 282.7872009277344, 126.34920501708984], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.151355", "confidence": 0.27211108803749084, "detection_id": "54-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.156541+00	2025-11-05 18:20:45.245003+00	2025-11-05 18:20:45.24501+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3b2c3dcb-1aca-4928-9e28-6a65beba35ce	INF-WRO-132045-18	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [175.94393920898438, 122.13102722167969, 301.43499755859375, 230.8424835205078], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.319562", "confidence": 0.9268316030502319, "detection_id": "56-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.330526+00	2025-11-05 18:20:45.352996+00	2025-11-05 18:20:45.353002+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
54258e51-e538-4c35-a2ed-32103a2afce3	INF-WRO-132045-95	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [194.93490600585938, 106.97483825683594, 221.81936645507812, 127.9775390625], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.321331", "confidence": 0.7250910401344299, "detection_id": "56-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.330881+00	2025-11-05 18:20:45.38582+00	2025-11-05 18:20:45.385826+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
eccbccaf-2aae-4416-a494-03876a694652	INF-WRO-132045-59	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [256.4524841308594, 111.48747253417969, 280.164794921875, 125.79391479492188], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.323139", "confidence": 0.5473249554634094, "detection_id": "56-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.331051+00	2025-11-05 18:20:45.41514+00	2025-11-05 18:20:45.415146+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2cde7e30-b77e-489b-96f6-fe623d303e24	INF-WRO-132045-96	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [176.09808349609375, 122.40953063964844, 302.01031494140625, 231.67543029785156], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.496762", "confidence": 0.9259917140007019, "detection_id": "58-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.509736+00	2025-11-05 18:20:45.538667+00	2025-11-05 18:20:45.538673+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
abaa5857-3845-4129-b7f9-d1b6665b54e5	INF-WRO-132045-11	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [199.65618896484375, 106.99967193603516, 225.02764892578125, 125.09387969970703], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.499032", "confidence": 0.5306798815727234, "detection_id": "58-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.510134+00	2025-11-05 18:20:45.566795+00	2025-11-05 18:20:45.566801+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
42c12a36-1568-42ff-8a15-12031d247936	INF-WRO-132045-90	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [256.4023132324219, 110.42866516113281, 277.2867736816406, 127.16432189941406], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.500944", "confidence": 0.43962714076042175, "detection_id": "58-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.510571+00	2025-11-05 18:20:45.601929+00	2025-11-05 18:20:45.601936+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2d35ba2c-7c91-4a69-b575-c7adc80b30af	INF-WRO-132045-34	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [174.38829040527344, 122.70915985107422, 302.5542907714844, 233.94021606445312], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.665800", "confidence": 0.9246728420257568, "detection_id": "60-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.676553+00	2025-11-05 18:20:45.701612+00	2025-11-05 18:20:45.701618+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
de18e0ab-f3ac-48ea-bf10-ee836bed9308	INF-WRO-132045-97	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [203.57276916503906, 107.28318786621094, 226.9947967529297, 123.94837188720703], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.667587", "confidence": 0.6275726556777954, "detection_id": "60-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.676788+00	2025-11-05 18:20:45.743674+00	2025-11-05 18:20:45.743682+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
33990e04-3f04-4291-a98d-2752896b2a20	INF-WRO-132045-27	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [255.63821411132812, 109.74980163574219, 277.2135314941406, 125.62916564941406], "source": "webcam_local", "timestamp": "2025-11-05T18:20:45.669795", "confidence": 0.3083585798740387, "detection_id": "60-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:45.676981+00	2025-11-05 18:20:45.773844+00	2025-11-05 18:20:45.773851+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9ee2c096-0708-4cfd-898f-bc67e83c72a8	INF-WRO-132046-52	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [172.94239807128906, 120.75517272949219, 298.2879638671875, 231.5149383544922], "source": "webcam_local", "timestamp": "2025-11-05T18:20:46.009684", "confidence": 0.9189416170120239, "detection_id": "64-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:46.014976+00	2025-11-05 18:20:46.034758+00	2025-11-05 18:20:46.034762+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e31819d7-f8cf-4b3a-91ef-6ad34df56b18	INF-WRO-132046-34	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [209.6659698486328, 105.1838607788086, 235.43655395507812, 121.62718963623047], "source": "webcam_local", "timestamp": "2025-11-05T18:20:46.010478", "confidence": 0.7389704585075378, "detection_id": "64-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:46.015163+00	2025-11-05 18:20:46.08103+00	2025-11-05 18:20:46.081042+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
00e6ba2a-0031-4420-8ba3-6ebdc0f05246	INF-WRO-132046-96	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [172.13644409179688, 121.18208312988281, 298.10498046875, 231.3599853515625], "source": "webcam_local", "timestamp": "2025-11-05T18:20:46.181586", "confidence": 0.9229045510292053, "detection_id": "66-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:46.191556+00	2025-11-05 18:20:46.217245+00	2025-11-05 18:20:46.217252+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1e5f099f-a078-4997-8bde-912735585f8e	INF-WRO-132046-81	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [213.74725341796875, 105.38685607910156, 236.64111328125, 120.69126892089844], "source": "webcam_local", "timestamp": "2025-11-05T18:20:46.182975", "confidence": 0.70367431640625, "detection_id": "66-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:46.191793+00	2025-11-05 18:20:46.262258+00	2025-11-05 18:20:46.262263+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0e5b7a20-5ea7-4a1f-9f61-12cb00acb5bb	INF-WRO-132046-84	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [173.24972534179688, 120.18587493896484, 298.6718444824219, 233.0130615234375], "source": "webcam_local", "timestamp": "2025-11-05T18:20:46.381601", "confidence": 0.9206150770187378, "detection_id": "68-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:46.392123+00	2025-11-05 18:20:46.419764+00	2025-11-05 18:20:46.419771+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d869b9b7-b7bd-4634-8172-59fd617a6467	INF-WRO-132046-16	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [216.8096923828125, 104.45753479003906, 239.96246337890625, 120.669189453125], "source": "webcam_local", "timestamp": "2025-11-05T18:20:46.383757", "confidence": 0.6154241561889648, "detection_id": "68-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:20:46.392481+00	2025-11-05 18:20:46.457432+00	2025-11-05 18:20:46.457439+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
04c301a5-79b9-46b9-b5ee-2cde4a0fc916	INF-RED-132119-81	red_light	medium	\N	\N		0	\N	\N			{"bbox": [5.214447021484375, 90.3477783203125, 115.77879333496094, 157.82748413085938], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.288429", "confidence": 0.897987425327301, "detection_id": "4-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.294699+00	2025-11-05 18:21:19.329657+00	2025-11-05 18:21:19.329664+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ebe23a1f-e5a8-4e94-87d8-88efc2fbd731	INF-RED-132119-90	red_light	medium	\N	\N		0	\N	\N			{"bbox": [243.60000610351562, 86.07099151611328, 261.0514831542969, 97.49433135986328], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.289358", "confidence": 0.32374516129493713, "detection_id": "4-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.294885+00	2025-11-05 18:21:19.363968+00	2025-11-05 18:21:19.363978+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4ad2e1f3-2a6e-4a72-87a1-f8b493b7bf6f	INF-SPE-132119-94	speed	medium	\N	\N		0	96.4	60			{"bbox": [243.53302001953125, 86.26714324951172, 261.16510009765625, 97.49791717529297], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.290030", "confidence": 0.2563742995262146, "detection_id": "4-5", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.295065+00	2025-11-05 18:21:19.410174+00	2025-11-05 18:21:19.410181+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0e97995e-a2f9-4daf-bf2a-fc94a3459d39	INF-SPE-132119-71	speed	medium	\N	\N		0	88.7	60			{"bbox": [28.424766540527344, 88.75782775878906, 125.5567398071289, 150.76768493652344], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.450270", "confidence": 0.8625330328941345, "detection_id": "6-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.458097+00	2025-11-05 18:21:19.482344+00	2025-11-05 18:21:19.482351+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7e3dea18-fbf6-4ff5-8c9b-73fbe1147598	INF-SPE-132119-67	speed	medium	\N	\N		0	95	60			{"bbox": [15.697277069091797, 82.63545227050781, 48.255226135253906, 120.08256530761719], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.451637", "confidence": 0.5794053077697754, "detection_id": "6-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.458293+00	2025-11-05 18:21:19.517244+00	2025-11-05 18:21:19.517251+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
351a99e7-e1bf-4a16-bf34-5c8ef5f52a22	INF-RED-132119-21	red_light	medium	\N	\N		0	\N	\N			{"bbox": [246.50616455078125, 84.81195831298828, 263.71630859375, 96.16658782958984], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.452585", "confidence": 0.4993191659450531, "detection_id": "6-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.458497+00	2025-11-05 18:21:19.577122+00	2025-11-05 18:21:19.577136+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
500c2391-fd39-4888-8f98-64b19cb60be0	INF-SPE-132119-28	speed	medium	\N	\N		0	84.2	60			{"bbox": [256.46246337890625, 85.51411437988281, 263.9951171875, 95.61424255371094], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.453541", "confidence": 0.26613616943359375, "detection_id": "6-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.458716+00	2025-11-05 18:21:19.623157+00	2025-11-05 18:21:19.623173+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5ad92be0-73ae-4ba2-b250-f163d6721480	INF-SPE-132119-93	speed	medium	\N	\N		0	72.7	60			{"bbox": [44.223541259765625, 89.12055969238281, 130.28720092773438, 148.3498077392578], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.636500", "confidence": 0.8092203736305237, "detection_id": "8-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.642874+00	2025-11-05 18:21:19.667834+00	2025-11-05 18:21:19.667842+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a8cc3fa5-0c4c-4abe-b5d0-36aa67f34dec	INF-SPE-132119-90	speed	medium	\N	\N		0	74.3	60			{"bbox": [0.07116317749023438, 81.35984802246094, 61.08905029296875, 120.41508483886719], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.637434", "confidence": 0.4625614881515503, "detection_id": "8-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.643112+00	2025-11-05 18:21:19.695757+00	2025-11-05 18:21:19.695763+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
582281d5-6714-4db4-8cc1-d837505ad944	INF-RED-132119-82	red_light	medium	\N	\N		0	\N	\N			{"bbox": [246.22335815429688, 86.50445556640625, 261.190185546875, 96.29788208007812], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.638315", "confidence": 0.40886563062667847, "detection_id": "8-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.643381+00	2025-11-05 18:21:19.751621+00	2025-11-05 18:21:19.751635+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0f73af7b-6e18-48fa-8b93-b80009a317f6	INF-RED-132119-79	red_light	medium	\N	\N		0	\N	\N			{"bbox": [256.3099365234375, 85.84323120117188, 264.530029296875, 95.76483154296875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.639215", "confidence": 0.3025096654891968, "detection_id": "8-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.643587+00	2025-11-05 18:21:19.796242+00	2025-11-05 18:21:19.796254+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4a776efa-514c-4d10-94f5-dfe563e8a732	INF-RED-132119-78	red_light	medium	\N	\N		0	\N	\N			{"bbox": [18.316146850585938, 85.29656982421875, 62.30583953857422, 122.99960327148438], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.806012", "confidence": 0.7958249449729919, "detection_id": "10-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.817151+00	2025-11-05 18:21:19.844247+00	2025-11-05 18:21:19.844254+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
940f5f5a-ce34-4087-9660-a3b342a84652	INF-SPE-132119-74	speed	medium	\N	\N		0	76.1	60			{"bbox": [59.75596618652344, 92.42094421386719, 134.08152770996094, 146.1434326171875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.807174", "confidence": 0.7886009812355042, "detection_id": "10-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.817427+00	2025-11-05 18:21:19.87281+00	2025-11-05 18:21:19.872816+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
68ea70d4-1d14-427f-bcc4-8333f3f31c46	INF-RED-132119-68	red_light	medium	\N	\N		0	\N	\N			{"bbox": [47.60585021972656, 73.2701187133789, 70.16722869873047, 98.1004409790039], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.808953", "confidence": 0.4127195477485657, "detection_id": "10-6", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.817763+00	2025-11-05 18:21:19.926781+00	2025-11-05 18:21:19.926791+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3556add0-89fc-4012-8165-6d90d13de879	INF-RED-132119-42	red_light	medium	\N	\N		0	\N	\N			{"bbox": [47.775390625, 73.12283325195312, 70.06629943847656, 98.35357666015625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.810302", "confidence": 0.34627825021743774, "detection_id": "10-7", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.818011+00	2025-11-05 18:21:19.969098+00	2025-11-05 18:21:19.969111+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9035a8ca-1874-45ed-9aad-92218607ccfd	INF-SPE-132120-79	speed	medium	\N	\N		0	92.8	60			{"bbox": [247.719970703125, 89.06221008300781, 265.84051513671875, 98.92085266113281], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.811556", "confidence": 0.33717355132102966, "detection_id": "10-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.818312+00	2025-11-05 18:21:20.016856+00	2025-11-05 18:21:20.016861+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
25db5d45-8512-4925-93d7-f1948d540556	INF-SPE-132120-36	speed	medium	\N	\N		0	99	60			{"bbox": [65.57046508789062, 95.58828735351562, 132.7163543701172, 148.74490356445312], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.978041", "confidence": 0.9223209023475647, "detection_id": "12-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.985416+00	2025-11-05 18:21:20.017468+00	2025-11-05 18:21:20.017474+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1543f083-2e55-4753-ad01-89d363693957	INF-RED-132120-85	red_light	medium	\N	\N		0	\N	\N			{"bbox": [17.620824813842773, 88.56417846679688, 53.03612518310547, 127.88323974609375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.979271", "confidence": 0.7846465706825256, "detection_id": "12-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.985634+00	2025-11-05 18:21:20.057677+00	2025-11-05 18:21:20.057686+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
20c911da-682f-4849-9551-a5fd5584cfc9	INF-RED-132120-91	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.005084037780761719, 137.9219970703125, 8.942036628723145, 179.44659423828125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.980388", "confidence": 0.5777115225791931, "detection_id": "12-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.985836+00	2025-11-05 18:21:20.103719+00	2025-11-05 18:21:20.103725+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
68da8d07-a0b3-45ce-a727-477513cf8ea3	INF-RED-132120-48	red_light	medium	\N	\N		0	\N	\N			{"bbox": [246.92933654785156, 94.60173034667969, 265.23681640625, 104.46278381347656], "source": "webcam_local", "timestamp": "2025-11-05T18:21:19.981260", "confidence": 0.39921870827674866, "detection_id": "12-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:19.986052+00	2025-11-05 18:21:20.139686+00	2025-11-05 18:21:20.139698+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ff8e3dfd-1a1c-4756-b294-5471b53c272c	INF-RED-132120-86	red_light	medium	\N	\N		0	\N	\N			{"bbox": [72.24760437011719, 96.61174011230469, 128.66891479492188, 146.7430419921875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.144277", "confidence": 0.9462580680847168, "detection_id": "14-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.150957+00	2025-11-05 18:21:20.174115+00	2025-11-05 18:21:20.174121+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9743b8f5-eedf-4eb7-af7d-f492938da97f	INF-SPE-132120-81	speed	medium	\N	\N		0	85.6	60			{"bbox": [0.0174713134765625, 110.01719665527344, 43.76341247558594, 179.05274963378906], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.145031", "confidence": 0.8585755825042725, "detection_id": "14-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.151095+00	2025-11-05 18:21:20.203083+00	2025-11-05 18:21:20.20309+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
aee0726c-eca7-4da8-bb93-4f20318fd64e	INF-SPE-132120-58	speed	medium	\N	\N		0	72.4	60			{"bbox": [19.02016830444336, 88.97494506835938, 49.441959381103516, 109.22512817382812], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.145899", "confidence": 0.5878342986106873, "detection_id": "14-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.151281+00	2025-11-05 18:21:20.238497+00	2025-11-05 18:21:20.238507+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
208c6f4f-bdee-41fb-a9a3-79b6a32b226e	INF-SPE-132120-40	speed	medium	\N	\N		0	72.8	60			{"bbox": [18.305320739746094, 89.81422424316406, 38.6068115234375, 124.62034606933594], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.146710", "confidence": 0.21731595695018768, "detection_id": "14-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.151416+00	2025-11-05 18:21:20.285019+00	2025-11-05 18:21:20.285028+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7cc7aae5-f561-4e36-8b2b-91a7a9746433	INF-RED-132120-30	red_light	medium	\N	\N		0	\N	\N			{"bbox": [47.18922424316406, 97.34757995605469, 62.659576416015625, 105.14030456542969], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.147609", "confidence": 0.20923684537410736, "detection_id": "14-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.151562+00	2025-11-05 18:21:20.322759+00	2025-11-05 18:21:20.322765+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
dff80e2c-69ad-4398-8810-839123415fa0	INF-RED-132120-70	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.084259033203125, 104.82323455810547, 64.08032989501953, 179.417236328125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.309927", "confidence": 0.904335618019104, "detection_id": "16-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.315382+00	2025-11-05 18:21:20.33927+00	2025-11-05 18:21:20.339277+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ebd9aebd-d17a-46ac-a2ba-6b1f7fe6e540	INF-SPE-132120-70	speed	medium	\N	\N		0	71.6	60			{"bbox": [74.52548217773438, 96.02459716796875, 129.0594482421875, 145.07650756835938], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.310930", "confidence": 0.8250601291656494, "detection_id": "16-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.315507+00	2025-11-05 18:21:20.370081+00	2025-11-05 18:21:20.370087+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f17cfaa6-0c3f-4ad7-bf23-abee11b12aff	INF-RED-132120-96	red_light	medium	\N	\N		0	\N	\N			{"bbox": [18.191715240478516, 89.785400390625, 48.7545051574707, 109.7786865234375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.311809", "confidence": 0.7334550619125366, "detection_id": "16-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.315655+00	2025-11-05 18:21:20.417422+00	2025-11-05 18:21:20.417558+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1c77cbcd-b3e3-4458-8ea8-321e4388890e	INF-SPE-132120-95	speed	medium	\N	\N		0	70.3	60			{"bbox": [0.0, 101.24523162841797, 82.41889190673828, 178.48834228515625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.467175", "confidence": 0.9166223406791687, "detection_id": "18-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.473303+00	2025-11-05 18:21:20.499401+00	2025-11-05 18:21:20.499407+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f7332160-e5cb-43fc-83fc-fae207df756d	INF-RED-132120-40	red_light	medium	\N	\N		0	\N	\N			{"bbox": [73.07264709472656, 95.29368591308594, 128.98313903808594, 142.60940551757812], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.468309", "confidence": 0.8553888201713562, "detection_id": "18-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.473525+00	2025-11-05 18:21:20.530279+00	2025-11-05 18:21:20.530289+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d8c6eac8-80bb-4da3-8ad0-f75fb4ef8b44	INF-RED-132120-53	red_light	medium	\N	\N		0	\N	\N			{"bbox": [20.57964515686035, 89.20614624023438, 50.538658142089844, 107.61080932617188], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.469459", "confidence": 0.3289188742637634, "detection_id": "18-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.4737+00	2025-11-05 18:21:20.587726+00	2025-11-05 18:21:20.587734+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
97e36055-4bff-44a7-b4f0-e0f7a7283fb6	INF-SPE-132120-69	speed	medium	\N	\N		0	93.9	60			{"bbox": [0.0, 100.44302368164062, 93.58779907226562, 173.88818359375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.621955", "confidence": 0.8704218864440918, "detection_id": "20-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.625675+00	2025-11-05 18:21:20.726798+00	2025-11-05 18:21:20.726807+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
976204ae-4bd2-4103-a65f-5116404a445a	INF-RED-132120-14	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.066497802734375, 98.19567108154297, 105.6416015625, 166.176025390625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.769864", "confidence": 0.8621348142623901, "detection_id": "22-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.777775+00	2025-11-05 18:21:20.799247+00	2025-11-05 18:21:20.799253+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0491c39d-49b4-4947-84f7-906ad4dade9b	INF-RED-132120-95	red_light	medium	\N	\N		0	\N	\N			{"bbox": [74.14212036132812, 93.14865112304688, 121.45962524414062, 136.32843017578125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.771962", "confidence": 0.860273540019989, "detection_id": "22-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.77797+00	2025-11-05 18:21:20.828293+00	2025-11-05 18:21:20.8283+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b22f860f-cd32-4b7b-a7a9-f45c2925ed13	INF-RED-132120-84	red_light	medium	\N	\N		0	\N	\N			{"bbox": [251.66610717773438, 94.31196594238281, 264.4512023925781, 103.13505554199219], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.774119", "confidence": 0.49468621611595154, "detection_id": "22-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.778156+00	2025-11-05 18:21:20.870037+00	2025-11-05 18:21:20.870048+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d40cc163-59db-4349-94f5-dde0c9f9e067	INF-SPE-132120-39	speed	medium	\N	\N		0	72.6	60			{"bbox": [6.7333984375, 99.56283569335938, 114.61802673339844, 163.54531860351562], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.931380", "confidence": 0.877084493637085, "detection_id": "24-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.939094+00	2025-11-05 18:21:20.962612+00	2025-11-05 18:21:20.962618+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d9b452a3-4145-4027-aedb-86918af23ceb	INF-SPE-132121-42	speed	medium	\N	\N		0	74.8	60			{"bbox": [22.673080444335938, 78.61001586914062, 67.98126983642578, 102.48959350585938], "source": "webcam_local", "timestamp": "2025-11-05T18:21:20.934884", "confidence": 0.28780457377433777, "detection_id": "24-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:20.9395+00	2025-11-05 18:21:21.082026+00	2025-11-05 18:21:21.082031+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
44834070-202d-4028-8e20-3f7d1505be26	INF-RED-132121-82	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.0735015869140625, 116.42488098144531, 94.62687683105469, 179.0030975341797], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.080027", "confidence": 0.8959242105484009, "detection_id": "26-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.086562+00	2025-11-05 18:21:21.108865+00	2025-11-05 18:21:21.108872+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d76dcfe4-c05e-43cd-859b-cea9b6fabd58	INF-RED-132121-97	red_light	medium	\N	\N		0	\N	\N			{"bbox": [31.272457122802734, 93.43756866455078, 121.4464111328125, 156.27716064453125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.080895", "confidence": 0.7776485085487366, "detection_id": "26-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.086748+00	2025-11-05 18:21:21.148894+00	2025-11-05 18:21:21.148902+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fae957c5-398a-49a0-9cdf-8080550b874c	INF-RED-132121-76	red_light	medium	\N	\N		0	\N	\N			{"bbox": [23.414783477783203, 79.18775177001953, 48.47267532348633, 106.33306121826172], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.081625", "confidence": 0.45254844427108765, "detection_id": "26-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.086944+00	2025-11-05 18:21:21.183145+00	2025-11-05 18:21:21.183154+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
64e46dce-588a-4311-9a3f-98bc3da64034	INF-RED-132121-72	red_light	medium	\N	\N		0	\N	\N			{"bbox": [254.58090209960938, 93.11813354492188, 264.1789245605469, 101.58348083496094], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.082490", "confidence": 0.4038076400756836, "detection_id": "26-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.087196+00	2025-11-05 18:21:21.222064+00	2025-11-05 18:21:21.22207+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f01f5b87-7b3e-450a-a784-9b164679835b	INF-RED-132121-62	red_light	medium	\N	\N		0	\N	\N			{"bbox": [24.554306030273438, 77.17964172363281, 66.54236602783203, 104.20545959472656], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.083276", "confidence": 0.22482305765151978, "detection_id": "26-8", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.087464+00	2025-11-05 18:21:21.264822+00	2025-11-05 18:21:21.264829+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
dc905868-974f-4159-9e71-f134d90eba3e	INF-RED-132121-81	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.03461456298828125, 112.03717041015625, 115.9903335571289, 178.76419067382812], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.260196", "confidence": 0.9082764387130737, "detection_id": "28-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.267433+00	2025-11-05 18:21:21.289497+00	2025-11-05 18:21:21.289504+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
adbf2097-c304-4eb3-88df-f373f1a02851	INF-SPE-132121-71	speed	medium	\N	\N		0	77.4	60			{"bbox": [41.98603820800781, 95.42021179199219, 126.66270446777344, 149.4843292236328], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.260854", "confidence": 0.7431678175926208, "detection_id": "28-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.267683+00	2025-11-05 18:21:21.323393+00	2025-11-05 18:21:21.323406+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4291996e-19fc-4f13-9cdb-53dbe04e76a8	INF-RED-132121-46	red_light	medium	\N	\N		0	\N	\N			{"bbox": [255.24166870117188, 93.9176025390625, 264.9173278808594, 102.4854736328125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.261753", "confidence": 0.3970116972923279, "detection_id": "28-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.267916+00	2025-11-05 18:21:21.365542+00	2025-11-05 18:21:21.36555+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3d8b6140-9dd2-4581-8769-13e2ac32ca37	INF-SPE-132121-45	speed	medium	\N	\N		0	74.6	60			{"bbox": [106.57086181640625, 95.18519592285156, 130.05337524414062, 117.71253967285156], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.262757", "confidence": 0.30251961946487427, "detection_id": "28-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.268204+00	2025-11-05 18:21:21.40265+00	2025-11-05 18:21:21.402665+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c9a80e7f-892e-456a-8dac-41c6c750862a	INF-RED-132121-57	red_light	medium	\N	\N		0	\N	\N			{"bbox": [20.252235412597656, 78.08119201660156, 65.79265594482422, 107.96958923339844], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.263680", "confidence": 0.23323126137256622, "detection_id": "28-9", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.268429+00	2025-11-05 18:21:21.452497+00	2025-11-05 18:21:21.452504+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a58803e7-8db1-47d2-8205-5be68a09ea75	INF-SPE-132121-68	speed	medium	\N	\N		0	80.9	60			{"bbox": [0.3385772705078125, 107.78335571289062, 137.32464599609375, 179.13888549804688], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.424219", "confidence": 0.9105523228645325, "detection_id": "30-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.430669+00	2025-11-05 18:21:21.454645+00	2025-11-05 18:21:21.454652+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e23594c1-90ae-44ba-9506-ce323206c8dc	INF-RED-132121-78	red_light	medium	\N	\N		0	\N	\N			{"bbox": [19.97770881652832, 76.66954040527344, 63.89460754394531, 104.08418273925781], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.426080", "confidence": 0.553278386592865, "detection_id": "30-4", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.431021+00	2025-11-05 18:21:21.59533+00	2025-11-05 18:21:21.595341+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
21695b53-3af9-4b7c-ab95-dda5bbe6f510	INF-RED-132121-13	red_light	medium	\N	\N		0	\N	\N			{"bbox": [104.05929565429688, 87.88489532470703, 128.0399169921875, 99.8088607788086], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.427165", "confidence": 0.2543470561504364, "detection_id": "30-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.43116+00	2025-11-05 18:21:21.667759+00	2025-11-05 18:21:21.667766+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e1b165ea-de40-4bab-be49-499e37329d67	INF-RED-132121-49	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.0, 104.4268569946289, 153.662353515625, 179.76742553710938], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.620969", "confidence": 0.9361425042152405, "detection_id": "32-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.628396+00	2025-11-05 18:21:21.668348+00	2025-11-05 18:21:21.668354+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
106769d0-2bfb-4edf-873a-256bfd3d1b77	INF-RED-132121-98	red_light	medium	\N	\N		0	\N	\N			{"bbox": [71.32499694824219, 93.60971069335938, 129.45639038085938, 115.45510864257812], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.622368", "confidence": 0.5490021705627441, "detection_id": "32-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.628618+00	2025-11-05 18:21:21.699792+00	2025-11-05 18:21:21.699801+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
06bb9a67-7157-40e4-be16-b62c0caf907b	INF-SPE-132121-70	speed	medium	\N	\N		0	84.7	60			{"bbox": [17.161239624023438, 88.91380310058594, 84.14253234863281, 111.75868225097656], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.624088", "confidence": 0.27248379588127136, "detection_id": "32-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.628833+00	2025-11-05 18:21:21.765823+00	2025-11-05 18:21:21.76583+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0b327b1c-7cd3-4481-8c29-bdabdb7c3845	INF-RED-132121-56	red_light	medium	\N	\N		0	\N	\N			{"bbox": [13.777008056640625, 101.21663665771484, 166.40011596679688, 179.08163452148438], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.820233", "confidence": 0.9176312685012817, "detection_id": "34-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.831303+00	2025-11-05 18:21:21.855925+00	2025-11-05 18:21:21.855933+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
019ae3dc-c63b-4085-ae02-730560d34868	INF-SPE-132121-83	speed	medium	\N	\N		0	77.1	60			{"bbox": [16.799774169921875, 87.0601806640625, 79.9231948852539, 120.31837463378906], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.821523", "confidence": 0.6912192106246948, "detection_id": "34-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.831593+00	2025-11-05 18:21:21.887702+00	2025-11-05 18:21:21.887709+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3f767a6f-0318-438d-8295-344441cde8af	INF-RED-132121-14	red_light	medium	\N	\N		0	\N	\N			{"bbox": [77.4487533569336, 91.27252197265625, 121.92316436767578, 103.42584228515625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.822879", "confidence": 0.37064340710639954, "detection_id": "34-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.831822+00	2025-11-05 18:21:21.929449+00	2025-11-05 18:21:21.929461+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
eb73d134-731e-4b6e-acbe-115b04da15a4	INF-RED-132121-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [14.799493789672852, 72.15501403808594, 62.177085876464844, 95.88008117675781], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.824780", "confidence": 0.27560773491859436, "detection_id": "34-6", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.832119+00	2025-11-05 18:21:21.985517+00	2025-11-05 18:21:21.985527+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
53c8c039-7a02-499f-8d9d-d46d84d5b843	INF-RED-132122-94	red_light	medium	\N	\N		0	\N	\N			{"bbox": [258.42474365234375, 88.05673217773438, 267.62750244140625, 96.70623779296875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:21.826014", "confidence": 0.2266341596841812, "detection_id": "34-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:21.832378+00	2025-11-05 18:21:22.028663+00	2025-11-05 18:21:22.028671+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
cf1f5d4c-18e8-4e7f-b7d9-d1ee8f73147d	INF-SPE-132122-40	speed	medium	\N	\N		0	77.7	60			{"bbox": [52.22859191894531, 102.6116714477539, 180.86343383789062, 179.21932983398438], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.022841", "confidence": 0.9324017763137817, "detection_id": "36-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.033021+00	2025-11-05 18:21:22.067765+00	2025-11-05 18:21:22.067773+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a4a3564e-38a0-49ea-be36-284c5d0253da	INF-SPE-132122-51	speed	medium	\N	\N		0	70.9	60			{"bbox": [18.08002471923828, 88.22634887695312, 70.23179626464844, 123.84320068359375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.025172", "confidence": 0.6041804552078247, "detection_id": "36-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.033436+00	2025-11-05 18:21:22.111741+00	2025-11-05 18:21:22.111751+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d2b8a098-dba6-4ef8-b06f-5caa4479e2f0	INF-RED-132122-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [79.08878326416016, 93.3326416015625, 121.4606704711914, 109.75132751464844], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.027407", "confidence": 0.5725193619728088, "detection_id": "36-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.03423+00	2025-11-05 18:21:22.167875+00	2025-11-05 18:21:22.167882+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
915e77b5-5db0-44f6-b00e-babe0ee4e0ec	INF-RED-132122-82	red_light	medium	\N	\N		0	\N	\N			{"bbox": [77.51339721679688, 104.08539581298828, 190.45553588867188, 178.851806640625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.201762", "confidence": 0.9015675187110901, "detection_id": "38-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.208563+00	2025-11-05 18:21:22.235243+00	2025-11-05 18:21:22.23525+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8cb7a15a-444d-4f6e-b406-3bad4e026203	INF-SPE-132122-34	speed	medium	\N	\N		0	93.7	60			{"bbox": [69.68002319335938, 95.23310852050781, 121.09893798828125, 137.5548553466797], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.202942", "confidence": 0.8395995497703552, "detection_id": "38-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.208849+00	2025-11-05 18:21:22.283917+00	2025-11-05 18:21:22.283926+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
40af7191-dd79-4cdb-b218-6fff67eb671a	INF-RED-132122-27	red_light	medium	\N	\N		0	\N	\N			{"bbox": [13.999786376953125, 76.13362121582031, 57.96808624267578, 124.82521057128906], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.204513", "confidence": 0.7771857380867004, "detection_id": "38-3", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.209148+00	2025-11-05 18:21:22.330328+00	2025-11-05 18:21:22.330339+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
706ee3a9-c3ac-4e66-8b39-981248ebd4d3	INF-RED-132122-91	red_light	medium	\N	\N		0	\N	\N			{"bbox": [93.53106689453125, 104.32818603515625, 196.43057250976562, 175.0498046875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.384771", "confidence": 0.8988313674926758, "detection_id": "40-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.391921+00	2025-11-05 18:21:22.414218+00	2025-11-05 18:21:22.414223+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3a74bfa2-81de-43db-aa4d-acdeeff69f89	INF-SPE-132122-88	speed	medium	\N	\N		0	79.3	60			{"bbox": [64.70448303222656, 96.0677490234375, 120.07637023925781, 137.98721313476562], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.385567", "confidence": 0.8120970726013184, "detection_id": "40-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.392117+00	2025-11-05 18:21:22.455996+00	2025-11-05 18:21:22.456003+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
415395a8-3971-4e36-9019-cb44f2f080d2	INF-RED-132122-15	red_light	medium	\N	\N		0	\N	\N			{"bbox": [16.274810791015625, 77.56343078613281, 55.95668029785156, 107.4378662109375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.386348", "confidence": 0.7089410424232483, "detection_id": "40-3", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.392316+00	2025-11-05 18:21:22.488708+00	2025-11-05 18:21:22.488714+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
843ed4a6-6816-44ec-a846-a22a8ceb7d95	INF-RED-132122-28	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.0, 86.34152221679688, 43.41845703125, 124.26446533203125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.387251", "confidence": 0.27321189641952515, "detection_id": "40-4", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.392456+00	2025-11-05 18:21:22.535209+00	2025-11-05 18:21:22.535223+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
20fc71cb-43e3-4e67-addc-dd588475153c	INF-SPE-132122-33	speed	medium	\N	\N		0	77.5	60			{"bbox": [14.609232902526855, 94.2943115234375, 43.845943450927734, 123.4443359375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.387881", "confidence": 0.22279570996761322, "detection_id": "40-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.392636+00	2025-11-05 18:21:22.575974+00	2025-11-05 18:21:22.575982+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4ff63531-8d0d-4313-a84f-95ef7e39f4ab	INF-SPE-132122-68	speed	medium	\N	\N		0	97	60			{"bbox": [109.38548278808594, 103.02139282226562, 204.1291961669922, 168.8642578125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.570661", "confidence": 0.891647219657898, "detection_id": "42-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.581671+00	2025-11-05 18:21:22.603995+00	2025-11-05 18:21:22.604001+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
403a0f2e-533b-4830-80a9-2d26e5daed22	INF-SPE-132122-32	speed	medium	\N	\N		0	95.3	60			{"bbox": [24.8314266204834, 88.41302490234375, 41.68146514892578, 106.83074951171875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.731560", "confidence": 0.39569100737571716, "detection_id": "44-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.735416+00	2025-11-05 18:21:22.764754+00	2025-11-05 18:21:22.764759+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e8c58c71-ec48-4dd1-a6bb-04f55ed40733	INF-RED-132122-41	red_light	medium	\N	\N		0	\N	\N			{"bbox": [25.131593704223633, 90.28067016601562, 40.365478515625, 107.87385559082031], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.577339", "confidence": 0.21380367875099182, "detection_id": "42-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.582339+00	2025-11-05 18:21:22.853941+00	2025-11-05 18:21:22.853948+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6afb2bb5-e7fd-4e55-a1f2-397971cead33	INF-RED-132122-97	red_light	medium	\N	\N		0	\N	\N			{"bbox": [43.309417724609375, 92.8077392578125, 112.41600036621094, 132.64407348632812], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.883830", "confidence": 0.8633572459220886, "detection_id": "46-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.889114+00	2025-11-05 18:21:22.909738+00	2025-11-05 18:21:22.909745+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
da2ab62e-91b2-4908-84f8-71f54630af43	INF-RED-132122-12	red_light	medium	\N	\N		0	\N	\N			{"bbox": [132.11941528320312, 100.71546936035156, 214.47732543945312, 159.2021026611328], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.884521", "confidence": 0.8597216010093689, "detection_id": "46-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.889284+00	2025-11-05 18:21:22.950414+00	2025-11-05 18:21:22.950421+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a7198922-4c2f-48b9-ad93-0dde312ef12b	INF-RED-132122-45	red_light	medium	\N	\N		0	\N	\N			{"bbox": [26.068683624267578, 86.81573486328125, 57.78168869018555, 104.81344604492188], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.885302", "confidence": 0.3494207262992859, "detection_id": "46-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.889418+00	2025-11-05 18:21:22.990247+00	2025-11-05 18:21:22.990253+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6d5e5ee4-aa50-43c4-9d16-3023b806bb5d	INF-RED-132123-51	red_light	medium	\N	\N		0	\N	\N			{"bbox": [25.189828872680664, 88.24336242675781, 41.898155212402344, 105.19126892089844], "source": "webcam_local", "timestamp": "2025-11-05T18:21:22.886046", "confidence": 0.2237330675125122, "detection_id": "46-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:22.889574+00	2025-11-05 18:21:23.031348+00	2025-11-05 18:21:23.03136+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3d1be1fd-92ce-4af2-b765-af2ebb512d12	INF-SPE-132123-76	speed	medium	\N	\N		0	89.1	60			{"bbox": [140.98231506347656, 99.46399688720703, 216.5867462158203, 153.870849609375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.050966", "confidence": 0.9020903706550598, "detection_id": "48-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.056999+00	2025-11-05 18:21:23.081205+00	2025-11-05 18:21:23.08121+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
bc311bcb-d75c-426d-b032-7ca6f2435d8f	INF-RED-132123-30	red_light	medium	\N	\N		0	\N	\N			{"bbox": [32.25941467285156, 91.97177124023438, 104.77857971191406, 130.00350952148438], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.052057", "confidence": 0.8968536853790283, "detection_id": "48-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.057226+00	2025-11-05 18:21:23.109367+00	2025-11-05 18:21:23.109376+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4535a6e0-bc12-4a2c-8a77-a5835a2c4365	INF-SPE-132123-10	speed	medium	\N	\N		0	83.6	60			{"bbox": [23.4127254486084, 87.558349609375, 47.782554626464844, 105.49749755859375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.053001", "confidence": 0.5006266236305237, "detection_id": "48-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.05745+00	2025-11-05 18:21:23.155938+00	2025-11-05 18:21:23.155952+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5a74dc2e-3f90-401a-8eef-f2146bce72c4	INF-RED-132123-90	red_light	medium	\N	\N		0	\N	\N			{"bbox": [23.992630004882812, 92.33926391601562, 97.58358764648438, 129.28594970703125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.206996", "confidence": 0.8744708895683289, "detection_id": "50-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.217016+00	2025-11-05 18:21:23.239038+00	2025-11-05 18:21:23.239044+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d84356e3-5785-4f07-b0d3-4beb70c5efbc	INF-SPE-132123-19	speed	medium	\N	\N		0	82.8	60			{"bbox": [146.39349365234375, 99.17784118652344, 218.480224609375, 150.3004913330078], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.208218", "confidence": 0.871700644493103, "detection_id": "50-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.217204+00	2025-11-05 18:21:23.277685+00	2025-11-05 18:21:23.277695+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5dc267c2-2755-41dc-af4e-f5ee77a13f71	INF-RED-132123-48	red_light	medium	\N	\N		0	\N	\N			{"bbox": [22.6646728515625, 87.84523010253906, 49.19135284423828, 106.52488708496094], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.209906", "confidence": 0.4249994158744812, "detection_id": "50-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.217371+00	2025-11-05 18:21:23.317535+00	2025-11-05 18:21:23.317541+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4fd81007-1f8d-450e-a730-455821069f22	INF-SPE-132123-17	speed	medium	\N	\N		0	75.1	60			{"bbox": [87.31233215332031, 87.032958984375, 107.40457153320312, 103.01895141601562], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.210977", "confidence": 0.3278029263019562, "detection_id": "50-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.217618+00	2025-11-05 18:21:23.360217+00	2025-11-05 18:21:23.360231+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8102f7df-32e2-4899-b013-95b40aac70e3	INF-RED-132123-94	red_light	medium	\N	\N		0	\N	\N			{"bbox": [1.3194656372070312, 73.72779846191406, 49.31719970703125, 98.25730895996094], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.212177", "confidence": 0.30078795552253723, "detection_id": "50-5", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.217797+00	2025-11-05 18:21:23.420755+00	2025-11-05 18:21:23.420762+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c37b164c-e33e-4a86-8384-10964defec83	INF-RED-132123-56	red_light	medium	\N	\N		0	\N	\N			{"bbox": [154.9119873046875, 99.40934753417969, 221.214599609375, 148.0238494873047], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.389692", "confidence": 0.8709604740142822, "detection_id": "52-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.396901+00	2025-11-05 18:21:23.423542+00	2025-11-05 18:21:23.423547+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
59e7f314-3e85-45e7-a030-0c84c658ecf8	INF-RED-132123-58	red_light	medium	\N	\N		0	\N	\N			{"bbox": [310.116943359375, 105.36264038085938, 319.9002685546875, 115.41058349609375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.213086", "confidence": 0.29020681977272034, "detection_id": "50-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.217949+00	2025-11-05 18:21:23.465072+00	2025-11-05 18:21:23.465081+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
cdbee6b8-f06a-4f24-9d4f-a9187dd8eb06	INF-SPE-132123-42	speed	medium	\N	\N		0	85.9	60			{"bbox": [21.418899536132812, 94.13240051269531, 85.4187240600586, 128.6273193359375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.390615", "confidence": 0.8424977660179138, "detection_id": "52-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.397166+00	2025-11-05 18:21:23.467185+00	2025-11-05 18:21:23.467195+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ec008844-572f-4c34-b364-c165c301b902	INF-RED-132123-49	red_light	medium	\N	\N		0	\N	\N			{"bbox": [310.49945068359375, 105.8584976196289, 319.890625, 116.34882354736328], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.392181", "confidence": 0.3063637912273407, "detection_id": "52-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.397414+00	2025-11-05 18:21:23.506036+00	2025-11-05 18:21:23.506043+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
dacec61d-3a31-4973-93b7-34251fd07bd1	INF-SPE-132123-77	speed	medium	\N	\N		0	78.6	60			{"bbox": [80.10421752929688, 88.3703384399414, 104.1651611328125, 103.27497100830078], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.393057", "confidence": 0.24615615606307983, "detection_id": "52-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.397662+00	2025-11-05 18:21:23.540388+00	2025-11-05 18:21:23.540396+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ff34ff93-9c16-4cfc-a768-4bbb51b80c38	INF-SPE-132123-35	speed	medium	\N	\N		0	91.5	60			{"bbox": [161.12911987304688, 98.61659240722656, 224.40216064453125, 144.99041748046875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.556197", "confidence": 0.8805893063545227, "detection_id": "54-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.561579+00	2025-11-05 18:21:23.582463+00	2025-11-05 18:21:23.582468+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e403e40e-193d-4815-8fea-1bb4bcc77582	INF-SPE-132123-72	speed	medium	\N	\N		0	73.4	60			{"bbox": [19.977523803710938, 89.47645568847656, 74.47310638427734, 127.19572448730469], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.557141", "confidence": 0.5855868458747864, "detection_id": "54-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.56175+00	2025-11-05 18:21:23.622454+00	2025-11-05 18:21:23.622462+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5d951f29-a2dc-4256-b9e9-531e46c6fdf2	INF-RED-132123-38	red_light	medium	\N	\N		0	\N	\N			{"bbox": [309.7461242675781, 105.76542663574219, 319.8918151855469, 115.96827697753906], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.558047", "confidence": 0.3865852355957031, "detection_id": "54-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.561949+00	2025-11-05 18:21:23.66257+00	2025-11-05 18:21:23.662582+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fefffd22-3986-4088-990f-73386b235e88	INF-SPE-132123-25	speed	medium	\N	\N		0	73	60			{"bbox": [168.42108154296875, 99.11479187011719, 227.59548950195312, 142.5876007080078], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.727559", "confidence": 0.8635169863700867, "detection_id": "56-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.735814+00	2025-11-05 18:21:23.759864+00	2025-11-05 18:21:23.75987+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d54ace10-a511-44eb-b512-e320299c0b8b	INF-RED-132123-40	red_light	medium	\N	\N		0	\N	\N			{"bbox": [21.792274475097656, 91.05397033691406, 63.570648193359375, 126.75047302246094], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.728801", "confidence": 0.5270834565162659, "detection_id": "56-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.736296+00	2025-11-05 18:21:23.792785+00	2025-11-05 18:21:23.792792+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e6c7c3a9-4721-46d8-a26e-b5c14cdc3b95	INF-RED-132123-46	red_light	medium	\N	\N		0	\N	\N			{"bbox": [21.727895736694336, 89.44430541992188, 63.972816467285156, 126.71768188476562], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.729995", "confidence": 0.24969784915447235, "detection_id": "56-5", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.736559+00	2025-11-05 18:21:23.829437+00	2025-11-05 18:21:23.829447+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9e8482b9-f855-4235-adf2-d76a1e4f431e	INF-RED-132123-26	red_light	medium	\N	\N		0	\N	\N			{"bbox": [310.9725646972656, 105.429931640625, 319.8803405761719, 117.00485229492188], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.731177", "confidence": 0.2363196462392807, "detection_id": "56-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.736799+00	2025-11-05 18:21:23.873174+00	2025-11-05 18:21:23.87318+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f8f71853-63ab-4314-86aa-f0fa544853f0	INF-RED-132123-72	red_light	medium	\N	\N		0	\N	\N			{"bbox": [174.96160888671875, 98.42568969726562, 229.4427490234375, 139.4213409423828], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.902440", "confidence": 0.8267071843147278, "detection_id": "58-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.910068+00	2025-11-05 18:21:23.934107+00	2025-11-05 18:21:23.934113+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2531111e-4fb8-4ae6-b9dd-db589768bf0b	INF-RED-132123-25	red_light	medium	\N	\N		0	\N	\N			{"bbox": [22.871999740600586, 93.51142883300781, 51.492393493652344, 124.58685302734375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.903817", "confidence": 0.4202239513397217, "detection_id": "58-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.910305+00	2025-11-05 18:21:23.964381+00	2025-11-05 18:21:23.964388+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6ff6cc1b-58c1-477a-94f3-9ba0d8025759	INF-SPE-132123-26	speed	medium	\N	\N		0	76.5	60			{"bbox": [111.83425903320312, 86.505126953125, 131.45037841796875, 101.15486145019531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.904621", "confidence": 0.31125378608703613, "detection_id": "58-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.910636+00	2025-11-05 18:21:24.001261+00	2025-11-05 18:21:24.001272+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4fd64bad-ec09-4b03-9290-dad1de03fd49	INF-RED-132124-33	red_light	medium	\N	\N		0	\N	\N			{"bbox": [97.6793212890625, 95.45181274414062, 108.54554748535156, 102.08699035644531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.905452", "confidence": 0.30671465396881104, "detection_id": "58-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.910888+00	2025-11-05 18:21:24.048748+00	2025-11-05 18:21:24.048754+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b648c2b6-e075-4972-af91-f47ba2b5b656	INF-RED-132124-94	red_light	medium	\N	\N		0	\N	\N			{"bbox": [78.4130859375, 88.50556945800781, 99.17263793945312, 103.82026672363281], "source": "webcam_local", "timestamp": "2025-11-05T18:21:23.906265", "confidence": 0.26505130529403687, "detection_id": "58-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:23.911081+00	2025-11-05 18:21:24.086394+00	2025-11-05 18:21:24.086401+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
288887ad-12f0-4df4-9170-c31919f33b2e	INF-SPE-132124-67	speed	medium	\N	\N		0	92.5	60			{"bbox": [180.54345703125, 98.02664184570312, 233.45538330078125, 137.4397735595703], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.087620", "confidence": 0.5994309186935425, "detection_id": "60-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.095608+00	2025-11-05 18:21:24.120096+00	2025-11-05 18:21:24.120103+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
aa5ceff8-8e85-4768-9613-f1ebca4aea5a	INF-SPE-132124-86	speed	medium	\N	\N		0	76.8	60			{"bbox": [110.37998962402344, 86.94957733154297, 131.5869903564453, 102.81873321533203], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.090075", "confidence": 0.24696744978427887, "detection_id": "60-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.096003+00	2025-11-05 18:21:24.250349+00	2025-11-05 18:21:24.250355+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
36a24a72-392b-4b1c-bea4-526b6222b038	INF-RED-132124-90	red_light	medium	\N	\N		0	\N	\N			{"bbox": [24.76030731201172, 88.69038391113281, 57.06580352783203, 107.37458801269531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.241893", "confidence": 0.6034839749336243, "detection_id": "62-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.249619+00	2025-11-05 18:21:24.270958+00	2025-11-05 18:21:24.270964+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
85d87421-f28c-4da4-aeb7-a0385fff6bb9	INF-RED-132124-25	red_light	medium	\N	\N		0	\N	\N			{"bbox": [21.64507293701172, 93.47047424316406, 37.06232833862305, 118.92636108398438], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.091237", "confidence": 0.23055139183998108, "detection_id": "60-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.096176+00	2025-11-05 18:21:24.28876+00	2025-11-05 18:21:24.288767+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
51410615-c7a0-4ecd-8853-072d1eb46be8	INF-SPE-132124-26	speed	medium	\N	\N		0	89.5	60			{"bbox": [186.22262573242188, 97.36643981933594, 236.50369262695312, 134.6029052734375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.243340", "confidence": 0.6009773015975952, "detection_id": "62-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.24977+00	2025-11-05 18:21:24.298414+00	2025-11-05 18:21:24.298418+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
791a35f7-e480-42fe-a52a-53aaecb37ebc	INF-RED-132124-67	red_light	medium	\N	\N		0	\N	\N			{"bbox": [109.93023681640625, 86.65049743652344, 134.29522705078125, 101.88816833496094], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.245121", "confidence": 0.3260171711444855, "detection_id": "62-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.249905+00	2025-11-05 18:21:24.340101+00	2025-11-05 18:21:24.340114+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c42acdb8-3fed-4e93-9c58-bbf149872f20	INF-SPE-132124-54	speed	medium	\N	\N		0	90.8	60			{"bbox": [312.60723876953125, 105.67855834960938, 319.88092041015625, 115.48583984375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.246632", "confidence": 0.20695504546165466, "detection_id": "62-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.250056+00	2025-11-05 18:21:24.398288+00	2025-11-05 18:21:24.398302+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
935df457-9fbb-4fc3-8ada-e90872818ad1	INF-SPE-132124-61	speed	medium	\N	\N		0	78.4	60			{"bbox": [25.351886749267578, 90.06109619140625, 56.98738479614258, 108.68281555175781], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.405724", "confidence": 0.6728599071502686, "detection_id": "64-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.416456+00	2025-11-05 18:21:24.442101+00	2025-11-05 18:21:24.442108+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2848ee44-c24e-494c-918d-cce7698ff0af	INF-RED-132124-58	red_light	medium	\N	\N		0	\N	\N			{"bbox": [190.68402099609375, 98.35847473144531, 238.35626220703125, 134.12103271484375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.406909", "confidence": 0.5006598234176636, "detection_id": "64-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.416691+00	2025-11-05 18:21:24.472088+00	2025-11-05 18:21:24.472096+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ab488243-e934-4306-9dfc-316acd48e8ea	INF-SPE-132124-17	speed	medium	\N	\N		0	71.1	60			{"bbox": [190.71859741210938, 98.33892822265625, 238.61312866210938, 134.1328582763672], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.407942", "confidence": 0.4558565318584442, "detection_id": "64-5", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.41695+00	2025-11-05 18:21:24.505665+00	2025-11-05 18:21:24.505672+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
88676212-a0b6-4f0d-b2f7-6323ef7eed3b	INF-RED-132124-14	red_light	medium	\N	\N		0	\N	\N			{"bbox": [108.8004150390625, 87.91249084472656, 132.56387329101562, 103.04057312011719], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.408916", "confidence": 0.3952998220920563, "detection_id": "64-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.417129+00	2025-11-05 18:21:24.549336+00	2025-11-05 18:21:24.549348+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
848edae6-90fa-4eb5-ad86-a8fa5f8bfb53	INF-SPE-132124-76	speed	medium	\N	\N		0	86.8	60			{"bbox": [79.85758972167969, 91.8257827758789, 95.38697814941406, 106.21019744873047], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.409920", "confidence": 0.2424989491701126, "detection_id": "64-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.417384+00	2025-11-05 18:21:24.590716+00	2025-11-05 18:21:24.590726+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9cc3da81-b0a5-44bd-8d4b-b07fd38a4507	INF-RED-132124-13	red_light	medium	\N	\N		0	\N	\N			{"bbox": [26.53900909423828, 89.32083129882812, 57.23609924316406, 107.528564453125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.592113", "confidence": 0.8106852769851685, "detection_id": "66-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.599194+00	2025-11-05 18:21:24.630953+00	2025-11-05 18:21:24.630958+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8234e813-81ce-4696-b54c-954c9072b446	INF-RED-132124-80	red_light	medium	\N	\N		0	\N	\N			{"bbox": [158.22703552246094, 92.750244140625, 165.65663146972656, 98.52742004394531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.411027", "confidence": 0.2023213654756546, "detection_id": "64-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.417629+00	2025-11-05 18:21:24.631644+00	2025-11-05 18:21:24.631648+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
106b1fd0-0b5d-41ca-b824-2f7baba80d25	INF-RED-132124-45	red_light	medium	\N	\N		0	\N	\N			{"bbox": [196.61184692382812, 96.33085632324219, 242.23324584960938, 131.5524139404297], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.593477", "confidence": 0.6227256059646606, "detection_id": "66-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.599403+00	2025-11-05 18:21:24.658518+00	2025-11-05 18:21:24.658523+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b982d54c-8dea-48b1-a625-bc6fab2c4ad9	INF-SPE-132124-21	speed	medium	\N	\N		0	92.2	60			{"bbox": [68.5871810913086, 95.49266052246094, 76.25806427001953, 105.52720642089844], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.595506", "confidence": 0.28303900361061096, "detection_id": "66-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.599779+00	2025-11-05 18:21:24.77742+00	2025-11-05 18:21:24.777426+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
56b5ad6a-1ea2-46c3-a6f2-3cccaf4c236b	INF-SPE-132124-84	speed	medium	\N	\N		0	70.2	60			{"bbox": [201.18521118164062, 95.6434326171875, 245.63632202148438, 128.40646362304688], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.777410", "confidence": 0.8302712440490723, "detection_id": "68-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.783936+00	2025-11-05 18:21:24.816691+00	2025-11-05 18:21:24.816696+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
59f1a9ba-8cf0-478e-97e5-bd67b0fbc8cc	INF-RED-132124-55	red_light	medium	\N	\N		0	\N	\N			{"bbox": [157.18283081054688, 90.90734100341797, 167.09939575195312, 98.03820037841797], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.596275", "confidence": 0.21425943076610565, "detection_id": "66-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.599986+00	2025-11-05 18:21:24.817633+00	2025-11-05 18:21:24.817638+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
21b070bb-86e9-40ad-baaf-aaaef0778bbd	INF-RED-132124-26	red_light	medium	\N	\N		0	\N	\N			{"bbox": [26.923709869384766, 88.24120330810547, 57.97825241088867, 107.22888946533203], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.778970", "confidence": 0.767828106880188, "detection_id": "68-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.784488+00	2025-11-05 18:21:24.847051+00	2025-11-05 18:21:24.847058+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a854afbb-a4da-4605-9a8a-28689f5147b4	INF-SPE-132124-78	speed	medium	\N	\N		0	74.2	60			{"bbox": [105.57400512695312, 85.74911499023438, 130.78005981445312, 102.87957763671875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.779872", "confidence": 0.3594200909137726, "detection_id": "68-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.784883+00	2025-11-05 18:21:24.881388+00	2025-11-05 18:21:24.8814+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1be27deb-4132-4ae3-98c0-428c7f5adb62	INF-RED-132124-51	red_light	medium	\N	\N		0	\N	\N			{"bbox": [154.22592163085938, 89.79949951171875, 167.580810546875, 97.64956665039062], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.780579", "confidence": 0.27848145365715027, "detection_id": "68-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.785086+00	2025-11-05 18:21:24.924783+00	2025-11-05 18:21:24.924795+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
074ee767-25ff-43e1-b9e0-f5013c1b7426	INF-RED-132124-48	red_light	medium	\N	\N		0	\N	\N			{"bbox": [207.60626220703125, 95.82405090332031, 249.37030029296875, 127.31465148925781], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.955999", "confidence": 0.8706572651863098, "detection_id": "70-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.963743+00	2025-11-05 18:21:24.986277+00	2025-11-05 18:21:24.986283+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ff01e27d-d1a7-465c-b3ff-b72d1aff7059	INF-SPE-132125-96	speed	medium	\N	\N		0	98.4	60			{"bbox": [29.120361328125, 88.18606567382812, 60.02473449707031, 106.55740356445312], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.957023", "confidence": 0.7924957275390625, "detection_id": "70-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.96401+00	2025-11-05 18:21:25.017078+00	2025-11-05 18:21:25.017084+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4e1b95f3-a1d8-4733-8138-4efa72f3cb4d	INF-RED-132125-57	red_light	medium	\N	\N		0	\N	\N			{"bbox": [103.84376525878906, 85.69564819335938, 128.4227294921875, 102.85110473632812], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.957963", "confidence": 0.5728029608726501, "detection_id": "70-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.964198+00	2025-11-05 18:21:25.046512+00	2025-11-05 18:21:25.046519+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e2f3bf06-823c-492c-a1bd-fe75d4de34bb	INF-SPE-132125-69	speed	medium	\N	\N		0	80.2	60			{"bbox": [127.34805297851562, 88.49737548828125, 137.85336303710938, 98.7529296875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.958843", "confidence": 0.42823526263237, "detection_id": "70-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.964451+00	2025-11-05 18:21:25.096518+00	2025-11-05 18:21:25.096531+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
66a180c7-5daf-40cb-92b3-1c87efb15106	INF-RED-132125-64	red_light	medium	\N	\N		0	\N	\N			{"bbox": [154.92263793945312, 89.92378997802734, 168.2325439453125, 98.37191009521484], "source": "webcam_local", "timestamp": "2025-11-05T18:21:24.960265", "confidence": 0.20450618863105774, "detection_id": "70-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:24.964688+00	2025-11-05 18:21:25.134162+00	2025-11-05 18:21:25.13417+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0f060c2b-4c0f-4b2d-9b8c-58e87a288d35	INF-SPE-132125-81	speed	medium	\N	\N		0	75.9	60			{"bbox": [30.567514419555664, 87.24158477783203, 62.09758758544922, 105.6943588256836], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.154333", "confidence": 0.6855545043945312, "detection_id": "72-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.160427+00	2025-11-05 18:21:25.184517+00	2025-11-05 18:21:25.184523+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
dc320d8f-c3fd-4ce7-bcc8-cf1b8619a340	INF-SPE-132125-97	speed	medium	\N	\N		0	73.2	60			{"bbox": [103.27757263183594, 84.83773803710938, 129.02037048339844, 102.03439331054688], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.155787", "confidence": 0.3644846975803375, "detection_id": "72-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.160704+00	2025-11-05 18:21:25.216354+00	2025-11-05 18:21:25.216362+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9a4bbcd8-03a8-4319-be90-970294e58223	INF-RED-132125-91	red_light	medium	\N	\N		0	\N	\N			{"bbox": [215.53842163085938, 94.84037780761719, 254.93734741210938, 123.064697265625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.355268", "confidence": 0.8244516253471375, "detection_id": "74-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.360911+00	2025-11-05 18:21:25.385084+00	2025-11-05 18:21:25.385091+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2dd298e5-216d-4782-8500-668076136222	INF-RED-132125-34	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.324901580810547, 86.60584259033203, 60.67679214477539, 105.60480499267578], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.356007", "confidence": 0.7382564544677734, "detection_id": "74-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.361103+00	2025-11-05 18:21:25.420585+00	2025-11-05 18:21:25.420592+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f607ab6c-c566-4a16-95d2-eb531b6f3de1	INF-RED-132125-89	red_light	medium	\N	\N		0	\N	\N			{"bbox": [83.6445083618164, 92.25358581542969, 94.83954620361328, 108.75521850585938], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.356864", "confidence": 0.2540399730205536, "detection_id": "74-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.361329+00	2025-11-05 18:21:25.449363+00	2025-11-05 18:21:25.44937+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b3e06529-2821-48d5-a639-642f40071449	INF-RED-132125-18	red_light	medium	\N	\N		0	\N	\N			{"bbox": [154.389404296875, 88.6629638671875, 168.90228271484375, 96.90121459960938], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.357672", "confidence": 0.20195087790489197, "detection_id": "74-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.36155+00	2025-11-05 18:21:25.510554+00	2025-11-05 18:21:25.510561+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6d2f90be-d500-4709-bbd4-fca4ebe272ae	INF-RED-132125-60	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.284164428710938, 87.43354797363281, 61.080406188964844, 105.82524108886719], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.544842", "confidence": 0.7043017148971558, "detection_id": "76-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.553718+00	2025-11-05 18:21:25.580542+00	2025-11-05 18:21:25.580548+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9bcbbd22-c7df-4f6a-b598-ce8b1fe2baaf	INF-SPE-132125-17	speed	medium	\N	\N		0	85.5	60			{"bbox": [220.85684204101562, 95.3145751953125, 257.3814392089844, 123.14605712890625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.545784", "confidence": 0.6988275051116943, "detection_id": "76-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.553961+00	2025-11-05 18:21:25.622032+00	2025-11-05 18:21:25.622039+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
af25f71b-4afc-46b2-8437-7d605fab6f39	INF-SPE-132125-86	speed	medium	\N	\N		0	80.3	60			{"bbox": [56.934234619140625, 87.22817993164062, 75.79385375976562, 104.68243408203125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.546963", "confidence": 0.2655341625213623, "detection_id": "76-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.554176+00	2025-11-05 18:21:25.655397+00	2025-11-05 18:21:25.655408+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
54c40632-f9e0-4934-b1d7-d49497115e86	INF-RED-132125-19	red_light	medium	\N	\N		0	\N	\N			{"bbox": [224.307373046875, 95.92095947265625, 259.41400146484375, 122.55694580078125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.721663", "confidence": 0.8289187550544739, "detection_id": "78-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.731954+00	2025-11-05 18:21:25.763399+00	2025-11-05 18:21:25.763406+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
15854dbf-4214-4f31-b59d-7220950ae8a7	INF-RED-132125-84	red_light	medium	\N	\N		0	\N	\N			{"bbox": [123.01348876953125, 88.21890258789062, 136.20413208007812, 97.97885131835938], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.548859", "confidence": 0.24447470903396606, "detection_id": "76-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.554501+00	2025-11-05 18:21:25.764458+00	2025-11-05 18:21:25.764464+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b0bba434-d053-4573-ad9b-a3764851dc81	INF-SPE-132125-30	speed	medium	\N	\N		0	80.5	60			{"bbox": [72.4452133178711, 87.68988037109375, 94.05596160888672, 111.93905639648438], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.549576", "confidence": 0.21803516149520874, "detection_id": "76-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.554668+00	2025-11-05 18:21:25.821611+00	2025-11-05 18:21:25.821617+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
142f57bb-a314-48f5-af01-03097bf85433	INF-RED-132125-95	red_light	medium	\N	\N		0	\N	\N			{"bbox": [100.72637939453125, 85.55144500732422, 122.0560302734375, 103.3943862915039], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.723558", "confidence": 0.47195732593536377, "detection_id": "78-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.732401+00	2025-11-05 18:21:25.901955+00	2025-11-05 18:21:25.901961+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
64974299-2639-464a-b7b8-68c0752858cc	INF-RED-132125-32	red_light	medium	\N	\N		0	\N	\N			{"bbox": [120.62339782714844, 88.29125213623047, 133.47998046875, 98.16167449951172], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.724530", "confidence": 0.36749467253685, "detection_id": "78-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.73259+00	2025-11-05 18:21:25.943018+00	2025-11-05 18:21:25.943023+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
eb7d438f-f5a0-4605-9f01-45d442ac889f	INF-SPE-132125-35	speed	medium	\N	\N		0	72.5	60			{"bbox": [28.164655685424805, 87.45562744140625, 59.439453125, 105.97677612304688], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.898359", "confidence": 0.8169387578964233, "detection_id": "80-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.904965+00	2025-11-05 18:21:25.943775+00	2025-11-05 18:21:25.943781+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6a7d2490-da1d-4f1b-936f-626fdae1aee9	INF-RED-132125-48	red_light	medium	\N	\N		0	\N	\N			{"bbox": [309.9466552734375, 93.79496765136719, 319.401123046875, 113.07362365722656], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.726122", "confidence": 0.2524576485157013, "detection_id": "78-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.732759+00	2025-11-05 18:21:25.977194+00	2025-11-05 18:21:25.9772+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6816c4eb-f9fd-4d65-8037-928da80b67bc	INF-RED-132125-47	red_light	medium	\N	\N		0	\N	\N			{"bbox": [225.798583984375, 95.81109619140625, 258.9222412109375, 120.63217163085938], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.899317", "confidence": 0.7370225191116333, "detection_id": "80-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.905158+00	2025-11-05 18:21:25.980967+00	2025-11-05 18:21:25.980978+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5ea75002-d20c-46ba-b7e5-6e1a4981f41d	INF-SPE-132126-84	speed	medium	\N	\N		0	74.6	60			{"bbox": [55.36003875732422, 87.5395736694336, 76.11841583251953, 104.61389923095703], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.727014", "confidence": 0.22793643176555634, "detection_id": "78-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.732913+00	2025-11-05 18:21:26.032803+00	2025-11-05 18:21:26.032813+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
779f1179-d149-421b-850f-4e62f5e001ca	INF-SPE-132126-96	speed	medium	\N	\N		0	73.7	60			{"bbox": [95.25498962402344, 85.55471801757812, 120.90834045410156, 103.22491455078125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.900176", "confidence": 0.570397675037384, "detection_id": "80-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.905324+00	2025-11-05 18:21:26.033858+00	2025-11-05 18:21:26.03387+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f97de469-30fd-4f98-8889-2fa645b44f4a	INF-RED-132126-94	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.82467651367188, 89.26564025878906, 112.94725036621094, 103.34367370605469], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.727986", "confidence": 0.21195267140865326, "detection_id": "78-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.733091+00	2025-11-05 18:21:26.088011+00	2025-11-05 18:21:26.088022+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
16114ce8-5a85-444e-863b-536f7d1fd9b9	INF-RED-132126-92	red_light	medium	\N	\N		0	\N	\N			{"bbox": [56.91297912597656, 87.12384796142578, 76.47288513183594, 104.30171966552734], "source": "webcam_local", "timestamp": "2025-11-05T18:21:25.901494", "confidence": 0.23122353851795197, "detection_id": "80-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:25.90549+00	2025-11-05 18:21:26.091412+00	2025-11-05 18:21:26.091418+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f3c5001d-7bec-481e-a0c1-ecca929fbc7a	INF-RED-132126-68	red_light	medium	\N	\N		0	\N	\N			{"bbox": [229.40414428710938, 95.3680648803711, 261.7058410644531, 120.06627655029297], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.099709", "confidence": 0.759951651096344, "detection_id": "82-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.106497+00	2025-11-05 18:21:26.129036+00	2025-11-05 18:21:26.129042+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c03f8bcf-f916-42d3-af1d-e6059730229d	INF-SPE-132126-59	speed	medium	\N	\N		0	75	60			{"bbox": [28.521635055541992, 87.68599700927734, 62.713714599609375, 105.6877212524414], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.100719", "confidence": 0.6806035041809082, "detection_id": "82-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.10668+00	2025-11-05 18:21:26.167918+00	2025-11-05 18:21:26.167926+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fd421aa5-d4ef-42f4-92a2-e886419e2421	INF-RED-132126-28	red_light	medium	\N	\N		0	\N	\N			{"bbox": [93.83910369873047, 85.50765228271484, 120.06291961669922, 103.10529327392578], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.101620", "confidence": 0.4991922378540039, "detection_id": "82-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.106875+00	2025-11-05 18:21:26.207938+00	2025-11-05 18:21:26.207952+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
38ad56af-5690-4467-8785-c497d13d6727	INF-RED-132126-90	red_light	medium	\N	\N		0	\N	\N			{"bbox": [100.6060791015625, 86.503173828125, 128.054443359375, 98.25921630859375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.102301", "confidence": 0.2148851603269577, "detection_id": "82-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.107067+00	2025-11-05 18:21:26.264947+00	2025-11-05 18:21:26.26496+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5b416638-7f23-4296-b4cf-af9b7aa17801	INF-SPE-132126-61	speed	medium	\N	\N		0	80.5	60			{"bbox": [114.1514892578125, 87.77262878417969, 128.09820556640625, 97.91511535644531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.102955", "confidence": 0.20677027106285095, "detection_id": "82-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.107283+00	2025-11-05 18:21:26.300325+00	2025-11-05 18:21:26.300332+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
275e1b96-a48a-4315-b071-06f4baaa1e65	INF-RED-132126-66	red_light	medium	\N	\N		0	\N	\N			{"bbox": [232.59173583984375, 95.44905090332031, 263.8985290527344, 118.23619079589844], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.297731", "confidence": 0.8087888956069946, "detection_id": "84-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.304515+00	2025-11-05 18:21:26.327023+00	2025-11-05 18:21:26.327029+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
50a847e3-5062-4357-a877-48e53bed35d1	INF-RED-132126-17	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.79309844970703, 87.03541564941406, 59.684547424316406, 105.60334777832031], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.298624", "confidence": 0.7319253087043762, "detection_id": "84-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.304665+00	2025-11-05 18:21:26.359483+00	2025-11-05 18:21:26.359491+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d8f80713-eb6c-43f3-91f9-c15005d39ead	INF-SPE-132126-52	speed	medium	\N	\N		0	79.6	60			{"bbox": [58.778656005859375, 93.23414611816406, 77.09202575683594, 104.28166198730469], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.299489", "confidence": 0.2633797526359558, "detection_id": "84-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.304852+00	2025-11-05 18:21:26.389461+00	2025-11-05 18:21:26.389468+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
919cb0e4-bfed-40dd-bb5a-69e5889d0ba3	INF-RED-132126-73	red_light	medium	\N	\N		0	\N	\N			{"bbox": [95.67599487304688, 84.85604095458984, 122.41207885742188, 102.22809600830078], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.300814", "confidence": 0.21023565530776978, "detection_id": "84-7", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.304995+00	2025-11-05 18:21:26.449307+00	2025-11-05 18:21:26.449343+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
84cea65d-50d6-42a0-9842-8a939b4a2a66	INF-SPE-132126-76	speed	medium	\N	\N		0	88.3	60			{"bbox": [234.69876098632812, 95.01359558105469, 263.8937072753906, 116.35847473144531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.492079", "confidence": 0.8324714303016663, "detection_id": "86-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.49723+00	2025-11-05 18:21:26.518362+00	2025-11-05 18:21:26.518368+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
be4fc758-b879-46b4-9ea0-a10c2728baaf	INF-RED-132126-83	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.371620178222656, 86.64152526855469, 61.87049102783203, 105.71113586425781], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.492939", "confidence": 0.6022634506225586, "detection_id": "86-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.497398+00	2025-11-05 18:21:26.553696+00	2025-11-05 18:21:26.553702+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3f69e29c-8f6f-4cee-ba37-61a11360672b	INF-SPE-132126-86	speed	medium	\N	\N		0	91.6	60			{"bbox": [88.32596588134766, 91.409912109375, 105.7743148803711, 102.77095031738281], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.494352", "confidence": 0.20691920816898346, "detection_id": "86-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.497674+00	2025-11-05 18:21:26.6696+00	2025-11-05 18:21:26.669611+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
59f3fd0c-ca94-4fdc-8f85-b78680725878	INF-RED-132126-16	red_light	medium	\N	\N		0	\N	\N			{"bbox": [238.74273681640625, 93.5193099975586, 264.9771728515625, 114.76886749267578], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.666942", "confidence": 0.8463314771652222, "detection_id": "88-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.673611+00	2025-11-05 18:21:26.700446+00	2025-11-05 18:21:26.700453+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6b4f8947-52b0-4c1c-a365-b049d5d9f21d	INF-RED-132126-14	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.390933990478516, 86.33226776123047, 60.285396575927734, 105.43415069580078], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.668450", "confidence": 0.27267196774482727, "detection_id": "88-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.673837+00	2025-11-05 18:21:26.732634+00	2025-11-05 18:21:26.732642+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
bcfbf1c1-bfd4-4324-8e2a-771369a4b5a6	INF-RED-132126-45	red_light	medium	\N	\N		0	\N	\N			{"bbox": [60.92873764038086, 93.72649383544922, 76.88803100585938, 103.7232437133789], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.669382", "confidence": 0.23611822724342346, "detection_id": "88-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.674073+00	2025-11-05 18:21:26.764918+00	2025-11-05 18:21:26.764929+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c90260ec-3a28-4880-a4e0-7b12f7a22ddb	INF-RED-132126-96	red_light	medium	\N	\N		0	\N	\N			{"bbox": [240.76068115234375, 92.79827880859375, 266.9970703125, 113.6884765625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.833589", "confidence": 0.8027603626251221, "detection_id": "90-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.846203+00	2025-11-05 18:21:26.870841+00	2025-11-05 18:21:26.870847+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3b11b5a2-a8a0-4967-abc6-88e62d4ff17d	INF-RED-132126-52	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.70359802246094, 83.92832946777344, 113.46669006347656, 102.14955139160156], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.835536", "confidence": 0.3461061418056488, "detection_id": "90-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.846335+00	2025-11-05 18:21:26.906985+00	2025-11-05 18:21:26.906991+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
86b2ced5-ec85-4098-98e1-06ac3f866813	INF-RED-132126-69	red_light	medium	\N	\N		0	\N	\N			{"bbox": [42.03174591064453, 87.11549377441406, 58.886268615722656, 104.74540710449219], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.837224", "confidence": 0.32632237672805786, "detection_id": "90-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.846484+00	2025-11-05 18:21:26.945179+00	2025-11-05 18:21:26.94519+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
964de44c-91a3-465e-8f74-b6275040d0d5	INF-RED-132126-93	red_light	medium	\N	\N		0	\N	\N			{"bbox": [100.70407104492188, 85.33494567871094, 119.44183349609375, 98.23817443847656], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.838963", "confidence": 0.2971874475479126, "detection_id": "90-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.846612+00	2025-11-05 18:21:26.98665+00	2025-11-05 18:21:26.986663+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3f90bd3f-eb09-4206-805f-1589396a6016	INF-SPE-132127-83	speed	medium	\N	\N		0	72.4	60			{"bbox": [56.58823776245117, 75.78184509277344, 78.41868591308594, 103.44001770019531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.840513", "confidence": 0.27627745270729065, "detection_id": "90-9", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.846761+00	2025-11-05 18:21:27.048083+00	2025-11-05 18:21:27.04809+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a50700a1-a71e-4321-875d-8270b88a77fd	INF-RED-132127-78	red_light	medium	\N	\N		0	\N	\N			{"bbox": [243.51419067382812, 93.20855712890625, 264.7834167480469, 112.79290771484375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.010309", "confidence": 0.6932877898216248, "detection_id": "92-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.01676+00	2025-11-05 18:21:27.049224+00	2025-11-05 18:21:27.04923+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7628d252-09a0-48e5-8309-22dcb1f9673e	INF-RED-132127-77	red_light	medium	\N	\N		0	\N	\N			{"bbox": [58.06072998046875, 92.59989929199219, 77.01815795898438, 103.96315002441406], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.841657", "confidence": 0.24618439376354218, "detection_id": "90-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.846949+00	2025-11-05 18:21:27.094657+00	2025-11-05 18:21:27.094665+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
459dd097-715e-4b2b-83e3-a256603de88f	INF-SPE-132127-10	speed	medium	\N	\N		0	74.3	60			{"bbox": [28.88419532775879, 86.34127807617188, 59.83049774169922, 103.759033203125], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.011053", "confidence": 0.6831130981445312, "detection_id": "92-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.016964+00	2025-11-05 18:21:27.096207+00	2025-11-05 18:21:27.096215+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4ae1957b-c563-4d53-901f-e92e8afb592e	INF-RED-132127-42	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.24142456054688, 83.80435943603516, 114.34957885742188, 101.7418441772461], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.012187", "confidence": 0.24493664503097534, "detection_id": "92-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.017111+00	2025-11-05 18:21:27.148378+00	2025-11-05 18:21:27.148386+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
86d7208d-ac18-49c4-a48d-155d7348f5b1	INF-RED-132127-94	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.87591552734375, 90.43110656738281, 105.29721069335938, 102.42335510253906], "source": "webcam_local", "timestamp": "2025-11-05T18:21:26.842675", "confidence": 0.2348041981458664, "detection_id": "90-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:26.847166+00	2025-11-05 18:21:27.14744+00	2025-11-05 18:21:27.147452+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
dd0d3646-6241-46f8-8bbf-2405d0811075	INF-RED-132127-97	red_light	medium	\N	\N		0	\N	\N			{"bbox": [58.905975341796875, 86.04998779296875, 78.44351196289062, 103.64157104492188], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.013192", "confidence": 0.21440689265727997, "detection_id": "92-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.017349+00	2025-11-05 18:21:27.192668+00	2025-11-05 18:21:27.192678+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
664ac90e-9cca-4d73-9a74-b38a4805cf36	INF-SPE-132127-39	speed	medium	\N	\N		0	77.1	60			{"bbox": [245.58706665039062, 92.99726867675781, 263.3194885253906, 112.07734680175781], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.194082", "confidence": 0.8001640439033508, "detection_id": "94-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.201836+00	2025-11-05 18:21:27.225868+00	2025-11-05 18:21:27.225875+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d957fecb-2262-4a1a-9902-df9c859eba1d	INF-RED-132127-50	red_light	medium	\N	\N		0	\N	\N			{"bbox": [59.72865295410156, 85.57829284667969, 78.6375732421875, 103.73551940917969], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.195362", "confidence": 0.532865583896637, "detection_id": "94-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.202053+00	2025-11-05 18:21:27.271095+00	2025-11-05 18:21:27.271105+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
34a238d8-84cc-410c-b5e0-93a1f2abe356	INF-SPE-132127-61	speed	medium	\N	\N		0	73.1	60			{"bbox": [86.48725891113281, 83.93242645263672, 114.36372375488281, 101.90990447998047], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.196185", "confidence": 0.4780133366584778, "detection_id": "94-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.202279+00	2025-11-05 18:21:27.310828+00	2025-11-05 18:21:27.310836+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
311ba7ac-7ff7-4315-b5bb-9adbe9fea00c	INF-RED-132127-41	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.024377822875977, 87.02218627929688, 59.17829132080078, 103.556640625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.197187", "confidence": 0.45723190903663635, "detection_id": "94-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.202506+00	2025-11-05 18:21:27.349956+00	2025-11-05 18:21:27.349965+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4564da0f-4bd6-48a0-8a72-52a89ef1369d	INF-SPE-132127-89	speed	medium	\N	\N		0	74.8	60			{"bbox": [247.6787872314453, 93.83963012695312, 265.99774169921875, 112.40484619140625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.352666", "confidence": 0.7165131568908691, "detection_id": "96-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.361824+00	2025-11-05 18:21:27.405873+00	2025-11-05 18:21:27.405879+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ea93a01a-07c3-442e-9c00-094c8219a5de	INF-RED-132127-20	red_light	medium	\N	\N		0	\N	\N			{"bbox": [127.80517578125, 87.86373901367188, 139.5753173828125, 97.0123291015625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.198184", "confidence": 0.2469761222600937, "detection_id": "94-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.202684+00	2025-11-05 18:21:27.406752+00	2025-11-05 18:21:27.406756+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
27f373c3-866f-4b81-9926-cfd1a9746a2c	INF-RED-132127-58	red_light	medium	\N	\N		0	\N	\N			{"bbox": [28.649690628051758, 87.94416809082031, 53.13438415527344, 106.06700134277344], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.353660", "confidence": 0.6614562273025513, "detection_id": "96-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.362052+00	2025-11-05 18:21:27.449639+00	2025-11-05 18:21:27.449653+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c6a8f212-2a6e-41f3-99ea-deda0735954d	INF-SPE-132127-53	speed	medium	\N	\N		0	98.4	60			{"bbox": [125.29537963867188, 89.57475280761719, 140.20101928710938, 97.97372436523438], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.354519", "confidence": 0.3951815962791443, "detection_id": "96-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.362257+00	2025-11-05 18:21:27.505745+00	2025-11-05 18:21:27.505756+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c2e45c08-b027-45e3-9183-4a3d6db9c7e5	INF-SPE-132127-73	speed	medium	\N	\N		0	86.7	60			{"bbox": [53.47523880004883, 76.52232360839844, 78.82420349121094, 104.83305358886719], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.355621", "confidence": 0.3094395399093628, "detection_id": "96-9", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.362467+00	2025-11-05 18:21:27.548414+00	2025-11-05 18:21:27.548422+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
29fb2952-df21-470e-8437-ae5cfe90c6d6	INF-RED-132127-34	red_light	medium	\N	\N		0	\N	\N			{"bbox": [87.13552856445312, 85.15730285644531, 114.30926513671875, 103.29084777832031], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.356588", "confidence": 0.2630072832107544, "detection_id": "96-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.362636+00	2025-11-05 18:21:27.581998+00	2025-11-05 18:21:27.582005+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
28d0012d-b40a-4398-878b-8ffda064fd52	INF-RED-132127-65	red_light	medium	\N	\N		0	\N	\N			{"bbox": [52.83055114746094, 76.67048645019531, 78.98390197753906, 104.84089660644531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.357698", "confidence": 0.2488543689250946, "detection_id": "96-13", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.362815+00	2025-11-05 18:21:27.637123+00	2025-11-05 18:21:27.637131+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
086fa53f-b8d8-4243-a544-922e61379203	INF-SPE-132127-59	speed	medium	\N	\N		0	98.9	60			{"bbox": [249.08612060546875, 94.09988403320312, 265.65216064453125, 111.89273071289062], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.540218", "confidence": 0.7127162218093872, "detection_id": "98-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.549541+00	2025-11-05 18:21:27.677565+00	2025-11-05 18:21:27.677611+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a17b479d-d441-45e8-a5e4-70a1d12deb61	INF-RED-132127-86	red_light	medium	\N	\N		0	\N	\N			{"bbox": [123.97163391113281, 89.82124328613281, 137.5233917236328, 98.24104309082031], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.541552", "confidence": 0.458061158657074, "detection_id": "98-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.549818+00	2025-11-05 18:21:27.721682+00	2025-11-05 18:21:27.721694+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
28cdcc8a-ce36-4c5a-a307-2c992b48bbaf	INF-SPE-132127-35	speed	medium	\N	\N		0	94.5	60			{"bbox": [29.72919464111328, 88.93556213378906, 59.9920654296875, 107.31468200683594], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.713746", "confidence": 0.8129462003707886, "detection_id": "100-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.725675+00	2025-11-05 18:21:27.762828+00	2025-11-05 18:21:27.762835+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
77a66e76-95be-4c5b-b518-10a7bbd72a46	INF-RED-132127-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.08650970458984, 85.51325988769531, 112.98957061767578, 103.14814758300781], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.543104", "confidence": 0.29306352138519287, "detection_id": "98-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.55007+00	2025-11-05 18:21:27.764888+00	2025-11-05 18:21:27.764893+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
63975e45-e5a4-4632-b085-f513836c3785	INF-RED-132127-13	red_light	medium	\N	\N		0	\N	\N			{"bbox": [122.55130004882812, 89.93981170654297, 137.18411254882812, 99.71570587158203], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.715551", "confidence": 0.47895053029060364, "detection_id": "100-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.725836+00	2025-11-05 18:21:27.812373+00	2025-11-05 18:21:27.81238+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
224931d2-1ff0-4c78-b6a5-7139d3c9319c	INF-RED-132127-61	red_light	medium	\N	\N		0	\N	\N			{"bbox": [59.297386169433594, 88.44393157958984, 78.1968765258789, 105.47582244873047], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.544162", "confidence": 0.28688210248947144, "detection_id": "98-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.550304+00	2025-11-05 18:21:27.818894+00	2025-11-05 18:21:27.818905+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f25c8929-a80e-4b0a-aa0e-b0e7cb0744f2	INF-RED-132127-64	red_light	medium	\N	\N		0	\N	\N			{"bbox": [49.09846496582031, 76.66984558105469, 78.88394927978516, 104.89976501464844], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.545379", "confidence": 0.22923249006271362, "detection_id": "98-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.550515+00	2025-11-05 18:21:27.866267+00	2025-11-05 18:21:27.866279+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
92cd3212-fde2-4d5e-8c23-95fcd4135286	INF-SPE-132127-50	speed	medium	\N	\N		0	97.5	60			{"bbox": [58.16912078857422, 88.79002380371094, 79.53113555908203, 106.31382751464844], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.717988", "confidence": 0.3671709895133972, "detection_id": "100-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.726037+00	2025-11-05 18:21:27.870734+00	2025-11-05 18:21:27.870741+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
10365eb2-3575-49af-84c1-f33a6617fd6a	INF-RED-132127-59	red_light	medium	\N	\N		0	\N	\N			{"bbox": [84.54446411132812, 87.10832214355469, 112.65118408203125, 103.95298767089844], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.719413", "confidence": 0.3453439772129059, "detection_id": "100-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.726238+00	2025-11-05 18:21:27.909314+00	2025-11-05 18:21:27.909321+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8be99113-db4e-4daa-bba1-4369f9424556	INF-SPE-132127-25	speed	medium	\N	\N		0	86.3	60			{"bbox": [30.2427978515625, 89.01831817626953, 61.204429626464844, 107.73783111572266], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.895517", "confidence": 0.6800746321678162, "detection_id": "102-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.903606+00	2025-11-05 18:21:27.926977+00	2025-11-05 18:21:27.926983+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
788caa93-3b33-4ef9-8268-37942effa88a	INF-RED-132127-35	red_light	medium	\N	\N		0	\N	\N			{"bbox": [50.852439880371094, 77.49046325683594, 79.7806167602539, 106.1131591796875], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.720470", "confidence": 0.3217782974243164, "detection_id": "100-10", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.72645+00	2025-11-05 18:21:27.937372+00	2025-11-05 18:21:27.937379+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
652ef426-32f5-4ef5-9855-c5af3c20225e	INF-SPE-132127-78	speed	medium	\N	\N		0	98.5	60			{"bbox": [251.17819213867188, 95.39436340332031, 265.2067565917969, 111.78968811035156], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.721435", "confidence": 0.25445929169654846, "detection_id": "100-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.726651+00	2025-11-05 18:21:27.978701+00	2025-11-05 18:21:27.97871+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3eae5249-fe6f-4d9c-9ccc-4cf66bb2af0e	INF-RED-132128-63	red_light	medium	\N	\N		0	\N	\N			{"bbox": [85.58919525146484, 87.34144592285156, 111.79607391357422, 106.52894592285156], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.897692", "confidence": 0.28828373551368713, "detection_id": "102-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.904027+00	2025-11-05 18:21:28.070299+00	2025-11-05 18:21:28.070304+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2c55dd9a-74c6-4386-a06c-f39e8e9e0e1f	INF-SPE-132128-20	speed	medium	\N	\N		0	93.7	60			{"bbox": [49.08617401123047, 77.63555908203125, 80.1931381225586, 106.749755859375], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.898624", "confidence": 0.2747631371021271, "detection_id": "102-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.904187+00	2025-11-05 18:21:28.108488+00	2025-11-05 18:21:28.108494+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e8998f9a-9385-4f16-97b2-06d594f00118	INF-RED-132128-15	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.65282440185547, 89.66983032226562, 63.717369079589844, 108.48825073242188], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.067941", "confidence": 0.5014740824699402, "detection_id": "104-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.073705+00	2025-11-05 18:21:28.109368+00	2025-11-05 18:21:28.109373+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2dc7d94f-34eb-4cda-b46d-66832d4a2edd	INF-RED-132128-88	red_light	medium	\N	\N		0	\N	\N			{"bbox": [48.94987106323242, 77.61456298828125, 80.37739562988281, 106.69749450683594], "source": "webcam_local", "timestamp": "2025-11-05T18:21:27.899818", "confidence": 0.2617783546447754, "detection_id": "102-11", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:27.904421+00	2025-11-05 18:21:28.151419+00	2025-11-05 18:21:28.151427+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
82c97994-7422-4658-8583-7395faae50f8	INF-RED-132128-85	red_light	medium	\N	\N		0	\N	\N			{"bbox": [118.76744079589844, 91.37619018554688, 136.6378936767578, 101.33840942382812], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.069213", "confidence": 0.4540706276893616, "detection_id": "104-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.073996+00	2025-11-05 18:21:28.152905+00	2025-11-05 18:21:28.152913+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1205d5b7-59a9-4b87-98b9-4afd3ba80a9f	INF-SPE-132128-74	speed	medium	\N	\N		0	70.5	60			{"bbox": [61.020652770996094, 89.90791320800781, 80.09041595458984, 107.01341247558594], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.070128", "confidence": 0.3312431573867798, "detection_id": "104-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.07429+00	2025-11-05 18:21:28.197302+00	2025-11-05 18:21:28.19731+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1f726072-e102-45a4-b504-fb52b9021822	INF-RED-132128-92	red_light	medium	\N	\N		0	\N	\N			{"bbox": [115.92681884765625, 90.24725341796875, 138.54257202148438, 103.00592041015625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.233005", "confidence": 0.6408722996711731, "detection_id": "106-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.241465+00	2025-11-05 18:21:28.265544+00	2025-11-05 18:21:28.265551+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ecb60e27-197d-4982-8a48-b979eca7bf86	INF-RED-132128-50	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.789043426513672, 89.57746887207031, 50.46560287475586, 108.29914855957031], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.234031", "confidence": 0.6221299767494202, "detection_id": "106-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.241819+00	2025-11-05 18:21:28.332984+00	2025-11-05 18:21:28.332994+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3a22f5a0-86c4-4f73-81e2-9315934249e8	INF-SPE-132128-44	speed	medium	\N	\N		0	73.7	60			{"bbox": [63.00830841064453, 88.26251220703125, 79.74347686767578, 106.65565490722656], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.235334", "confidence": 0.3098756670951843, "detection_id": "106-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.24214+00	2025-11-05 18:21:28.395219+00	2025-11-05 18:21:28.395228+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1499f8f5-dc0c-4d5a-98d1-95aa855936bf	INF-RED-132128-42	red_light	medium	\N	\N		0	\N	\N			{"bbox": [47.87620544433594, 77.41896057128906, 80.2034912109375, 106.58992004394531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.236328", "confidence": 0.23658239841461182, "detection_id": "106-9", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.242516+00	2025-11-05 18:21:28.435406+00	2025-11-05 18:21:28.435413+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
256b7e56-a334-4449-9d9f-2cd6736e8a91	INF-SPE-132128-31	speed	medium	\N	\N		0	75.9	60			{"bbox": [28.587331771850586, 89.91439056396484, 50.37236785888672, 108.81188201904297], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.424659", "confidence": 0.620966374874115, "detection_id": "108-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.431164+00	2025-11-05 18:21:28.460076+00	2025-11-05 18:21:28.460082+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c5ae3501-d08d-4bbf-a4ef-2530c42867db	INF-RED-132128-44	red_light	medium	\N	\N		0	\N	\N			{"bbox": [47.83705139160156, 77.48217010498047, 79.94552612304688, 106.45032501220703], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.237326", "confidence": 0.22748012840747833, "detection_id": "106-10", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.242751+00	2025-11-05 18:21:28.460998+00	2025-11-05 18:21:28.461002+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e708d47b-0824-4cda-b8c9-c798dc325a36	INF-RED-132128-64	red_light	medium	\N	\N		0	\N	\N			{"bbox": [44.83221435546875, 77.68446350097656, 79.56686401367188, 107.02302551269531], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.425730", "confidence": 0.5991631150245667, "detection_id": "108-4", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.431602+00	2025-11-05 18:21:28.483708+00	2025-11-05 18:21:28.483713+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
be40bcac-1a92-4e31-a854-db757c82d255	INF-RED-132128-24	red_light	medium	\N	\N		0	\N	\N			{"bbox": [62.64897155761719, 89.31021881103516, 79.62098693847656, 107.08895111083984], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.426715", "confidence": 0.37651652097702026, "detection_id": "108-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.431998+00	2025-11-05 18:21:28.509844+00	2025-11-05 18:21:28.50985+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e51e8594-d663-463a-8fd6-cde742164d02	INF-SPE-132128-68	speed	medium	\N	\N		0	71.5	60			{"bbox": [113.03129577636719, 91.14071655273438, 131.43482971191406, 102.40289306640625], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.427475", "confidence": 0.3628237247467041, "detection_id": "108-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.432222+00	2025-11-05 18:21:28.534415+00	2025-11-05 18:21:28.53442+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
cb50e086-647d-4c0d-bf4d-4f1215dc980f	INF-RED-132128-84	red_light	medium	\N	\N		0	\N	\N			{"bbox": [84.8310317993164, 86.69461059570312, 107.25806427001953, 108.93434143066406], "source": "webcam_local", "timestamp": "2025-11-05T18:21:28.428351", "confidence": 0.2522524297237396, "detection_id": "108-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:21:28.43246+00	2025-11-05 18:21:28.557556+00	2025-11-05 18:21:28.557561+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f31849fb-c47a-4a65-b8b3-e1147a653213	INF001090	speed	high	\N	\N		0	\N	\N			{}	pending	\N		\N	\N	\N	2025-11-05 18:27:55.360657+00	2025-11-05 18:27:55.36813+00	2025-11-05 18:33:49.1378+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	5d989090-6cf9-4062-ba86-b7603f793659	\N	0.8	{}	18.85	1.234
d5626ca3-16b6-40c8-903e-a220a7dd954a	INF-RED-133626-53	red_light	medium	\N	\N		0	\N	\N			{"bbox": [105.65098571777344, 153.49514770507812, 298.66387939453125, 268.9081726074219], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.677572", "confidence": 0.9301855564117432, "detection_id": "68-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.688336+00	2025-11-05 18:36:26.738079+00	2025-11-05 18:36:26.738088+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
207d19ab-5585-4189-bea5-d93385a980c8	INF-RED-133626-82	red_light	medium	\N	\N		0	\N	\N			{"bbox": [285.9243469238281, 114.92992401123047, 303.4388122558594, 126.77574920654297], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.679069", "confidence": 0.5509453415870667, "detection_id": "68-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.688682+00	2025-11-05 18:36:26.77289+00	2025-11-05 18:36:26.772896+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
61bcac8a-9dbd-46ee-9820-9c4380fd9b4d	INF-SPE-133626-37	speed	medium	\N	\N		0	80.7	60			{"bbox": [191.7984161376953, 115.3652572631836, 206.9954833984375, 127.11737823486328], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.680060", "confidence": 0.5277655720710754, "detection_id": "68-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.689098+00	2025-11-05 18:36:26.811388+00	2025-11-05 18:36:26.811396+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a79839f5-68c0-472b-a8a7-e5230dab405d	INF-RED-133626-77	red_light	medium	\N	\N		0	\N	\N			{"bbox": [212.16522216796875, 116.84598541259766, 226.25335693359375, 127.30840301513672], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.681036", "confidence": 0.5225405693054199, "detection_id": "68-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.689719+00	2025-11-05 18:36:26.847977+00	2025-11-05 18:36:26.847986+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0758e3db-88ce-4828-92ba-4d2669208c33	INF-RED-133626-72	red_light	medium	\N	\N		0	\N	\N			{"bbox": [395.1850891113281, 117.45284271240234, 413.8135070800781, 132.97848510742188], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.681989", "confidence": 0.4980592727661133, "detection_id": "68-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.690387+00	2025-11-05 18:36:26.889783+00	2025-11-05 18:36:26.889791+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9f61e46f-3819-4d46-ab3f-13978a6b6b02	INF-SPE-133626-69	speed	medium	\N	\N		0	76.8	60			{"bbox": [279.7314453125, 113.54484558105469, 289.5613708496094, 123.8653793334961], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.682846", "confidence": 0.2909432351589203, "detection_id": "68-13", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.690714+00	2025-11-05 18:36:26.956664+00	2025-11-05 18:36:26.956671+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7a27472e-c5c6-4d4c-b8b6-436ee7ad9e6e	INF-RED-133626-39	red_light	medium	\N	\N		0	\N	\N			{"bbox": [108.72338104248047, 152.82907104492188, 297.2251892089844, 268.6851501464844], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.892392", "confidence": 0.920860767364502, "detection_id": "70-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.905934+00	2025-11-05 18:36:26.959716+00	2025-11-05 18:36:26.959722+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8427502b-067a-44d4-bdeb-53244dab9e10	INF-SPE-133626-87	speed	medium	\N	\N		0	74.2	60			{"bbox": [191.47515869140625, 115.78882598876953, 207.2516326904297, 127.0641860961914], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.893995", "confidence": 0.5833242535591125, "detection_id": "70-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.906217+00	2025-11-05 18:36:26.996718+00	2025-11-05 18:36:26.996725+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6030feb2-36b5-445c-b9a9-447b88d821fc	INF-RED-133627-79	red_light	medium	\N	\N		0	\N	\N			{"bbox": [285.06353759765625, 115.08206176757812, 303.31365966796875, 126.67103576660156], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.895337", "confidence": 0.5525937080383301, "detection_id": "70-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.906454+00	2025-11-05 18:36:27.039473+00	2025-11-05 18:36:27.039482+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
96ca2dd2-43b2-46dc-8d0d-7478c44d75ab	INF-RED-133627-19	red_light	medium	\N	\N		0	\N	\N			{"bbox": [211.49990844726562, 116.80540466308594, 226.55612182617188, 127.49617767333984], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.896705", "confidence": 0.48520544171333313, "detection_id": "70-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.906644+00	2025-11-05 18:36:27.110485+00	2025-11-05 18:36:27.1105+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
799830b0-af8b-4316-87a2-455875788cb0	INF-SPE-133627-71	speed	medium	\N	\N		0	86.4	60			{"bbox": [399.1040344238281, 119.95829772949219, 413.6047058105469, 132.71836853027344], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.897756", "confidence": 0.4072715938091278, "detection_id": "70-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.906897+00	2025-11-05 18:36:27.159972+00	2025-11-05 18:36:27.159979+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a019d057-5f5c-44ff-b464-4334922e4d50	INF-SPE-133627-34	speed	medium	\N	\N		0	76.9	60			{"bbox": [114.30634307861328, 151.00257873535156, 295.1513671875, 268.6973876953125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.151241", "confidence": 0.9315836429595947, "detection_id": "72-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.163879+00	2025-11-05 18:36:27.200198+00	2025-11-05 18:36:27.200204+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
123457ad-6281-45fb-8781-8d382c0d9ee3	INF-RED-133627-61	red_light	medium	\N	\N		0	\N	\N			{"bbox": [279.67730712890625, 113.61563873291016, 289.4651794433594, 123.93578338623047], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.899015", "confidence": 0.30026912689208984, "detection_id": "70-13", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.9071+00	2025-11-05 18:36:27.200788+00	2025-11-05 18:36:27.200794+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d64bc3cc-f560-49ec-946e-b3fd9e812b46	INF-RED-133627-86	red_light	medium	\N	\N		0	\N	\N			{"bbox": [190.87765502929688, 115.12676239013672, 208.01971435546875, 127.03667449951172], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.152415", "confidence": 0.56394362449646, "detection_id": "72-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.164202+00	2025-11-05 18:36:27.248702+00	2025-11-05 18:36:27.248707+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b9fdd908-936d-4393-86b4-0607f5916035	INF-RED-133627-56	red_light	medium	\N	\N		0	\N	\N			{"bbox": [272.2397766113281, 111.5064926147461, 281.35321044921875, 120.38738250732422], "source": "webcam_local", "timestamp": "2025-11-05T18:36:26.900430", "confidence": 0.28280121088027954, "detection_id": "70-15", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:26.9073+00	2025-11-05 18:36:27.249498+00	2025-11-05 18:36:27.249502+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1e2daa85-3f46-45c5-b8c8-9a81a7a19f9b	INF-RED-133627-96	red_light	medium	\N	\N		0	\N	\N			{"bbox": [211.35227966308594, 116.79753112792969, 226.45948791503906, 127.33978271484375], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.153240", "confidence": 0.4926975965499878, "detection_id": "72-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.164418+00	2025-11-05 18:36:27.283499+00	2025-11-05 18:36:27.283507+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8df5d8d3-284f-445b-a37d-c74438f31721	INF-RED-133627-66	red_light	medium	\N	\N		0	\N	\N			{"bbox": [285.04388427734375, 113.95408630371094, 302.9593811035156, 126.57440185546875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.154075", "confidence": 0.4810373783111572, "detection_id": "72-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.164693+00	2025-11-05 18:36:27.321685+00	2025-11-05 18:36:27.321692+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
384d28da-4deb-414b-a675-c6dd7bae7435	INF-RED-133627-78	red_light	medium	\N	\N		0	\N	\N			{"bbox": [402.4137268066406, 120.7239990234375, 414.7859802246094, 131.61448669433594], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.155209", "confidence": 0.416951447725296, "detection_id": "72-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.165009+00	2025-11-05 18:36:27.358923+00	2025-11-05 18:36:27.358932+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fddc157a-ad41-4d6a-8e06-344fe7b9cd81	INF-RED-133627-63	red_light	medium	\N	\N		0	\N	\N			{"bbox": [121.44868469238281, 147.97581481933594, 290.5830078125, 269.3002624511719], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.361738", "confidence": 0.9335612654685974, "detection_id": "74-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.372855+00	2025-11-05 18:36:27.410472+00	2025-11-05 18:36:27.410477+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
13295219-4eb2-42fd-89bf-f88930f3bd11	INF-SPE-133627-73	speed	medium	\N	\N		0	85.8	60			{"bbox": [278.32232666015625, 112.19080352783203, 289.95208740234375, 122.73307800292969], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.156037", "confidence": 0.3983689844608307, "detection_id": "72-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.165236+00	2025-11-05 18:36:27.412447+00	2025-11-05 18:36:27.412452+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d169137e-e00d-461e-b5a7-b9e7ba1da1db	INF-SPE-133627-82	speed	medium	\N	\N		0	80.6	60			{"bbox": [191.61378479003906, 115.4875717163086, 207.6332244873047, 126.83544158935547], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.362905", "confidence": 0.6278314590454102, "detection_id": "74-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.373079+00	2025-11-05 18:36:27.4502+00	2025-11-05 18:36:27.450207+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7913e25a-4f56-42fe-aef1-3dfed686a862	INF-RED-133627-34	red_light	medium	\N	\N		0	\N	\N			{"bbox": [273.0214538574219, 111.69798278808594, 284.0671081542969, 120.72277069091797], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.157196", "confidence": 0.2705669403076172, "detection_id": "72-16", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.165517+00	2025-11-05 18:36:27.451118+00	2025-11-05 18:36:27.451123+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
55b5bc76-e64a-45ed-9703-ff8f8f3ed684	INF-SPE-133627-94	speed	medium	\N	\N		0	88.9	60			{"bbox": [281.147216796875, 112.94290924072266, 303.4284973144531, 126.20890045166016], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.363935", "confidence": 0.5242270231246948, "detection_id": "74-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.373249+00	2025-11-05 18:36:27.507776+00	2025-11-05 18:36:27.507789+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
22161e9a-6369-4f6b-a5f7-4ea2e76d904c	INF-SPE-133627-14	speed	medium	\N	\N		0	88.4	60			{"bbox": [270.79833984375, 111.44890594482422, 279.9522705078125, 119.33361053466797], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.158064", "confidence": 0.22568024694919586, "detection_id": "72-18", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.165742+00	2025-11-05 18:36:27.510466+00	2025-11-05 18:36:27.510476+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7db767e9-c277-44c3-8392-571925f435ec	INF-RED-133627-55	red_light	medium	\N	\N		0	\N	\N			{"bbox": [211.57383728027344, 114.39129638671875, 226.7413787841797, 127.17864990234375], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.364935", "confidence": 0.5166415572166443, "detection_id": "74-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.373414+00	2025-11-05 18:36:27.547063+00	2025-11-05 18:36:27.547072+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
71dbbfe7-3703-4109-93c1-9398837f7115	INF-RED-133627-47	red_light	medium	\N	\N		0	\N	\N			{"bbox": [278.5470886230469, 111.99740600585938, 290.0831604003906, 122.889892578125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.366026", "confidence": 0.3683909773826599, "detection_id": "74-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.373601+00	2025-11-05 18:36:27.58372+00	2025-11-05 18:36:27.583733+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e9ea3ef0-52b5-4fa3-9b29-e1b14e6f45ff	INF-RED-133627-22	red_light	medium	\N	\N		0	\N	\N			{"bbox": [127.12246704101562, 146.60531616210938, 288.1228942871094, 268.4355773925781], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.589121", "confidence": 0.9408723711967468, "detection_id": "76-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.599913+00	2025-11-05 18:36:27.631774+00	2025-11-05 18:36:27.631781+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d95d1af8-1023-474e-90e1-8a8038ab4cde	INF-SPE-133627-56	speed	medium	\N	\N		0	77.2	60			{"bbox": [270.826904296875, 110.82499694824219, 279.7174377441406, 119.30049133300781], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.367138", "confidence": 0.26224055886268616, "detection_id": "74-16", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.373784+00	2025-11-05 18:36:27.634374+00	2025-11-05 18:36:27.634378+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
73f57f1b-4a5b-4ac5-9454-94c90a1df5ab	INF-RED-133627-36	red_light	medium	\N	\N		0	\N	\N			{"bbox": [190.6439666748047, 114.61317443847656, 207.42320251464844, 126.87744140625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.590232", "confidence": 0.6074504852294922, "detection_id": "76-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.600052+00	2025-11-05 18:36:27.661869+00	2025-11-05 18:36:27.661876+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2a882823-a9ca-4503-aa2d-f2a9300b2b79	INF-RED-133627-28	red_light	medium	\N	\N		0	\N	\N			{"bbox": [210.95631408691406, 115.35990905761719, 226.36505126953125, 126.94728088378906], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.591490", "confidence": 0.48801857233047485, "detection_id": "76-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.6002+00	2025-11-05 18:36:27.692454+00	2025-11-05 18:36:27.692462+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2907cf20-8ccb-459a-8267-18f436897f51	INF-RED-133627-42	red_light	medium	\N	\N		0	\N	\N			{"bbox": [286.4249572753906, 113.74560546875, 302.9305419921875, 126.76996612548828], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.592737", "confidence": 0.4777868688106537, "detection_id": "76-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.600366+00	2025-11-05 18:36:27.729247+00	2025-11-05 18:36:27.729253+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ce93d5fa-fa2f-457c-8c9e-81486056e3d3	INF-SPE-133627-87	speed	medium	\N	\N		0	86.5	60			{"bbox": [137.29721069335938, 144.466064453125, 283.9727783203125, 268.7215576171875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.785192", "confidence": 0.9298610687255859, "detection_id": "78-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.797807+00	2025-11-05 18:36:27.829752+00	2025-11-05 18:36:27.829762+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
33bcf91f-1586-4af7-a01b-4ce810318de3	INF-SPE-133627-35	speed	medium	\N	\N		0	80.5	60			{"bbox": [270.80328369140625, 111.07233428955078, 279.47113037109375, 119.50358581542969], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.594611", "confidence": 0.20920972526073456, "detection_id": "76-14", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.600642+00	2025-11-05 18:36:27.850674+00	2025-11-05 18:36:27.850681+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f5c81027-03ec-481c-8e46-aa0916272c9d	INF-RED-133627-10	red_light	medium	\N	\N		0	\N	\N			{"bbox": [191.03997802734375, 115.447265625, 206.12425231933594, 125.97798156738281], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.787106", "confidence": 0.5908321738243103, "detection_id": "78-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.797996+00	2025-11-05 18:36:27.872321+00	2025-11-05 18:36:27.872333+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ee92a566-277a-4461-996b-645b406f6928	INF-SPE-133627-44	speed	medium	\N	\N		0	84.7	60			{"bbox": [286.6907958984375, 114.06440734863281, 304.00482177734375, 125.53834533691406], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.788664", "confidence": 0.4917888045310974, "detection_id": "78-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.798187+00	2025-11-05 18:36:27.9088+00	2025-11-05 18:36:27.908807+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
dd13292d-8dc8-443e-a8f8-787107293d91	INF-RED-133627-62	red_light	medium	\N	\N		0	\N	\N			{"bbox": [403.3568115234375, 108.79408264160156, 474.8262634277344, 139.11634826660156], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.789762", "confidence": 0.4728695750236511, "detection_id": "78-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.79831+00	2025-11-05 18:36:27.941124+00	2025-11-05 18:36:27.941131+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
395c8504-a3e9-4ac3-9d04-4a3444ea2c9b	INF-RED-133627-33	red_light	medium	\N	\N		0	\N	\N			{"bbox": [142.9285888671875, 141.40391540527344, 281.57366943359375, 269.07550048828125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.948302", "confidence": 0.9305020570755005, "detection_id": "80-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.960858+00	2025-11-05 18:36:27.990961+00	2025-11-05 18:36:27.990968+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a25ba7cd-f862-4844-b08c-69141ea4737f	INF-SPE-133627-24	speed	medium	\N	\N		0	88	60			{"bbox": [208.0300750732422, 114.17505645751953, 226.20809936523438, 126.76488494873047], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.790431", "confidence": 0.4622165858745575, "detection_id": "78-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.798477+00	2025-11-05 18:36:27.997615+00	2025-11-05 18:36:27.99762+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ebbf6291-c42f-4117-8aa8-55aaad66044a	INF-RED-133628-33	red_light	medium	\N	\N		0	\N	\N			{"bbox": [392.09063720703125, 105.29907989501953, 467.3152160644531, 139.00123596191406], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.949474", "confidence": 0.5573375821113586, "detection_id": "80-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.961054+00	2025-11-05 18:36:28.030939+00	2025-11-05 18:36:28.030948+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1f43cd0e-141e-4793-8fe6-8e47297fd0c5	INF-RED-133628-63	red_light	medium	\N	\N		0	\N	\N			{"bbox": [278.71728515625, 111.50086975097656, 289.834716796875, 121.88230895996094], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.791245", "confidence": 0.3660910129547119, "detection_id": "78-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.798607+00	2025-11-05 18:36:28.042619+00	2025-11-05 18:36:28.042629+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f927791c-2900-464e-a639-76156b52eac8	INF-SPE-133628-18	speed	medium	\N	\N		0	79.2	60			{"bbox": [190.95753479003906, 114.10753631591797, 205.2326202392578, 124.03826141357422], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.950433", "confidence": 0.5385084748268127, "detection_id": "80-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.961246+00	2025-11-05 18:36:28.096947+00	2025-11-05 18:36:28.09696+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
bab02e84-3471-4112-aa75-aada3f869135	INF-RED-133628-95	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.73895263671875, 110.27030944824219, 279.7042236328125, 119.13554382324219], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.791989", "confidence": 0.2751028835773468, "detection_id": "78-13", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.798794+00	2025-11-05 18:36:28.097669+00	2025-11-05 18:36:28.097674+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3c993c5b-87ce-44fd-bebb-89936cafeadc	INF-RED-133628-85	red_light	medium	\N	\N		0	\N	\N			{"bbox": [403.3975524902344, 111.7012939453125, 428.4192810058594, 138.74578857421875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.792863", "confidence": 0.24871523678302765, "detection_id": "78-14", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.798978+00	2025-11-05 18:36:28.161154+00	2025-11-05 18:36:28.161158+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2f62c725-ce0b-480f-af7c-330c2cdc90d6	INF-RED-133628-36	red_light	medium	\N	\N		0	\N	\N			{"bbox": [145.75254821777344, 138.68658447265625, 278.2602844238281, 268.4742126464844], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.126925", "confidence": 0.8713540434837341, "detection_id": "82-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.137678+00	2025-11-05 18:36:28.162544+00	2025-11-05 18:36:28.162548+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
48304ed5-bdab-4eec-b98c-b378f4b4b4f8	INF-RED-133628-13	red_light	medium	\N	\N		0	\N	\N			{"bbox": [208.79795837402344, 114.05248260498047, 225.5193328857422, 124.90729522705078], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.951305", "confidence": 0.5230244994163513, "detection_id": "80-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.961406+00	2025-11-05 18:36:28.165077+00	2025-11-05 18:36:28.165084+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f2964e3a-8ab2-4a53-8ff4-c082b323c014	INF-SPE-133628-30	speed	medium	\N	\N		0	72.7	60			{"bbox": [383.56182861328125, 103.96587371826172, 455.5904846191406, 138.67259216308594], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.127714", "confidence": 0.7523080110549927, "detection_id": "82-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.137923+00	2025-11-05 18:36:28.20888+00	2025-11-05 18:36:28.208885+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1b228d40-4c73-47b6-ba37-502a8462bb0d	INF-RED-133628-42	red_light	medium	\N	\N		0	\N	\N			{"bbox": [279.61029052734375, 109.8749771118164, 291.5411682128906, 121.69470977783203], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.952349", "confidence": 0.4088379144668579, "detection_id": "80-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.961563+00	2025-11-05 18:36:28.21327+00	2025-11-05 18:36:28.213276+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
880c8d5f-2bf0-4dac-bb0c-c0b5c86e99f4	INF-RED-133628-38	red_light	medium	\N	\N		0	\N	\N			{"bbox": [287.3043212890625, 110.53772735595703, 304.6529846191406, 123.02323150634766], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.128450", "confidence": 0.5333210825920105, "detection_id": "82-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.138175+00	2025-11-05 18:36:28.249644+00	2025-11-05 18:36:28.249652+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
88eed64d-13f7-49a5-aa62-1c21f248ca78	INF-RED-133628-30	red_light	medium	\N	\N		0	\N	\N			{"bbox": [288.8395690917969, 111.54084777832031, 304.1673278808594, 123.82328796386719], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.953298", "confidence": 0.39023882150650024, "detection_id": "80-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.961758+00	2025-11-05 18:36:28.252126+00	2025-11-05 18:36:28.252133+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
20da1799-4fe1-4272-94a4-2ec12d5f712e	INF-SPE-133628-52	speed	medium	\N	\N		0	76	60			{"bbox": [189.55288696289062, 111.47266387939453, 204.68527221679688, 123.56597900390625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.129041", "confidence": 0.5230758786201477, "detection_id": "82-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.13834+00	2025-11-05 18:36:28.303417+00	2025-11-05 18:36:28.303425+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3f90a7dd-2633-4132-b282-eceab44b4274	INF-RED-133628-37	red_light	medium	\N	\N		0	\N	\N			{"bbox": [381.4848937988281, 112.15015411376953, 399.0646667480469, 126.25254821777344], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.954245", "confidence": 0.24580146372318268, "detection_id": "80-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.962001+00	2025-11-05 18:36:28.30421+00	2025-11-05 18:36:28.304215+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9669eade-1fd2-4f53-8ef1-38568e445a65	INF-SPE-133628-88	speed	medium	\N	\N		0	80.9	60			{"bbox": [272.2297058105469, 109.39281463623047, 284.7627258300781, 119.1811752319336], "source": "webcam_local", "timestamp": "2025-11-05T18:36:27.954957", "confidence": 0.23124299943447113, "detection_id": "80-13", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:27.962158+00	2025-11-05 18:36:28.350383+00	2025-11-05 18:36:28.350389+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1d98bca0-728a-4dd7-8a0d-a028d309a3fc	INF-SPE-133628-29	speed	medium	\N	\N		0	72.8	60			{"bbox": [151.78306579589844, 136.44041442871094, 275.63800048828125, 258.65777587890625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.349299", "confidence": 0.9014877080917358, "detection_id": "84-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.36123+00	2025-11-05 18:36:28.396653+00	2025-11-05 18:36:28.396659+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
75d5c0bb-a6ca-493e-9125-7629230653cc	INF-SPE-133628-25	speed	medium	\N	\N		0	91.9	60			{"bbox": [404.915771484375, 114.84109497070312, 471.43121337890625, 142.68324279785156], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.130533", "confidence": 0.44335901737213135, "detection_id": "82-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.138672+00	2025-11-05 18:36:28.428749+00	2025-11-05 18:36:28.428755+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ccf139cb-5b61-4ff8-8046-ba70762919e4	INF-RED-133628-88	red_light	medium	\N	\N		0	\N	\N			{"bbox": [376.6295471191406, 101.43377685546875, 450.4626159667969, 138.4608154296875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.350283", "confidence": 0.821454644203186, "detection_id": "84-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.361434+00	2025-11-05 18:36:28.430006+00	2025-11-05 18:36:28.430012+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
901f42df-54ed-4502-b5d7-9cb1f9302fb8	INF-RED-133628-43	red_light	medium	\N	\N		0	\N	\N			{"bbox": [388.7987365722656, 117.94230651855469, 463.2051086425781, 147.18902587890625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.558349", "confidence": 0.8454036116600037, "detection_id": "86-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.570506+00	2025-11-05 18:36:28.640526+00	2025-11-05 18:36:28.640535+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3843362b-2d13-46b0-a493-02224c89f442	INF-SPE-133628-33	speed	medium	\N	\N		0	86.4	60			{"bbox": [155.81346130371094, 135.56700134277344, 272.1145935058594, 245.27249145507812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.558974", "confidence": 0.7946739196777344, "detection_id": "86-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.570678+00	2025-11-05 18:36:28.722497+00	2025-11-05 18:36:28.722513+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0640cc2c-d98c-4c13-8440-be9ed2394f7c	INF-RED-133628-94	red_light	medium	\N	\N		0	\N	\N			{"bbox": [208.90548706054688, 109.4509506225586, 224.47439575195312, 123.26394653320312], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.352144", "confidence": 0.6013274192810059, "detection_id": "84-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.361812+00	2025-11-05 18:36:28.725544+00	2025-11-05 18:36:28.725551+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6a375c4d-bd3c-4b47-9009-b9963037b0af	INF-RED-133628-57	red_light	medium	\N	\N		0	\N	\N			{"bbox": [406.07061767578125, 119.38460540771484, 441.42535400390625, 144.3334503173828], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.132062", "confidence": 0.22103311121463776, "detection_id": "82-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.13901+00	2025-11-05 18:36:28.727658+00	2025-11-05 18:36:28.727665+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c09c4d3f-4107-4924-b2e2-8198f4852a6d	INF-RED-133628-82	red_light	medium	\N	\N		0	\N	\N			{"bbox": [288.959228515625, 110.10134887695312, 304.988525390625, 121.73939514160156], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.352939", "confidence": 0.5766760110855103, "detection_id": "84-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.362066+00	2025-11-05 18:36:28.775133+00	2025-11-05 18:36:28.775139+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5ac51a9f-0070-40d1-ab83-715e63bf198c	INF-RED-133628-15	red_light	medium	\N	\N		0	\N	\N			{"bbox": [159.84600830078125, 132.20489501953125, 271.5655212402344, 226.3802490234375], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.769183", "confidence": 0.9236057996749878, "detection_id": "88-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.781296+00	2025-11-05 18:36:28.84014+00	2025-11-05 18:36:28.840146+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
91e16402-5421-4480-856a-1666bae74d09	INF-SPE-133628-53	speed	medium	\N	\N		0	73.2	60			{"bbox": [188.64463806152344, 108.64908599853516, 211.39622497558594, 122.70014190673828], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.353640", "confidence": 0.4688447117805481, "detection_id": "84-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.362248+00	2025-11-05 18:36:28.840769+00	2025-11-05 18:36:28.840774+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
90a346cb-e242-4404-80e6-d352abc9fecc	INF-RED-133628-80	red_light	medium	\N	\N		0	\N	\N			{"bbox": [206.85704040527344, 108.56854248046875, 223.98170471191406, 122.05696105957031], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.560433", "confidence": 0.6312135457992554, "detection_id": "86-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.570918+00	2025-11-05 18:36:28.86083+00	2025-11-05 18:36:28.860836+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5d78debe-250e-40b8-ae04-1ce89c45efa9	INF-RED-133628-97	red_light	medium	\N	\N		0	\N	\N			{"bbox": [378.2798767089844, 117.53034973144531, 458.5426025390625, 149.95632934570312], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.770292", "confidence": 0.8639346957206726, "detection_id": "88-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.781432+00	2025-11-05 18:36:28.888192+00	2025-11-05 18:36:28.888197+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
33e9b76e-3077-441a-bcce-1b595d28059e	INF-RED-133628-99	red_light	medium	\N	\N		0	\N	\N			{"bbox": [279.30706787109375, 107.39694213867188, 291.24462890625, 118.19192504882812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.354511", "confidence": 0.46646225452423096, "detection_id": "84-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.362471+00	2025-11-05 18:36:28.889306+00	2025-11-05 18:36:28.889311+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
847fef29-5160-4a69-bb79-7a1cdc675ca0	INF-RED-133628-51	red_light	medium	\N	\N		0	\N	\N			{"bbox": [287.44903564453125, 108.54068756103516, 306.23828125, 121.13129425048828], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.561302", "confidence": 0.6126755475997925, "detection_id": "86-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.571065+00	2025-11-05 18:36:28.890653+00	2025-11-05 18:36:28.890659+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c9cc1655-3851-441c-a2a3-504c505fdfd8	INF-RED-133628-17	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.7378234863281, 106.21820831298828, 283.65142822265625, 116.6170883178711], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.355529", "confidence": 0.2915162444114685, "detection_id": "84-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.362696+00	2025-11-05 18:36:28.93969+00	2025-11-05 18:36:28.939698+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3cb3ad8d-3f2e-4b8a-97ef-93cf479cacd3	INF-SPE-133628-58	speed	medium	\N	\N		0	93.4	60			{"bbox": [352.5081481933594, 99.19063568115234, 439.6663513183594, 139.42828369140625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.771252", "confidence": 0.7616158723831177, "detection_id": "88-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.781635+00	2025-11-05 18:36:28.940528+00	2025-11-05 18:36:28.940534+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
50fea6ca-74b4-46c3-bdcb-a773fd3e056f	INF-RED-133628-55	red_light	medium	\N	\N		0	\N	\N			{"bbox": [186.86119079589844, 109.03944396972656, 203.3339080810547, 121.35445404052734], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.562172", "confidence": 0.5549198985099792, "detection_id": "86-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.571197+00	2025-11-05 18:36:28.944226+00	2025-11-05 18:36:28.944235+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
35e03aa4-ce98-4041-b99b-e88d31d2022f	INF-SPE-133628-40	speed	medium	\N	\N		0	77.9	60			{"bbox": [322.8944091796875, 110.22262573242188, 337.3576354980469, 122.19877624511719], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.356301", "confidence": 0.2316375970840454, "detection_id": "84-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.362862+00	2025-11-05 18:36:29.008225+00	2025-11-05 18:36:29.008233+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ff0ba87a-2151-476f-afbe-919ab5c52c17	INF-RED-133629-40	red_light	medium	\N	\N		0	\N	\N			{"bbox": [440.4783630371094, 109.12321472167969, 479.8110656738281, 133.3666534423828], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.772502", "confidence": 0.610242486000061, "detection_id": "88-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.781821+00	2025-11-05 18:36:29.009603+00	2025-11-05 18:36:29.009612+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f8dbb2e8-e650-4054-b7a9-c830c883ebff	INF-SPE-133629-31	speed	medium	\N	\N		0	92.3	60			{"bbox": [9.309113502502441, 111.55801391601562, 31.16312599182129, 128.62252807617188], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.562820", "confidence": 0.44162291288375854, "detection_id": "86-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.571321+00	2025-11-05 18:36:29.010664+00	2025-11-05 18:36:29.010672+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d3830745-f22c-4575-8bbc-19b80809a383	INF-RED-133629-12	red_light	medium	\N	\N		0	\N	\N			{"bbox": [344.6146240234375, 183.69859313964844, 460.3098449707031, 262.46697998046875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.563457", "confidence": 0.3815669119358063, "detection_id": "86-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.571515+00	2025-11-05 18:36:29.070006+00	2025-11-05 18:36:29.070015+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7549e39f-cf51-44ce-9f84-0f21753ccc24	INF-SPE-133629-61	speed	medium	\N	\N		0	96.2	60			{"bbox": [161.93331909179688, 128.6246337890625, 270.3782653808594, 223.21902465820312], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.006657", "confidence": 0.9047549366950989, "detection_id": "90-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.019469+00	2025-11-05 18:36:29.073271+00	2025-11-05 18:36:29.073276+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1b3bd5f4-cbd9-4254-83a0-bd073b9bf93a	INF-RED-133629-54	red_light	medium	\N	\N		0	\N	\N			{"bbox": [204.7833251953125, 107.66445922851562, 221.50588989257812, 121.13951110839844], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.773228", "confidence": 0.5584012866020203, "detection_id": "88-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.78204+00	2025-11-05 18:36:29.071368+00	2025-11-05 18:36:29.071373+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a688b361-128f-40ac-b4de-7c95df0370d8	INF-RED-133629-31	red_light	medium	\N	\N		0	\N	\N			{"bbox": [280.2478942871094, 106.51931762695312, 291.72393798828125, 118.43046569824219], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.564055", "confidence": 0.3765539228916168, "detection_id": "86-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.571704+00	2025-11-05 18:36:29.119637+00	2025-11-05 18:36:29.119646+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7e1f50a0-609d-4900-b27e-37fabeec594b	INF-RED-133629-30	red_light	medium	\N	\N		0	\N	\N			{"bbox": [368.5718078613281, 116.36186218261719, 456.87396240234375, 152.8554229736328], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.007474", "confidence": 0.8907850384712219, "detection_id": "90-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.019643+00	2025-11-05 18:36:29.121705+00	2025-11-05 18:36:29.121711+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2e0f3380-58a0-4b04-ae14-326d847dddcc	INF-SPE-133629-11	speed	medium	\N	\N		0	94.4	60			{"bbox": [285.0259094238281, 106.21849822998047, 308.9129333496094, 120.31617736816406], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.773829", "confidence": 0.5547183752059937, "detection_id": "88-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.782258+00	2025-11-05 18:36:29.12253+00	2025-11-05 18:36:29.122537+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ecf3e4ea-6118-44bf-bbb9-6f0b5998dcf5	INF-RED-133629-91	red_light	medium	\N	\N		0	\N	\N			{"bbox": [359.8581848144531, 108.18443298339844, 379.6871337890625, 123.38358306884766], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.564726", "confidence": 0.2580462098121643, "detection_id": "86-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.57184+00	2025-11-05 18:36:29.181572+00	2025-11-05 18:36:29.181579+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e4bec731-0bd5-4616-8e18-fd00ebd5795d	INF-RED-133629-94	red_light	medium	\N	\N		0	\N	\N			{"bbox": [340.0478210449219, 97.13236999511719, 430.5764465332031, 139.90097045898438], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.008268", "confidence": 0.8361215591430664, "detection_id": "90-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.019764+00	2025-11-05 18:36:29.182332+00	2025-11-05 18:36:29.182339+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
019aae4e-ba94-4edc-87fd-0b22d8f1b476	INF-RED-133629-24	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.02057504653930664, 112.0093002319336, 21.224285125732422, 127.85181427001953], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.774564", "confidence": 0.45171862840652466, "detection_id": "88-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.782449+00	2025-11-05 18:36:29.184811+00	2025-11-05 18:36:29.184816+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8e929e18-f80b-462f-a2bf-503f53b8b11a	INF-SPE-133629-51	speed	medium	\N	\N		0	85.7	60			{"bbox": [452.1856384277344, 107.33546447753906, 479.7464904785156, 130.16116333007812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.008798", "confidence": 0.7520036101341248, "detection_id": "90-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.019875+00	2025-11-05 18:36:29.241908+00	2025-11-05 18:36:29.241914+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
74858dc9-e0ea-4673-baef-71257bc69c72	INF-RED-133629-44	red_light	medium	\N	\N		0	\N	\N			{"bbox": [183.12313842773438, 105.83621978759766, 205.82647705078125, 120.87531280517578], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.775244", "confidence": 0.4453623294830322, "detection_id": "88-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.782645+00	2025-11-05 18:36:29.242604+00	2025-11-05 18:36:29.24261+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d0bb134c-bf9e-4d0c-a985-f09cddfdecaf	INF-RED-133629-72	red_light	medium	\N	\N		0	\N	\N			{"bbox": [308.35980224609375, 107.9608383178711, 321.0450744628906, 118.63899993896484], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.565330", "confidence": 0.23196280002593994, "detection_id": "86-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.571957+00	2025-11-05 18:36:29.245671+00	2025-11-05 18:36:29.245678+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
48412738-9e4d-4f0c-b9ae-aa0b0f3955cf	INF-SPE-133629-36	speed	medium	\N	\N		0	87.9	60			{"bbox": [208.19541931152344, 106.36180877685547, 222.58938598632812, 115.74969482421875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:28.775746", "confidence": 0.378781795501709, "detection_id": "88-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:28.78284+00	2025-11-05 18:36:29.299345+00	2025-11-05 18:36:29.299351+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7c5f34de-6f16-43f6-a11d-76bc8547dc59	INF-RED-133629-17	red_light	medium	\N	\N		0	\N	\N			{"bbox": [179.84181213378906, 104.14520263671875, 196.65744018554688, 118.99288177490234], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.009481", "confidence": 0.6770937442779541, "detection_id": "90-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.019988+00	2025-11-05 18:36:29.300059+00	2025-11-05 18:36:29.300065+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
cb1cffc5-a4b8-45c7-994a-617a48b08eef	INF-RED-133629-33	red_light	medium	\N	\N		0	\N	\N			{"bbox": [162.43182373046875, 126.2300033569336, 269.1428527832031, 216.048583984375], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.242362", "confidence": 0.8724983334541321, "detection_id": "92-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.253881+00	2025-11-05 18:36:29.302099+00	2025-11-05 18:36:29.302106+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2e1ff839-1fcf-41f2-8ced-ba894cbcc744	INF-SPE-133629-53	speed	medium	\N	\N		0	77.5	60			{"bbox": [357.7357482910156, 115.52982330322266, 455.5429992675781, 158.23248291015625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.243155", "confidence": 0.8531304597854614, "detection_id": "92-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.254118+00	2025-11-05 18:36:29.360647+00	2025-11-05 18:36:29.360653+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
44fc4ab5-55df-44d5-a550-2c1fcf0af438	INF-RED-133629-77	red_light	medium	\N	\N		0	\N	\N			{"bbox": [292.2538757324219, 104.65734100341797, 310.758544921875, 119.1404800415039], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.010311", "confidence": 0.6656513214111328, "detection_id": "90-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.020129+00	2025-11-05 18:36:29.368254+00	2025-11-05 18:36:29.368264+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f0c7ed2d-e146-45e7-9c95-e719ec2a4e89	INF-SPE-133629-22	speed	medium	\N	\N		0	74.1	60			{"bbox": [201.77261352539062, 105.16902923583984, 220.91665649414062, 119.51868438720703], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.011167", "confidence": 0.6412661075592041, "detection_id": "90-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.020308+00	2025-11-05 18:36:29.438554+00	2025-11-05 18:36:29.438561+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
12154f73-a895-4f5c-93c6-571b00fb5d3a	INF-RED-133629-55	red_light	medium	\N	\N		0	\N	\N			{"bbox": [328.4015808105469, 93.51557922363281, 426.3213806152344, 141.1300048828125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.244007", "confidence": 0.8027870059013367, "detection_id": "92-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.254318+00	2025-11-05 18:36:29.442017+00	2025-11-05 18:36:29.442023+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
464510aa-1e52-4459-9b46-b9af6e277081	INF-RED-133629-10	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.02680206298828125, 111.01366424560547, 27.498762130737305, 127.78365325927734], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.012241", "confidence": 0.40813860297203064, "detection_id": "90-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.020553+00	2025-11-05 18:36:29.51531+00	2025-11-05 18:36:29.515316+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
972e4775-9006-45a1-b65a-64338b45e5f6	INF-RED-133629-97	red_light	medium	\N	\N		0	\N	\N			{"bbox": [291.2046203613281, 102.17882537841797, 313.1617126464844, 116.99883270263672], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.244959", "confidence": 0.7285675406455994, "detection_id": "92-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.254496+00	2025-11-05 18:36:29.516134+00	2025-11-05 18:36:29.516138+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7505446d-d38b-4f11-b603-ae7e65d42f7f	INF-RED-133629-21	red_light	medium	\N	\N		0	\N	\N			{"bbox": [345.49981689453125, 114.18882751464844, 459.2843933105469, 161.5322265625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.466825", "confidence": 0.8700252771377563, "detection_id": "94-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.489721+00	2025-11-05 18:36:29.518149+00	2025-11-05 18:36:29.518155+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9f6d379d-c307-4007-8fad-694763412d84	INF-SPE-133629-27	speed	medium	\N	\N		0	85.3	60			{"bbox": [175.16322326660156, 102.05175018310547, 193.85784912109375, 117.5833969116211], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.245658", "confidence": 0.6840958595275879, "detection_id": "92-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.254681+00	2025-11-05 18:36:29.565598+00	2025-11-05 18:36:29.565605+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
50aa0f06-6408-4d01-b9f5-ba1834c1b945	INF-RED-133629-63	red_light	medium	\N	\N		0	\N	\N			{"bbox": [282.0183410644531, 103.52792358398438, 295.3777160644531, 116.12091064453125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.013094", "confidence": 0.3189835548400879, "detection_id": "90-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.020743+00	2025-11-05 18:36:29.569418+00	2025-11-05 18:36:29.569424+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
076422d3-1a9e-4193-8a4e-0abda12f6879	INF-RED-133629-95	red_light	medium	\N	\N		0	\N	\N			{"bbox": [196.12811279296875, 104.53074645996094, 216.77764892578125, 118.11264038085938], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.246395", "confidence": 0.5608886480331421, "detection_id": "92-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.25483+00	2025-11-05 18:36:29.635575+00	2025-11-05 18:36:29.635587+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4ca84ce7-7823-46c6-ae0a-73d253e3e3df	INF-RED-133629-82	red_light	medium	\N	\N		0	\N	\N			{"bbox": [46.7841682434082, 110.21076965332031, 63.87813949584961, 122.49197387695312], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.013854", "confidence": 0.2140129655599594, "detection_id": "90-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.020854+00	2025-11-05 18:36:29.63794+00	2025-11-05 18:36:29.637947+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
665e2f28-bcc2-4d76-8bd9-1674e53dc824	INF-SPE-133629-99	speed	medium	\N	\N		0	83.4	60			{"bbox": [315.2057189941406, 88.705078125, 427.83087158203125, 141.15078735351562], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.468754", "confidence": 0.7483811378479004, "detection_id": "94-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.489946+00	2025-11-05 18:36:29.690174+00	2025-11-05 18:36:29.690186+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
924a3869-3601-444c-9d61-ca35015761e3	INF-SPE-133629-86	speed	medium	\N	\N		0	98.6	60			{"bbox": [471.6907653808594, 110.48991394042969, 479.84234619140625, 130.8745880126953], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.014648", "confidence": 0.20886392891407013, "detection_id": "90-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.020971+00	2025-11-05 18:36:29.694859+00	2025-11-05 18:36:29.694866+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1cd83d60-c513-4b50-bfbd-0b7ee002f200	INF-RED-133629-67	red_light	medium	\N	\N		0	\N	\N			{"bbox": [338.5757141113281, 114.82054138183594, 468.0428466796875, 170.31039428710938], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.701437", "confidence": 0.8823522925376892, "detection_id": "96-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.71298+00	2025-11-05 18:36:29.977168+00	2025-11-05 18:36:29.977176+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5aba0eee-759a-44e6-a753-c1eba1e3d65e	INF-RED-133629-87	red_light	medium	\N	\N		0	\N	\N			{"bbox": [333.75311279296875, 115.99715423583984, 480.0, 188.5454864501953], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.912701", "confidence": 0.9174093008041382, "detection_id": "98-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.926581+00	2025-11-05 18:36:29.989015+00	2025-11-05 18:36:29.989023+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
bea3d0ad-838d-4f09-86f1-9b855c008a90	INF-RED-133629-90	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.71710205078125, 97.61551666259766, 282.7442321777344, 107.7854232788086], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.248186", "confidence": 0.3609990179538727, "detection_id": "92-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.255397+00	2025-11-05 18:36:29.991399+00	2025-11-05 18:36:29.991404+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
79f8e288-8cb3-4dcf-8c17-9224ddae8c44	INF-RED-133629-71	red_light	medium	\N	\N		0	\N	\N			{"bbox": [192.44915771484375, 101.01848602294922, 213.728759765625, 115.74117279052734], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.470724", "confidence": 0.5875686407089233, "detection_id": "94-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.490261+00	2025-11-05 18:36:29.995681+00	2025-11-05 18:36:29.995689+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d050468a-a6b0-4f81-aad5-7230033e67ef	INF-RED-133630-92	red_light	medium	\N	\N		0	\N	\N			{"bbox": [188.7942352294922, 96.66968536376953, 210.19898986816406, 114.38518524169922], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.702554", "confidence": 0.7227768898010254, "detection_id": "96-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.713166+00	2025-11-05 18:36:30.006646+00	2025-11-05 18:36:30.006652+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ba049f17-094f-454a-9583-458c87d8acab	INF-SPE-133630-13	speed	medium	\N	\N		0	95.4	60			{"bbox": [204.75563049316406, 101.1031723022461, 220.9102020263672, 111.06365203857422], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.248840", "confidence": 0.2316332459449768, "detection_id": "92-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.255558+00	2025-11-05 18:36:30.053514+00	2025-11-05 18:36:30.053526+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
db4dee78-9681-445c-a83c-21c1da87fc50	INF-SPE-133630-40	speed	medium	\N	\N		0	76.6	60			{"bbox": [292.2109680175781, 97.84278106689453, 314.8715515136719, 114.44154357910156], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.471505", "confidence": 0.42902901768684387, "detection_id": "94-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.490411+00	2025-11-05 18:36:30.054534+00	2025-11-05 18:36:30.054543+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
19102833-4f8d-4f24-b613-5db00f5a240e	INF-SPE-133630-53	speed	medium	\N	\N		0	99.4	60			{"bbox": [169.7523651123047, 115.5307846069336, 278.60406494140625, 198.12091064453125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.913538", "confidence": 0.8931511044502258, "detection_id": "98-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.926818+00	2025-11-05 18:36:30.055139+00	2025-11-05 18:36:30.055145+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6f05cf72-e601-4b9c-9544-b56b8afe4c6a	INF-SPE-133630-43	speed	medium	\N	\N		0	70.8	60			{"bbox": [163.8317108154297, 96.41349792480469, 184.6522216796875, 112.969482421875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.703260", "confidence": 0.6693605780601501, "detection_id": "96-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.713337+00	2025-11-05 18:36:30.059125+00	2025-11-05 18:36:30.059134+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f6e64945-a678-4182-af44-9c603edfe96d	INF-RED-133630-10	red_light	medium	\N	\N		0	\N	\N			{"bbox": [269.5884704589844, 94.12085723876953, 282.8607177734375, 105.01780700683594], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.472363", "confidence": 0.42490535974502563, "detection_id": "94-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.490518+00	2025-11-05 18:36:30.128994+00	2025-11-05 18:36:30.129005+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
91e97c55-a86d-4308-9c60-d2751b6a8973	INF-RED-133630-28	red_light	medium	\N	\N		0	\N	\N			{"bbox": [293.5978088378906, 96.39608001708984, 319.1781921386719, 113.58263397216797], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.703981", "confidence": 0.651976466178894, "detection_id": "96-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.713454+00	2025-11-05 18:36:30.131265+00	2025-11-05 18:36:30.13127+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
da71ccd3-43e8-404e-b6d3-ee586e4171c0	INF-RED-133630-46	red_light	medium	\N	\N		0	\N	\N			{"bbox": [181.38937377929688, 95.24845123291016, 205.83326721191406, 113.60012817382812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.914502", "confidence": 0.7100344300270081, "detection_id": "98-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.927154+00	2025-11-05 18:36:30.130329+00	2025-11-05 18:36:30.130337+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2433bcae-8123-44f9-b9db-50b9b2595bb5	INF-RED-133630-43	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.6110534667969, 91.89334106445312, 283.2578430175781, 103.45734405517578], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.704685", "confidence": 0.6309345960617065, "detection_id": "96-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.713604+00	2025-11-05 18:36:30.213635+00	2025-11-05 18:36:30.213642+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
eb917da8-6d37-45d5-a92f-6e16478190ec	INF-RED-133630-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [156.5586700439453, 93.3398208618164, 181.921142578125, 112.33280181884766], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.915337", "confidence": 0.6766679883003235, "detection_id": "98-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.927409+00	2025-11-05 18:36:30.214307+00	2025-11-05 18:36:30.214313+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a26ca784-729f-47ae-8760-087e14224746	INF-RED-133630-75	red_light	medium	\N	\N		0	\N	\N			{"bbox": [281.84124755859375, 96.09489440917969, 297.3473815917969, 110.80087280273438], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.473251", "confidence": 0.38672253489494324, "detection_id": "94-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.49065+00	2025-11-05 18:36:30.215386+00	2025-11-05 18:36:30.21539+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a45fac8c-e7c8-41c6-91cc-ee729d4bace0	INF-RED-133630-30	red_light	medium	\N	\N		0	\N	\N			{"bbox": [333.3771057128906, 117.75178527832031, 479.6137390136719, 201.04531860351562], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.157572", "confidence": 0.9349842071533203, "detection_id": "100-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.184576+00	2025-11-05 18:36:30.216464+00	2025-11-05 18:36:30.216468+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ee616a7f-e448-40f5-bbbe-4968ee90ec98	INF-SPE-133630-93	speed	medium	\N	\N		0	77.3	60			{"bbox": [305.2900085449219, 83.82318878173828, 428.5458068847656, 144.20376586914062], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.705277", "confidence": 0.6307644248008728, "detection_id": "96-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.71389+00	2025-11-05 18:36:30.280549+00	2025-11-05 18:36:30.280558+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d7f9328d-16b4-47e8-aeee-f1eb75d164b7	INF-RED-133630-70	red_light	medium	\N	\N		0	\N	\N			{"bbox": [203.13255310058594, 97.96742248535156, 217.9620361328125, 107.79707336425781], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.474431", "confidence": 0.35762062668800354, "detection_id": "94-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.490817+00	2025-11-05 18:36:30.279816+00	2025-11-05 18:36:30.279822+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
afefb2f0-c4cc-4e64-9647-8fcef5cdec01	INF-RED-133630-81	red_light	medium	\N	\N		0	\N	\N			{"bbox": [175.48960876464844, 115.06983947753906, 281.606689453125, 195.07452392578125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.158805", "confidence": 0.9067636132240295, "detection_id": "100-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.184717+00	2025-11-05 18:36:30.281791+00	2025-11-05 18:36:30.281799+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
651bb4e1-69d8-4da2-a8c1-41d3806bce5c	INF-SPE-133630-35	speed	medium	\N	\N		0	97.9	60			{"bbox": [282.47930908203125, 91.28004455566406, 303.07012939453125, 107.58416748046875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.916039", "confidence": 0.6380411982536316, "detection_id": "98-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.927592+00	2025-11-05 18:36:30.283028+00	2025-11-05 18:36:30.283037+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
27387941-9383-469d-a02c-6ac3ebbfc5c9	INF-RED-133630-65	red_light	medium	\N	\N		0	\N	\N			{"bbox": [282.23553466796875, 93.16191864013672, 296.4998474121094, 108.35928344726562], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.706051", "confidence": 0.5723450779914856, "detection_id": "96-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.714143+00	2025-11-05 18:36:30.365291+00	2025-11-05 18:36:30.365298+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
56cd2f45-6178-4b42-bdf5-8ec4c36b1b93	INF-SPE-133630-22	speed	medium	\N	\N		0	79.1	60			{"bbox": [149.5070037841797, 93.04389953613281, 174.59194946289062, 112.08943176269531], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.160026", "confidence": 0.797041118144989, "detection_id": "100-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.184848+00	2025-11-05 18:36:30.366452+00	2025-11-05 18:36:30.366459+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0328dd9d-32cc-48f0-bce2-9b23f99f6f3e	INF-RED-133630-13	red_light	medium	\N	\N		0	\N	\N			{"bbox": [291.3116760253906, 81.22616577148438, 433.16357421875, 149.826416015625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.916872", "confidence": 0.5790568590164185, "detection_id": "98-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.927797+00	2025-11-05 18:36:30.367474+00	2025-11-05 18:36:30.367483+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1db38086-eadd-4ec1-a627-36ababc738dd	INF-RED-133630-60	red_light	medium	\N	\N		0	\N	\N			{"bbox": [253.44357299804688, 92.28829193115234, 265.9977722167969, 100.4762191772461], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.475627", "confidence": 0.2773544490337372, "detection_id": "94-13", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.491017+00	2025-11-05 18:36:30.36841+00	2025-11-05 18:36:30.368418+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fe6d37be-af1f-4a85-9e87-cbb34aea68c7	INF-RED-133630-20	red_light	medium	\N	\N		0	\N	\N			{"bbox": [201.92062377929688, 94.92176055908203, 215.4190673828125, 104.49968719482422], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.706751", "confidence": 0.4018130600452423, "detection_id": "96-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.714367+00	2025-11-05 18:36:30.466048+00	2025-11-05 18:36:30.466057+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fa168c62-fbd4-4545-a2da-53f71de40705	INF-SPE-133630-98	speed	medium	\N	\N		0	99.4	60			{"bbox": [335.12457275390625, 120.53443908691406, 479.7864990234375, 209.31765747070312], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.411868", "confidence": 0.9232573509216309, "detection_id": "102-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.437059+00	2025-11-05 18:36:30.500507+00	2025-11-05 18:36:30.500513+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d0d31195-4949-4bb9-aef5-b59a2ea40432	INF-RED-133630-72	red_light	medium	\N	\N		0	\N	\N			{"bbox": [280.0269775390625, 79.22737884521484, 438.2089538574219, 160.1454315185547], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.161193", "confidence": 0.7910752892494202, "detection_id": "100-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.185071+00	2025-11-05 18:36:30.499821+00	2025-11-05 18:36:30.499828+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6efa4c4a-4b99-4bae-9e42-455513f90a23	INF-SPE-133630-30	speed	medium	\N	\N		0	72.7	60			{"bbox": [270.82293701171875, 90.22456359863281, 283.71942138671875, 101.68083190917969], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.917768", "confidence": 0.4884660243988037, "detection_id": "98-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.927938+00	2025-11-05 18:36:30.501747+00	2025-11-05 18:36:30.501753+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8830554a-0f40-4ff8-9b5b-1dbdb11a5f72	INF-RED-133630-63	red_light	medium	\N	\N		0	\N	\N			{"bbox": [175.84681701660156, 94.66145324707031, 191.67184448242188, 109.47908020019531], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.707517", "confidence": 0.28895002603530884, "detection_id": "96-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.714536+00	2025-11-05 18:36:30.503364+00	2025-11-05 18:36:30.50337+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ccf8b9c8-0a35-4da0-b139-4500c6ca3b2d	INF-SPE-133630-38	speed	medium	\N	\N		0	82.5	60			{"bbox": [434.7393798828125, 101.77940368652344, 480.0, 123.77208709716797], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.476544", "confidence": 0.20480342209339142, "detection_id": "94-17", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.491218+00	2025-11-05 18:36:30.504867+00	2025-11-05 18:36:30.504873+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ba3b856c-5490-4aec-9ca8-d872e9241148	INF-SPE-133630-94	speed	medium	\N	\N		0	98.6	60			{"bbox": [252.73745727539062, 88.0594253540039, 268.9908142089844, 96.0186996459961], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.918701", "confidence": 0.32364997267723083, "detection_id": "98-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.928152+00	2025-11-05 18:36:30.58601+00	2025-11-05 18:36:30.586023+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8840fca7-7f83-47d9-a599-5925ac5f149b	INF-RED-133630-50	red_light	medium	\N	\N		0	\N	\N			{"bbox": [177.77670288085938, 93.72759246826172, 202.6789093017578, 114.04804229736328], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.162059", "confidence": 0.6860853433609009, "detection_id": "100-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.185281+00	2025-11-05 18:36:30.58059+00	2025-11-05 18:36:30.5806+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a80d6f51-043b-44fa-864d-e7140a4178b7	INF-SPE-133630-48	speed	medium	\N	\N		0	83.8	60			{"bbox": [283.9880676269531, 90.3230209350586, 305.1329650878906, 107.18131256103516], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.162736", "confidence": 0.6294808387756348, "detection_id": "100-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.185482+00	2025-11-05 18:36:30.684414+00	2025-11-05 18:36:30.684421+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
96b60fd1-0ce8-4a0c-8ccb-42a928b0015f	INF-RED-133630-69	red_light	medium	\N	\N		0	\N	\N			{"bbox": [333.5030212402344, 121.41840362548828, 479.8894348144531, 209.24461364746094], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.688472", "confidence": 0.9275643229484558, "detection_id": "104-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.705371+00	2025-11-05 18:36:30.758612+00	2025-11-05 18:36:30.758618+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6e4da672-2c2b-4037-913e-782feda2321a	INF-RED-133630-41	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.4858703613281, 88.27965545654297, 285.0480651855469, 101.4891586303711], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.163676", "confidence": 0.48564261198043823, "detection_id": "100-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.18565+00	2025-11-05 18:36:30.761459+00	2025-11-05 18:36:30.761463+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
925b1b8d-d2ee-4791-a82c-7d8f2fd2ca28	INF-RED-133630-62	red_light	medium	\N	\N		0	\N	\N			{"bbox": [173.26516723632812, 91.99512481689453, 197.99740600585938, 113.75306701660156], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.413775", "confidence": 0.7410277128219604, "detection_id": "102-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.437485+00	2025-11-05 18:36:30.762041+00	2025-11-05 18:36:30.762046+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4bf0254f-eb50-485c-b832-987901114fc4	INF-RED-133630-19	red_light	medium	\N	\N		0	\N	\N			{"bbox": [468.1517028808594, 94.99081420898438, 479.8695373535156, 127.40066528320312], "source": "webcam_local", "timestamp": "2025-11-05T18:36:29.920636", "confidence": 0.2154289186000824, "detection_id": "98-15", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:29.928488+00	2025-11-05 18:36:30.807479+00	2025-11-05 18:36:30.807489+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5cd0ca5f-dd04-4090-829a-2cecaa5757f0	INF-RED-133630-64	red_light	medium	\N	\N		0	\N	\N			{"bbox": [196.99305725097656, 92.8115234375, 208.45289611816406, 104.0845718383789], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.164531", "confidence": 0.365693598985672, "detection_id": "100-13", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.185797+00	2025-11-05 18:36:30.808079+00	2025-11-05 18:36:30.808083+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d5dc8e42-7f8d-46fd-a2bb-336cbd7df494	INF-RED-133630-85	red_light	medium	\N	\N		0	\N	\N			{"bbox": [142.85623168945312, 91.8281021118164, 171.89410400390625, 111.88744354248047], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.414758", "confidence": 0.640220582485199, "detection_id": "102-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.437618+00	2025-11-05 18:36:30.809019+00	2025-11-05 18:36:30.809023+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3b73908d-106c-4750-b198-db5fda9ff771	INF-SPE-133630-61	speed	medium	\N	\N		0	71.9	60			{"bbox": [179.02923583984375, 111.8459701538086, 301.2469177246094, 191.1276092529297], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.689411", "confidence": 0.9060496091842651, "detection_id": "104-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.705544+00	2025-11-05 18:36:30.810015+00	2025-11-05 18:36:30.810019+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fec33168-3aba-4fe7-b802-f4cfe041b8c8	INF-RED-133630-54	red_light	medium	\N	\N		0	\N	\N			{"bbox": [249.94725036621094, 86.7367172241211, 264.9523620605469, 94.77250671386719], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.165470", "confidence": 0.26781386137008667, "detection_id": "100-18", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.186047+00	2025-11-05 18:36:30.865971+00	2025-11-05 18:36:30.865979+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b27d78e4-5639-4ffb-ae91-4b81bb9a5c57	INF-RED-133630-58	red_light	medium	\N	\N		0	\N	\N			{"bbox": [273.78857421875, 75.52381896972656, 446.4842224121094, 169.5701446533203], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.415599", "confidence": 0.6226376891136169, "detection_id": "102-5", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.437769+00	2025-11-05 18:36:30.869544+00	2025-11-05 18:36:30.869555+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fe32aa94-ce87-469d-9363-2c8d8e9889b0	INF-RED-133630-52	red_light	medium	\N	\N		0	\N	\N			{"bbox": [285.0674133300781, 87.62606811523438, 306.56536865234375, 106.26002502441406], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.416521", "confidence": 0.5659383535385132, "detection_id": "102-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.438008+00	2025-11-05 18:36:30.936434+00	2025-11-05 18:36:30.936443+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
76ff66e0-b166-4307-9c6e-ea774020f10e	INF-RED-133630-89	red_light	medium	\N	\N		0	\N	\N			{"bbox": [138.34608459472656, 90.11819458007812, 165.2646484375, 111.16941833496094], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.693026", "confidence": 0.6930221319198608, "detection_id": "104-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.705822+00	2025-11-05 18:36:31.003621+00	2025-11-05 18:36:31.003628+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
011cdf45-64d2-44c1-898b-9fa78a8e7215	INF-RED-133630-22	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.7748107910156, 85.22731018066406, 286.05572509765625, 100.121337890625], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.417361", "confidence": 0.5309121012687683, "detection_id": "102-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.438168+00	2025-11-05 18:36:31.004821+00	2025-11-05 18:36:31.004827+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
717302df-bf0e-42b5-b4aa-7f0b6b3aaaff	INF-RED-133631-96	red_light	medium	\N	\N		0	\N	\N			{"bbox": [129.0469207763672, 108.78382873535156, 306.1155700683594, 187.2458953857422], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.966769", "confidence": 0.9346184134483337, "detection_id": "106-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.977581+00	2025-11-05 18:36:31.005876+00	2025-11-05 18:36:31.005881+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1eebf089-c999-4609-87fc-a2934b1f32e0	INF-SPE-133631-54	speed	medium	\N	\N		0	99.3	60			{"bbox": [270.5428466796875, 83.20603942871094, 288.7018737792969, 98.3962631225586], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.694291", "confidence": 0.6631226539611816, "detection_id": "104-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.706017+00	2025-11-05 18:36:31.054745+00	2025-11-05 18:36:31.05475+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
95a1f3fb-83d8-47df-a0f2-65ca7cbd8889	INF-SPE-133631-81	speed	medium	\N	\N		0	84	60			{"bbox": [274.5611572265625, 75.97834014892578, 445.8274230957031, 169.28150939941406], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.418150", "confidence": 0.49942588806152344, "detection_id": "102-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.438349+00	2025-11-05 18:36:31.055845+00	2025-11-05 18:36:31.055849+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5fc2033a-494b-49d1-b207-c73a9607c458	INF-RED-133631-64	red_light	medium	\N	\N		0	\N	\N			{"bbox": [331.3479919433594, 118.01765441894531, 479.7396240234375, 212.4488067626953], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.967663", "confidence": 0.9229623079299927, "detection_id": "106-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.977688+00	2025-11-05 18:36:31.057059+00	2025-11-05 18:36:31.057065+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1702ab6a-bbd7-4ece-839b-46b55a97c26d	INF-RED-133631-49	red_light	medium	\N	\N		0	\N	\N			{"bbox": [285.3183288574219, 85.19384765625, 309.8544616699219, 105.7199935913086], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.695075", "confidence": 0.6001623868942261, "detection_id": "104-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.706256+00	2025-11-05 18:36:31.11549+00	2025-11-05 18:36:31.115499+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d6ce5003-1d4b-48e4-b05c-53391f30b036	INF-RED-133631-19	red_light	medium	\N	\N		0	\N	\N			{"bbox": [191.57412719726562, 91.40201568603516, 205.7793731689453, 102.42668151855469], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.419221", "confidence": 0.3742856979370117, "detection_id": "102-14", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.438549+00	2025-11-05 18:36:31.117915+00	2025-11-05 18:36:31.117921+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
631e5353-ee86-46ef-9ec3-316649025e22	INF-SPE-133631-49	speed	medium	\N	\N		0	97.1	60			{"bbox": [167.411865234375, 89.5015640258789, 194.0390167236328, 112.44847869873047], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.968384", "confidence": 0.7399737238883972, "detection_id": "106-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.977815+00	2025-11-05 18:36:31.120195+00	2025-11-05 18:36:31.1202+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
426b2a0e-e537-420d-a8e4-b9832925f104	INF-RED-133631-60	red_light	medium	\N	\N		0	\N	\N			{"bbox": [277.025390625, 73.0503158569336, 459.80731201171875, 173.65467834472656], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.695962", "confidence": 0.5244113206863403, "detection_id": "104-8", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.706365+00	2025-11-05 18:36:31.189626+00	2025-11-05 18:36:31.189637+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5ca03854-4425-4438-81a1-96e5b8d87d0d	INF-RED-133631-43	red_light	medium	\N	\N		0	\N	\N			{"bbox": [164.2813262939453, 90.32801818847656, 177.490966796875, 104.9448013305664], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.420334", "confidence": 0.2031078189611435, "detection_id": "102-20", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.438748+00	2025-11-05 18:36:31.191528+00	2025-11-05 18:36:31.191539+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
12a4a529-e387-4941-8e41-202bd2eb0e6a	INF-RED-133631-42	red_light	medium	\N	\N		0	\N	\N			{"bbox": [189.09823608398438, 87.48314666748047, 203.93399047851562, 101.36004638671875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.696646", "confidence": 0.5197200775146484, "detection_id": "104-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.706463+00	2025-11-05 18:36:31.269208+00	2025-11-05 18:36:31.269215+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6db8a699-8c41-4054-9a5c-be7d13b3d643	INF-RED-133631-51	red_light	medium	\N	\N		0	\N	\N			{"bbox": [135.61203002929688, 87.76392364501953, 164.6191864013672, 110.09830474853516], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.969901", "confidence": 0.6871312260627747, "detection_id": "106-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.978101+00	2025-11-05 18:36:31.279228+00	2025-11-05 18:36:31.279235+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
045d8042-dc56-4773-b80b-006cf86dc43e	INF-RED-133631-92	red_light	medium	\N	\N		0	\N	\N			{"bbox": [277.4232177734375, 73.78884887695312, 461.68829345703125, 173.80178833007812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.697529", "confidence": 0.4672263562679291, "detection_id": "104-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.706552+00	2025-11-05 18:36:31.316243+00	2025-11-05 18:36:31.316249+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4fdd8779-aec2-4934-b070-699d8e7b6a9b	INF-RED-133631-13	red_light	medium	\N	\N		0	\N	\N			{"bbox": [284.8924560546875, 84.08887481689453, 312.2583923339844, 103.41277313232422], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.970754", "confidence": 0.6682074069976807, "detection_id": "106-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.978226+00	2025-11-05 18:36:31.323404+00	2025-11-05 18:36:31.323412+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1139e2b4-ebd4-4b63-937b-b9a176995308	INF-RED-133631-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [202.128662109375, 87.17827606201172, 210.5812225341797, 94.3282699584961], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.698788", "confidence": 0.292202353477478, "detection_id": "104-18", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.706733+00	2025-11-05 18:36:31.383504+00	2025-11-05 18:36:31.38351+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3c2c148e-4fbb-4d2c-b2e2-e03500bd8ca1	INF-RED-133631-76	red_light	medium	\N	\N		0	\N	\N			{"bbox": [186.0076446533203, 84.267822265625, 203.0111846923828, 99.27748107910156], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.971569", "confidence": 0.4819452464580536, "detection_id": "106-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.978324+00	2025-11-05 18:36:31.384752+00	2025-11-05 18:36:31.384759+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4d6290c2-fe62-47c4-b921-81f9251ae040	INF-RED-133631-86	red_light	medium	\N	\N		0	\N	\N			{"bbox": [328.44378662109375, 118.56655883789062, 480.0, 205.49098205566406], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.226331", "confidence": 0.8632723093032837, "detection_id": "108-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.240967+00	2025-11-05 18:36:31.385728+00	2025-11-05 18:36:31.385734+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3dc9fe47-f55b-4432-a740-529784b32612	INF-RED-133631-18	red_light	medium	\N	\N		0	\N	\N			{"bbox": [160.82086181640625, 87.60359191894531, 180.43031311035156, 101.12767028808594], "source": "webcam_local", "timestamp": "2025-11-05T18:36:30.699748", "confidence": 0.20840494334697723, "detection_id": "104-20", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:30.706961+00	2025-11-05 18:36:31.4514+00	2025-11-05 18:36:31.451413+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6ceba90b-6146-45f8-bfec-da221f314851	INF-RED-133631-50	red_light	medium	\N	\N		0	\N	\N			{"bbox": [168.0442352294922, 88.24491119384766, 194.63865661621094, 109.84192657470703], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.227388", "confidence": 0.6122574210166931, "detection_id": "108-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.241219+00	2025-11-05 18:36:31.453244+00	2025-11-05 18:36:31.453255+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c0664073-4b15-4de2-ae68-51e27fbb0210	INF-SPE-133631-24	speed	medium	\N	\N		0	97.3	60			{"bbox": [276.63446044921875, 71.35186004638672, 470.019287109375, 162.9356231689453], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.228265", "confidence": 0.5717654228210449, "detection_id": "108-6", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.24147+00	2025-11-05 18:36:31.524007+00	2025-11-05 18:36:31.524019+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
abb9979c-a3d1-4280-93ca-564b36ababf8	INF-RED-133631-48	red_light	medium	\N	\N		0	\N	\N			{"bbox": [51.135475158691406, 108.27777862548828, 254.20904541015625, 183.1281280517578], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.548422", "confidence": 0.9200767874717712, "detection_id": "110-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.564839+00	2025-11-05 18:36:31.590935+00	2025-11-05 18:36:31.59094+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0f8eef3d-8c01-4e36-b109-c8dbd05780b4	INF-SPE-133631-51	speed	medium	\N	\N		0	90.9	60			{"bbox": [324.7041320800781, 119.07664489746094, 479.9744567871094, 204.19464111328125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.549127", "confidence": 0.7001925706863403, "detection_id": "110-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.565042+00	2025-11-05 18:36:31.641693+00	2025-11-05 18:36:31.641699+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4cdb3bc2-e900-4397-85f9-f0a745b49e44	INF-SPE-133631-18	speed	medium	\N	\N		0	80.9	60			{"bbox": [285.574951171875, 83.4486312866211, 310.47967529296875, 102.4330062866211], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.229881", "confidence": 0.4600738286972046, "detection_id": "108-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.241828+00	2025-11-05 18:36:31.676697+00	2025-11-05 18:36:31.676703+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5beec695-4051-4a5d-9be6-3603082156f4	INF-SPE-133631-27	speed	medium	\N	\N		0	80	60			{"bbox": [168.6256866455078, 89.0830078125, 194.11669921875, 109.36653900146484], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.550114", "confidence": 0.6444932818412781, "detection_id": "110-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.565173+00	2025-11-05 18:36:31.677721+00	2025-11-05 18:36:31.677725+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a58a995b-9560-4608-8b08-9fa2c7c6908b	INF-RED-133631-34	red_light	medium	\N	\N		0	\N	\N			{"bbox": [135.1802215576172, 87.69514465332031, 163.70127868652344, 109.29733276367188], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.551250", "confidence": 0.5980492234230042, "detection_id": "110-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.565332+00	2025-11-05 18:36:31.743963+00	2025-11-05 18:36:31.743972+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
40ebe69c-9f61-4adf-9744-f6161cf2883e	INF-RED-133631-41	red_light	medium	\N	\N		0	\N	\N			{"bbox": [5.145744323730469, 108.02105712890625, 210.73109436035156, 184.13104248046875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.811636", "confidence": 0.9331640005111694, "detection_id": "112-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.830024+00	2025-11-05 18:36:31.873488+00	2025-11-05 18:36:31.873494+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
78507702-1818-4e21-9621-488fa97d0583	INF-SPE-133631-20	speed	medium	\N	\N		0	94.9	60			{"bbox": [270.4909973144531, 80.94884490966797, 286.38568115234375, 95.74097442626953], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.231431", "confidence": 0.37866273522377014, "detection_id": "108-15", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.242296+00	2025-11-05 18:36:31.874133+00	2025-11-05 18:36:31.874138+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a683d932-688b-41b6-a354-8377edb4067f	INF-RED-133631-39	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.2489929199219, 80.24776458740234, 286.2843017578125, 95.64837646484375], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.553514", "confidence": 0.5007425546646118, "detection_id": "110-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.565731+00	2025-11-05 18:36:31.890209+00	2025-11-05 18:36:31.890216+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c86e851e-6c08-44ab-8b96-e530cccc646e	INF-RED-133631-44	red_light	medium	\N	\N		0	\N	\N			{"bbox": [186.63368225097656, 83.43683624267578, 202.8954620361328, 98.34169006347656], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.232317", "confidence": 0.3731329143047333, "detection_id": "108-16", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.242475+00	2025-11-05 18:36:31.910536+00	2025-11-05 18:36:31.910542+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
16c15dde-b57f-4aa5-a201-78dc3162c122	INF-RED-133631-62	red_light	medium	\N	\N		0	\N	\N			{"bbox": [187.26922607421875, 84.31122589111328, 202.3413848876953, 99.229248046875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.555316", "confidence": 0.40799450874328613, "detection_id": "110-14", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.56594+00	2025-11-05 18:36:31.932828+00	2025-11-05 18:36:31.932835+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c56abea4-c5c0-4fe0-9347-1109900e05ac	INF-RED-133631-35	red_light	medium	\N	\N		0	\N	\N			{"bbox": [198.46783447265625, 82.51654815673828, 210.68829345703125, 92.1309585571289], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.233249", "confidence": 0.27849894762039185, "detection_id": "108-20", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.242699+00	2025-11-05 18:36:31.967616+00	2025-11-05 18:36:31.96763+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ff446b25-eecc-4fba-aa4c-c2f0b1f65ef8	INF-RED-133631-37	red_light	medium	\N	\N		0	\N	\N			{"bbox": [285.7760009765625, 83.01366424560547, 305.946044921875, 102.38876342773438], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.556581", "confidence": 0.3974195420742035, "detection_id": "110-15", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.566171+00	2025-11-05 18:36:31.985256+00	2025-11-05 18:36:31.985264+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b8d75ebb-1010-4a15-aeb4-65d498fca841	INF-SPE-133632-45	speed	medium	\N	\N		0	74.7	60			{"bbox": [135.99285888671875, 87.8316650390625, 164.7233428955078, 110.53104400634766], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.814055", "confidence": 0.6743847131729126, "detection_id": "112-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.83048+00	2025-11-05 18:36:32.043395+00	2025-11-05 18:36:32.043405+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
eeadcdf3-0c47-4230-b878-d4c00ae5abbd	INF-SPE-133632-74	speed	medium	\N	\N		0	73.8	60			{"bbox": [267.6004943847656, 70.27908325195312, 464.5938720703125, 157.9954071044922], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.557380", "confidence": 0.36604225635528564, "detection_id": "110-16", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.566377+00	2025-11-05 18:36:32.044816+00	2025-11-05 18:36:32.044825+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
49ae6a74-4948-4aa0-b34f-0d824a578585	INF-RED-133632-21	red_light	medium	\N	\N		0	\N	\N			{"bbox": [154.873046875, 85.00753784179688, 177.72854614257812, 108.86258697509766], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.234380", "confidence": 0.24076342582702637, "detection_id": "108-22", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.242949+00	2025-11-05 18:36:32.045758+00	2025-11-05 18:36:32.045767+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b0e9d791-7695-4c51-8252-cffb5245d95b	INF-RED-133632-19	red_light	medium	\N	\N		0	\N	\N			{"bbox": [198.3508758544922, 82.37901306152344, 210.8126220703125, 91.87410736083984], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.558294", "confidence": 0.3649703860282898, "detection_id": "110-17", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.566518+00	2025-11-05 18:36:32.114918+00	2025-11-05 18:36:32.114925+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1d8c7ddb-622c-461b-90e9-c0eb5b008a3a	INF-SPE-133632-82	speed	medium	\N	\N		0	99.9	60			{"bbox": [309.9671630859375, 113.69556427001953, 478.7347412109375, 221.17153930664062], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.072527", "confidence": 0.9261156916618347, "detection_id": "114-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.089027+00	2025-11-05 18:36:32.115945+00	2025-11-05 18:36:32.11595+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
42b8b22a-f4a8-4f98-9283-5fb1cb39150c	INF-RED-133632-61	red_light	medium	\N	\N		0	\N	\N			{"bbox": [157.3514404296875, 84.96370697021484, 178.25875854492188, 96.15406036376953], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.559409", "confidence": 0.22309325635433197, "detection_id": "110-23", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.566723+00	2025-11-05 18:36:32.187631+00	2025-11-05 18:36:32.187636+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
17ad13d2-d3be-4063-ab0c-c7a7b1d0ce6a	INF-RED-133632-20	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.0, 109.06704711914062, 174.82211303710938, 183.63739013671875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.073493", "confidence": 0.9258196949958801, "detection_id": "114-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.089232+00	2025-11-05 18:36:32.190418+00	2025-11-05 18:36:32.190426+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2033c689-399a-421d-8baf-cd8903547094	INF-RED-133632-38	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.16973876953125, 81.11116790771484, 286.4696960449219, 95.77713775634766], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.816705", "confidence": 0.5678933262825012, "detection_id": "112-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.830937+00	2025-11-05 18:36:32.234373+00	2025-11-05 18:36:32.234383+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c9a7e512-a774-4a32-884c-c76bbafb5b8f	INF-RED-133632-57	red_light	medium	\N	\N		0	\N	\N			{"bbox": [167.24072265625, 88.86939239501953, 195.30780029296875, 111.19219207763672], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.074482", "confidence": 0.7927696704864502, "detection_id": "114-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.089479+00	2025-11-05 18:36:32.239488+00	2025-11-05 18:36:32.239497+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a5a69a64-08f9-40e6-9682-9ca38799b716	INF-RED-133632-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [262.4320983886719, 71.0830307006836, 458.0032958984375, 158.89486694335938], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.817979", "confidence": 0.5462011694908142, "detection_id": "112-9", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.831178+00	2025-11-05 18:36:32.311752+00	2025-11-05 18:36:32.311766+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
734495c7-aa8f-4fc3-8059-c12d720f4428	INF-SPE-133632-28	speed	medium	\N	\N		0	77.2	60			{"bbox": [136.154296875, 87.7920913696289, 166.28201293945312, 109.7252426147461], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.075283", "confidence": 0.7009070515632629, "detection_id": "114-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.089714+00	2025-11-05 18:36:32.31689+00	2025-11-05 18:36:32.316903+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c4220e7d-baea-469e-97da-edcce8f08465	INF-SPE-133632-16	speed	medium	\N	\N		0	96.4	60			{"bbox": [262.3052978515625, 70.28782653808594, 457.3509521484375, 158.322021484375], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.818980", "confidence": 0.518875241279602, "detection_id": "112-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.83143+00	2025-11-05 18:36:32.374371+00	2025-11-05 18:36:32.37438+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
700fbc47-6406-4165-a7f8-f751e04b4fa2	INF-RED-133632-98	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.2637634277344, 80.8260726928711, 286.0499267578125, 96.32855987548828], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.076181", "confidence": 0.63427734375, "detection_id": "114-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.090034+00	2025-11-05 18:36:32.375788+00	2025-11-05 18:36:32.375794+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f0f5fe54-1ec1-4687-8837-54d06957a17d	INF-RED-133632-31	red_light	medium	\N	\N		0	\N	\N			{"bbox": [309.02545166015625, 113.19495391845703, 479.2502746582031, 221.61923217773438], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.366382", "confidence": 0.9067516326904297, "detection_id": "116-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.380186+00	2025-11-05 18:36:32.442496+00	2025-11-05 18:36:32.442502+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b4a71cc5-fe86-4ee4-bd95-f2079bc74892	INF-SPE-133632-32	speed	medium	\N	\N		0	78.2	60			{"bbox": [262.33294677734375, 71.55519104003906, 455.14630126953125, 159.3306427001953], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.076993", "confidence": 0.5647523403167725, "detection_id": "114-6", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.090338+00	2025-11-05 18:36:32.445609+00	2025-11-05 18:36:32.445618+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5f0d900b-448c-4521-9e02-98f611e89c4b	INF-SPE-133632-10	speed	medium	\N	\N		0	90.6	60			{"bbox": [0.11080169677734375, 108.46861267089844, 133.3668975830078, 183.88568115234375], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.367211", "confidence": 0.9042022228240967, "detection_id": "116-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.380334+00	2025-11-05 18:36:32.503101+00	2025-11-05 18:36:32.503142+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
29c1dd2f-9ce8-48db-89c3-787f3734f36f	INF-SPE-133632-92	speed	medium	\N	\N		0	88.6	60			{"bbox": [198.36676025390625, 82.644287109375, 210.41912841796875, 92.44715881347656], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.821268", "confidence": 0.3972606360912323, "detection_id": "112-14", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.831777+00	2025-11-05 18:36:32.553947+00	2025-11-05 18:36:32.554242+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
63854cb7-64be-4f68-a4e5-948aa9fe7d0f	INF-SPE-133632-29	speed	medium	\N	\N		0	89.4	60			{"bbox": [185.81671142578125, 84.36248779296875, 202.4014892578125, 98.83857727050781], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.079011", "confidence": 0.4590614140033722, "detection_id": "114-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.090843+00	2025-11-05 18:36:32.710702+00	2025-11-05 18:36:32.710716+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
360b9880-e3bc-4ae4-8d2a-5d33523210f7	INF-RED-133632-83	red_light	medium	\N	\N		0	\N	\N			{"bbox": [306.6703186035156, 113.50607299804688, 479.02001953125, 222.51795959472656], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.713692", "confidence": 0.9044888615608215, "detection_id": "118-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.739417+00	2025-11-05 18:36:32.837978+00	2025-11-05 18:36:32.83799+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
75bdb984-43e4-4625-a3b1-9742dcc86690	INF-RED-133632-90	red_light	medium	\N	\N		0	\N	\N			{"bbox": [285.1295471191406, 82.03825378417969, 307.71759033203125, 101.69631958007812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:31.823214", "confidence": 0.2473025619983673, "detection_id": "112-18", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:31.832136+00	2025-11-05 18:36:32.849402+00	2025-11-05 18:36:32.849411+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c1681393-2316-4d15-a931-42615569e91b	INF-RED-133632-95	red_light	medium	\N	\N		0	\N	\N			{"bbox": [198.38255310058594, 82.74362182617188, 210.4343719482422, 92.24137115478516], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.079931", "confidence": 0.43955957889556885, "detection_id": "114-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.091072+00	2025-11-05 18:36:32.850178+00	2025-11-05 18:36:32.850182+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6d71f61d-ed3a-4a3c-84d6-02dcf551750d	INF-RED-133632-10	red_light	medium	\N	\N		0	\N	\N			{"bbox": [136.45025634765625, 87.98046112060547, 165.78663635253906, 109.33358001708984], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.368949", "confidence": 0.6868506073951721, "detection_id": "116-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.380765+00	2025-11-05 18:36:32.85393+00	2025-11-05 18:36:32.853935+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d0419d6d-daba-41c4-b018-998e30157e4e	INF-RED-133632-85	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.00853729248046875, 108.82594299316406, 83.06526947021484, 184.10829162597656], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.715487", "confidence": 0.8957535028457642, "detection_id": "118-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.739908+00	2025-11-05 18:36:32.923289+00	2025-11-05 18:36:32.923298+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3816e295-abc2-4efa-a214-12dfdae8e62d	INF-RED-133632-74	red_light	medium	\N	\N		0	\N	\N			{"bbox": [151.52024841308594, 86.92845916748047, 172.38204956054688, 106.69636535644531], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.081277", "confidence": 0.20004941523075104, "detection_id": "114-20", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.091284+00	2025-11-05 18:36:32.924944+00	2025-11-05 18:36:32.924953+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
495871bf-a346-4cdc-bb6d-7246fff2944e	INF-RED-133632-88	red_light	medium	\N	\N		0	\N	\N			{"bbox": [262.7638854980469, 71.24449157714844, 455.2492980957031, 157.00978088378906], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.370348", "confidence": 0.5579958558082581, "detection_id": "116-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.381004+00	2025-11-05 18:36:32.929224+00	2025-11-05 18:36:32.929247+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
93a04c1f-bc68-43e8-b209-2c3aa80aa584	INF-SPE-133633-63	speed	medium	\N	\N		0	93	60			{"bbox": [167.6931610107422, 88.11096954345703, 195.97677612304688, 111.1329116821289], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.717483", "confidence": 0.7834808230400085, "detection_id": "118-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.740278+00	2025-11-05 18:36:33.013106+00	2025-11-05 18:36:33.013117+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0a4852a7-c40f-4e09-a358-56b7fe5d435f	INF-RED-133633-20	red_light	medium	\N	\N		0	\N	\N			{"bbox": [270.75115966796875, 81.2825698852539, 286.94134521484375, 96.2684326171875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.371357", "confidence": 0.5407750010490417, "detection_id": "116-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.381167+00	2025-11-05 18:36:33.035932+00	2025-11-05 18:36:33.035944+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f0c88d01-d0b1-40a3-af46-22f2f44ff48d	INF-RED-133633-38	red_light	medium	\N	\N		0	\N	\N			{"bbox": [137.35496520996094, 87.50178527832031, 166.5691680908203, 109.04572296142578], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.719693", "confidence": 0.7522339820861816, "detection_id": "118-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.740738+00	2025-11-05 18:36:33.074055+00	2025-11-05 18:36:33.074077+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
15c1965e-619b-4b3e-96ab-8d7191a94af7	INF-RED-133633-81	red_light	medium	\N	\N		0	\N	\N			{"bbox": [262.8428955078125, 71.00587463378906, 455.44989013671875, 157.32762145996094], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.372389", "confidence": 0.5109044909477234, "detection_id": "116-8", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.381375+00	2025-11-05 18:36:33.089035+00	2025-11-05 18:36:33.089044+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d5e3c9e8-d798-438b-b715-025c16f40168	INF-RED-133633-60	red_light	medium	\N	\N		0	\N	\N			{"bbox": [186.07669067382812, 84.11290740966797, 202.8686981201172, 98.85983276367188], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.373306", "confidence": 0.503973662853241, "detection_id": "116-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.381506+00	2025-11-05 18:36:33.158544+00	2025-11-05 18:36:33.158554+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b1a93cab-209d-451e-8c52-202ced496ec7	INF-RED-133633-21	red_light	medium	\N	\N		0	\N	\N			{"bbox": [186.9627227783203, 84.34046173095703, 203.84934997558594, 98.96404266357422], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.721560", "confidence": 0.5733721852302551, "detection_id": "118-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.741115+00	2025-11-05 18:36:33.157249+00	2025-11-05 18:36:33.15726+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a0a097f8-7dcb-4ac7-9a7d-90366c98da9b	INF-RED-133633-23	red_light	medium	\N	\N		0	\N	\N			{"bbox": [263.3937683105469, 71.24627685546875, 455.5836181640625, 160.59548950195312], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.722959", "confidence": 0.5320350527763367, "detection_id": "118-7", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.741596+00	2025-11-05 18:36:33.258978+00	2025-11-05 18:36:33.258995+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
01fc9cc9-bc29-4c8a-b036-506bcc6ba605	INF-SPE-133633-67	speed	medium	\N	\N		0	79.1	60			{"bbox": [197.82769775390625, 82.22731018066406, 210.50564575195312, 92.27960205078125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.374094", "confidence": 0.45567744970321655, "detection_id": "116-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.38165+00	2025-11-05 18:36:33.261642+00	2025-11-05 18:36:33.261687+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b9e0619a-702b-46c5-9e09-2b88ac5128b7	INF-SPE-133633-27	speed	medium	\N	\N		0	89.6	60			{"bbox": [303.79052734375, 113.42557525634766, 479.1354675292969, 221.99044799804688], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.241160", "confidence": 0.9110877513885498, "detection_id": "120-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.261272+00	2025-11-05 18:36:33.314549+00	2025-11-05 18:36:33.314563+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c25d44cd-b3f8-429a-a5e7-b40380bbf089	INF-SPE-133633-20	speed	medium	\N	\N		0	95.8	60			{"bbox": [271.1126403808594, 81.01659393310547, 287.3064880371094, 95.12503051757812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.724270", "confidence": 0.5269492864608765, "detection_id": "118-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.742086+00	2025-11-05 18:36:33.316639+00	2025-11-05 18:36:33.316653+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8b3dcdf1-a14a-4480-9e54-f97909ac61ff	INF-RED-133633-49	red_light	medium	\N	\N		0	\N	\N			{"bbox": [263.33148193359375, 71.62506103515625, 455.3194885253906, 159.87741088867188], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.725689", "confidence": 0.4974829852581024, "detection_id": "118-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.742423+00	2025-11-05 18:36:33.372187+00	2025-11-05 18:36:33.372195+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1d797234-df59-4869-99c1-eb0bdfc23041	INF-RED-133633-46	red_light	medium	\N	\N		0	\N	\N			{"bbox": [167.62490844726562, 87.97145080566406, 196.27413940429688, 111.27212524414062], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.243003", "confidence": 0.7678636908531189, "detection_id": "120-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.261617+00	2025-11-05 18:36:33.373409+00	2025-11-05 18:36:33.373421+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
85374050-2cde-4c1e-9e38-feb1e20cd83e	INF-SPE-133633-59	speed	medium	\N	\N		0	82	60			{"bbox": [285.2029113769531, 82.91766357421875, 307.3929138183594, 102.07058715820312], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.727097", "confidence": 0.4522463083267212, "detection_id": "118-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.74283+00	2025-11-05 18:36:33.435634+00	2025-11-05 18:36:33.435647+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d4fadfe5-c813-4ec5-942d-55fb0a9c5414	INF-RED-133633-53	red_light	medium	\N	\N		0	\N	\N			{"bbox": [137.5895233154297, 87.81170654296875, 164.31582641601562, 109.01206970214844], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.244688", "confidence": 0.7591881155967712, "detection_id": "120-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.261898+00	2025-11-05 18:36:33.441476+00	2025-11-05 18:36:33.441491+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
041d42ab-1c25-40a5-84b4-7b61bce0c4f2	INF-SPE-133633-24	speed	medium	\N	\N		0	88.2	60			{"bbox": [199.52435302734375, 83.1288070678711, 210.87863159179688, 92.97422790527344], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.728255", "confidence": 0.41928336024284363, "detection_id": "118-14", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.743199+00	2025-11-05 18:36:33.505506+00	2025-11-05 18:36:33.505518+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
266c71f1-4221-431e-9ede-c090d92eb7a3	INF-RED-133633-74	red_light	medium	\N	\N		0	\N	\N			{"bbox": [271.2664489746094, 81.23865509033203, 287.8114013671875, 96.00581359863281], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.246436", "confidence": 0.6198636293411255, "detection_id": "120-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.262131+00	2025-11-05 18:36:33.511028+00	2025-11-05 18:36:33.511036+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0167813e-2abf-4efe-a3d3-18d2db76d527	INF-RED-133633-25	red_light	medium	\N	\N		0	\N	\N			{"bbox": [236.82778930664062, 78.03273010253906, 249.58863830566406, 86.2261734008789], "source": "webcam_local", "timestamp": "2025-11-05T18:36:32.730558", "confidence": 0.20176810026168823, "detection_id": "118-24", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:32.743566+00	2025-11-05 18:36:33.60192+00	2025-11-05 18:36:33.60193+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
57607f66-ca96-4b49-8b6a-64ed46d0ccdf	INF-RED-133633-62	red_light	medium	\N	\N		0	\N	\N			{"bbox": [263.77471923828125, 71.79856872558594, 455.2068176269531, 158.7902374267578], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.248616", "confidence": 0.6015060544013977, "detection_id": "120-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.262374+00	2025-11-05 18:36:33.617729+00	2025-11-05 18:36:33.617741+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c37dc2de-1ad9-44f5-98b8-502b901b3faa	INF-RED-133633-88	red_light	medium	\N	\N		0	\N	\N			{"bbox": [61.981544494628906, 109.09657287597656, 223.6977081298828, 170.79940795898438], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.592249", "confidence": 0.9131269454956055, "detection_id": "122-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.616383+00	2025-11-05 18:36:33.676238+00	2025-11-05 18:36:33.676257+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5757d677-e08e-4153-a425-f5b7dcea4878	INF-SPE-133633-98	speed	medium	\N	\N		0	78.5	60			{"bbox": [189.09536743164062, 84.55958557128906, 204.57350158691406, 99.23389434814453], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.250387", "confidence": 0.5127207636833191, "detection_id": "120-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.262561+00	2025-11-05 18:36:33.680035+00	2025-11-05 18:36:33.680041+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c3661002-e873-4374-83c4-3d7bda8d8a33	INF-SPE-133633-25	speed	medium	\N	\N		0	70.8	60			{"bbox": [296.6899108886719, 116.09934997558594, 471.02764892578125, 208.0469207763672], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.593405", "confidence": 0.8987441062927246, "detection_id": "122-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.616677+00	2025-11-05 18:36:33.736433+00	2025-11-05 18:36:33.73644+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6b7dad88-beed-4070-b42a-c8d67bf58dbb	INF-RED-133633-19	red_light	medium	\N	\N		0	\N	\N			{"bbox": [285.6658630371094, 83.16629791259766, 307.23114013671875, 103.1828842163086], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.252108", "confidence": 0.4107789695262909, "detection_id": "120-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.262823+00	2025-11-05 18:36:33.738992+00	2025-11-05 18:36:33.739+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0da56568-bb9b-4c21-97f8-aa0a685ee11a	INF-RED-133633-96	red_light	medium	\N	\N		0	\N	\N			{"bbox": [262.3228454589844, 80.57720947265625, 423.7774658203125, 155.0380096435547], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.594873", "confidence": 0.6571008563041687, "detection_id": "122-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.616888+00	2025-11-05 18:36:33.79716+00	2025-11-05 18:36:33.797172+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b5757a3e-9eb2-4e2e-b1b9-06cc119c6d99	INF-SPE-133633-95	speed	medium	\N	\N		0	93.2	60			{"bbox": [201.02430725097656, 83.20313262939453, 210.69117736816406, 92.63798522949219], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.253812", "confidence": 0.2687211036682129, "detection_id": "120-18", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.263131+00	2025-11-05 18:36:33.803099+00	2025-11-05 18:36:33.803108+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ddf7c5fd-d65c-4150-9a7e-2da2f635abe5	INF-RED-133633-89	red_light	medium	\N	\N		0	\N	\N			{"bbox": [157.01715087890625, 92.96726989746094, 182.6118927001953, 111.56295776367188], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.595997", "confidence": 0.5919687747955322, "detection_id": "122-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.617373+00	2025-11-05 18:36:33.858027+00	2025-11-05 18:36:33.858054+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
45abc720-210e-45e5-9607-3e94f8648890	INF-RED-133633-41	red_light	medium	\N	\N		0	\N	\N			{"bbox": [181.9870147705078, 93.44430541992188, 206.52923583984375, 113.15247344970703], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.597188", "confidence": 0.5276992917060852, "detection_id": "122-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.617707+00	2025-11-05 18:36:33.911955+00	2025-11-05 18:36:33.911967+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
44c7ff53-bb70-438c-9d32-90d7801b3ffa	INF-RED-133633-57	red_light	medium	\N	\N		0	\N	\N			{"bbox": [297.59490966796875, 117.0109634399414, 470.8717346191406, 207.54396057128906], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.937655", "confidence": 0.9100748896598816, "detection_id": "124-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.956802+00	2025-11-05 18:36:33.99159+00	2025-11-05 18:36:33.991605+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f8039baa-77ba-4e67-bfbe-c5b2dccf0e73	INF-SPE-133633-71	speed	medium	\N	\N		0	71.7	60			{"bbox": [268.64898681640625, 88.35248565673828, 283.0442810058594, 100.3978042602539], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.598202", "confidence": 0.524452269077301, "detection_id": "122-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.618213+00	2025-11-05 18:36:33.993177+00	2025-11-05 18:36:33.993184+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0b3e3b4a-2e59-4692-9bd1-64a8304b464b	INF-RED-133634-52	red_light	medium	\N	\N		0	\N	\N			{"bbox": [281.082275390625, 89.25813293457031, 296.478515625, 107.12824249267578], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.599225", "confidence": 0.5127442479133606, "detection_id": "122-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.618737+00	2025-11-05 18:36:34.079786+00	2025-11-05 18:36:34.079795+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
69dad750-f396-4594-aca7-7ff8b79f8d18	INF-RED-133634-92	red_light	medium	\N	\N		0	\N	\N			{"bbox": [82.21773529052734, 109.94691467285156, 242.8593292236328, 168.6136016845703], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.939400", "confidence": 0.9097585678100586, "detection_id": "124-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.95711+00	2025-11-05 18:36:34.08099+00	2025-11-05 18:36:34.080997+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
bec65eb1-42ca-41c2-ace4-234f69f6830c	INF-RED-133634-98	red_light	medium	\N	\N		0	\N	\N			{"bbox": [262.35821533203125, 80.64347076416016, 424.3900451660156, 155.5872039794922], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.941252", "confidence": 0.7026047706604004, "detection_id": "124-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.957305+00	2025-11-05 18:36:34.143302+00	2025-11-05 18:36:34.143314+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
11873d6e-c6a3-4a6e-999e-1ea11e2af655	INF-RED-133634-62	red_light	medium	\N	\N		0	\N	\N			{"bbox": [198.18392944335938, 90.85453033447266, 214.01669311523438, 103.376953125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.600054", "confidence": 0.3463747799396515, "detection_id": "122-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.619105+00	2025-11-05 18:36:34.144372+00	2025-11-05 18:36:34.144379+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3f2b7895-e19f-4028-96f4-07894f5ae89c	INF-SPE-133634-66	speed	medium	\N	\N		0	96.7	60			{"bbox": [157.00686645507812, 91.1404037475586, 205.9244842529297, 112.92853546142578], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.604625", "confidence": 0.2938356101512909, "detection_id": "122-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.619349+00	2025-11-05 18:36:34.214695+00	2025-11-05 18:36:34.214741+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0000ad4f-5d08-4dca-b477-bc35087541f4	INF-RED-133634-39	red_light	medium	\N	\N		0	\N	\N			{"bbox": [157.55801391601562, 92.02716064453125, 205.2620086669922, 112.72901916503906], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.942880", "confidence": 0.5705649256706238, "detection_id": "124-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.957507+00	2025-11-05 18:36:34.218781+00	2025-11-05 18:36:34.218792+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5d772072-b2f7-48f3-9e21-2a40f3acabb3	INF-RED-133634-28	red_light	medium	\N	\N		0	\N	\N			{"bbox": [182.74807739257812, 93.2297134399414, 206.15904235839844, 113.08889770507812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.944439", "confidence": 0.49451130628585815, "detection_id": "124-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.957763+00	2025-11-05 18:36:34.275171+00	2025-11-05 18:36:34.275183+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4dc625e4-3e0e-4b80-96ae-73a3c32eb4ba	INF-SPE-133634-46	speed	medium	\N	\N		0	81.1	60			{"bbox": [268.68353271484375, 88.48933410644531, 283.73077392578125, 100.08556365966797], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.945547", "confidence": 0.42768776416778564, "detection_id": "124-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.957929+00	2025-11-05 18:36:34.341525+00	2025-11-05 18:36:34.341533+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b4b6eb89-de71-4769-a2fa-ffcf7a6f09b9	INF-SPE-133634-85	speed	medium	\N	\N		0	86.7	60			{"bbox": [297.7462463378906, 115.7105712890625, 471.42352294921875, 208.1349334716797], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.282738", "confidence": 0.9249854683876038, "detection_id": "126-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.297719+00	2025-11-05 18:36:34.342359+00	2025-11-05 18:36:34.342365+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
35bda576-5ecf-492e-a9b7-31deec4efbbc	INF-RED-133634-20	red_light	medium	\N	\N		0	\N	\N			{"bbox": [280.76727294921875, 89.01483154296875, 299.3741455078125, 106.8451156616211], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.946829", "confidence": 0.4229719340801239, "detection_id": "124-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.958168+00	2025-11-05 18:36:34.404284+00	2025-11-05 18:36:34.404291+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8f88fe2e-9151-4cc4-a578-2c1ea7c927d9	INF-RED-133634-32	red_light	medium	\N	\N		0	\N	\N			{"bbox": [105.77066802978516, 109.7721176147461, 263.63385009765625, 168.23780822753906], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.283856", "confidence": 0.9152067303657532, "detection_id": "126-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.298051+00	2025-11-05 18:36:34.40646+00	2025-11-05 18:36:34.406468+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a44a87aa-c294-471c-9951-438b4568f068	INF-RED-133634-16	red_light	medium	\N	\N		0	\N	\N			{"bbox": [198.1652069091797, 91.1668930053711, 213.61244201660156, 103.8154525756836], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.947814", "confidence": 0.36260950565338135, "detection_id": "124-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.958487+00	2025-11-05 18:36:34.452683+00	2025-11-05 18:36:34.452692+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
270df699-0482-4763-8551-9d4f4727a206	INF-RED-133634-40	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.11769390106201172, 108.91268920898438, 41.283199310302734, 156.668701171875], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.284777", "confidence": 0.799877941608429, "detection_id": "126-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.298265+00	2025-11-05 18:36:34.456867+00	2025-11-05 18:36:34.45688+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f8533c36-da34-4637-8979-d885047443f5	INF-RED-133634-33	red_light	medium	\N	\N		0	\N	\N			{"bbox": [253.38894653320312, 88.77399444580078, 264.9427185058594, 98.58959197998047], "source": "webcam_local", "timestamp": "2025-11-05T18:36:33.948993", "confidence": 0.20058895647525787, "detection_id": "124-13", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:33.958769+00	2025-11-05 18:36:34.518004+00	2025-11-05 18:36:34.518013+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
10466ec1-8898-4051-bef3-5a0dd8024dae	INF-SPE-133634-78	speed	medium	\N	\N		0	74.7	60			{"bbox": [446.5997314453125, 112.55516052246094, 479.864501953125, 148.5282440185547], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.285495", "confidence": 0.7867729663848877, "detection_id": "126-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.298541+00	2025-11-05 18:36:34.523175+00	2025-11-05 18:36:34.523186+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
91876b63-9341-46c0-abce-ec1e8ff02106	INF-RED-133634-90	red_light	medium	\N	\N		0	\N	\N			{"bbox": [296.9633483886719, 117.70923614501953, 473.01104736328125, 208.69822692871094], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.585266", "confidence": 0.9574795961380005, "detection_id": "128-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.602599+00	2025-11-05 18:36:34.650288+00	2025-11-05 18:36:34.650297+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b9cb22dc-dba0-4140-82d1-44f71f4aebf0	INF-SPE-133634-96	speed	medium	\N	\N		0	81.9	60			{"bbox": [157.3915252685547, 92.64464569091797, 184.60585021972656, 109.4023208618164], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.287097", "confidence": 0.5859811305999756, "detection_id": "126-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.298896+00	2025-11-05 18:36:34.667531+00	2025-11-05 18:36:34.667537+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a6065d0b-abe3-40fa-8c9c-af8329357e6e	INF-SPE-133634-86	speed	medium	\N	\N		0	88.9	60			{"bbox": [116.04947662353516, 109.13207244873047, 273.13555908203125, 168.84210205078125], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.586841", "confidence": 0.9245073199272156, "detection_id": "128-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.602779+00	2025-11-05 18:36:34.714684+00	2025-11-05 18:36:34.714694+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2240da15-90f2-44c7-b4de-9c775e357b91	INF-RED-133634-76	red_light	medium	\N	\N		0	\N	\N			{"bbox": [182.8439483642578, 92.0724105834961, 205.8904266357422, 111.4486312866211], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.288301", "confidence": 0.47810637950897217, "detection_id": "126-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.299038+00	2025-11-05 18:36:34.718067+00	2025-11-05 18:36:34.718078+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
abe1af1e-fc26-4972-94b4-8963aad56cb6	INF-RED-133634-37	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.10368919372558594, 105.85734558105469, 66.59390258789062, 157.83334350585938], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.589323", "confidence": 0.8571662902832031, "detection_id": "128-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.602972+00	2025-11-05 18:36:34.792331+00	2025-11-05 18:36:34.79234+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
902cd1f2-8fa7-4b3f-8f42-061cba19877f	INF-RED-133634-46	red_light	medium	\N	\N		0	\N	\N			{"bbox": [268.6304931640625, 88.79981231689453, 283.24871826171875, 99.9762954711914], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.289682", "confidence": 0.3471454679965973, "detection_id": "126-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.299181+00	2025-11-05 18:36:34.796497+00	2025-11-05 18:36:34.796505+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
99e8826a-bd1e-443a-8126-d62d06cfcbe4	INF-SPE-133634-60	speed	medium	\N	\N		0	72.6	60			{"bbox": [280.5552062988281, 89.06989288330078, 300.1702880859375, 107.38643646240234], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.290608", "confidence": 0.31886008381843567, "detection_id": "126-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.299382+00	2025-11-05 18:36:34.847108+00	2025-11-05 18:36:34.847123+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9c3f1631-fdcf-44c1-91f7-1638ea03014f	INF-RED-133634-63	red_light	medium	\N	\N		0	\N	\N			{"bbox": [198.947021484375, 91.74678039550781, 213.6456298828125, 103.74234008789062], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.291785", "confidence": 0.20079779624938965, "detection_id": "126-17", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.299565+00	2025-11-05 18:36:34.899772+00	2025-11-05 18:36:34.89978+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c02e39e6-3539-4ddd-a947-356969de2b50	INF-SPE-133634-52	speed	medium	\N	\N		0	85.7	60			{"bbox": [273.3833312988281, 79.90319061279297, 433.66436767578125, 156.34286499023438], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.592175", "confidence": 0.7839010953903198, "detection_id": "128-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.603392+00	2025-11-05 18:36:34.931963+00	2025-11-05 18:36:34.93197+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d3c81352-9f1b-4992-8147-5ad2a897fba4	INF-SPE-133635-65	speed	medium	\N	\N		0	83.6	60			{"bbox": [182.5618133544922, 92.84637451171875, 205.3187255859375, 108.85208129882812], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.594787", "confidence": 0.5886934995651245, "detection_id": "128-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.603852+00	2025-11-05 18:36:35.030367+00	2025-11-05 18:36:35.030373+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
abe92cbd-fb18-41d8-832f-d074aadd6da6	INF-RED-133635-54	red_light	medium	\N	\N		0	\N	\N			{"bbox": [281.5589599609375, 89.81770324707031, 301.3342590332031, 106.46837615966797], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.595950", "confidence": 0.5258133411407471, "detection_id": "128-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.604057+00	2025-11-05 18:36:35.057425+00	2025-11-05 18:36:35.057431+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
cf4e9c45-7c34-43a9-a6fd-d16f88cea0e1	INF-RED-133635-99	red_light	medium	\N	\N		0	\N	\N			{"bbox": [269.069091796875, 89.14160919189453, 282.9825439453125, 100.32170867919922], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.596929", "confidence": 0.3629574775695801, "detection_id": "128-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.604365+00	2025-11-05 18:36:35.083497+00	2025-11-05 18:36:35.083504+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
75dbb562-a53c-4116-b4ce-6cacfb9452ae	INF-RED-133635-57	red_light	medium	\N	\N		0	\N	\N			{"bbox": [252.98602294921875, 88.20636749267578, 264.6114807128906, 98.1906509399414], "source": "webcam_local", "timestamp": "2025-11-05T18:36:34.598014", "confidence": 0.20031704008579254, "detection_id": "128-17", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:36:34.604566+00	2025-11-05 18:36:35.108878+00	2025-11-05 18:36:35.108884+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
19888a79-2f79-412e-9af7-e3fa49997f25	INF-RED-133950-31	red_light	medium	\N	\N		0	\N	\N			{"bbox": [31.601417541503906, 88.17880249023438, 127.2144546508789, 150.10427856445312], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.651693", "confidence": 0.8785521388053894, "detection_id": "4-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.669413+00	2025-11-05 18:39:50.721417+00	2025-11-05 18:39:50.721429+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6a476e00-ba44-4ff1-9837-ae6b9469608a	INF-SPE-133950-96	speed	medium	\N	\N		0	82	60			{"bbox": [16.830791473388672, 83.70884704589844, 47.82394027709961, 119.76496887207031], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.653608", "confidence": 0.7013546824455261, "detection_id": "4-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.669667+00	2025-11-05 18:39:50.773678+00	2025-11-05 18:39:50.773687+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f3236115-7182-4081-bd09-bc651ed1efdb	INF-SPE-133950-77	speed	medium	\N	\N		0	96.1	60			{"bbox": [244.84469604492188, 85.06800842285156, 263.6512145996094, 95.75379943847656], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.654920", "confidence": 0.5130096077919006, "detection_id": "4-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.669966+00	2025-11-05 18:39:50.822745+00	2025-11-05 18:39:50.822757+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
efb95062-be6d-4777-8183-9d4990280b42	INF-RED-133950-77	red_light	medium	\N	\N		0	\N	\N			{"bbox": [255.58572387695312, 85.42926025390625, 263.7613830566406, 95.23764038085938], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.656238", "confidence": 0.30727821588516235, "detection_id": "4-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.670258+00	2025-11-05 18:39:50.871148+00	2025-11-05 18:39:50.871155+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4856cded-70a0-410b-be04-e322eb1e07ea	INF-SPE-133950-50	speed	medium	\N	\N		0	80	60			{"bbox": [63.86302185058594, 94.97459411621094, 133.1169891357422, 147.45010375976562], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.870048", "confidence": 0.9062816500663757, "detection_id": "6-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.883188+00	2025-11-05 18:39:50.915528+00	2025-11-05 18:39:50.915534+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
640ac20c-54bd-42ce-a60a-5961ff525ca0	INF-RED-133950-59	red_light	medium	\N	\N		0	\N	\N			{"bbox": [17.997215270996094, 87.8177490234375, 55.970611572265625, 127.00714111328125], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.871703", "confidence": 0.7992259860038757, "detection_id": "6-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.88356+00	2025-11-05 18:39:50.94987+00	2025-11-05 18:39:50.949877+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
797c83a8-a02d-4857-9495-d8633e808f52	INF-RED-133950-13	red_light	medium	\N	\N		0	\N	\N			{"bbox": [249.84268188476562, 94.22807312011719, 263.6812438964844, 103.24725341796875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.873508", "confidence": 0.4824351668357849, "detection_id": "6-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.883924+00	2025-11-05 18:39:51.008105+00	2025-11-05 18:39:51.008115+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0a5f669b-3346-4969-ae86-1a2c23e91def	INF-RED-133951-87	red_light	medium	\N	\N		0	\N	\N			{"bbox": [57.86559295654297, 95.3771743774414, 67.9420394897461, 103.57198333740234], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.874900", "confidence": 0.3589678704738617, "detection_id": "6-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.884302+00	2025-11-05 18:39:51.059971+00	2025-11-05 18:39:51.059979+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
82a343d0-822f-4ffb-a834-e8ef74fa6199	INF-SPE-133951-39	speed	medium	\N	\N		0	74.1	60			{"bbox": [46.08793640136719, 77.969970703125, 69.03791809082031, 103.06742858886719], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.877118", "confidence": 0.3460959196090698, "detection_id": "6-6", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.884689+00	2025-11-05 18:39:51.124551+00	2025-11-05 18:39:51.124557+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e9187afc-2fe6-4f49-8b21-6b3c01d647a4	INF-RED-133951-33	red_light	medium	\N	\N		0	\N	\N			{"bbox": [72.24760437011719, 96.61174011230469, 128.66891479492188, 146.7430419921875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.086389", "confidence": 0.9462580680847168, "detection_id": "8-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.096218+00	2025-11-05 18:39:51.125727+00	2025-11-05 18:39:51.125736+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ffeb99b2-31c8-4740-8924-1e4d283ff68b	INF-SPE-133951-36	speed	medium	\N	\N		0	77.7	60			{"bbox": [0.0174713134765625, 110.01719665527344, 43.76341247558594, 179.05274963378906], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.087624", "confidence": 0.8585755825042725, "detection_id": "8-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.096632+00	2025-11-05 18:39:51.199268+00	2025-11-05 18:39:51.199284+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
58b52d94-5863-412f-a6fb-55f3c7cd434c	INF-SPE-133951-54	speed	medium	\N	\N		0	77.2	60			{"bbox": [45.759735107421875, 77.76139831542969, 69.230224609375, 102.98988342285156], "source": "webcam_local", "timestamp": "2025-11-05T18:39:50.878950", "confidence": 0.2604764997959137, "detection_id": "6-9", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:50.885137+00	2025-11-05 18:39:51.200585+00	2025-11-05 18:39:51.2006+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3f7fe11f-7eda-4b2d-a296-7948f7bd152a	INF-SPE-133951-12	speed	medium	\N	\N		0	83	60			{"bbox": [19.02016830444336, 88.97494506835938, 49.441959381103516, 109.22512817382812], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.088932", "confidence": 0.5878342986106873, "detection_id": "8-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.096888+00	2025-11-05 18:39:51.247897+00	2025-11-05 18:39:51.247908+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d8039cc0-a3ec-42a1-b40c-e18a2c40f955	INF-SPE-133951-74	speed	medium	\N	\N		0	97.6	60			{"bbox": [18.305320739746094, 89.81422424316406, 38.6068115234375, 124.62034606933594], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.090174", "confidence": 0.21731595695018768, "detection_id": "8-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.097222+00	2025-11-05 18:39:51.292485+00	2025-11-05 18:39:51.292492+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5e39e377-b4b4-4c36-b68f-db6c36121ce3	INF-RED-133951-47	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.03912353515625, 102.99176025390625, 72.86723327636719, 179.474609375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.297453", "confidence": 0.9142065048217773, "detection_id": "10-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.306858+00	2025-11-05 18:39:51.340397+00	2025-11-05 18:39:51.340403+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
aaa546f7-39b7-4d79-b9b7-3f1ee866a488	INF-RED-133951-28	red_light	medium	\N	\N		0	\N	\N			{"bbox": [47.18922424316406, 97.34757995605469, 62.659576416015625, 105.14030456542969], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.091485", "confidence": 0.20923684537410736, "detection_id": "8-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.097724+00	2025-11-05 18:39:51.342369+00	2025-11-05 18:39:51.342374+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f115773d-b5ed-455f-a7f7-e5c4683ca89d	INF-RED-133951-12	red_light	medium	\N	\N		0	\N	\N			{"bbox": [74.51129150390625, 96.01168823242188, 128.84088134765625, 144.20510864257812], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.298766", "confidence": 0.8794093728065491, "detection_id": "10-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.307121+00	2025-11-05 18:39:51.374598+00	2025-11-05 18:39:51.374604+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
731ac562-5b64-489f-aeb0-b4d20a6d0935	INF-RED-133951-10	red_light	medium	\N	\N		0	\N	\N			{"bbox": [18.92483139038086, 90.25650024414062, 48.37107467651367, 109.53640747070312], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.300233", "confidence": 0.6860604286193848, "detection_id": "10-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.307397+00	2025-11-05 18:39:51.422481+00	2025-11-05 18:39:51.422495+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f1e99cf5-5ded-46b6-918e-05e1ed45719f	INF-RED-133951-86	red_light	medium	\N	\N		0	\N	\N			{"bbox": [46.71446990966797, 98.72032165527344, 59.05467987060547, 105.73460388183594], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.301245", "confidence": 0.2627246677875519, "detection_id": "10-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.307636+00	2025-11-05 18:39:51.471266+00	2025-11-05 18:39:51.471276+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
418b5c8d-e291-43ca-8ffb-ab71f43336f6	INF-RED-133951-21	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.008093833923339844, 97.25393676757812, 9.941081047058105, 104.59237670898438], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.302300", "confidence": 0.25411221385002136, "detection_id": "10-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.307867+00	2025-11-05 18:39:51.530495+00	2025-11-05 18:39:51.530507+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5c763ca9-43cd-4ff1-bfba-c26aa3a81ae2	INF-SPE-133951-41	speed	medium	\N	\N		0	97.3	60			{"bbox": [0.0, 99.6812744140625, 91.38336181640625, 174.72494506835938], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.517034", "confidence": 0.8555426597595215, "detection_id": "12-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.524649+00	2025-11-05 18:39:51.554933+00	2025-11-05 18:39:51.55494+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8108ddad-b021-46b9-9c3b-253124ff7343	INF-RED-133951-81	red_light	medium	\N	\N		0	\N	\N			{"bbox": [73.60948181152344, 95.30311584472656, 126.19627380371094, 141.2010498046875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.518448", "confidence": 0.8467018604278564, "detection_id": "12-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.525345+00	2025-11-05 18:39:51.58768+00	2025-11-05 18:39:51.587689+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a8a788c3-1fae-4613-9b94-623af2af18c6	INF-RED-133951-65	red_light	medium	\N	\N		0	\N	\N			{"bbox": [249.4131622314453, 95.21910095214844, 264.95147705078125, 105.29719543457031], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.519806", "confidence": 0.3039313554763794, "detection_id": "12-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.52592+00	2025-11-05 18:39:51.637497+00	2025-11-05 18:39:51.637507+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a1d17580-e6c4-40ff-9514-cb9dbdc3678e	INF-RED-133951-34	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.02782440185546875, 98.48233795166016, 107.60182189941406, 166.58187866210938], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.690565", "confidence": 0.8844941258430481, "detection_id": "14-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.697906+00	2025-11-05 18:39:51.722867+00	2025-11-05 18:39:51.722873+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6274cf58-bca2-4395-bf46-0a09b8962db5	INF-RED-133951-68	red_light	medium	\N	\N		0	\N	\N			{"bbox": [74.96124267578125, 93.87054443359375, 120.73966979980469, 136.6752471923828], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.691609", "confidence": 0.8393293023109436, "detection_id": "14-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.698202+00	2025-11-05 18:39:51.761946+00	2025-11-05 18:39:51.761956+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c38e1b96-0613-4b27-a562-4d5d9dbbddfa	INF-SPE-133951-77	speed	medium	\N	\N		0	76.2	60			{"bbox": [0.08388519287109375, 129.43353271484375, 70.49595642089844, 178.5189208984375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.849660", "confidence": 0.7460195422172546, "detection_id": "16-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.857373+00	2025-11-05 18:39:51.888499+00	2025-11-05 18:39:51.888507+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
931861fe-0972-4e4b-99e0-6eb6c03076d1	INF-SPE-133951-92	speed	medium	\N	\N		0	87.3	60			{"bbox": [25.00945281982422, 78.00628662109375, 68.37661743164062, 99.73736572265625], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.693885", "confidence": 0.21622493863105774, "detection_id": "14-7", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.698753+00	2025-11-05 18:39:51.908487+00	2025-11-05 18:39:51.908493+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7e80884b-797f-4e4b-acc5-7c0bc91f3aa7	INF-SPE-133952-59	speed	medium	\N	\N		0	83.1	60			{"bbox": [0.0735015869140625, 116.42488098144531, 94.62687683105469, 179.0030975341797], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.005101", "confidence": 0.8959242105484009, "detection_id": "18-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.012768+00	2025-11-05 18:39:52.134507+00	2025-11-05 18:39:52.134517+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
69686b52-76bb-4f29-a332-36ce2306c97b	INF-SPE-133952-71	speed	medium	\N	\N		0	95.7	60			{"bbox": [252.65896606445312, 94.64299011230469, 264.4398498535156, 103.64356994628906], "source": "webcam_local", "timestamp": "2025-11-05T18:39:51.852533", "confidence": 0.27049633860588074, "detection_id": "16-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:51.857773+00	2025-11-05 18:39:52.182805+00	2025-11-05 18:39:52.18281+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
42d2cca6-7d9b-4be7-805d-13d75ab2ac6b	INF-RED-133952-30	red_light	medium	\N	\N		0	\N	\N			{"bbox": [31.272457122802734, 93.43756866455078, 121.4464111328125, 156.27716064453125], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.006433", "confidence": 0.7776485085487366, "detection_id": "18-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.013063+00	2025-11-05 18:39:52.185807+00	2025-11-05 18:39:52.185812+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9402d8c5-b5a8-43bf-a60b-61b8ca3dc60c	INF-RED-133952-20	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.38423919677734375, 111.65165710449219, 120.2232894897461, 178.84352111816406], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.181619", "confidence": 0.928164541721344, "detection_id": "20-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.189945+00	2025-11-05 18:39:52.22354+00	2025-11-05 18:39:52.223545+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c286ed2f-52e9-4b49-aac3-8daa926c83a5	INF-SPE-133952-28	speed	medium	\N	\N		0	99.7	60			{"bbox": [23.414783477783203, 79.18775177001953, 48.47267532348633, 106.33306121826172], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.007466", "confidence": 0.45254844427108765, "detection_id": "18-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.013428+00	2025-11-05 18:39:52.227801+00	2025-11-05 18:39:52.227807+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
85e804be-ddef-4732-9ed9-26dcdd917229	INF-RED-133952-79	red_light	medium	\N	\N		0	\N	\N			{"bbox": [48.112003326416016, 97.4081039428711, 127.38180541992188, 147.98672485351562], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.182309", "confidence": 0.8255016803741455, "detection_id": "20-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.190159+00	2025-11-05 18:39:52.285777+00	2025-11-05 18:39:52.285784+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
19590f19-2954-4efb-a958-b4cab71b77b6	INF-SPE-133952-26	speed	medium	\N	\N		0	73.3	60			{"bbox": [254.58090209960938, 93.11813354492188, 264.1789245605469, 101.58348083496094], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.008253", "confidence": 0.4038076400756836, "detection_id": "18-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.013714+00	2025-11-05 18:39:52.287946+00	2025-11-05 18:39:52.287957+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5c2eb1a7-435b-4a25-a97e-c26d146e06ec	INF-RED-133952-35	red_light	medium	\N	\N		0	\N	\N			{"bbox": [24.554306030273438, 77.17964172363281, 66.54236602783203, 104.20545959472656], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.009007", "confidence": 0.22482305765151978, "detection_id": "18-8", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.014075+00	2025-11-05 18:39:52.344659+00	2025-11-05 18:39:52.344671+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
22085987-7793-467b-9570-5839ee601c6d	INF-RED-133952-69	red_light	medium	\N	\N		0	\N	\N			{"bbox": [19.424440383911133, 76.72647094726562, 65.49127197265625, 105.71623229980469], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.183046", "confidence": 0.25203433632850647, "detection_id": "20-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.190327+00	2025-11-05 18:39:52.346173+00	2025-11-05 18:39:52.346183+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
76fe1696-061e-4478-9994-431db717732c	INF-SPE-133952-31	speed	medium	\N	\N		0	72.1	60			{"bbox": [21.592025756835938, 76.58097839355469, 65.63680267333984, 105.84506225585938], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.183940", "confidence": 0.2381988763809204, "detection_id": "20-7", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.190505+00	2025-11-05 18:39:52.388688+00	2025-11-05 18:39:52.388697+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3eedb1e0-5c94-44e7-aa8b-8685f92e9100	INF-RED-133952-48	red_light	medium	\N	\N		0	\N	\N			{"bbox": [26.458362579345703, 89.66482543945312, 49.30204391479492, 105.78904724121094], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.184826", "confidence": 0.23166826367378235, "detection_id": "20-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.190695+00	2025-11-05 18:39:52.424257+00	2025-11-05 18:39:52.424264+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d754a8c9-2d5a-4bfc-b0c4-9a80b6534149	INF-RED-133952-47	red_light	medium	\N	\N		0	\N	\N			{"bbox": [0.203582763671875, 104.599609375, 140.01943969726562, 179.04959106445312], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.381725", "confidence": 0.9021773338317871, "detection_id": "22-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.388662+00	2025-11-05 18:39:52.424904+00	2025-11-05 18:39:52.424909+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e6d397ec-d9a6-431a-948f-a2891144af3a	INF-SPE-133952-66	speed	medium	\N	\N		0	87.9	60			{"bbox": [21.71752166748047, 76.35425567626953, 65.90117645263672, 105.7112808227539], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.185750", "confidence": 0.20188073813915253, "detection_id": "20-10", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.190876+00	2025-11-05 18:39:52.468147+00	2025-11-05 18:39:52.468158+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ce9d16bb-f611-4549-872b-8f85407fd2dc	INF-SPE-133952-53	speed	medium	\N	\N		0	72.3	60			{"bbox": [60.892059326171875, 94.99578857421875, 129.0449981689453, 138.232421875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.382672", "confidence": 0.6311067938804626, "detection_id": "22-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.388906+00	2025-11-05 18:39:52.473132+00	2025-11-05 18:39:52.47314+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e22b5c46-8e7b-45ad-b21d-ec68a3eda811	INF-RED-133952-52	red_light	medium	\N	\N		0	\N	\N			{"bbox": [17.958112716674805, 76.087646484375, 64.65599060058594, 102.48672485351562], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.383854", "confidence": 0.3602380156517029, "detection_id": "22-7", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.389506+00	2025-11-05 18:39:52.520446+00	2025-11-05 18:39:52.520453+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9faa19fa-7a82-4cc6-9c86-4fcfbabe401c	INF-RED-133952-92	red_light	medium	\N	\N		0	\N	\N			{"bbox": [104.03240966796875, 87.97084045410156, 127.50381469726562, 100.38075256347656], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.384805", "confidence": 0.23922018706798553, "detection_id": "22-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.389946+00	2025-11-05 18:39:52.569571+00	2025-11-05 18:39:52.569578+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f52b741e-7910-4188-86c0-6c6acf31c865	INF-SPE-133952-77	speed	medium	\N	\N		0	96.4	60			{"bbox": [0.0, 103.83818054199219, 156.06373596191406, 179.18617248535156], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.555985", "confidence": 0.9074625372886658, "detection_id": "24-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.562313+00	2025-11-05 18:39:52.586958+00	2025-11-05 18:39:52.586964+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f312c66f-c3f8-4347-ae13-855ba810654a	INF-RED-133952-64	red_light	medium	\N	\N		0	\N	\N			{"bbox": [71.79971313476562, 92.82536315917969, 126.02325439453125, 111.20417785644531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.557202", "confidence": 0.5833308696746826, "detection_id": "24-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.562713+00	2025-11-05 18:39:52.617785+00	2025-11-05 18:39:52.617793+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f7f87445-91c2-4a7f-b1f5-0e6333bb3724	INF-SPE-133952-58	speed	medium	\N	\N		0	73.7	60			{"bbox": [18.883825302124023, 87.08997344970703, 79.62027740478516, 113.37316131591797], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.558499", "confidence": 0.3164284825325012, "detection_id": "24-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.563079+00	2025-11-05 18:39:52.672477+00	2025-11-05 18:39:52.672484+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fa583ccb-b973-45b3-b5cd-2aeb2c70849e	INF-RED-133952-78	red_light	medium	\N	\N		0	\N	\N			{"bbox": [19.62664794921875, 101.0623779296875, 168.83718872070312, 179.814208984375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.716042", "confidence": 0.9141409397125244, "detection_id": "26-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.724843+00	2025-11-05 18:39:52.748857+00	2025-11-05 18:39:52.748862+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
76809408-5a3b-469a-8a9c-aad3b39528e1	INF-RED-133952-38	red_light	medium	\N	\N		0	\N	\N			{"bbox": [15.31939697265625, 86.16932678222656, 80.02279663085938, 121.6790771484375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.717607", "confidence": 0.7696257829666138, "detection_id": "26-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.725497+00	2025-11-05 18:39:52.783758+00	2025-11-05 18:39:52.783766+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e3f52a05-f77e-4e5f-9362-538a3d692ab8	INF-RED-133952-22	red_light	medium	\N	\N		0	\N	\N			{"bbox": [79.30967712402344, 91.27301025390625, 122.10075378417969, 102.57560729980469], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.718658", "confidence": 0.49905407428741455, "detection_id": "26-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.725802+00	2025-11-05 18:39:52.824832+00	2025-11-05 18:39:52.82484+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fe510736-ae7b-4f4a-af19-0071e3ca028c	INF-SPE-133952-63	speed	medium	\N	\N		0	96.1	60			{"bbox": [259.7176208496094, 87.66779327392578, 268.8563537597656, 96.57097625732422], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.720254", "confidence": 0.25444361567497253, "detection_id": "26-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.726058+00	2025-11-05 18:39:52.8706+00	2025-11-05 18:39:52.870608+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5f8db420-7339-4fa6-858f-13209cfbb8d6	INF-RED-133952-67	red_light	medium	\N	\N		0	\N	\N			{"bbox": [47.34283447265625, 101.56953430175781, 178.72689819335938, 179.1899871826172], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.884800", "confidence": 0.9132293462753296, "detection_id": "28-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.891922+00	2025-11-05 18:39:52.917309+00	2025-11-05 18:39:52.917315+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
444f30d7-05b2-496b-9772-42371533dca2	INF-SPE-133952-97	speed	medium	\N	\N		0	90.3	60			{"bbox": [80.24790954589844, 91.85188293457031, 120.36463928222656, 105.6766357421875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.885848", "confidence": 0.46986883878707886, "detection_id": "28-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.892247+00	2025-11-05 18:39:52.948928+00	2025-11-05 18:39:52.948934+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8dfe6346-c7e7-46af-8319-a766170820db	INF-RED-133953-34	red_light	medium	\N	\N		0	\N	\N			{"bbox": [10.92437744140625, 71.17012023925781, 78.64454650878906, 122.17266845703125], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.886913", "confidence": 0.28128528594970703, "detection_id": "28-4", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.892556+00	2025-11-05 18:39:53.012362+00	2025-11-05 18:39:53.012369+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
89c47251-a23e-40ed-ab06-dd0c5eaaf5a2	INF-RED-133953-42	red_light	medium	\N	\N		0	\N	\N			{"bbox": [261.45159912109375, 89.28968811035156, 269.12957763671875, 97.15725708007812], "source": "webcam_local", "timestamp": "2025-11-05T18:39:52.888188", "confidence": 0.2143554985523224, "detection_id": "28-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:52.892905+00	2025-11-05 18:39:53.059918+00	2025-11-05 18:39:53.059926+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f9a77c8b-d285-4cb0-9815-a3809d76bf84	INF-SPE-133953-45	speed	medium	\N	\N		0	92	60			{"bbox": [72.68405151367188, 104.01605224609375, 189.11422729492188, 178.95504760742188], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.078861", "confidence": 0.9120342135429382, "detection_id": "30-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.088855+00	2025-11-05 18:39:53.113213+00	2025-11-05 18:39:53.113218+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8a414932-6317-406e-a610-e807906dcce9	INF-RED-133953-56	red_light	medium	\N	\N		0	\N	\N			{"bbox": [70.9224853515625, 94.67289733886719, 121.4718017578125, 135.53738403320312], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.081272", "confidence": 0.845629870891571, "detection_id": "30-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.089159+00	2025-11-05 18:39:53.141578+00	2025-11-05 18:39:53.141586+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1c7f07fe-8b53-4302-8431-12e85d8db7f5	INF-SPE-133953-39	speed	medium	\N	\N		0	78.4	60			{"bbox": [18.917879104614258, 90.70631408691406, 58.02674865722656, 124.48789978027344], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.082537", "confidence": 0.7236368060112, "detection_id": "30-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.089451+00	2025-11-05 18:39:53.209667+00	2025-11-05 18:39:53.209681+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4a6cabc4-eff9-4a15-8eef-bbaabd10d468	INF-RED-133953-95	red_light	medium	\N	\N		0	\N	\N			{"bbox": [15.890220642089844, 76.06108093261719, 58.501953125, 99.35014343261719], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.083839", "confidence": 0.21374575793743134, "detection_id": "30-4", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.089794+00	2025-11-05 18:39:53.252825+00	2025-11-05 18:39:53.252833+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
73a18eeb-47f6-486d-98ba-4f14040cd95b	INF-RED-133953-87	red_light	medium	\N	\N		0	\N	\N			{"bbox": [89.69005584716797, 104.2958755493164, 195.19110107421875, 176.80422973632812], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.254205", "confidence": 0.9081177711486816, "detection_id": "32-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.260495+00	2025-11-05 18:39:53.283809+00	2025-11-05 18:39:53.283815+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d3e37cf8-4ee8-4a8e-bb8b-40a59ce8b963	INF-RED-133953-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [65.3297119140625, 95.90702819824219, 120.42416381835938, 138.66102600097656], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.255074", "confidence": 0.8259562849998474, "detection_id": "32-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.260739+00	2025-11-05 18:39:53.313274+00	2025-11-05 18:39:53.313281+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3811dceb-9ed3-4ba7-9826-39ee049ec5f4	INF-RED-133953-64	red_light	medium	\N	\N		0	\N	\N			{"bbox": [14.669414520263672, 95.70426940917969, 45.36552429199219, 124.45976257324219], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.256048", "confidence": 0.32126128673553467, "detection_id": "32-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.261158+00	2025-11-05 18:39:53.349169+00	2025-11-05 18:39:53.349178+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9423518b-d28f-47d6-8de6-1436942f669c	INF-SPE-133953-28	speed	medium	\N	\N		0	89.2	60			{"bbox": [15.941999435424805, 76.83464050292969, 56.003875732421875, 108.09092712402344], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.256707", "confidence": 0.2862533926963806, "detection_id": "32-4", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.261444+00	2025-11-05 18:39:53.396107+00	2025-11-05 18:39:53.396121+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
826ee9d7-d7a9-4974-a011-380fee1d8fb8	INF-RED-133953-24	red_light	medium	\N	\N		0	\N	\N			{"bbox": [109.38548278808594, 103.02139282226562, 204.1291961669922, 168.8642578125], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.426525", "confidence": 0.891647219657898, "detection_id": "34-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.434512+00	2025-11-05 18:39:53.459877+00	2025-11-05 18:39:53.459885+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
215fd741-8013-49fa-9aaf-a8f621690ddb	INF-RED-133953-71	red_light	medium	\N	\N		0	\N	\N			{"bbox": [15.978214263916016, 76.48959350585938, 56.401737213134766, 107.54373168945312], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.428535", "confidence": 0.6412487030029297, "detection_id": "34-4", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.435718+00	2025-11-05 18:39:53.595641+00	2025-11-05 18:39:53.595647+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5dbfe6bd-8dc7-4e53-8c55-5f6557ce852e	INF-SPE-133953-96	speed	medium	\N	\N		0	88.1	60			{"bbox": [119.4999771118164, 102.53370666503906, 208.14468383789062, 164.87489318847656], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.588635", "confidence": 0.9185335040092468, "detection_id": "36-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.593659+00	2025-11-05 18:39:53.62685+00	2025-11-05 18:39:53.626858+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5ff919da-3444-4ef5-8776-d07c94bd6ed5	INF-SPE-133953-84	speed	medium	\N	\N		0	81.3	60			{"bbox": [0.030611038208007812, 91.64933013916016, 30.566591262817383, 120.68160247802734], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.429378", "confidence": 0.36984798312187195, "detection_id": "34-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.436522+00	2025-11-05 18:39:53.62791+00	2025-11-05 18:39:53.627915+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
acd5b3ec-7cfe-439e-9245-1b9ab1f5ad6c	INF-RED-133953-83	red_light	medium	\N	\N		0	\N	\N			{"bbox": [25.131593704223633, 90.28067016601562, 40.365478515625, 107.87385559082031], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.430389", "confidence": 0.21380367875099182, "detection_id": "34-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.437065+00	2025-11-05 18:39:53.656048+00	2025-11-05 18:39:53.656055+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9c12c662-dfb2-4c88-9663-e684eb07438c	INF-RED-133953-26	red_light	medium	\N	\N		0	\N	\N			{"bbox": [43.309417724609375, 92.8077392578125, 112.41600036621094, 132.64407348632812], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.742893", "confidence": 0.8633572459220886, "detection_id": "38-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.750587+00	2025-11-05 18:39:53.775503+00	2025-11-05 18:39:53.775509+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
350fb35c-2446-4004-b0e4-26f2c7bdac3d	INF-SPE-133953-18	speed	medium	\N	\N		0	97.4	60			{"bbox": [132.11941528320312, 100.71546936035156, 214.47732543945312, 159.2021026611328], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.744243", "confidence": 0.8597216010093689, "detection_id": "38-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.750886+00	2025-11-05 18:39:53.806898+00	2025-11-05 18:39:53.806908+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e4b1aac0-2af9-44f2-985d-2f3b11ecc0b8	INF-SPE-133953-48	speed	medium	\N	\N		0	79.2	60			{"bbox": [26.068683624267578, 86.81573486328125, 57.78168869018555, 104.81344604492188], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.745442", "confidence": 0.3494207262992859, "detection_id": "38-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.75132+00	2025-11-05 18:39:53.856218+00	2025-11-05 18:39:53.856226+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0687ddc8-110c-47da-b909-1b04fd9ce1f4	INF-RED-133953-74	red_light	medium	\N	\N		0	\N	\N			{"bbox": [25.189828872680664, 88.24336242675781, 41.898155212402344, 105.19126892089844], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.746700", "confidence": 0.2237330675125122, "detection_id": "38-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.75163+00	2025-11-05 18:39:53.905998+00	2025-11-05 18:39:53.906007+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7e8ff81e-0a78-46d1-8faf-fea0d8a1ad6b	INF-RED-133953-36	red_light	medium	\N	\N		0	\N	\N			{"bbox": [138.80465698242188, 99.42509460449219, 215.58352661132812, 154.7195587158203], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.908759", "confidence": 0.9033183455467224, "detection_id": "40-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.915991+00	2025-11-05 18:39:53.94611+00	2025-11-05 18:39:53.946122+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3a7837c3-86a0-4810-a250-b53c41b8b5a8	INF-RED-133953-14	red_light	medium	\N	\N		0	\N	\N			{"bbox": [34.1671142578125, 91.40669250488281, 105.98561096191406, 129.88949584960938], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.909762", "confidence": 0.8693643808364868, "detection_id": "40-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.916306+00	2025-11-05 18:39:53.983273+00	2025-11-05 18:39:53.983282+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
84c7df2c-5c06-4ec5-9902-220c1365f192	INF-RED-133954-49	red_light	medium	\N	\N		0	\N	\N			{"bbox": [23.908517837524414, 86.89867401123047, 46.412925720214844, 104.83734893798828], "source": "webcam_local", "timestamp": "2025-11-05T18:39:53.911904", "confidence": 0.47921308875083923, "detection_id": "40-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:53.916573+00	2025-11-05 18:39:54.022885+00	2025-11-05 18:39:54.022893+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2438b100-7aba-4cd0-87f1-601545e17284	INF-SPE-133954-19	speed	medium	\N	\N		0	91.3	60			{"bbox": [23.992630004882812, 92.33926391601562, 97.58358764648438, 129.28594970703125], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.057502", "confidence": 0.8744708895683289, "detection_id": "42-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.068815+00	2025-11-05 18:39:54.092699+00	2025-11-05 18:39:54.092705+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
01472877-8027-4555-b02b-665c41257e6c	INF-RED-133954-50	red_light	medium	\N	\N		0	\N	\N			{"bbox": [146.39349365234375, 99.17784118652344, 218.480224609375, 150.3004913330078], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.059045", "confidence": 0.871700644493103, "detection_id": "42-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.069359+00	2025-11-05 18:39:54.12485+00	2025-11-05 18:39:54.124858+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d66e9959-2393-4b32-87ed-4131a95a9b4b	INF-SPE-133954-94	speed	medium	\N	\N		0	78.6	60			{"bbox": [22.6646728515625, 87.84523010253906, 49.19135284423828, 106.52488708496094], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.060210", "confidence": 0.4249994158744812, "detection_id": "42-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.069592+00	2025-11-05 18:39:54.161487+00	2025-11-05 18:39:54.161501+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
27eb9484-61de-4fb3-a095-d51d622b49fa	INF-RED-133954-94	red_light	medium	\N	\N		0	\N	\N			{"bbox": [87.31233215332031, 87.032958984375, 107.40457153320312, 103.01895141601562], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.061448", "confidence": 0.3278029263019562, "detection_id": "42-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.069901+00	2025-11-05 18:39:54.209776+00	2025-11-05 18:39:54.209788+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b61a404e-4be0-4fbe-8588-5e0bb2f96859	INF-RED-133954-37	red_light	medium	\N	\N		0	\N	\N			{"bbox": [1.3194656372070312, 73.72779846191406, 49.31719970703125, 98.25730895996094], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.063686", "confidence": 0.30078795552253723, "detection_id": "42-5", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.070138+00	2025-11-05 18:39:54.252293+00	2025-11-05 18:39:54.2523+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9a43d91c-d30e-49b3-84f4-2bd60b3c3b42	INF-RED-133954-45	red_light	medium	\N	\N		0	\N	\N			{"bbox": [152.863037109375, 100.03572082519531, 220.60366821289062, 148.5569610595703], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.241645", "confidence": 0.8883043527603149, "detection_id": "44-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.250827+00	2025-11-05 18:39:54.291382+00	2025-11-05 18:39:54.291388+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0ec6b07a-a43c-40cc-b82d-10f11c0f681c	INF-SPE-133954-70	speed	medium	\N	\N		0	83	60			{"bbox": [310.116943359375, 105.36264038085938, 319.9002685546875, 115.41058349609375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.064710", "confidence": 0.29020681977272034, "detection_id": "42-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.070441+00	2025-11-05 18:39:54.293313+00	2025-11-05 18:39:54.293318+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e174a71c-61a9-4f1b-8631-2fd20ebc1d50	INF-SPE-133954-40	speed	medium	\N	\N		0	90.3	60			{"bbox": [21.462539672851562, 93.74533081054688, 89.5080795288086, 129.3285369873047], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.242952", "confidence": 0.8804963827133179, "detection_id": "44-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.251066+00	2025-11-05 18:39:54.325035+00	2025-11-05 18:39:54.325042+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b1f0a3b0-3b0c-4b67-8f6e-9bddaff71e99	INF-SPE-133954-41	speed	medium	\N	\N		0	95.2	60			{"bbox": [81.97210693359375, 89.03999328613281, 102.98049926757812, 103.10914611816406], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.244316", "confidence": 0.34211963415145874, "detection_id": "44-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.251665+00	2025-11-05 18:39:54.365086+00	2025-11-05 18:39:54.365095+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8bc03202-bf08-474f-8fb7-0d8b4b71e555	INF-RED-133954-26	red_light	medium	\N	\N		0	\N	\N			{"bbox": [310.1597595214844, 105.03228759765625, 319.8805847167969, 116.25601196289062], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.245632", "confidence": 0.24278201162815094, "detection_id": "44-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.252052+00	2025-11-05 18:39:54.408975+00	2025-11-05 18:39:54.408987+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e502efb1-4286-4795-b2e3-a93e0ab81fe6	INF-RED-133954-96	red_light	medium	\N	\N		0	\N	\N			{"bbox": [160.26943969726562, 99.06314086914062, 224.31314086914062, 145.822021484375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.414309", "confidence": 0.871928870677948, "detection_id": "46-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.422257+00	2025-11-05 18:39:54.453516+00	2025-11-05 18:39:54.453522+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
354111e0-8c09-4ccc-91d8-2b1c3974a155	INF-RED-133954-33	red_light	medium	\N	\N		0	\N	\N			{"bbox": [22.284963607788086, 88.69584655761719, 50.984657287597656, 104.60581970214844], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.247013", "confidence": 0.23528234660625458, "detection_id": "44-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.252364+00	2025-11-05 18:39:54.456943+00	2025-11-05 18:39:54.456949+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
74517882-3689-4a34-99f2-a43b5ac5bf1b	INF-SPE-133954-78	speed	medium	\N	\N		0	86.7	60			{"bbox": [19.815208435058594, 91.32655334472656, 76.63236999511719, 127.67674255371094], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.415463", "confidence": 0.5868823528289795, "detection_id": "46-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.422572+00	2025-11-05 18:39:54.490749+00	2025-11-05 18:39:54.490758+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
16dba8d3-6a12-45a3-b700-8151be96e865	INF-RED-133954-19	red_light	medium	\N	\N		0	\N	\N			{"bbox": [19.98528480529785, 91.02381896972656, 76.50389862060547, 127.89222717285156], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.416961", "confidence": 0.5122842788696289, "detection_id": "46-4", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.422853+00	2025-11-05 18:39:54.530741+00	2025-11-05 18:39:54.530752+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b00139e0-6220-4b74-b194-d10b03b0beff	INF-SPE-133954-73	speed	medium	\N	\N		0	73.3	60			{"bbox": [309.84271240234375, 105.79945373535156, 319.89141845703125, 116.41413879394531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.418224", "confidence": 0.37502267956733704, "detection_id": "46-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.423041+00	2025-11-05 18:39:54.575173+00	2025-11-05 18:39:54.575182+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5d50cf29-b0b5-47ce-ac17-dc2d3546cc50	INF-RED-133954-32	red_light	medium	\N	\N		0	\N	\N			{"bbox": [167.29632568359375, 99.37022399902344, 226.2955322265625, 143.96844482421875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.589669", "confidence": 0.8559227585792542, "detection_id": "48-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.596097+00	2025-11-05 18:39:54.618681+00	2025-11-05 18:39:54.618688+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f69763a6-c004-4b43-a01d-ec5f8e5bafaa	INF-RED-133954-12	red_light	medium	\N	\N		0	\N	\N			{"bbox": [20.98224639892578, 92.93388366699219, 66.0836410522461, 127.29913330078125], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.590637", "confidence": 0.7351011633872986, "detection_id": "48-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.596304+00	2025-11-05 18:39:54.669235+00	2025-11-05 18:39:54.669244+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e0b7a2c2-c036-4225-9b95-9e9ce6a27ac1	INF-RED-133954-81	red_light	medium	\N	\N		0	\N	\N			{"bbox": [310.73681640625, 107.83053588867188, 319.8546142578125, 116.6580810546875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.591764", "confidence": 0.23721791803836823, "detection_id": "48-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.59654+00	2025-11-05 18:39:54.709087+00	2025-11-05 18:39:54.709094+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8471c15a-9a84-440f-bb1c-ec57d3ca74d4	INF-SPE-133954-43	speed	medium	\N	\N		0	77.4	60			{"bbox": [77.73715209960938, 89.70323944091797, 97.0322265625, 105.65264129638672], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.592509", "confidence": 0.2058635801076889, "detection_id": "48-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.596849+00	2025-11-05 18:39:54.744718+00	2025-11-05 18:39:54.744726+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b6287795-e405-4572-b084-d4e9e1fddcd2	INF-SPE-133954-59	speed	medium	\N	\N		0	80.9	60			{"bbox": [174.96160888671875, 98.42568969726562, 229.4427490234375, 139.4213409423828], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.747648", "confidence": 0.8267071843147278, "detection_id": "50-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.755771+00	2025-11-05 18:39:54.788856+00	2025-11-05 18:39:54.788863+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9f6d55c5-df07-405b-b98b-a7d440fb68f7	INF-RED-133954-99	red_light	medium	\N	\N		0	\N	\N			{"bbox": [111.83425903320312, 86.505126953125, 131.45037841796875, 101.15486145019531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.749748", "confidence": 0.31125378608703613, "detection_id": "50-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.756485+00	2025-11-05 18:39:54.937352+00	2025-11-05 18:39:54.937358+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8f6a0b66-879b-4683-a5b8-07ac83953c7b	INF-RED-133954-20	red_light	medium	\N	\N		0	\N	\N			{"bbox": [97.6793212890625, 95.45181274414062, 108.54554748535156, 102.08699035644531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.750676", "confidence": 0.30671465396881104, "detection_id": "50-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.75682+00	2025-11-05 18:39:54.974847+00	2025-11-05 18:39:54.974853+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5ab31937-6d22-46fb-8bb6-ab533df33b7c	INF-RED-133954-10	red_light	medium	\N	\N		0	\N	\N			{"bbox": [178.69569396972656, 97.64833068847656, 232.5870819091797, 137.3443603515625], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.938404", "confidence": 0.6749942898750305, "detection_id": "52-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.943846+00	2025-11-05 18:39:54.975516+00	2025-11-05 18:39:54.975521+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6774adfb-ddf4-4293-8044-1d3523a40963	INF-SPE-133955-18	speed	medium	\N	\N		0	97.6	60			{"bbox": [78.4130859375, 88.50556945800781, 99.17263793945312, 103.82026672363281], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.751543", "confidence": 0.26505130529403687, "detection_id": "50-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.75711+00	2025-11-05 18:39:55.028045+00	2025-11-05 18:39:55.028054+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1d75fad9-fc87-4632-8391-bb3892259a70	INF-SPE-133955-49	speed	medium	\N	\N		0	89.9	60			{"bbox": [22.31688117980957, 94.74151611328125, 42.1251220703125, 123.79257202148438], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.939166", "confidence": 0.5227550268173218, "detection_id": "52-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.944014+00	2025-11-05 18:39:55.029546+00	2025-11-05 18:39:55.029554+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8903dd34-88c4-4134-a14e-5323e91f3536	INF-RED-133955-15	red_light	medium	\N	\N		0	\N	\N			{"bbox": [110.68540954589844, 86.65585327148438, 132.13560485839844, 102.00363159179688], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.939906", "confidence": 0.29817652702331543, "detection_id": "52-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.944194+00	2025-11-05 18:39:55.07026+00	2025-11-05 18:39:55.070268+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
119a22c7-4997-4225-bb71-ee15b19fa602	INF-SPE-133955-32	speed	medium	\N	\N		0	99.3	60			{"bbox": [79.55420684814453, 88.78086853027344, 97.3051528930664, 106.89347839355469], "source": "webcam_local", "timestamp": "2025-11-05T18:39:54.940621", "confidence": 0.23686416447162628, "detection_id": "52-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:54.944419+00	2025-11-05 18:39:55.107028+00	2025-11-05 18:39:55.107035+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3a36ff3c-79d9-4c18-915e-0962399ba25d	INF-SPE-133955-37	speed	medium	\N	\N		0	98.7	60			{"bbox": [183.9171905517578, 96.41908264160156, 234.8833770751953, 134.00408935546875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.101176", "confidence": 0.8626044392585754, "detection_id": "54-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.108937+00	2025-11-05 18:39:55.133529+00	2025-11-05 18:39:55.133537+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3420cdca-97d5-46eb-a4da-df9d51bd5b2e	INF-SPE-133955-52	speed	medium	\N	\N		0	71.1	60			{"bbox": [24.61772918701172, 87.61871337890625, 54.41078186035156, 106.43710327148438], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.102036", "confidence": 0.7400954961776733, "detection_id": "54-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.109135+00	2025-11-05 18:39:55.162594+00	2025-11-05 18:39:55.162601+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2443dc56-63d2-4196-ba5c-255243c7c76c	INF-RED-133955-68	red_light	medium	\N	\N		0	\N	\N			{"bbox": [109.22064208984375, 85.11708068847656, 132.69775390625, 101.66650390625], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.102909", "confidence": 0.57990562915802, "detection_id": "54-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.109492+00	2025-11-05 18:39:55.216845+00	2025-11-05 18:39:55.216857+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2c0d9ccd-af93-4e35-8f57-a629a622ccd8	INF-RED-133955-22	red_light	medium	\N	\N		0	\N	\N			{"bbox": [79.56494140625, 88.29273986816406, 96.571533203125, 103.60353088378906], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.104043", "confidence": 0.274993360042572, "detection_id": "54-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.109731+00	2025-11-05 18:39:55.261732+00	2025-11-05 18:39:55.261741+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
cce37bf4-5459-4f44-93cb-b17a94a32e17	INF-SPE-133955-57	speed	medium	\N	\N		0	81.7	60			{"bbox": [0.0074825286865234375, 78.03094482421875, 28.839277267456055, 121.44427490234375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.104997", "confidence": 0.2539367973804474, "detection_id": "54-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.109931+00	2025-11-05 18:39:55.296617+00	2025-11-05 18:39:55.296626+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fb3fcc82-3b11-45f3-b816-b48037756006	INF-RED-133955-57	red_light	medium	\N	\N		0	\N	\N			{"bbox": [25.351886749267578, 90.06109619140625, 56.98738479614258, 108.68281555175781], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.287957", "confidence": 0.6728599071502686, "detection_id": "56-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.295604+00	2025-11-05 18:39:55.320323+00	2025-11-05 18:39:55.320329+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5febcb2d-c301-4995-8e67-20b2ce6b3a17	INF-SPE-133955-48	speed	medium	\N	\N		0	71.3	60			{"bbox": [190.68402099609375, 98.35847473144531, 238.35626220703125, 134.12103271484375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.288850", "confidence": 0.5006598234176636, "detection_id": "56-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.295898+00	2025-11-05 18:39:55.35097+00	2025-11-05 18:39:55.350976+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ac02e754-e66d-4ce0-82a7-e55ca7608fa7	INF-RED-133955-97	red_light	medium	\N	\N		0	\N	\N			{"bbox": [190.71859741210938, 98.33892822265625, 238.61312866210938, 134.1328582763672], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.289666", "confidence": 0.4558565318584442, "detection_id": "56-5", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.296135+00	2025-11-05 18:39:55.398044+00	2025-11-05 18:39:55.398057+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b835c4bc-5f0e-46a3-bd0c-ad3a418ef21a	INF-RED-133955-40	red_light	medium	\N	\N		0	\N	\N			{"bbox": [108.8004150390625, 87.91249084472656, 132.56387329101562, 103.04057312011719], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.290574", "confidence": 0.3952998220920563, "detection_id": "56-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.296382+00	2025-11-05 18:39:55.438133+00	2025-11-05 18:39:55.43814+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5d92a9eb-511c-4b50-b582-a64910e04c8e	INF-RED-133955-72	red_light	medium	\N	\N		0	\N	\N			{"bbox": [79.85758972167969, 91.8257827758789, 95.38697814941406, 106.21019744873047], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.291439", "confidence": 0.2424989491701126, "detection_id": "56-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.296673+00	2025-11-05 18:39:55.478221+00	2025-11-05 18:39:55.478227+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e6a89df5-76c2-43af-ad2c-f808c73b7c7f	INF-RED-133955-25	red_light	medium	\N	\N		0	\N	\N			{"bbox": [26.53900909423828, 89.32083129882812, 57.23609924316406, 107.528564453125], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.473464", "confidence": 0.8106852769851685, "detection_id": "58-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.483833+00	2025-11-05 18:39:55.516574+00	2025-11-05 18:39:55.51658+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
2917ed8e-38af-4581-a9af-a69b3a579d4e	INF-SPE-133955-50	speed	medium	\N	\N		0	71.3	60			{"bbox": [158.22703552246094, 92.750244140625, 165.65663146972656, 98.52742004394531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.292134", "confidence": 0.2023213654756546, "detection_id": "56-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.297006+00	2025-11-05 18:39:55.51719+00	2025-11-05 18:39:55.517196+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
274d9a39-c702-4883-8cef-860091aa23a0	INF-SPE-133955-77	speed	medium	\N	\N		0	97.6	60			{"bbox": [196.61184692382812, 96.33085632324219, 242.23324584960938, 131.5524139404297], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.475096", "confidence": 0.6227256059646606, "detection_id": "58-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.484119+00	2025-11-05 18:39:55.549987+00	2025-11-05 18:39:55.549993+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
eafc8e7a-58a4-4b8e-be61-1ddc237f9f37	INF-SPE-133955-71	speed	medium	\N	\N		0	85.9	60			{"bbox": [107.035888671875, 86.60655212402344, 134.5812225341797, 101.26814270019531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.476513", "confidence": 0.4866676330566406, "detection_id": "58-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.484423+00	2025-11-05 18:39:55.585983+00	2025-11-05 18:39:55.585994+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
21cfca43-998d-4f16-839d-20eb9f469888	INF-RED-133955-10	red_light	medium	\N	\N		0	\N	\N			{"bbox": [68.5871810913086, 95.49266052246094, 76.25806427001953, 105.52720642089844], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.477539", "confidence": 0.28303900361061096, "detection_id": "58-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.484651+00	2025-11-05 18:39:55.627923+00	2025-11-05 18:39:55.627931+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
cc3921a4-b75f-47d2-9f15-ab5d09ab0af4	INF-SPE-133955-30	speed	medium	\N	\N		0	80	60			{"bbox": [157.18283081054688, 90.90734100341797, 167.09939575195312, 98.03820037841797], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.478543", "confidence": 0.21425943076610565, "detection_id": "58-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.48487+00	2025-11-05 18:39:55.668249+00	2025-11-05 18:39:55.66826+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0a7dd81b-8f70-4ddd-b816-0b20c21f7c4b	INF-RED-133955-88	red_light	medium	\N	\N		0	\N	\N			{"bbox": [201.18521118164062, 95.6434326171875, 245.63632202148438, 128.40646362304688], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.666520", "confidence": 0.8302712440490723, "detection_id": "60-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.673699+00	2025-11-05 18:39:55.708573+00	2025-11-05 18:39:55.70858+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8712302a-00f5-45b5-bd08-e3e1106660fa	INF-RED-133955-12	red_light	medium	\N	\N		0	\N	\N			{"bbox": [26.923709869384766, 88.24120330810547, 57.97825241088867, 107.22888946533203], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.667489", "confidence": 0.767828106880188, "detection_id": "60-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.673931+00	2025-11-05 18:39:55.742871+00	2025-11-05 18:39:55.742878+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
f836e676-33d8-406d-b01d-2d5bd8e02588	INF-RED-133955-32	red_light	medium	\N	\N		0	\N	\N			{"bbox": [105.57400512695312, 85.74911499023438, 130.78005981445312, 102.87957763671875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.668723", "confidence": 0.3594200909137726, "detection_id": "60-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.674202+00	2025-11-05 18:39:55.784659+00	2025-11-05 18:39:55.784671+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e6732a4e-6696-4b5d-abe4-e1b61b07938e	INF-RED-133955-79	red_light	medium	\N	\N		0	\N	\N			{"bbox": [154.22592163085938, 89.79949951171875, 167.580810546875, 97.64956665039062], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.669685", "confidence": 0.27848145365715027, "detection_id": "60-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.674469+00	2025-11-05 18:39:55.833758+00	2025-11-05 18:39:55.833764+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5a2be87c-667c-4c39-8db3-b2fcfd2d8055	INF-RED-133955-59	red_light	medium	\N	\N		0	\N	\N			{"bbox": [207.60626220703125, 95.82405090332031, 249.37030029296875, 127.31465148925781], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.826047", "confidence": 0.8706572651863098, "detection_id": "62-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.836147+00	2025-11-05 18:39:55.862589+00	2025-11-05 18:39:55.862595+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b62f95a4-85e0-4583-9ce4-24cc103c3c3b	INF-RED-133955-96	red_light	medium	\N	\N		0	\N	\N			{"bbox": [103.84376525878906, 85.69564819335938, 128.4227294921875, 102.85110473632812], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.828725", "confidence": 0.5728029608726501, "detection_id": "62-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.836563+00	2025-11-05 18:39:55.985713+00	2025-11-05 18:39:55.985725+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a3060f1e-33cf-4db3-949a-9e621ce648c6	INF-RED-133956-33	red_light	medium	\N	\N		0	\N	\N			{"bbox": [211.85586547851562, 94.6949462890625, 252.44473266601562, 124.86062622070312], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.994112", "confidence": 0.8460083603858948, "detection_id": "64-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.003507+00	2025-11-05 18:39:56.045802+00	2025-11-05 18:39:56.045808+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8968d837-8348-4aba-b7de-da0083bbf530	INF-RED-133956-84	red_light	medium	\N	\N		0	\N	\N			{"bbox": [127.34805297851562, 88.49737548828125, 137.85336303710938, 98.7529296875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.830248", "confidence": 0.42823526263237, "detection_id": "62-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.836767+00	2025-11-05 18:39:56.046372+00	2025-11-05 18:39:56.046377+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9a7559b4-1a4b-4349-b1aa-17fdd5ace5ba	INF-RED-133956-40	red_light	medium	\N	\N		0	\N	\N			{"bbox": [30.280853271484375, 87.02006530761719, 62.19413757324219, 105.53533935546875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.995262", "confidence": 0.5154137015342712, "detection_id": "64-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.003725+00	2025-11-05 18:39:56.097197+00	2025-11-05 18:39:56.097204+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
96231a42-9f21-4c5f-ba2c-1d8dcbfad9f8	INF-RED-133956-78	red_light	medium	\N	\N		0	\N	\N			{"bbox": [154.92263793945312, 89.92378997802734, 168.2325439453125, 98.37191009521484], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.832096", "confidence": 0.20450618863105774, "detection_id": "62-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:55.837019+00	2025-11-05 18:39:56.098507+00	2025-11-05 18:39:56.098512+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fff24e29-e63e-408c-b109-b34e19e3ec54	INF-SPE-133956-25	speed	medium	\N	\N		0	72.1	60			{"bbox": [127.42230224609375, 87.78024291992188, 137.15109252929688, 97.1138916015625], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.996654", "confidence": 0.4615614414215088, "detection_id": "64-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.0039+00	2025-11-05 18:39:56.133903+00	2025-11-05 18:39:56.133916+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
05bb3d76-3cdb-410e-8254-33c03f33971f	INF-RED-133956-67	red_light	medium	\N	\N		0	\N	\N			{"bbox": [98.55853271484375, 85.40393829345703, 126.9365234375, 101.83663177490234], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.997743", "confidence": 0.4496217966079712, "detection_id": "64-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.004141+00	2025-11-05 18:39:56.17419+00	2025-11-05 18:39:56.1742+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ec020d7b-967f-4009-89e7-6f53682f84e2	INF-RED-133956-21	red_light	medium	\N	\N		0	\N	\N			{"bbox": [215.17449951171875, 94.58721923828125, 255.19879150390625, 122.5927734375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.173674", "confidence": 0.7946473956108093, "detection_id": "66-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.180485+00	2025-11-05 18:39:56.210381+00	2025-11-05 18:39:56.210387+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
611c4ee8-87b4-4a87-bdbe-32a2d9c3422f	INF-RED-133956-75	red_light	medium	\N	\N		0	\N	\N			{"bbox": [213.606201171875, 88.82244873046875, 221.934326171875, 95.02279663085938], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.998964", "confidence": 0.25676774978637695, "detection_id": "64-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.00433+00	2025-11-05 18:39:56.211337+00	2025-11-05 18:39:56.211341+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
31cf52dc-dbd7-44f2-8877-a19cb6bac988	INF-RED-133956-22	red_light	medium	\N	\N		0	\N	\N			{"bbox": [155.93646240234375, 87.58963012695312, 171.28390502929688, 97.382568359375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:55.999843", "confidence": 0.24603025615215302, "detection_id": "64-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.004561+00	2025-11-05 18:39:56.25282+00	2025-11-05 18:39:56.252827+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1155b76a-d2c0-416e-a960-3bee1304e7df	INF-RED-133956-99	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.854999542236328, 86.42160034179688, 60.83235549926758, 105.46841430664062], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.174448", "confidence": 0.7530568242073059, "detection_id": "66-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.18069+00	2025-11-05 18:39:56.254031+00	2025-11-05 18:39:56.254038+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e64182d5-7d00-4f5a-b1ed-fd829a58c66b	INF-RED-133956-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [102.80548095703125, 84.08799743652344, 135.06112670898438, 101.30433654785156], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.175464", "confidence": 0.3136482238769531, "detection_id": "66-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.180833+00	2025-11-05 18:39:56.295517+00	2025-11-05 18:39:56.295529+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7e6e9bbf-5743-4f73-a255-9ed6ecaad9e2	INF-SPE-133956-36	speed	medium	\N	\N		0	94.9	60			{"bbox": [102.14356994628906, 88.1297378540039, 120.02803039550781, 101.58621978759766], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.176090", "confidence": 0.307720422744751, "detection_id": "66-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.181077+00	2025-11-05 18:39:56.346269+00	2025-11-05 18:39:56.346281+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
29ba9296-3542-4ac2-a03a-f6fc79f6e79d	INF-SPE-133956-90	speed	medium	\N	\N		0	93.2	60			{"bbox": [29.190444946289062, 87.11640930175781, 61.586456298828125, 105.78883361816406], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.350222", "confidence": 0.7712487578392029, "detection_id": "68-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.359337+00	2025-11-05 18:39:56.39427+00	2025-11-05 18:39:56.394276+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6dbed317-b3c9-489d-a1a7-4f243ce8b292	INF-RED-133956-87	red_light	medium	\N	\N		0	\N	\N			{"bbox": [118.46171569824219, 86.76380157470703, 136.46849060058594, 98.6183853149414], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.176829", "confidence": 0.2175983488559723, "detection_id": "66-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.181337+00	2025-11-05 18:39:56.394851+00	2025-11-05 18:39:56.394857+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
4dad0999-3ba0-486f-9285-689f110ef328	INF-RED-133956-69	red_light	medium	\N	\N		0	\N	\N			{"bbox": [218.991943359375, 95.45494079589844, 256.1578369140625, 122.66659545898438], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.351360", "confidence": 0.545768678188324, "detection_id": "68-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.359675+00	2025-11-05 18:39:56.425205+00	2025-11-05 18:39:56.425212+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6e980d9f-2cf0-4c04-b35b-2f3ff6f0045a	INF-SPE-133956-94	speed	medium	\N	\N		0	85	60			{"bbox": [218.6193389892578, 95.102783203125, 255.98390197753906, 122.90580749511719], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.352200", "confidence": 0.4568282961845398, "detection_id": "68-4", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.360046+00	2025-11-05 18:39:56.484964+00	2025-11-05 18:39:56.484975+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
61a1f1c4-0d18-4fe1-a235-bd1f0efdb70f	INF-RED-133956-83	red_light	medium	\N	\N		0	\N	\N			{"bbox": [184.1002197265625, 102.89049530029297, 200.22891235351562, 119.27385711669922], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.353368", "confidence": 0.255655974149704, "detection_id": "68-9", "vehicle_type": "motorcycle"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.360263+00	2025-11-05 18:39:56.54581+00	2025-11-05 18:39:56.545821+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6eb9a54d-125f-44d3-97f6-752ea87e63d7	INF-SPE-133956-82	speed	medium	\N	\N		0	72.6	60			{"bbox": [29.57221221923828, 87.28688049316406, 61.477020263671875, 105.81048583984375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.565926", "confidence": 0.7386765480041504, "detection_id": "70-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.570529+00	2025-11-05 18:39:56.59361+00	2025-11-05 18:39:56.593617+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
e452b778-0a9a-45ad-ad63-677e4a88af0e	INF-SPE-133956-30	speed	medium	\N	\N		0	98.3	60			{"bbox": [122.5831527709961, 88.35720825195312, 136.29122924804688, 100.70379638671875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.354332", "confidence": 0.24406222999095917, "detection_id": "68-10", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.360442+00	2025-11-05 18:39:56.596599+00	2025-11-05 18:39:56.59661+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
bdf71939-0e94-452e-aefc-d2a76213a458	INF-SPE-133956-97	speed	medium	\N	\N		0	78.1	60			{"bbox": [29.01848602294922, 87.16144561767578, 62.26121520996094, 105.48200225830078], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.757921", "confidence": 0.6434252858161926, "detection_id": "72-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.76478+00	2025-11-05 18:39:56.791326+00	2025-11-05 18:39:56.791334+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
685aaa74-066c-4e56-a2de-1674a6807876	INF-SPE-133956-64	speed	medium	\N	\N		0	77.6	60			{"bbox": [28.752622604370117, 87.90394592285156, 62.341156005859375, 106.28950500488281], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.913098", "confidence": 0.7686604261398315, "detection_id": "74-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.921246+00	2025-11-05 18:39:56.95054+00	2025-11-05 18:39:56.950547+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
664c470f-3ee3-4c0b-99cf-1a2706a4f837	INF-RED-133956-66	red_light	medium	\N	\N		0	\N	\N			{"bbox": [229.28900146484375, 95.80406188964844, 261.5853271484375, 120.29478454589844], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.914307", "confidence": 0.741929292678833, "detection_id": "74-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.921722+00	2025-11-05 18:39:56.990007+00	2025-11-05 18:39:56.990019+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6a5ed916-c2b3-4363-985a-5cc52fae912d	INF-RED-133957-30	red_light	medium	\N	\N		0	\N	\N			{"bbox": [94.07508850097656, 85.59318542480469, 124.72370910644531, 103.07081604003906], "source": "webcam_local", "timestamp": "2025-11-05T18:39:56.915553", "confidence": 0.44500067830085754, "detection_id": "74-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:56.92219+00	2025-11-05 18:39:57.041276+00	2025-11-05 18:39:57.041288+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
c6df7758-20a5-40d6-a7df-72a570b3385f	INF-RED-133957-67	red_light	medium	\N	\N		0	\N	\N			{"bbox": [231.52047729492188, 95.16531372070312, 262.3491516113281, 119.06010437011719], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.072698", "confidence": 0.7735648155212402, "detection_id": "76-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.077992+00	2025-11-05 18:39:57.114452+00	2025-11-05 18:39:57.114459+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d2143183-440a-43e8-80a2-78f596d30d3c	INF-SPE-133957-93	speed	medium	\N	\N		0	84.2	60			{"bbox": [28.115402221679688, 87.7681884765625, 62.08319091796875, 105.83338928222656], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.073405", "confidence": 0.7463747262954712, "detection_id": "76-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.078834+00	2025-11-05 18:39:57.159646+00	2025-11-05 18:39:57.159659+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7aabb983-ca06-4183-b08b-ecc3906849d9	INF-SPE-133957-41	speed	medium	\N	\N		0	91.8	60			{"bbox": [93.5196533203125, 85.21467590332031, 125.97645568847656, 103.31822204589844], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.074189", "confidence": 0.4897160232067108, "detection_id": "76-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.079679+00	2025-11-05 18:39:57.204326+00	2025-11-05 18:39:57.204334+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
920b49fc-bfae-4e9a-aaa1-a96a8e3b9798	INF-RED-133957-65	red_light	medium	\N	\N		0	\N	\N			{"bbox": [233.898193359375, 95.42823791503906, 264.81939697265625, 117.72367858886719], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.260012", "confidence": 0.8303701281547546, "detection_id": "78-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.269433+00	2025-11-05 18:39:57.301505+00	2025-11-05 18:39:57.301513+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
93c02615-9929-4abd-955a-98212ff3b752	INF-SPE-133957-33	speed	medium	\N	\N		0	83.7	60			{"bbox": [30.25110626220703, 87.11491394042969, 59.359230041503906, 105.25825500488281], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.261317", "confidence": 0.6844279170036316, "detection_id": "78-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.26972+00	2025-11-05 18:39:57.340408+00	2025-11-05 18:39:57.34042+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
aa39af79-ef84-4c43-84e1-76b274efa229	INF-SPE-133957-23	speed	medium	\N	\N		0	92.8	60			{"bbox": [95.11003112792969, 84.79823303222656, 122.56117248535156, 102.51922607421875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.262524", "confidence": 0.31092673540115356, "detection_id": "78-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.269894+00	2025-11-05 18:39:57.397368+00	2025-11-05 18:39:57.397377+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b31fe106-43db-4fcd-b299-769c2d592254	INF-RED-133957-66	red_light	medium	\N	\N		0	\N	\N			{"bbox": [58.287010192871094, 92.87532043457031, 77.67708587646484, 104.36021423339844], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.263670", "confidence": 0.28236711025238037, "detection_id": "78-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.270264+00	2025-11-05 18:39:57.452511+00	2025-11-05 18:39:57.452522+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
71e49311-8ef8-4b51-8c12-ab34f5ad4a56	INF-RED-133957-16	red_light	medium	\N	\N		0	\N	\N			{"bbox": [92.5281982421875, 91.4491195678711, 108.11407470703125, 103.04950714111328], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.264724", "confidence": 0.2056841254234314, "detection_id": "78-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.270789+00	2025-11-05 18:39:57.507627+00	2025-11-05 18:39:57.507635+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b660eb87-bdd9-4f86-8d0d-7ac5e623cb63	INF-SPE-133957-25	speed	medium	\N	\N		0	79.9	60			{"bbox": [236.21710205078125, 94.33998107910156, 265.040283203125, 115.78628540039062], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.528971", "confidence": 0.8516441583633423, "detection_id": "80-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.540086+00	2025-11-05 18:39:57.570549+00	2025-11-05 18:39:57.570558+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5618c289-e376-497b-b63f-648b8ba6fe27	INF-RED-133957-27	red_light	medium	\N	\N		0	\N	\N			{"bbox": [31.443634033203125, 87.53410339355469, 61.548194885253906, 105.04991149902344], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.530378", "confidence": 0.414994478225708, "detection_id": "80-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.540338+00	2025-11-05 18:39:57.60947+00	2025-11-05 18:39:57.609477+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
6456ad2a-36a5-4bd1-b274-f5e992bc9f1e	INF-SPE-133957-15	speed	medium	\N	\N		0	95.1	60			{"bbox": [59.4496955871582, 93.69232940673828, 77.35169982910156, 103.8559799194336], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.531588", "confidence": 0.312248557806015, "detection_id": "80-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.540592+00	2025-11-05 18:39:57.669253+00	2025-11-05 18:39:57.669266+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fae14c66-37a6-45a0-a9a3-5d540b193891	INF-RED-133957-22	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.5452880859375, 84.75251770019531, 115.5499267578125, 102.17005920410156], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.533168", "confidence": 0.28838402032852173, "detection_id": "80-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.540803+00	2025-11-05 18:39:57.728275+00	2025-11-05 18:39:57.728293+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
8c58bb3a-d3ef-4ae7-91e5-a399276f5403	INF-RED-133957-74	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.46343994140625, 84.60307312011719, 122.39654541015625, 102.30339050292969], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.534766", "confidence": 0.2345718890428543, "detection_id": "80-6", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.541032+00	2025-11-05 18:39:57.781369+00	2025-11-05 18:39:57.781383+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
44dca959-d1cd-4972-9f34-03337fd5f8b3	INF-SPE-133957-19	speed	medium	\N	\N		0	85.6	60			{"bbox": [240.9449462890625, 92.57997131347656, 267.6559753417969, 113.56141662597656], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.797024", "confidence": 0.8393853306770325, "detection_id": "82-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.808031+00	2025-11-05 18:39:57.84146+00	2025-11-05 18:39:57.841468+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
548de004-32a7-48d1-8997-b20d8a3095de	INF-RED-133957-90	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.88768005371094, 84.14888000488281, 113.82276916503906, 101.98597717285156], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.797900", "confidence": 0.40018579363822937, "detection_id": "82-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.808687+00	2025-11-05 18:39:57.896365+00	2025-11-05 18:39:57.896373+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
23a13064-9b0a-4059-ad48-724e8723f039	INF-RED-133957-48	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.030982971191406, 85.83134460449219, 59.741973876953125, 104.123046875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.798826", "confidence": 0.32416412234306335, "detection_id": "82-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.809136+00	2025-11-05 18:39:57.96142+00	2025-11-05 18:39:57.96143+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
91b40b79-767a-4ab7-8963-437990f20f78	INF-RED-133958-71	red_light	medium	\N	\N		0	\N	\N			{"bbox": [46.05371856689453, 87.42154693603516, 59.499488830566406, 104.20568084716797], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.799905", "confidence": 0.2322310209274292, "detection_id": "82-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.809572+00	2025-11-05 18:39:58.013627+00	2025-11-05 18:39:58.013636+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fff561b2-cdf7-492f-a3d1-236a97ada197	INF-RED-133958-23	red_light	medium	\N	\N		0	\N	\N			{"bbox": [58.34316635131836, 74.75836181640625, 78.783203125, 103.31884765625], "source": "webcam_local", "timestamp": "2025-11-05T18:39:57.801231", "confidence": 0.2175864726305008, "detection_id": "82-10", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:57.809986+00	2025-11-05 18:39:58.067464+00	2025-11-05 18:39:58.067479+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
62adfee3-9b4e-44ea-9095-3bc6435efc67	INF-RED-133958-62	red_light	medium	\N	\N		0	\N	\N			{"bbox": [88.6999740600586, 82.80998992919922, 118.12165069580078, 101.58223724365234], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.091578", "confidence": 0.727003276348114, "detection_id": "84-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.103592+00	2025-11-05 18:39:58.13401+00	2025-11-05 18:39:58.134017+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
72358806-fe6d-4410-b15c-7ae0c6d8c309	INF-SPE-133958-77	speed	medium	\N	\N		0	79.8	60			{"bbox": [29.171661376953125, 85.90785217285156, 60.02794647216797, 103.46443176269531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.092678", "confidence": 0.692505419254303, "detection_id": "84-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.103898+00	2025-11-05 18:39:58.174294+00	2025-11-05 18:39:58.174302+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
0e14d539-803c-4ca6-bfc9-a026b1bd4b82	INF-RED-133958-45	red_light	medium	\N	\N		0	\N	\N			{"bbox": [244.68899536132812, 92.0494155883789, 263.6094970703125, 111.8221206665039], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.094422", "confidence": 0.579124391078949, "detection_id": "84-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.104143+00	2025-11-05 18:39:58.220612+00	2025-11-05 18:39:58.220627+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
83fe2d40-1b03-455e-a073-54cb2f0eec0e	INF-RED-133958-56	red_light	medium	\N	\N		0	\N	\N			{"bbox": [57.98894500732422, 84.83827209472656, 78.36682891845703, 103.49903869628906], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.097024", "confidence": 0.3461955189704895, "detection_id": "84-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.104403+00	2025-11-05 18:39:58.276448+00	2025-11-05 18:39:58.276457+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ff332a7c-a60a-4a59-b0c5-6f443a95ae2c	INF-RED-133958-51	red_light	medium	\N	\N		0	\N	\N			{"bbox": [128.82589721679688, 87.62574768066406, 141.58822631835938, 96.50267028808594], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.098700", "confidence": 0.33224618434906006, "detection_id": "84-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.104679+00	2025-11-05 18:39:58.339416+00	2025-11-05 18:39:58.339429+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a4175487-aa62-45ad-b955-88f6266464cb	INF-RED-133958-61	red_light	medium	\N	\N		0	\N	\N			{"bbox": [246.9398193359375, 93.3569564819336, 264.31011962890625, 112.4460678100586], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.354558", "confidence": 0.7344434857368469, "detection_id": "86-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.365086+00	2025-11-05 18:39:58.397446+00	2025-11-05 18:39:58.397454+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
7746f143-5860-4cb1-aac0-4d9b6b101a07	INF-RED-133958-44	red_light	medium	\N	\N		0	\N	\N			{"bbox": [28.627986907958984, 88.24246215820312, 50.490970611572266, 105.31124877929688], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.355579", "confidence": 0.5988270044326782, "detection_id": "86-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.365361+00	2025-11-05 18:39:58.434419+00	2025-11-05 18:39:58.434427+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b41b0b7b-cb46-4d28-8fc3-93e48ccea32f	INF-SPE-133958-58	speed	medium	\N	\N		0	87.2	60			{"bbox": [86.71633911132812, 84.94410705566406, 114.29441833496094, 102.84922790527344], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.356507", "confidence": 0.5451577305793762, "detection_id": "86-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.365644+00	2025-11-05 18:39:58.490305+00	2025-11-05 18:39:58.490317+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3f228055-a72a-4d66-9d8e-83a5e92975da	INF-RED-133958-29	red_light	medium	\N	\N		0	\N	\N			{"bbox": [125.67098999023438, 88.33531188964844, 140.393798828125, 97.89103698730469], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.357472", "confidence": 0.42465853691101074, "detection_id": "86-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.365988+00	2025-11-05 18:39:58.545856+00	2025-11-05 18:39:58.545868+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
b7602e93-a506-45ae-b173-1b4478509d8e	INF-RED-133958-24	red_light	medium	\N	\N		0	\N	\N			{"bbox": [59.576053619384766, 87.11607360839844, 78.39566040039062, 104.15867614746094], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.358481", "confidence": 0.3866502344608307, "detection_id": "86-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.36629+00	2025-11-05 18:39:58.599856+00	2025-11-05 18:39:58.599866+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
ba54a6be-dcb2-4852-98ca-4fc517665242	INF-RED-133958-58	red_light	medium	\N	\N		0	\N	\N			{"bbox": [153.40170288085938, 87.82574462890625, 167.73226928710938, 96.96270751953125], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.359598", "confidence": 0.34265628457069397, "detection_id": "86-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.366572+00	2025-11-05 18:39:58.668101+00	2025-11-05 18:39:58.668107+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
51e06336-5f97-419f-a141-25426b7bc086	INF-RED-133958-49	red_light	medium	\N	\N		0	\N	\N			{"bbox": [29.20513916015625, 88.26383972167969, 61.33385467529297, 106.36672973632812], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.626907", "confidence": 0.755579948425293, "detection_id": "88-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.638026+00	2025-11-05 18:39:58.673775+00	2025-11-05 18:39:58.673781+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
246210b0-bb7c-4ff4-986e-d30bdca910f3	INF-RED-133958-72	red_light	medium	\N	\N		0	\N	\N			{"bbox": [122.49790954589844, 89.14898681640625, 135.9192657470703, 98.802978515625], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.628280", "confidence": 0.4646205008029938, "detection_id": "88-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.63831+00	2025-11-05 18:39:58.724575+00	2025-11-05 18:39:58.724582+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
118914a2-3c7e-4c0b-a637-77939ae525ba	INF-RED-133958-10	red_light	medium	\N	\N		0	\N	\N			{"bbox": [250.19155883789062, 94.07945251464844, 264.9306945800781, 111.80125427246094], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.629525", "confidence": 0.3970852196216583, "detection_id": "88-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.638478+00	2025-11-05 18:39:58.812956+00	2025-11-05 18:39:58.812972+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
5395df28-125a-494e-9a5c-4422bc60b3c3	INF-SPE-133958-78	speed	medium	\N	\N		0	87.1	60			{"bbox": [50.37751007080078, 76.5880355834961, 78.92595672607422, 105.12523651123047], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.630435", "confidence": 0.34097251296043396, "detection_id": "88-8", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.638651+00	2025-11-05 18:39:58.870504+00	2025-11-05 18:39:58.870516+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3b7a79a0-0d21-451a-a797-30f8970d0073	INF-RED-133958-83	red_light	medium	\N	\N		0	\N	\N			{"bbox": [58.84455871582031, 87.95486450195312, 78.62727355957031, 105.5185546875], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.631531", "confidence": 0.323747843503952, "detection_id": "88-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.638873+00	2025-11-05 18:39:58.94933+00	2025-11-05 18:39:58.949337+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
51274359-90a2-4676-80fc-df4ded3aa5d7	INF-RED-133959-26	red_light	medium	\N	\N		0	\N	\N			{"bbox": [120.25422668457031, 90.424560546875, 139.09083557128906, 103.5484619140625], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.900991", "confidence": 0.5725100040435791, "detection_id": "90-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.910921+00	2025-11-05 18:39:59.08211+00	2025-11-05 18:39:59.082126+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
d1fe1c3a-6c23-445e-9790-7072d54c417b	INF-RED-133959-64	red_light	medium	\N	\N		0	\N	\N			{"bbox": [59.9783935546875, 88.88752746582031, 80.28375244140625, 106.23396301269531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.901914", "confidence": 0.3010527491569519, "detection_id": "90-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.911503+00	2025-11-05 18:39:59.145302+00	2025-11-05 18:39:59.145315+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
962e4861-8d84-40d5-b018-4a41a3ab233c	INF-RED-133959-60	red_light	medium	\N	\N		0	\N	\N			{"bbox": [50.17420959472656, 77.54299926757812, 80.38714599609375, 106.0146484375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.903003", "confidence": 0.26806989312171936, "detection_id": "90-8", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.911841+00	2025-11-05 18:39:59.205477+00	2025-11-05 18:39:59.20549+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9c7bbb27-133f-49df-8342-dc310499717e	INF-SPE-133959-71	speed	medium	\N	\N		0	78.7	60			{"bbox": [254.18368530273438, 95.45478820800781, 264.0881042480469, 111.52500915527344], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.904095", "confidence": 0.2461455762386322, "detection_id": "90-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.91221+00	2025-11-05 18:39:59.266492+00	2025-11-05 18:39:59.266498+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
06fd79bb-2a71-4176-90d3-471cf1daf15c	INF-RED-133959-46	red_light	medium	\N	\N		0	\N	\N			{"bbox": [115.92681884765625, 90.24725341796875, 138.54257202148438, 103.00592041015625], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.262849", "confidence": 0.6408722996711731, "detection_id": "92-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.271556+00	2025-11-05 18:39:59.308766+00	2025-11-05 18:39:59.308773+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
967f9e29-d39f-4356-9166-16cebca5e8fb	INF-RED-133959-61	red_light	medium	\N	\N		0	\N	\N			{"bbox": [50.14671325683594, 77.63976287841797, 80.27838134765625, 106.08342742919922], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.905259", "confidence": 0.20365527272224426, "detection_id": "90-11", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.91256+00	2025-11-05 18:39:59.312363+00	2025-11-05 18:39:59.312369+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1de90d0a-09bd-43b0-b78a-72cb3ef87fa2	INF-SPE-133959-57	speed	medium	\N	\N		0	90.8	60			{"bbox": [29.789043426513672, 89.57746887207031, 50.46560287475586, 108.29914855957031], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.264108", "confidence": 0.6221299767494202, "detection_id": "92-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.271872+00	2025-11-05 18:39:59.364306+00	2025-11-05 18:39:59.364317+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
fe253cfa-9a42-4249-b58a-550328468d78	INF-SPE-133959-18	speed	medium	\N	\N		0	73.5	60			{"bbox": [86.03248596191406, 88.42779541015625, 111.45127868652344, 105.83749389648438], "source": "webcam_local", "timestamp": "2025-11-05T18:39:58.906060", "confidence": 0.20286837220191956, "detection_id": "90-12", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:58.912854+00	2025-11-05 18:39:59.365833+00	2025-11-05 18:39:59.365844+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
90a3c77e-a81c-4b43-b599-5717687688ae	INF-RED-133959-68	red_light	medium	\N	\N		0	\N	\N			{"bbox": [63.00830841064453, 88.26251220703125, 79.74347686767578, 106.65565490722656], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.265263", "confidence": 0.3098756670951843, "detection_id": "92-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.272129+00	2025-11-05 18:39:59.420692+00	2025-11-05 18:39:59.4207+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a9b20849-4857-43d8-bfdf-655073c3f643	INF-RED-133959-59	red_light	medium	\N	\N		0	\N	\N			{"bbox": [47.87620544433594, 77.41896057128906, 80.2034912109375, 106.58992004394531], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.266150", "confidence": 0.23658239841461182, "detection_id": "92-9", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.272333+00	2025-11-05 18:39:59.461953+00	2025-11-05 18:39:59.461964+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
a1ca7ed5-12e1-4139-9333-4621dbc25f93	INF-SPE-133959-53	speed	medium	\N	\N		0	96.8	60			{"bbox": [47.83705139160156, 77.48217010498047, 79.94552612304688, 106.45032501220703], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.266842", "confidence": 0.22748012840747833, "detection_id": "92-10", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.272686+00	2025-11-05 18:39:59.519754+00	2025-11-05 18:39:59.519762+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
1a84fecd-284d-48f4-ab60-5f2b0de4faa5	INF-RED-133959-78	red_light	medium	\N	\N		0	\N	\N			{"bbox": [28.69435691833496, 89.18016052246094, 50.76953887939453, 107.78030395507812], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.486189", "confidence": 0.5339058041572571, "detection_id": "94-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.491547+00	2025-11-05 18:39:59.521479+00	2025-11-05 18:39:59.521488+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
538fcca2-db58-4e6e-a9bc-d3a425333fea	INF-RED-133959-54	red_light	medium	\N	\N		0	\N	\N			{"bbox": [111.153076171875, 90.65316772460938, 128.7412109375, 102.99098205566406], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.487023", "confidence": 0.34937113523483276, "detection_id": "94-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.491774+00	2025-11-05 18:39:59.563139+00	2025-11-05 18:39:59.563155+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
175580b5-77f0-4baf-be5f-5d919054ca4a	INF-RED-133959-47	red_light	medium	\N	\N		0	\N	\N			{"bbox": [44.295135498046875, 76.77055358886719, 79.68356323242188, 106.1781005859375], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.487656", "confidence": 0.3260963261127472, "detection_id": "94-6", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.492062+00	2025-11-05 18:39:59.637465+00	2025-11-05 18:39:59.637476+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
768b8079-d59a-4fb5-8a16-0512703410db	INF-RED-133959-22	red_light	medium	\N	\N		0	\N	\N			{"bbox": [63.27485275268555, 88.1401138305664, 79.22636413574219, 106.5005874633789], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.488277", "confidence": 0.21666203439235687, "detection_id": "94-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.49225+00	2025-11-05 18:39:59.688475+00	2025-11-05 18:39:59.688485+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
9fde9d15-7151-4040-afa3-c99ba5403097	INF-SPE-133959-68	speed	medium	\N	\N		0	71.4	60			{"bbox": [0.02940082550048828, 131.66525268554688, 11.089418411254883, 179.29910278320312], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.713231", "confidence": 0.5283059477806091, "detection_id": "96-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.71994+00	2025-11-05 18:39:59.944571+00	2025-11-05 18:39:59.944578+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
3eb16354-ff13-457a-a0bb-869d8077f427	INF-RED-133959-77	red_light	medium	\N	\N		0	\N	\N			{"bbox": [84.69515991210938, 86.64491271972656, 107.6119384765625, 109.90115356445312], "source": "webcam_local", "timestamp": "2025-11-05T18:39:59.713780", "confidence": 0.3070771396160126, "detection_id": "96-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-05 23:39:59.720207+00	2025-11-05 18:39:59.980411+00	2025-11-05 18:39:59.980419+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	\N
63cb13d1-2d28-446b-a5f5-716a7f54eb5f	INF-SPE-145725-73	speed	medium	\N	\N		0	82.5	60			{"bbox": [12.267486572265625, 92.17376708984375, 44.5744743347168, 110.72486877441406], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.094415", "confidence": 0.5992732644081116, "detection_id": "100-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.099389+00	2025-11-05 19:57:25.127288+00	2025-11-05 19:57:25.127295+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.092
bcd758d9-b758-4b0b-a119-4578dd4ec0f5	INF-SPE-145725-36	speed	medium	\N	\N		0	75.5	60			{"bbox": [225.7462158203125, 97.42800903320312, 246.4814453125, 113.08805847167969], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.192547", "confidence": 0.5272951126098633, "detection_id": "102-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.198518+00	2025-11-05 19:57:25.223332+00	2025-11-05 19:57:25.223338+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.054
f0f6cb8a-305b-4218-b0b8-ea0be3c0b6bd	INF-SPE-145725-25	speed	medium	\N	\N		0	96.6	60			{"bbox": [12.682403564453125, 92.46843719482422, 44.956695556640625, 111.5331802368164], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.194235", "confidence": 0.2059628814458847, "detection_id": "102-6", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.19903+00	2025-11-05 19:57:25.273846+00	2025-11-05 19:57:25.273869+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.054
481384a7-2cf4-44da-985d-9212e2bb305d	INF-SPE-145725-15	speed	medium	\N	\N		0	81.7	60			{"bbox": [60.49485778808594, 95.71102905273438, 129.7229461669922, 148.96450805664062], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.299327", "confidence": 0.7685292959213257, "detection_id": "104-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.307421+00	2025-11-05 19:57:25.332552+00	2025-11-05 19:57:25.332558+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.071
ab5abed8-77ef-4e14-8174-fcaeb309326f	INF-SPE-145725-53	speed	medium	\N	\N		0	73.4	60			{"bbox": [12.78567886352539, 91.50308990478516, 45.80657196044922, 110.31305694580078], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.300822", "confidence": 0.45686575770378113, "detection_id": "104-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.307931+00	2025-11-05 19:57:25.371632+00	2025-11-05 19:57:25.371682+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.071
6a0433cc-6d37-40f4-bfe8-7570b0b268fe	INF-SPE-145725-46	speed	medium	\N	\N		0	81.4	60			{"bbox": [240.36851501464844, 98.97467041015625, 248.3509063720703, 109.84536743164062], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.302653", "confidence": 0.2103777825832367, "detection_id": "104-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.308288+00	2025-11-05 19:57:25.430263+00	2025-11-05 19:57:25.43027+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.071
5ff0c9a0-a1b0-46ae-9073-d545bc5ce67d	INF-SPE-145725-22	speed	medium	\N	\N		0	96.4	60			{"bbox": [13.427928924560547, 91.22126770019531, 45.9911003112793, 110.31837463378906], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.427229", "confidence": 0.764127254486084, "detection_id": "106-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.433259+00	2025-11-05 19:57:25.460625+00	2025-11-05 19:57:25.46063+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.081
7c83654a-1e69-444e-89e8-3e94c5c7f1b1	INF-SPE-145725-74	speed	medium	\N	\N		0	84	60			{"bbox": [68.92112731933594, 95.45449829101562, 128.3501434326172, 142.95411682128906], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.546199", "confidence": 0.901921808719635, "detection_id": "108-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.556572+00	2025-11-05 19:57:25.583045+00	2025-11-05 19:57:25.583052+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
92d2faf4-f565-4e09-bac9-5c2905fb95df	INF-SPE-145725-61	speed	medium	\N	\N		0	92.8	60			{"bbox": [251.87716674804688, 87.44320678710938, 262.7386169433594, 109.53155517578125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.662686", "confidence": 0.2657277584075928, "detection_id": "110-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.668188+00	2025-11-05 19:57:25.69437+00	2025-11-05 19:57:25.694377+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
54c74f4a-5296-43c4-abcf-0e727734320a	INF-SPE-145725-96	speed	medium	\N	\N		0	80.9	60			{"bbox": [13.628494262695312, 85.90837097167969, 46.31625747680664, 105.52879333496094], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.767821", "confidence": 0.7591909170150757, "detection_id": "112-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.775217+00	2025-11-05 19:57:25.800051+00	2025-11-05 19:57:25.800057+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.072
a346dd2a-537b-4f41-95fa-94d8743ed5da	INF-SPE-145725-14	speed	medium	\N	\N		0	91.6	60			{"bbox": [81.83636474609375, 79.69084167480469, 114.00990295410156, 94.43504333496094], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.770971", "confidence": 0.2060137540102005, "detection_id": "112-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.775536+00	2025-11-05 19:57:25.843138+00	2025-11-05 19:57:25.843226+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.072
1ccde94a-d0c8-4891-846f-b89b1fd5b694	INF-WRO-145725-29	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [69.90481567382812, 92.88368225097656, 124.1815185546875, 138.33230590820312], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.884583", "confidence": 0.8074585199356079, "detection_id": "114-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.889792+00	2025-11-05 19:57:25.915203+00	2025-11-05 19:57:25.915208+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.067
d15007a3-d0c6-422d-a3a3-24909a007d43	INF-WRO-145725-87	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [13.138614654541016, 86.34002685546875, 46.110809326171875, 105.54592895507812], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.885533", "confidence": 0.6382140517234802, "detection_id": "114-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.890189+00	2025-11-05 19:57:25.972382+00	2025-11-05 19:57:25.972398+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.067
e77b6d56-1f40-476d-bfb1-9e6790c6b410	INF-SPE-145726-93	speed	medium	\N	\N		0	99.8	60			{"bbox": [67.05133819580078, 92.07815551757812, 122.7676010131836, 137.97222900390625], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.992383", "confidence": 0.7292339205741882, "detection_id": "116-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:25.999781+00	2025-11-05 19:57:26.024378+00	2025-11-05 19:57:26.024385+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.069
92c7c021-c3ff-40e6-9bd8-8b0f99d21d59	INF-SPE-145726-50	speed	medium	\N	\N		0	86.3	60			{"bbox": [232.95181274414062, 92.07744598388672, 251.40338134765625, 105.21862030029297], "source": "webcam_local", "timestamp": "2025-11-05T19:57:25.994933", "confidence": 0.36598074436187744, "detection_id": "116-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.000415+00	2025-11-05 19:57:26.059511+00	2025-11-05 19:57:26.059521+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.069
bcb0eed3-dbd6-4d41-a51b-adbf7856ceb1	INF-SPE-145726-10	speed	medium	\N	\N		0	96.3	60			{"bbox": [13.508373260498047, 85.98991394042969, 45.833351135253906, 105.077880859375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.094266", "confidence": 0.6936986446380615, "detection_id": "118-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.101962+00	2025-11-05 19:57:26.127954+00	2025-11-05 19:57:26.12796+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
bc2a997d-fda0-42a6-8138-08a5fe17042a	INF-SPE-145726-55	speed	medium	\N	\N		0	80.6	60			{"bbox": [234.56204223632812, 92.37893676757812, 252.16073608398438, 104.78861999511719], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.095430", "confidence": 0.2759472727775574, "detection_id": "118-5", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.102375+00	2025-11-05 19:57:26.16267+00	2025-11-05 19:57:26.162677+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
b9a062ab-5553-414e-885f-82a326703422	INF-SPE-145726-85	speed	medium	\N	\N		0	77.2	60			{"bbox": [79.41879272460938, 79.81134033203125, 109.14279174804688, 94.33758544921875], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.097043", "confidence": 0.21399571001529694, "detection_id": "118-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.102738+00	2025-11-05 19:57:26.203395+00	2025-11-05 19:57:26.203402+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
378f8306-e63b-4c18-b104-bfe8652c1eaa	INF-SPE-145726-35	speed	medium	\N	\N		0	72.7	60			{"bbox": [61.335227966308594, 92.4459228515625, 122.00760650634766, 135.98377990722656], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.197645", "confidence": 0.8325397968292236, "detection_id": "120-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.202524+00	2025-11-05 19:57:26.23124+00	2025-11-05 19:57:26.231246+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.057
bffe3e9d-8270-45ac-a6bb-ad67281f48d7	INF-SPE-145726-91	speed	medium	\N	\N		0	70.9	60			{"bbox": [235.4730224609375, 93.46458435058594, 253.00994873046875, 105.03865051269531], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.297387", "confidence": 0.517058789730072, "detection_id": "122-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.30343+00	2025-11-05 19:57:26.330673+00	2025-11-05 19:57:26.330679+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.058
a8a47b7d-8c51-4706-9cab-a60cf3284fd3	INF-SPE-145726-43	speed	medium	\N	\N		0	96.9	60			{"bbox": [13.10721206665039, 86.25616455078125, 44.90083312988281, 105.62130737304688], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.409526", "confidence": 0.6859781742095947, "detection_id": "124-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.418456+00	2025-11-05 19:57:26.443351+00	2025-11-05 19:57:26.443358+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.067
cb6f10e8-8039-4e5f-93ad-ef3071953dda	INF-SPE-145726-24	speed	medium	\N	\N		0	86	60			{"bbox": [51.45983123779297, 86.11408996582031, 64.21021270751953, 104.21946716308594], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.411747", "confidence": 0.2703130841255188, "detection_id": "124-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.418814+00	2025-11-05 19:57:26.496257+00	2025-11-05 19:57:26.496265+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.067
eb7b7e7c-c177-4896-ab4c-bf4923f311e3	INF-SPE-145726-41	speed	medium	\N	\N		0	75.4	60			{"bbox": [47.700382232666016, 92.21180725097656, 114.7435302734375, 134.0607452392578], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.519113", "confidence": 0.8653750419616699, "detection_id": "126-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.524585+00	2025-11-05 19:57:26.548273+00	2025-11-05 19:57:26.54828+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
4e382f46-2986-4dc2-9371-71abdbb77220	INF-SPE-145726-34	speed	medium	\N	\N		0	81.3	60			{"bbox": [12.23236083984375, 87.58529663085938, 32.086822509765625, 105.52798461914062], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.520997", "confidence": 0.24124203622341156, "detection_id": "126-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.524879+00	2025-11-05 19:57:26.59357+00	2025-11-05 19:57:26.59358+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
a0e4f49d-56a3-4e75-ba8c-fd7e6ca526bc	INF-SPE-145726-23	speed	medium	\N	\N		0	73.7	60			{"bbox": [236.41311645507812, 90.62193298339844, 252.38552856445312, 102.60929870605469], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.626948", "confidence": 0.37620800733566284, "detection_id": "128-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.631436+00	2025-11-05 19:57:26.65597+00	2025-11-05 19:57:26.655978+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.062
378f05a1-de52-4bbf-b8f6-4457795d816a	INF-SPE-145726-26	speed	medium	\N	\N		0	73.7	60			{"bbox": [11.492420196533203, 84.82508850097656, 48.56099319458008, 104.71675109863281], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.728616", "confidence": 0.4886355698108673, "detection_id": "130-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.735871+00	2025-11-05 19:57:26.759575+00	2025-11-05 19:57:26.759582+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.066
0e3830a1-b348-42b5-9c07-2e32a986289d	INF-SPE-145726-15	speed	medium	\N	\N		0	87.6	60			{"bbox": [35.214744567871094, 89.00080871582031, 107.77169036865234, 130.0061492919922], "source": "webcam_local", "timestamp": "2025-11-05T19:57:26.821420", "confidence": 0.9190796613693237, "detection_id": "132-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:26.829029+00	2025-11-05 19:57:26.853944+00	2025-11-05 19:57:26.853949+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.057
419ba8cb-1068-4036-bf35-6236f284f7d5	INF-SPE-145727-94	speed	medium	\N	\N		0	97.2	60			{"bbox": [0.09497833251953125, 90.86306762695312, 98.55779266357422, 166.4227294921875], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.140877", "confidence": 0.9052637219429016, "detection_id": "138-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.147956+00	2025-11-05 19:57:27.184195+00	2025-11-05 19:57:27.184201+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.057
6be1d260-7126-4866-9972-20f07cf9d27b	INF-SPE-145727-66	speed	medium	\N	\N		0	70.4	60			{"bbox": [241.11907958984375, 87.18058776855469, 260.1072998046875, 98.45616149902344], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.143467", "confidence": 0.5896000862121582, "detection_id": "138-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.148652+00	2025-11-05 19:57:27.229453+00	2025-11-05 19:57:27.22947+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.057
5e488b1a-3ed5-4597-880a-59d7fbc0df8e	INF-SPE-145727-55	speed	medium	\N	\N		0	99.5	60			{"bbox": [16.706613540649414, 81.15086364746094, 55.72924041748047, 93.21820068359375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.354832", "confidence": 0.23068538308143616, "detection_id": "142-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.360605+00	2025-11-05 19:57:27.390165+00	2025-11-05 19:57:27.390173+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
6aa33447-cb67-4d8a-a47a-70ea0cc132d9	INF-SPE-145727-33	speed	medium	\N	\N		0	91.6	60			{"bbox": [13.606826782226562, 89.17790222167969, 119.0, 155.55873107910156], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.460312", "confidence": 0.9020023345947266, "detection_id": "144-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.4668+00	2025-11-05 19:57:27.498762+00	2025-11-05 19:57:27.498769+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.064
26c4cce3-6efb-4daf-b57f-edab7aa1cde7	INF-SPE-145727-11	speed	medium	\N	\N		0	83.6	60			{"bbox": [245.82846069335938, 85.72633361816406, 258.7140197753906, 96.60954284667969], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.567276", "confidence": 0.4537173807621002, "detection_id": "146-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.57379+00	2025-11-05 19:57:27.598996+00	2025-11-05 19:57:27.599003+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.062
e6cff1af-dcc6-47a9-b250-22b7f93e66ac	INF-SPE-145727-62	speed	medium	\N	\N		0	99.6	60			{"bbox": [17.27758026123047, 83.48750305175781, 48.625221252441406, 120.07273864746094], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.679480", "confidence": 0.5957469344139099, "detection_id": "148-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.686875+00	2025-11-05 19:57:27.710892+00	2025-11-05 19:57:27.710897+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.074
944cd394-68f1-4028-ad4c-15f558f1743c	INF-SPE-145727-93	speed	medium	\N	\N		0	96.6	60			{"bbox": [49.210975646972656, 71.84799194335938, 68.40373229980469, 83.45425415039062], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.682424", "confidence": 0.20971885323524475, "detection_id": "148-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.687138+00	2025-11-05 19:57:27.756686+00	2025-11-05 19:57:27.756694+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.074
178ba3fa-4a2b-4914-bb00-66b48aa3e065	INF-SPE-145727-16	speed	medium	\N	\N		0	92.3	60			{"bbox": [17.886098861694336, 82.66093444824219, 60.92229461669922, 121.37898254394531], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.783980", "confidence": 0.5013061165809631, "detection_id": "150-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.788448+00	2025-11-05 19:57:27.814923+00	2025-11-05 19:57:27.814931+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.058
e550562e-d20a-4fff-b2fe-d6bc307ad170	INF-SPE-145727-39	speed	medium	\N	\N		0	83.7	60			{"bbox": [18.8909854888916, 83.69406127929688, 64.0582046508789, 121.98330688476562], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.891860", "confidence": 0.3786293864250183, "detection_id": "152-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:27.896322+00	2025-11-05 19:57:27.923316+00	2025-11-05 19:57:27.923323+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.056
9abd63b9-ce68-4c4b-be25-5aae1c4f4b85	INF-SPE-145728-14	speed	medium	\N	\N		0	73.4	60			{"bbox": [18.248735427856445, 84.35147094726562, 60.33247375488281, 123.95343017578125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.993456", "confidence": 0.7808601260185242, "detection_id": "154-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.001473+00	2025-11-05 19:57:28.027067+00	2025-11-05 19:57:28.027072+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.053
d1ad5310-68a7-4c68-a251-f41eb854ee6f	INF-SPE-145728-71	speed	medium	\N	\N		0	84.7	60			{"bbox": [249.05328369140625, 89.6362075805664, 266.19873046875, 99.52454376220703], "source": "webcam_local", "timestamp": "2025-11-05T19:57:27.995774", "confidence": 0.3114910423755646, "detection_id": "154-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.002091+00	2025-11-05 19:57:28.076652+00	2025-11-05 19:57:28.076663+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.053
75c75107-b40c-446e-831d-780dfa818d58	INF-SPE-145728-31	speed	medium	\N	\N		0	86.1	60			{"bbox": [65.57046508789062, 95.58828735351562, 132.7163543701172, 148.74490356445312], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.101589", "confidence": 0.9223209023475647, "detection_id": "156-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.106632+00	2025-11-05 19:57:28.130816+00	2025-11-05 19:57:28.130821+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.05
4c81d4f5-e4f6-4954-a949-724c1396b043	INF-SPE-145728-88	speed	medium	\N	\N		0	84.4	60			{"bbox": [17.766563415527344, 90.79824829101562, 48.77892303466797, 128.76193237304688], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.202641", "confidence": 0.46014150977134705, "detection_id": "158-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.212187+00	2025-11-05 19:57:28.237607+00	2025-11-05 19:57:28.237613+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.061
66f35d94-6f2a-43b1-9ab7-ca94fb16ad00	INF-SPE-145728-91	speed	medium	\N	\N		0	99.9	60			{"bbox": [54.82610321044922, 99.08572387695312, 65.20331573486328, 106.13697814941406], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.204804", "confidence": 0.242581307888031, "detection_id": "158-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.212567+00	2025-11-05 19:57:28.291717+00	2025-11-05 19:57:28.291728+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.061
590cc7e1-64bf-4133-9b2e-3ef4197af39c	INF-SPE-145728-48	speed	medium	\N	\N		0	73.5	60			{"bbox": [47.18922424316406, 97.34757995605469, 62.659576416015625, 105.14030456542969], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.321418", "confidence": 0.20923684537410736, "detection_id": "160-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.325251+00	2025-11-05 19:57:28.348325+00	2025-11-05 19:57:28.348332+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.076
bc97f667-91cf-4333-8a70-b42225324c4d	INF-SPE-145728-83	speed	medium	\N	\N		0	70.7	60			{"bbox": [0.084259033203125, 104.82323455810547, 64.08032989501953, 179.417236328125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.430944", "confidence": 0.904335618019104, "detection_id": "162-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.440021+00	2025-11-05 19:57:28.46423+00	2025-11-05 19:57:28.464237+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.062
d06bc1b9-0ace-4880-a25b-00fa583d9f7f	INF-WRO-145728-61	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [0.048675537109375, 102.1470718383789, 75.74397277832031, 179.23794555664062], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.545724", "confidence": 0.8962475061416626, "detection_id": "164-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.552699+00	2025-11-05 19:57:28.592879+00	2025-11-05 19:57:28.592892+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.078
4e8572f1-bf22-45cc-aca4-c1f553fa76fa	INF-SPE-145728-61	speed	medium	\N	\N		0	71.8	60			{"bbox": [74.50250244140625, 95.8804931640625, 129.21096801757812, 143.2425994873047], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.546682", "confidence": 0.8934465646743774, "detection_id": "164-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.553464+00	2025-11-05 19:57:28.655395+00	2025-11-05 19:57:28.655404+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.078
ed150a14-2e01-47e3-824b-8369bc8bf119	INF-WRO-145728-77	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [19.325271606445312, 90.00162506103516, 49.50465393066406, 108.75353240966797], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.547804", "confidence": 0.6636852025985718, "detection_id": "164-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.554176+00	2025-11-05 19:57:28.70355+00	2025-11-05 19:57:28.703556+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.078
9072212d-7cb1-412c-b3e3-62e38782d026	INF-SPE-145728-60	speed	medium	\N	\N		0	71.7	60			{"bbox": [72.07467651367188, 95.5989990234375, 128.0475311279297, 142.57521057128906], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.657207", "confidence": 0.8600189685821533, "detection_id": "166-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.662924+00	2025-11-05 19:57:28.704849+00	2025-11-05 19:57:28.704856+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.069
9752cf6d-62bf-40ca-9693-db09cda227a5	INF-SPE-145728-55	speed	medium	\N	\N		0	82.9	60			{"bbox": [18.026365280151367, 90.60592651367188, 53.152099609375, 106.44979858398438], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.658542", "confidence": 0.27564167976379395, "detection_id": "166-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.663174+00	2025-11-05 19:57:28.75059+00	2025-11-05 19:57:28.750599+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.069
6e68991f-f885-408a-b4d7-d16b9aa5f8fa	INF-SPE-145728-10	speed	medium	\N	\N		0	97.4	60			{"bbox": [0.06903076171875, 99.43809509277344, 96.09968566894531, 172.49134826660156], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.765687", "confidence": 0.899042546749115, "detection_id": "168-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.773898+00	2025-11-05 19:57:28.798272+00	2025-11-05 19:57:28.798278+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.063
36e0b051-bc93-40aa-a8c8-b00b77891827	INF-WRO-145728-31	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [72.37379455566406, 95.26057434082031, 125.15049743652344, 139.60826110839844], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.767087", "confidence": 0.8809398412704468, "detection_id": "168-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.774222+00	2025-11-05 19:57:28.832174+00	2025-11-05 19:57:28.832185+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.063
f0e4dd14-ed3a-420a-af0b-829bf80c2013	INF-WRO-145728-88	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [27.88055419921875, 78.82351684570312, 68.93582153320312, 106.94403076171875], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.769487", "confidence": 0.20203469693660736, "detection_id": "168-7", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.774527+00	2025-11-05 19:57:28.875416+00	2025-11-05 19:57:28.875422+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.063
92a74328-f2a1-4d04-9030-c1fdacc69ed4	INF-SPE-145728-17	speed	medium	\N	\N		0	76.4	60			{"bbox": [73.66485595703125, 93.18710327148438, 122.75407409667969, 137.06593322753906], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.872497", "confidence": 0.8458296656608582, "detection_id": "170-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.876479+00	2025-11-05 19:57:28.90556+00	2025-11-05 19:57:28.905567+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.057
48bfc96d-d52c-4d27-b85d-051f5c49017e	INF-SPE-145729-59	speed	medium	\N	\N		0	90.6	60			{"bbox": [0.39342498779296875, 99.61357116699219, 109.22653198242188, 166.15208435058594], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.989783", "confidence": 0.8367231488227844, "detection_id": "172-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.99785+00	2025-11-05 19:57:29.022113+00	2025-11-05 19:57:29.02212+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.067
11d5a067-8715-470a-9ca9-513787b93ceb	INF-SPE-145729-40	speed	medium	\N	\N		0	80.3	60			{"bbox": [252.63818359375, 94.34605407714844, 264.507568359375, 103.35134887695312], "source": "webcam_local", "timestamp": "2025-11-05T19:57:28.992369", "confidence": 0.32660409808158875, "detection_id": "172-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:28.998159+00	2025-11-05 19:57:29.064391+00	2025-11-05 19:57:29.064403+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.067
c2f1ace8-0678-4a88-9e79-412ffaaf269c	INF-SPE-145729-56	speed	medium	\N	\N		0	90.3	60			{"bbox": [15.298748016357422, 99.63348388671875, 115.97886657714844, 162.20394897460938], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.101532", "confidence": 0.8781191110610962, "detection_id": "174-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.111227+00	2025-11-05 19:57:29.134731+00	2025-11-05 19:57:29.134736+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.07
8ad641a3-12a1-4e50-ab5f-463d026ae646	INF-SPE-145729-28	speed	medium	\N	\N		0	87.9	60			{"bbox": [22.3529052734375, 78.70689392089844, 68.33828735351562, 106.75843811035156], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.105709", "confidence": 0.3799039125442505, "detection_id": "174-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.11156+00	2025-11-05 19:57:29.180935+00	2025-11-05 19:57:29.180948+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.07
e5fbd7d5-22bf-4e4d-9736-85e304d00b0b	INF-SPE-145729-65	speed	medium	\N	\N		0	98.1	60			{"bbox": [62.904815673828125, 92.89817810058594, 113.60009765625, 118.83973693847656], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.211432", "confidence": 0.5388062596321106, "detection_id": "176-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.217499+00	2025-11-05 19:57:29.242716+00	2025-11-05 19:57:29.242723+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
72a5271b-5d39-4359-a449-50b51538e9ad	INF-SPE-145729-25	speed	medium	\N	\N		0	80.5	60			{"bbox": [22.88379669189453, 77.72406005859375, 48.53364562988281, 106.81748962402344], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.212864", "confidence": 0.38628676533699036, "detection_id": "176-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.217798+00	2025-11-05 19:57:29.283504+00	2025-11-05 19:57:29.283515+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
67891d4f-20bc-4e30-898f-08eed36178f9	INF-SPE-145729-72	speed	medium	\N	\N		0	97.7	60			{"bbox": [38.23899841308594, 96.78960418701172, 123.85011291503906, 156.01861572265625], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.312639", "confidence": 0.7628746628761292, "detection_id": "178-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.320954+00	2025-11-05 19:57:29.346494+00	2025-11-05 19:57:29.3465+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
0428cc91-8420-468c-9960-e35eb06478f1	INF-SPE-145729-34	speed	medium	\N	\N		0	79.3	60			{"bbox": [23.630319595336914, 78.05632019042969, 65.9577407836914, 106.31538391113281], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.315122", "confidence": 0.3897855579853058, "detection_id": "178-5", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.321299+00	2025-11-05 19:57:29.3834+00	2025-11-05 19:57:29.383412+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
d956797a-bb3e-4109-ac14-a7d02fddc912	INF-SPE-145729-64	speed	medium	\N	\N		0	73.1	60			{"bbox": [0.38423919677734375, 111.65165710449219, 120.2232894897461, 178.84352111816406], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.420477", "confidence": 0.928164541721344, "detection_id": "180-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.431669+00	2025-11-05 19:57:29.457282+00	2025-11-05 19:57:29.457287+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.06
a20404f0-f746-4fed-b90c-88e30043bd6d	INF-WRO-145729-66	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [48.112003326416016, 97.4081039428711, 127.38180541992188, 147.98672485351562], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.421799", "confidence": 0.8255016803741455, "detection_id": "180-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.432004+00	2025-11-05 19:57:29.49406+00	2025-11-05 19:57:29.494072+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.06
548f1dc0-080d-472e-a545-46b30c0e7bf5	INF-SPE-145729-30	speed	medium	\N	\N		0	91.8	60			{"bbox": [19.424440383911133, 76.72647094726562, 65.49127197265625, 105.71623229980469], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.423066", "confidence": 0.25203433632850647, "detection_id": "180-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.432378+00	2025-11-05 19:57:29.54825+00	2025-11-05 19:57:29.548257+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.06
fbff0b61-113e-4c3c-8114-c8c563a50628	INF-WRO-145729-45	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [21.592025756835938, 76.58097839355469, 65.63680267333984, 105.84506225585938], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.424771", "confidence": 0.2381988763809204, "detection_id": "180-7", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.432659+00	2025-11-05 19:57:29.586169+00	2025-11-05 19:57:29.586175+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.06
fbebf03b-c4a2-4d8c-83e6-7a6131438daa	INF-SPE-145729-12	speed	medium	\N	\N		0	95.3	60			{"bbox": [26.458362579345703, 89.66482543945312, 49.30204391479492, 105.78904724121094], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.425925", "confidence": 0.23166826367378235, "detection_id": "180-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.432898+00	2025-11-05 19:57:29.639438+00	2025-11-05 19:57:29.639449+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.06
165dd092-43d4-41d5-b02e-381dcb5d5fbb	INF-SPE-145729-46	speed	medium	\N	\N		0	72.4	60			{"bbox": [18.194595336914062, 76.12570190429688, 67.19369506835938, 105.45541381835938], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.649153", "confidence": 0.2663194239139557, "detection_id": "184-5", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.655106+00	2025-11-05 19:57:29.68866+00	2025-11-05 19:57:29.688667+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
d2cc8239-dd4a-4c00-838b-b34ff54190ac	INF-WRO-145729-96	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [21.71752166748047, 76.35425567626953, 65.90117645263672, 105.7112808227539], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.427520", "confidence": 0.20188073813915253, "detection_id": "180-10", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.433144+00	2025-11-05 19:57:29.691685+00	2025-11-05 19:57:29.691691+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.06
25a5e532-5db3-42a3-b3be-82dfdf2937ec	INF-SPE-145729-83	speed	medium	\N	\N		0	74.5	60			{"bbox": [0.0, 104.4268569946289, 153.662353515625, 179.76742553710938], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.753691", "confidence": 0.9361425042152405, "detection_id": "186-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.760766+00	2025-11-05 19:57:29.789951+00	2025-11-05 19:57:29.789957+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.054
3361ff5b-9551-4a3f-ab42-9a5dfe32d568	INF-WRO-145730-82	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [19.62664794921875, 101.0623779296875, 168.83718872070312, 179.814208984375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.978023", "confidence": 0.9141409397125244, "detection_id": "190-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.988229+00	2025-11-05 19:57:30.013635+00	2025-11-05 19:57:30.013642+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.079
12ab52a0-f652-4faa-94bf-e40515f254d9	INF-SPE-145730-66	speed	medium	\N	\N		0	71.9	60			{"bbox": [15.31939697265625, 86.16932678222656, 80.02279663085938, 121.6790771484375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.979208", "confidence": 0.7696257829666138, "detection_id": "190-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.988473+00	2025-11-05 19:57:30.048367+00	2025-11-05 19:57:30.048376+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.079
52b4f00c-2944-4e5d-b223-8183fb539ea5	INF-WRO-145730-60	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [79.30967712402344, 91.27301025390625, 122.10075378417969, 102.57560729980469], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.980348", "confidence": 0.49905407428741455, "detection_id": "190-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.988721+00	2025-11-05 19:57:30.098157+00	2025-11-05 19:57:30.098171+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.079
0e6fc155-fdf1-4041-941e-f990a2300891	INF-WRO-145730-93	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [12.313438415527344, 72.20929718017578, 63.43572235107422, 95.4117660522461], "source": "webcam_local", "timestamp": "2025-11-05T19:57:29.982446", "confidence": 0.26512381434440613, "detection_id": "190-6", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:29.988861+00	2025-11-05 19:57:30.142229+00	2025-11-05 19:57:30.142235+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.079
9f1e1688-6978-499e-91db-f5114ad77edf	INF-SPE-145730-37	speed	medium	\N	\N		0	90.9	60			{"bbox": [42.15631103515625, 100.3094711303711, 177.2730712890625, 179.44161987304688], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.087472", "confidence": 0.9129337668418884, "detection_id": "192-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.093732+00	2025-11-05 19:57:30.143261+00	2025-11-05 19:57:30.143267+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.058
bc536817-b9bc-4110-8c97-8970d8269503	INF-WRO-145730-55	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [72.68405151367188, 104.01605224609375, 189.11422729492188, 178.95504760742188], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.279721", "confidence": 0.9120342135429382, "detection_id": "196-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.287567+00	2025-11-05 19:57:30.313888+00	2025-11-05 19:57:30.313894+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.047
f12d3295-097a-4309-8a10-cd7099ec318e	INF-WRO-145730-74	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [70.9224853515625, 94.67289733886719, 121.4718017578125, 135.53738403320312], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.280911", "confidence": 0.845629870891571, "detection_id": "196-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.287946+00	2025-11-05 19:57:30.373855+00	2025-11-05 19:57:30.373867+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.047
78702f6c-1689-4d8d-891c-7b1a2e7581d4	INF-WRO-145730-45	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [18.917879104614258, 90.70631408691406, 58.02674865722656, 124.48789978027344], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.282064", "confidence": 0.7236368060112, "detection_id": "196-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.288346+00	2025-11-05 19:57:30.414252+00	2025-11-05 19:57:30.414259+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.047
1849b579-9d10-4a17-863d-b812ca3d42c2	INF-SPE-145730-19	speed	medium	\N	\N		0	75.6	60			{"bbox": [80.11607360839844, 104.11317443847656, 191.7060089111328, 178.49989318847656], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.402966", "confidence": 0.8933175206184387, "detection_id": "198-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.407839+00	2025-11-05 19:57:30.433444+00	2025-11-05 19:57:30.43345+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.083
e8d1df63-a1c1-44e1-befd-fdb734372330	INF-WRO-145730-44	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [15.890220642089844, 76.06108093261719, 58.501953125, 99.35014343261719], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.283311", "confidence": 0.21374575793743134, "detection_id": "196-4", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.288826+00	2025-11-05 19:57:30.44792+00	2025-11-05 19:57:30.447927+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.047
39ae171f-bbad-4d52-b582-2d47e95c829e	INF-SPE-145730-87	speed	medium	\N	\N		0	72.2	60			{"bbox": [13.423385620117188, 76.1981201171875, 56.89508819580078, 123.71121215820312], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.404227", "confidence": 0.2909236252307892, "detection_id": "198-3", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.40815+00	2025-11-05 19:57:30.470533+00	2025-11-05 19:57:30.470541+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.083
1ac52a3a-56a3-48cc-8cca-7263072f5691	INF-WRO-145730-12	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [93.53106689453125, 104.32818603515625, 196.43057250976562, 175.0498046875], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.507685", "confidence": 0.8988313674926758, "detection_id": "200-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.517686+00	2025-11-05 19:57:30.544378+00	2025-11-05 19:57:30.544385+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.055
32e9a1ef-c59b-4ed1-b062-2930b9832aa7	INF-WRO-145730-96	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [64.70448303222656, 96.0677490234375, 120.07637023925781, 137.98721313476562], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.509242", "confidence": 0.8120970726013184, "detection_id": "200-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.518107+00	2025-11-05 19:57:30.603397+00	2025-11-05 19:57:30.603409+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.055
c84933bf-412b-4a89-8cc3-144e1ca971b7	INF-WRO-145730-79	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [16.274810791015625, 77.56343078613281, 55.95668029785156, 107.4378662109375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.510607", "confidence": 0.7089410424232483, "detection_id": "200-3", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.518433+00	2025-11-05 19:57:30.656663+00	2025-11-05 19:57:30.656673+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.055
b4167b37-09dc-4a15-8c00-92ad3584f5b0	INF-SPE-145730-22	speed	medium	\N	\N		0	86.3	60			{"bbox": [0.0, 86.34152221679688, 43.41845703125, 124.26446533203125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.511530", "confidence": 0.27321189641952515, "detection_id": "200-4", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.518787+00	2025-11-05 19:57:30.710006+00	2025-11-05 19:57:30.710015+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.055
fe416cd4-7c40-4bd1-b8aa-375c98dd2ec1	INF-WRO-145730-21	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [14.609232902526855, 94.2943115234375, 43.845943450927734, 123.4443359375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.512787", "confidence": 0.22279570996761322, "detection_id": "200-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.519164+00	2025-11-05 19:57:30.755432+00	2025-11-05 19:57:30.755444+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.055
336e2f98-7cd1-492a-872e-0ffeff5b7f14	INF-SPE-145730-65	speed	medium	\N	\N		0	75.7	60			{"bbox": [116.65923309326172, 102.61139678955078, 207.73065185546875, 165.93402099609375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.770965", "confidence": 0.8954905271530151, "detection_id": "204-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.779038+00	2025-11-05 19:57:30.803944+00	2025-11-05 19:57:30.803953+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.062
91cd44ae-816a-412f-9c55-205e7c6813eb	INF-SPE-145730-43	speed	medium	\N	\N		0	85.8	60			{"bbox": [46.832977294921875, 94.06875610351562, 56.621177673339844, 107.20950317382812], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.774675", "confidence": 0.2569141983985901, "detection_id": "204-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.779314+00	2025-11-05 19:57:30.836145+00	2025-11-05 19:57:30.836153+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.062
554397a1-5158-4b71-b8f0-db5e90ae2fe5	INF-SPE-145730-25	speed	medium	\N	\N		0	87.1	60			{"bbox": [24.8314266204834, 88.41302490234375, 41.68146514892578, 106.83074951171875], "source": "webcam_local", "timestamp": "2025-11-05T19:57:30.880318", "confidence": 0.39569100737571716, "detection_id": "206-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:30.884403+00	2025-11-05 19:57:30.907853+00	2025-11-05 19:57:30.907858+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.057
dd84b88e-f9be-4c34-9239-d34bfa507fc5	INF-SPE-145731-28	speed	medium	\N	\N		0	73.6	60			{"bbox": [135.58041381835938, 101.24755096435547, 215.39791870117188, 157.34124755859375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.100402", "confidence": 0.8813372850418091, "detection_id": "210-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:31.10684+00	2025-11-05 19:57:31.132893+00	2025-11-05 19:57:31.132899+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.074
c6f8943c-30e0-4060-a9f3-47653617aceb	INF-WRO-145731-80	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [142.8256072998047, 99.39578247070312, 216.67909240722656, 153.30221557617188], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.206227", "confidence": 0.908046305179596, "detection_id": "212-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:31.218692+00	2025-11-05 19:57:31.247958+00	2025-11-05 19:57:31.247965+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.066
cedf82a3-e8be-4afc-9d5f-45715843c192	INF-SPE-145731-83	speed	medium	\N	\N		0	78.9	60			{"bbox": [30.916584014892578, 92.22653198242188, 102.75642395019531, 129.94415283203125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.208754", "confidence": 0.8731220364570618, "detection_id": "212-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:31.219143+00	2025-11-05 19:57:31.295309+00	2025-11-05 19:57:31.295317+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.066
44a716c6-69e8-4618-8b95-89ed44089869	INF-WRO-145731-70	wrong_lane	medium	\N	\N		0	\N	\N			{"bbox": [23.392807006835938, 87.0779037475586, 50.95381164550781, 105.13994598388672], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.211695", "confidence": 0.42088988423347473, "detection_id": "212-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:31.21982+00	2025-11-05 19:57:31.367746+00	2025-11-05 19:57:31.367755+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.066
8816e739-8e9e-4669-a4f7-6a7168338efd	INF-SPE-145731-91	speed	medium	\N	\N		0	79.3	60			{"bbox": [1.3194656372070312, 73.72779846191406, 49.31719970703125, 98.25730895996094], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.370614", "confidence": 0.30078795552253723, "detection_id": "214-5", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:31.376164+00	2025-11-05 19:57:31.405419+00	2025-11-05 19:57:31.405427+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.103
bbd2dabf-d395-4dea-b427-2e57f7f9ab10	INF-SPE-145731-31	speed	medium	\N	\N		0	72.4	60			{"bbox": [309.90216064453125, 105.46082305908203, 319.87225341796875, 116.07524871826172], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.473950", "confidence": 0.5070239901542664, "detection_id": "216-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:31.480569+00	2025-11-05 19:57:31.607484+00	2025-11-05 19:57:31.60749+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.052
5890c582-4124-4d6a-8e59-815afd519d04	INF-SPE-145731-10	speed	medium	\N	\N		0	79.6	60			{"bbox": [309.7351989746094, 106.0394287109375, 319.8843688964844, 116.6229248046875], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.600596", "confidence": 0.3222458064556122, "detection_id": "218-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:31.605565+00	2025-11-05 19:57:31.635517+00	2025-11-05 19:57:31.635526+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.068
d2fd57e8-e782-4fda-8e23-3a411b09aeca	INF-SPE-145732-70	speed	medium	\N	\N		0	82.8	60			{"bbox": [172.42349243164062, 98.635498046875, 229.2945556640625, 140.88552856445312], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.993384", "confidence": 0.5912003517150879, "detection_id": "222-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.00408+00	2025-11-05 19:57:32.037376+00	2025-11-05 19:57:32.037388+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.108
9cfd5424-e1df-456e-8ab9-5af06ec88ae3	INF-SPE-145732-10	speed	medium	\N	\N		0	96.5	60			{"bbox": [172.45169067382812, 98.58976745605469, 228.96157836914062, 141.0572052001953], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.995453", "confidence": 0.3481113612651825, "detection_id": "222-6", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.004467+00	2025-11-05 19:57:32.087808+00	2025-11-05 19:57:32.087819+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.108
cae0c9b6-750b-460a-9103-3261ca203e3f	INF-SPE-145732-79	speed	medium	\N	\N		0	86.7	60			{"bbox": [78.00410461425781, 88.39924621582031, 99.86476135253906, 104.82185363769531], "source": "webcam_local", "timestamp": "2025-11-05T19:57:31.998069", "confidence": 0.2601143717765808, "detection_id": "222-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.004731+00	2025-11-05 19:57:32.130538+00	2025-11-05 19:57:32.130547+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.108
dcaf9fc1-e2c4-4ae2-beda-a58711c8f177	INF-SPE-145732-56	speed	medium	\N	\N		0	73.3	60			{"bbox": [79.56494140625, 88.29273986816406, 96.571533203125, 103.60353088378906], "source": "webcam_local", "timestamp": "2025-11-05T19:57:32.369202", "confidence": 0.274993360042572, "detection_id": "226-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.377428+00	2025-11-05 19:57:32.411032+00	2025-11-05 19:57:32.41104+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.083
0d10c6c5-a629-43ce-9a7a-c46b8cc08660	INF-SPE-145732-92	speed	medium	\N	\N		0	73.5	60			{"bbox": [158.090087890625, 92.81939697265625, 165.88232421875, 98.34475708007812], "source": "webcam_local", "timestamp": "2025-11-05T19:57:32.523465", "confidence": 0.22036127746105194, "detection_id": "228-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.53014+00	2025-11-05 19:57:32.559501+00	2025-11-05 19:57:32.55951+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.061
70d0d17e-c34f-4bc1-b2aa-eff1e8070e6b	INF-SPE-145732-80	speed	medium	\N	\N		0	90.8	60			{"bbox": [26.554418563842773, 88.88325500488281, 57.79357147216797, 107.65635681152344], "source": "webcam_local", "timestamp": "2025-11-05T19:57:32.704690", "confidence": 0.7788181304931641, "detection_id": "230-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.712205+00	2025-11-05 19:57:32.756802+00	2025-11-05 19:57:32.75681+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.101
c2855ab9-5f62-4d23-bf88-ab99fd912101	INF-SPE-145732-71	speed	medium	\N	\N		0	95.2	60			{"bbox": [27.276792526245117, 89.03822326660156, 59.048004150390625, 107.74565124511719], "source": "webcam_local", "timestamp": "2025-11-05T19:57:32.839065", "confidence": 0.7121012806892395, "detection_id": "232-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.854083+00	2025-11-05 19:57:32.88667+00	2025-11-05 19:57:32.886677+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.081
95244817-7bac-4980-b7fd-27642de386ce	INF-SPE-145732-45	speed	medium	\N	\N		0	79.5	60			{"bbox": [106.5174560546875, 86.77969360351562, 133.86105346679688, 103.0147705078125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:32.840367", "confidence": 0.5640332698822021, "detection_id": "232-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.854565+00	2025-11-05 19:57:32.932828+00	2025-11-05 19:57:32.932836+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.081
4120e5c7-16d6-49ad-9ecf-2a678a4c81ad	INF-SPE-145732-54	speed	medium	\N	\N		0	91.7	60			{"bbox": [68.95045471191406, 95.25382995605469, 76.73011779785156, 105.58522033691406], "source": "webcam_local", "timestamp": "2025-11-05T19:57:32.848730", "confidence": 0.2761034667491913, "detection_id": "232-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:32.854974+00	2025-11-05 19:57:32.985485+00	2025-11-05 19:57:32.985495+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.081
5ee287e7-90d6-4d53-a611-a1d9e9f2be75	INF-SPE-145733-44	speed	medium	\N	\N		0	83.4	60			{"bbox": [204.75265502929688, 97.63522338867188, 247.86935424804688, 128.795166015625], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.036465", "confidence": 0.7108046412467957, "detection_id": "234-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.04439+00	2025-11-05 19:57:33.074033+00	2025-11-05 19:57:33.074042+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.084
171063e2-9308-45f9-b0cd-7db81ae1bac3	INF-SPE-145733-51	speed	medium	\N	\N		0	94.9	60			{"bbox": [210.07608032226562, 94.59565734863281, 251.94223022460938, 125.19960021972656], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.166882", "confidence": 0.8395277261734009, "detection_id": "236-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.174748+00	2025-11-05 19:57:33.205146+00	2025-11-05 19:57:33.205152+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
43cb75b3-9ab5-414f-98bf-bfc8f82e804a	INF-SPE-145733-11	speed	medium	\N	\N		0	95.2	60			{"bbox": [104.60260009765625, 84.73561096191406, 129.53573608398438, 101.82679748535156], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.168252", "confidence": 0.6472803950309753, "detection_id": "236-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.175025+00	2025-11-05 19:57:33.249465+00	2025-11-05 19:57:33.249476+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
9b73400e-f629-4ff5-944f-980699f12181	INF-SPE-145733-66	speed	medium	\N	\N		0	74.2	60			{"bbox": [155.8431396484375, 88.10577392578125, 170.29864501953125, 97.49697875976562], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.169326", "confidence": 0.3024367094039917, "detection_id": "236-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.17523+00	2025-11-05 19:57:33.321035+00	2025-11-05 19:57:33.321045+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
336a1f73-6490-407b-a7fc-7fd57a18cf65	INF-SPE-145733-30	speed	medium	\N	\N		0	94.7	60			{"bbox": [213.67889404296875, 94.58543395996094, 254.61944580078125, 124.34422302246094], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.358009", "confidence": 0.7642563581466675, "detection_id": "238-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.366807+00	2025-11-05 19:57:33.396476+00	2025-11-05 19:57:33.396483+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.105
122f48d6-4209-42d1-894c-568e8b2cd03e	INF-SPE-145733-28	speed	medium	\N	\N		0	88.8	60			{"bbox": [216.27674865722656, 94.87940979003906, 254.9760284423828, 122.82064819335938], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.524246", "confidence": 0.8244507908821106, "detection_id": "240-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.535314+00	2025-11-05 19:57:33.569215+00	2025-11-05 19:57:33.569223+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.099
4cc65162-0134-4cf7-a404-41e7ebf16263	INF-SPE-145733-21	speed	medium	\N	\N		0	71.4	60			{"bbox": [29.284164428710938, 87.43354797363281, 61.080406188964844, 105.82524108886719], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.687517", "confidence": 0.7043017148971558, "detection_id": "242-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.698558+00	2025-11-05 19:57:33.729525+00	2025-11-05 19:57:33.729531+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.08
7d535d0d-55f3-4900-8601-096145459736	INF-SPE-145733-83	speed	medium	\N	\N		0	70.1	60			{"bbox": [123.01348876953125, 88.21890258789062, 136.20413208007812, 97.97885131835938], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.693473", "confidence": 0.24447470903396606, "detection_id": "242-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.698848+00	2025-11-05 19:57:33.77754+00	2025-11-05 19:57:33.777549+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.08
cb940ede-bed4-461d-b30c-0b8276a29766	INF-SPE-145733-98	speed	medium	\N	\N		0	82.4	60			{"bbox": [121.03324890136719, 88.75450134277344, 134.8654327392578, 98.04960632324219], "source": "webcam_local", "timestamp": "2025-11-05T19:57:33.835420", "confidence": 0.46254438161849976, "detection_id": "244-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:33.843455+00	2025-11-05 19:57:33.986424+00	2025-11-05 19:57:33.986432+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.071
95ffb0c1-f220-462e-9ac4-ed0991afbaf6	INF-SPE-145734-57	speed	medium	\N	\N		0	93.4	60			{"bbox": [29.005603790283203, 87.84288787841797, 60.11189651489258, 106.08768463134766], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.002329", "confidence": 0.6292990446090698, "detection_id": "246-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.009365+00	2025-11-05 19:57:34.036285+00	2025-11-05 19:57:34.036291+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.099
aea5f844-b335-4842-97fc-3d7034c3821a	INF-SPE-145734-53	speed	medium	\N	\N		0	82.3	60			{"bbox": [118.61640930175781, 88.60918426513672, 130.97340393066406, 97.54882049560547], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.004086", "confidence": 0.3354122042655945, "detection_id": "246-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.009755+00	2025-11-05 19:57:34.067784+00	2025-11-05 19:57:34.06779+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.099
bf58390b-386a-43fe-9c23-38b3fd132dfa	INF-SPE-145734-33	speed	medium	\N	\N		0	91.3	60			{"bbox": [27.822586059570312, 88.07716369628906, 60.72084045410156, 106.17146301269531], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.136547", "confidence": 0.828513503074646, "detection_id": "248-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.144817+00	2025-11-05 19:57:34.175956+00	2025-11-05 19:57:34.175962+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.073
98f99306-32e5-41b8-a530-be47bc3fe0bf	INF-SPE-145734-25	speed	medium	\N	\N		0	93.4	60			{"bbox": [95.37164306640625, 85.80233764648438, 119.32369995117188, 103.19268798828125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.138401", "confidence": 0.5589373707771301, "detection_id": "248-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.145347+00	2025-11-05 19:57:34.227245+00	2025-11-05 19:57:34.227261+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.073
7a6f7e1c-bafd-48a1-8db1-c0f8183bf2b5	INF-SPE-145734-59	speed	medium	\N	\N		0	82.3	60			{"bbox": [114.92431640625, 88.37651062011719, 128.33221435546875, 100.09849548339844], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.139747", "confidence": 0.2277894765138626, "detection_id": "248-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.146021+00	2025-11-05 19:57:34.273293+00	2025-11-05 19:57:34.273301+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.073
9bacc6a9-41ac-4fcc-abbe-f9c9facde810	INF-SPE-145734-52	speed	medium	\N	\N		0	92.3	60			{"bbox": [230.99691772460938, 95.5379638671875, 261.7669982910156, 119.73701477050781], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.260592", "confidence": 0.7875032424926758, "detection_id": "250-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.266565+00	2025-11-05 19:57:34.294166+00	2025-11-05 19:57:34.294173+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.063
43e5228e-ed74-47de-9be6-c77f6975d605	INF-SPE-145734-80	speed	medium	\N	\N		0	86.7	60			{"bbox": [92.31216430664062, 85.90849304199219, 116.7891845703125, 103.65667724609375], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.374560", "confidence": 0.44931313395500183, "detection_id": "252-6", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.380809+00	2025-11-05 19:57:34.408713+00	2025-11-05 19:57:34.40872+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.064
cb17f9bb-de6f-48ff-9325-f852cca1dc81	INF-SPE-145734-45	speed	medium	\N	\N		0	89.4	60			{"bbox": [233.898193359375, 95.42823791503906, 264.81939697265625, 117.72367858886719], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.480732", "confidence": 0.8303701281547546, "detection_id": "254-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.491814+00	2025-11-05 19:57:34.525745+00	2025-11-05 19:57:34.525751+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.061
ff98f595-a091-4444-ac81-17dbce9c628d	INF-SPE-145734-75	speed	medium	\N	\N		0	86.5	60			{"bbox": [58.287010192871094, 92.87532043457031, 77.67708587646484, 104.36021423339844], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.486192", "confidence": 0.28236711025238037, "detection_id": "254-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.492075+00	2025-11-05 19:57:34.567232+00	2025-11-05 19:57:34.567241+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.061
4494c0d1-7a5a-4bb5-b321-9700390d3d2a	INF-SPE-145734-81	speed	medium	\N	\N		0	94.5	60			{"bbox": [31.443634033203125, 87.53410339355469, 61.548194885253906, 105.04991149902344], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.690028", "confidence": 0.414994478225708, "detection_id": "258-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.700846+00	2025-11-05 19:57:34.728618+00	2025-11-05 19:57:34.728625+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
47510b8a-4605-4d24-bb0f-bba7c86f3111	INF-SPE-145734-61	speed	medium	\N	\N		0	71.5	60			{"bbox": [88.46343994140625, 84.60307312011719, 122.39654541015625, 102.30339050292969], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.694993", "confidence": 0.2345718890428543, "detection_id": "258-6", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.701175+00	2025-11-05 19:57:34.765162+00	2025-11-05 19:57:34.765173+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
6cd80acc-2620-4d45-890d-b151a88a1de9	INF-SPE-145734-65	speed	medium	\N	\N		0	73.1	60			{"bbox": [60.92873764038086, 93.72649383544922, 76.88803100585938, 103.7232437133789], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.800716", "confidence": 0.23611822724342346, "detection_id": "260-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.80501+00	2025-11-05 19:57:34.930736+00	2025-11-05 19:57:34.930744+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.052
810c9680-8c19-4b26-9c73-932f6ae0a652	INF-SPE-145734-21	speed	medium	\N	\N		0	86	60			{"bbox": [240.3670654296875, 92.81782531738281, 266.3765563964844, 113.66783142089844], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.921745", "confidence": 0.8299011588096619, "detection_id": "262-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.931646+00	2025-11-05 19:57:34.961398+00	2025-11-05 19:57:34.961403+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.07
ccc38ba3-e740-4b54-8009-a9816adaa2c8	INF-SPE-145734-96	speed	medium	\N	\N		0	88.8	60			{"bbox": [59.113834381103516, 74.87322998046875, 79.06112670898438, 103.46044921875], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.922850", "confidence": 0.34520116448402405, "detection_id": "262-5", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.932053+00	2025-11-05 19:57:34.997272+00	2025-11-05 19:57:34.997281+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.07
5138054d-f210-4b20-882c-888dc309157a	INF-SPE-145735-59	speed	medium	\N	\N		0	83.7	60			{"bbox": [58.830230712890625, 75.17137145996094, 79.16923522949219, 103.37202453613281], "source": "webcam_local", "timestamp": "2025-11-05T19:57:34.926143", "confidence": 0.24752289056777954, "detection_id": "262-8", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:34.932488+00	2025-11-05 19:57:35.042417+00	2025-11-05 19:57:35.042423+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.07
6c7b3e2b-f821-4159-a4de-93a715eb83d8	INF-SPE-145735-89	speed	medium	\N	\N		0	77	60			{"bbox": [215.64761352539062, 101.06300354003906, 231.95309448242188, 118.45637512207031], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.048590", "confidence": 0.2622816264629364, "detection_id": "264-6", "vehicle_type": "motorcycle"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.057993+00	2025-11-05 19:57:35.084345+00	2025-11-05 19:57:35.084352+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.064
334bd797-1ea0-458f-81dd-6921839cff9d	INF-SPE-145735-48	speed	medium	\N	\N		0	72.6	60			{"bbox": [60.108253479003906, 86.5887451171875, 78.51728057861328, 103.61654663085938], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.052576", "confidence": 0.24693787097930908, "detection_id": "264-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.058264+00	2025-11-05 19:57:35.118299+00	2025-11-05 19:57:35.118311+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.064
1b5343d6-74d5-40ed-bdad-05aea9bc470c	INF-SPE-145735-56	speed	medium	\N	\N		0	70.4	60			{"bbox": [28.88419532775879, 86.34127807617188, 59.83049774169922, 103.759033203125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.172790", "confidence": 0.6831130981445312, "detection_id": "266-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.17943+00	2025-11-05 19:57:35.203411+00	2025-11-05 19:57:35.203418+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.054
b5798301-b6f3-4262-adb8-ace836e26e2d	INF-SPE-145735-46	speed	medium	\N	\N		0	93.7	60			{"bbox": [29.0651912689209, 86.47425842285156, 59.90099334716797, 103.55577087402344], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.311552", "confidence": 0.7327226996421814, "detection_id": "268-2", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.321543+00	2025-11-05 19:57:35.347009+00	2025-11-05 19:57:35.347015+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.07
8d94eea0-783d-4a4a-8990-2b621fad1520	INF-SPE-145735-23	speed	medium	\N	\N		0	82.5	60			{"bbox": [88.29682922363281, 83.25340270996094, 113.31983947753906, 101.48149108886719], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.315597", "confidence": 0.3575870096683502, "detection_id": "268-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.321826+00	2025-11-05 19:57:35.386256+00	2025-11-05 19:57:35.386263+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.07
9c0c04cb-a877-4487-9b3a-0158a194da42	INF-SPE-145735-18	speed	medium	\N	\N		0	71.1	60			{"bbox": [29.107769012451172, 87.83169555664062, 50.021846771240234, 105.08346557617188], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.443378", "confidence": 0.5574257969856262, "detection_id": "270-3", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.45185+00	2025-11-05 19:57:35.476283+00	2025-11-05 19:57:35.476289+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.053
76d6c6ed-869d-40ab-b581-28cbf7727683	INF-SPE-145735-70	speed	medium	\N	\N		0	81.3	60			{"bbox": [247.938232421875, 93.56265258789062, 264.53717041015625, 112.64141845703125], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.569986", "confidence": 0.6016300320625305, "detection_id": "272-4", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.57955+00	2025-11-05 19:57:35.610575+00	2025-11-05 19:57:35.61058+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.074
f960b165-b10e-4e86-b8a4-6c51edd2e3a1	INF-SPE-145735-39	speed	medium	\N	\N		0	87.9	60			{"bbox": [125.09991455078125, 89.76490783691406, 137.08779907226562, 98.99864196777344], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.573340", "confidence": 0.4395708739757538, "detection_id": "272-7", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.579971+00	2025-11-05 19:57:35.656341+00	2025-11-05 19:57:35.65635+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.074
fb7bce50-49f2-4a6a-969a-9259f46f2fee	INF-SPE-145735-96	speed	medium	\N	\N		0	84	60			{"bbox": [50.21186828613281, 76.88397979736328, 79.75482177734375, 104.86258697509766], "source": "webcam_local", "timestamp": "2025-11-05T19:57:35.849035", "confidence": 0.2339414805173874, "detection_id": "276-12", "vehicle_type": "truck"}	pending	\N		\N	\N	\N	2025-11-06 00:57:35.85327+00	2025-11-05 19:57:35.874533+00	2025-11-05 19:57:35.874538+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.05
a1ae18eb-2061-4e12-ab4e-1c27f0d7497a	INF-SPE-145736-28	speed	medium	\N	\N		0	98	60			{"bbox": [86.84866333007812, 87.33495330810547, 110.10806274414062, 106.57855987548828], "source": "webcam_local", "timestamp": "2025-11-05T19:57:36.292841", "confidence": 0.27794206142425537, "detection_id": "282-9", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:36.298567+00	2025-11-05 19:57:36.326378+00	2025-11-05 19:57:36.326384+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
d0fdd6d6-0737-41b6-8f72-89ed77c3868f	INF-SPE-145736-42	speed	medium	\N	\N		0	89.6	60			{"bbox": [47.388877868652344, 77.26173400878906, 79.58667755126953, 106.43026733398438], "source": "webcam_local", "timestamp": "2025-11-05T19:57:36.449221", "confidence": 0.4093431532382965, "detection_id": "284-7", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:36.455474+00	2025-11-05 19:57:36.479877+00	2025-11-05 19:57:36.479883+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.074
53b26372-25f1-4fcb-95f1-6677ca1eb159	INF-SPE-145736-64	speed	medium	\N	\N		0	78.6	60			{"bbox": [113.32600402832031, 90.58154296875, 129.3453826904297, 100.90762329101562], "source": "webcam_local", "timestamp": "2025-11-05T19:57:36.598167", "confidence": 0.4104284644126892, "detection_id": "286-8", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:36.604314+00	2025-11-05 19:57:36.633198+00	2025-11-05 19:57:36.633204+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.065
ef286cfd-58ce-4d55-80d7-ad5ab131ccd4	INF-SPE-145736-70	speed	medium	\N	\N		0	91	60			{"bbox": [44.501800537109375, 77.47224426269531, 79.6597900390625, 106.55580139160156], "source": "webcam_local", "timestamp": "2025-11-05T19:57:36.742557", "confidence": 0.3953951299190521, "detection_id": "288-6", "vehicle_type": "bus"}	pending	\N		\N	\N	\N	2025-11-06 00:57:36.750369+00	2025-11-05 19:57:36.777283+00	2025-11-05 19:57:36.777289+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.062
726e7fa3-9462-4322-b837-d3918b1bce90	INF-SPE-145736-31	speed	medium	\N	\N		0	90.8	60			{"bbox": [0.0552372932434082, 133.3022003173828, 16.01455307006836, 179.47279357910156], "source": "webcam_local", "timestamp": "2025-11-05T19:57:36.898771", "confidence": 0.7422701120376587, "detection_id": "290-1", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:36.908398+00	2025-11-05 19:57:36.935233+00	2025-11-05 19:57:36.935241+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.067
7bce5853-a43d-4416-bd75-1b613f171f65	INF-SPE-145737-78	speed	medium	\N	\N		0	77.8	60			{"bbox": [106.71217346191406, 91.34945678710938, 127.97012329101562, 104.86054992675781], "source": "webcam_local", "timestamp": "2025-11-05T19:57:37.067936", "confidence": 0.4499257504940033, "detection_id": "292-5", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:37.075278+00	2025-11-05 19:57:37.10476+00	2025-11-05 19:57:37.104765+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.08
d004d6f1-5307-4a3f-ad62-9f2a908d1090	INF-SPE-145737-84	speed	medium	\N	\N		0	92.8	60			{"bbox": [83.54044342041016, 86.6475830078125, 99.77742767333984, 110.82533264160156], "source": "webcam_local", "timestamp": "2025-11-05T19:57:37.070962", "confidence": 0.2050320953130722, "detection_id": "292-11", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 00:57:37.0756+00	2025-11-05 19:57:37.145181+00	2025-11-05 19:57:37.145188+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.08
811354d5-c74a-4fa0-a27e-1b3205ed8b37	INF-SPE-151230-32	speed	medium	\N	\N		0	75.5	60			{"bbox": [118.34185791015625, 41.47018051147461, 269.26763916015625, 160.22195434570312], "source": "webcam_local", "timestamp": "2025-11-05T20:12:30.325228", "confidence": 0.8525269627571106, "detection_id": "6-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:12:30.328293+00	2025-11-05 20:12:30.381597+00	2025-11-05 20:12:30.381604+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.048
3675aed5-5850-44a6-8aa4-977922d3035b	INF-SPE-151230-43	speed	medium	\N	\N		0	86.2	60			{"bbox": [118.8544692993164, 43.614654541015625, 268.3373107910156, 158.32861328125], "source": "webcam_local", "timestamp": "2025-11-05T20:12:30.690324", "confidence": 0.873690664768219, "detection_id": "12-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:12:30.695426+00	2025-11-05 20:12:30.733896+00	2025-11-05 20:12:30.733905+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.044
20bb67ab-a9bd-4cfe-a01e-7cdf357cb51c	INF-SPE-151231-17	speed	medium	\N	\N		0	75.1	60			{"bbox": [115.99734497070312, 27.594730377197266, 262.34442138671875, 155.03424072265625], "source": "webcam_local", "timestamp": "2025-11-05T20:12:31.036097", "confidence": 0.807637631893158, "detection_id": "18-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:12:31.04015+00	2025-11-05 20:12:31.067451+00	2025-11-05 20:12:31.067456+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.046
9f480677-9814-4af0-b910-cb8ca446e395	INF-SPE-151231-10	speed	medium	\N	\N		0	99.1	60			{"bbox": [112.63693237304688, 43.373504638671875, 256.30999755859375, 151.40469360351562], "source": "webcam_local", "timestamp": "2025-11-05T20:12:31.367378", "confidence": 0.8840094804763794, "detection_id": "24-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:12:31.371929+00	2025-11-05 20:12:31.399007+00	2025-11-05 20:12:31.399013+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.06
d0ebefeb-aa3a-4482-9033-9d6bf23cdf80	INF-SPE-151231-54	speed	medium	\N	\N		0	75.2	60			{"bbox": [109.70989227294922, 37.616275787353516, 250.4093017578125, 149.67800903320312], "source": "webcam_local", "timestamp": "2025-11-05T20:12:31.671351", "confidence": 0.846087634563446, "detection_id": "30-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:12:31.675084+00	2025-11-05 20:12:31.703607+00	2025-11-05 20:12:31.703614+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.051
f678905d-bdb7-4e96-84f1-29e209139084	INF-SPE-151232-37	speed	medium	\N	\N		0	93.5	60			{"bbox": [103.40259552001953, 45.06938171386719, 242.467041015625, 150.97872924804688], "source": "webcam_local", "timestamp": "2025-11-05T20:12:31.997426", "confidence": 0.9107507467269897, "detection_id": "36-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:12:32.002546+00	2025-11-05 20:12:32.030312+00	2025-11-05 20:12:32.030319+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.059
c12c93c6-92c8-464a-8db6-08c890bebe1f	INF-SPE-151232-53	speed	medium	\N	\N		0	74.4	60			{"bbox": [98.24414825439453, 44.78607177734375, 238.05126953125, 155.79263305664062], "source": "webcam_local", "timestamp": "2025-11-05T20:12:32.326143", "confidence": 0.8836140036582947, "detection_id": "42-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:12:32.331438+00	2025-11-05 20:12:32.359185+00	2025-11-05 20:12:32.35919+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.062
79dc84a5-ddb9-48a2-9cd0-2e55d337c66b	INF-SPE-152100-60	speed	medium	\N	\N		0	75.6	60			{"bbox": [260.36981201171875, 76.84182739257812, 297.82147216796875, 104.22850036621094], "source": "webcam_local", "timestamp": "2025-11-05T20:21:00.847721", "confidence": 0.5738234519958496, "detection_id": "2-1", "vehicle_type": "motorcycle"}	pending	\N		\N	\N	\N	2025-11-06 01:21:00.854753+00	2025-11-05 20:21:00.899936+00	2025-11-05 20:21:00.899944+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.045
d59a0ce2-0615-47d0-8df0-5331a6cf5c8b	INF-SPE-152101-70	speed	medium	\N	\N		0	70.2	60			{"bbox": [111.09626007080078, 40.78361511230469, 263.596435546875, 163.80691528320312], "source": "webcam_local", "timestamp": "2025-11-05T20:21:01.009904", "confidence": 0.8377717733383179, "detection_id": "6-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:01.015311+00	2025-11-05 20:21:01.047055+00	2025-11-05 20:21:01.047062+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.042
c7e7ddc5-8e02-4020-9de5-99eeaa7b219a	INF-SPE-152101-25	speed	medium	\N	\N		0	77.2	60			{"bbox": [114.41656494140625, 29.489944458007812, 266.21307373046875, 161.0464324951172], "source": "webcam_local", "timestamp": "2025-11-05T20:21:01.301057", "confidence": 0.8579197525978088, "detection_id": "12-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:01.306883+00	2025-11-05 20:21:01.337709+00	2025-11-05 20:21:01.337715+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.049
1c236fce-7981-496c-8661-5926e7fa0a23	INF-SPE-152101-17	speed	medium	\N	\N		0	88.3	60			{"bbox": [118.0159683227539, 44.47951126098633, 269.1499938964844, 158.3200225830078], "source": "webcam_local", "timestamp": "2025-11-05T20:21:01.582293", "confidence": 0.8737325072288513, "detection_id": "18-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:01.58788+00	2025-11-05 20:21:01.620119+00	2025-11-05 20:21:01.620125+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.05
8140511f-bcd6-4477-bde5-b679d17b2275	INF-SPE-152101-93	speed	medium	\N	\N		0	95.9	60			{"bbox": [118.60186767578125, 41.78921127319336, 268.82135009765625, 160.0997314453125], "source": "webcam_local", "timestamp": "2025-11-05T20:21:01.880177", "confidence": 0.8141309022903442, "detection_id": "24-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:01.885755+00	2025-11-05 20:21:01.917528+00	2025-11-05 20:21:01.917538+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.05
57a7039a-17b8-4d1d-abd6-7ec926d61f7d	INF-SPE-152102-88	speed	medium	\N	\N		0	97.7	60			{"bbox": [117.07339477539062, 27.918014526367188, 265.1463928222656, 152.1172637939453], "source": "webcam_local", "timestamp": "2025-11-05T20:21:02.185621", "confidence": 0.815018892288208, "detection_id": "30-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:02.192035+00	2025-11-05 20:21:02.223744+00	2025-11-05 20:21:02.223751+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.051
33ab3cca-d85e-46cd-a588-eaa8e4fc71d7	INF-SPE-152102-20	speed	medium	\N	\N		0	85.2	60			{"bbox": [113.80410766601562, 27.867584228515625, 259.5431213378906, 152.43138122558594], "source": "webcam_local", "timestamp": "2025-11-05T20:21:02.515864", "confidence": 0.7788317203521729, "detection_id": "36-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:02.520664+00	2025-11-05 20:21:02.558401+00	2025-11-05 20:21:02.558409+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.049
15b5db42-03d3-4759-ae23-87af98e7d0f8	INF-SPE-152102-96	speed	medium	\N	\N		0	86.6	60			{"bbox": [111.06906127929688, 42.09393310546875, 253.29498291015625, 152.36569213867188], "source": "webcam_local", "timestamp": "2025-11-05T20:21:02.885479", "confidence": 0.8788393139839172, "detection_id": "42-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:02.891307+00	2025-11-05 20:21:02.92082+00	2025-11-05 20:21:02.920826+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.058
965836b8-19ac-4aef-a13b-0bf35787357b	INF-SPE-152103-63	speed	medium	\N	\N		0	89.7	60			{"bbox": [104.01513671875, 44.1749153137207, 244.56417846679688, 150.9897918701172], "source": "webcam_local", "timestamp": "2025-11-05T20:21:03.272790", "confidence": 0.8736509680747986, "detection_id": "48-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:03.279803+00	2025-11-05 20:21:03.31484+00	2025-11-05 20:21:03.314846+00	f0c56a7b-8508-4988-9848-ab997e873c3b	\N	\N	\N	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	\N	{}	\N	0.054
a6bd9f10-92e7-4255-91a2-b96b129db979	INF-SPE-152103-23	speed	medium	\N	\N	ABC123	0.95	77.3	60			{"bbox": [98.24414825439453, 44.78607177734375, 238.05126953125, 155.79263305664062], "source": "webcam_local", "timestamp": "2025-11-05T20:21:03.632158", "confidence": 0.8836140036582947, "detection_id": "54-0", "vehicle_type": "car"}	pending	\N		\N	\N	\N	2025-11-06 01:21:03.636444+00	2025-11-05 20:21:03.674768+00	2025-11-05 20:27:15.264565+00	f0c56a7b-8508-4988-9848-ab997e873c3b	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	2e8ab3f0-0bdc-4485-b5ab-b943f7bf14b6	59bfe8d5-ac43-4605-8d73-23990290b0ad	\N	0.88	{"factors": [{"value": 8, "factor": "infraction_count_90d", "importance": 0.35, "description": "Alto número de infracciones recientes (8 en 90 días)"}, {"value": 0.01, "factor": "recency", "importance": 0.28, "description": "Infracción muy reciente (0.01 días)"}, {"value": 4, "factor": "diversity", "importance": 0.1, "description": "Múltiples tipos de infracciones (4 tipos diferentes)"}]}	24.826	0.045
\.


--
-- Data for Name: infractions_infractionevent; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.infractions_infractionevent (id, event_type, notes, metadata, "timestamp", infraction_id, user_id) FROM stdin;
\.


--
-- Data for Name: infractions_vehicledetection; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.infractions_vehicledetection (id, vehicle_type, confidence, license_plate_detected, license_plate_confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, estimated_speed, has_infraction, metadata, source, detected_at, created_at, device_id, infraction_id, vehicle_id, zone_id) FROM stdin;
\.


--
-- Data for Name: login_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.login_history (id, login_at, logout_at, ip_address, user_agent, success, failure_reason, user_id) FROM stdin;
2ccc5eca-84b3-4561-9518-b0793f331ada	2025-11-05 03:03:00.404094+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		614dda88-105d-4865-bdef-53a10ffcbfa9
a9d946e6-4ed0-4580-869a-0414ffa8beeb	2025-11-05 04:03:49.835599+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		614dda88-105d-4865-bdef-53a10ffcbfa9
9843beab-c5b4-4969-89f8-6177be44053d	2025-11-05 05:13:33.59079+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
4cbaa82b-e392-4cf8-a7de-4a78687c685c	2025-11-05 06:19:15.40601+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
eb70ddac-33fa-466b-8d4e-6f45cf118342	2025-11-05 07:20:34.476001+00	2025-11-05 07:32:55.190407+00	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
7357ee51-aeae-4af3-b2d8-a9f94b2f6fa0	2025-11-05 07:33:00.183605+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
3f9f970a-3652-4d5e-8cf7-539cd08a914e	2025-11-05 08:58:54.736009+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
04eb9bfe-84a3-4962-a3a0-ecc7900db189	2025-11-05 17:25:40.217509+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
f13faaa0-3a93-4dbe-8c1e-44f37ff46028	2025-11-05 18:36:11.958374+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
398d879e-c9c4-4b1a-8bb3-26be663292be	2025-11-05 19:57:00.6692+00	2025-11-05 20:14:41.937791+00	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
a65bbd4c-ab12-49fc-842c-44f7ab64649b	2025-11-05 20:14:50.794034+00	\N	172.28.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	t		a0807937-823f-4913-8dce-df36ea89b864
\.


--
-- Data for Name: ml_models_mlmodel; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ml_models_mlmodel (id, model_name, version, model_type, framework, framework_version, model_path, model_size_mb, mlflow_run_id, mlflow_experiment_id, mlflow_model_uri, metrics, hyperparameters, training_dataset_path, training_dataset_size, validation_dataset_path, test_dataset_path, feature_names, feature_importance, is_active, deployed_at, deployment_environment, prediction_count, avg_prediction_time_ms, last_prediction_at, data_drift_detected, concept_drift_detected, drift_check_at, description, notes, created_at, updated_at, metadata, created_by_id, deployed_by_id) FROM stdin;
c502454c-0372-42de-a0ee-27fb0380c11a	recidivism_heuristic	v1.0.0	classification	sklearn		heuristic://recidivism_v1.0.0	\N				{"note": "Heuristic model - placeholder for XGBoost", "accuracy": 0.75}	{}		\N			[]	{}	t	\N	development	1	24.826	2025-11-05 20:27:01.97222+00	f	f	\N			2025-11-05 18:18:08.505431+00	2025-11-05 18:18:08.505441+00	{}	\N	\N
\.


--
-- Data for Name: ml_models_mlprediction; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ml_models_mlprediction (id, prediction_type, prediction_value, prediction_class, prediction_confidence, features, actual_value, actual_class, prediction_time_ms, predicted_at, metadata, driver_id, infraction_id, model_id) FROM stdin;
1	recidivism	0.8	critical	0.75	{"driver_age": 30, "recency_score": 0.3333333333333333, "lane_invasions": 0, "infraction_rate": 0.05555555555555555, "avg_speed_excess": 22.0, "infraction_trend": 2.5, "max_speed_excess": 30.0, "speed_violations": 5, "driver_risk_score": 0.0, "infractions_night": 0, "avg_severity_score": 2.3, "driver_is_suspended": 0, "infraction_count_7d": 2, "infractions_weekend": 3, "infraction_count_30d": 5, "infraction_count_90d": 7, "no_helmet_violations": 1, "red_light_violations": 3, "infraction_count_365d": 10, "infractions_rush_hour": 0, "infraction_count_total": 10, "no_seatbelt_violations": 0, "infraction_type_diversity": 4, "days_since_last_infraction": 2}	\N		18.852	2025-11-05 18:18:08.52739+00	{}	e5222de9-aeac-4877-9cb6-beee06f4451d	\N	c502454c-0372-42de-a0ee-27fb0380c11a
2	recidivism	0.88	critical	0.75	{"driver_age": 30, "recency_score": 0.9900990099009901, "lane_invasions": 0, "infraction_rate": 0.06111111111111111, "avg_speed_excess": 21.216666666666665, "infraction_trend": 3.0, "max_speed_excess": 30.0, "speed_violations": 6, "driver_risk_score": 0.8, "infractions_night": 0, "avg_severity_score": 2.272727272727273, "driver_is_suspended": 0, "infraction_count_7d": 3, "infractions_weekend": 3, "infraction_count_30d": 6, "infraction_count_90d": 8, "no_helmet_violations": 1, "red_light_violations": 3, "infraction_count_365d": 11, "infractions_rush_hour": 0, "infraction_count_total": 11, "no_seatbelt_violations": 0, "infraction_type_diversity": 4, "days_since_last_infraction": 0.01}	\N		24.826	2025-11-05 20:27:01.966923+00	{}	e5222de9-aeac-4877-9cb6-beee06f4451d	a6bd9f10-92e7-4255-91a2-b96b129db979	c502454c-0372-42de-a0ee-27fb0380c11a
\.


--
-- Data for Name: notifications_notification; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications_notification (id, title, message, notification_type, link, is_read, created_at, read_at, user_id) FROM stdin;
\.


--
-- Data for Name: token_blacklist_blacklistedtoken; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.token_blacklist_blacklistedtoken (id, blacklisted_at, token_id) FROM stdin;
1	2025-11-05 07:32:55.181996+00	5
2	2025-11-05 20:14:41.929051+00	10
\.


--
-- Data for Name: token_blacklist_outstandingtoken; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.token_blacklist_outstandingtoken (id, token, created_at, expires_at, user_id, jti) FROM stdin;
1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjkxNjU4MCwiaWF0IjoxNzYyMzExNzgwLCJqdGkiOiI0Y2RlNzc1MjhhNjE0NDFhODk0NTA3NThhN2M0Y2Q2NiIsInVzZXJfaWQiOiI2MTRkZGE4OC0xMDVkLTQ4NjUtYmRlZi01M2ExMGZmY2JmYTkifQ.rQSYiPnWRXq_L7DmsUmgIlPxmHUVe1MC1V1-GfTZ-Qw	2025-11-05 03:03:00.40016+00	2025-11-12 03:03:00+00	614dda88-105d-4865-bdef-53a10ffcbfa9	4cde77528a61441a89450758a7c4cd66
2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjkyMDIyOSwiaWF0IjoxNzYyMzE1NDI5LCJqdGkiOiIxYjNlYjA2OTYxNDA0MDE1OTZhNGU3OTJmMGQ1ZjViYiIsInVzZXJfaWQiOiI2MTRkZGE4OC0xMDVkLTQ4NjUtYmRlZi01M2ExMGZmY2JmYTkifQ.mS_gvU-zCUEFBGh2FPYBnbUspQhNz0z7olhMt4xAt_g	2025-11-05 04:03:49.819491+00	2025-11-12 04:03:49+00	614dda88-105d-4865-bdef-53a10ffcbfa9	1b3eb0696140401596a4e792f0d5f5bb
3	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjkyNDQxMywiaWF0IjoxNzYyMzE5NjEzLCJqdGkiOiI1MjFkOTU0NjgyYzQ0YTc2OThjOWE2Y2Y1MzQ2ZjQ0NyIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.M3tu0fL6nXBUtZ134crF-M1AWi21yy5uLEef2h8EFNU	2025-11-05 05:13:33.565127+00	2025-11-12 05:13:33+00	a0807937-823f-4913-8dce-df36ea89b864	521d954682c44a7698c9a6cf5346f447
4	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjkyODM1NSwiaWF0IjoxNzYyMzIzNTU1LCJqdGkiOiI4MGYwNzRkN2M3ODM0NWY1OTc1YWFhOWMyMTMyMjU2MiIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.Dux3H4vLR0b1oJmeMt54eXzUYwiJExYMLBc9_Q6XLME	2025-11-05 06:19:15.399519+00	2025-11-12 06:19:15+00	a0807937-823f-4913-8dce-df36ea89b864	80f074d7c78345f5975aaa9c21322562
5	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjkzMjAzNCwiaWF0IjoxNzYyMzI3MjM0LCJqdGkiOiJmZjQ4ZjQ5MGZhYWM0NWVhOWU1NTliZjdhMjdkNTg2ZSIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.6seihVlrDXPrKFtlIjjK64X6_SrsNZ_RiBapro5iq4U	2025-11-05 07:20:34.470515+00	2025-11-12 07:20:34+00	a0807937-823f-4913-8dce-df36ea89b864	ff48f490faac45ea9e559bf7a27d586e
6	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjkzMjc4MCwiaWF0IjoxNzYyMzI3OTgwLCJqdGkiOiIwMzZhNWRiYjBkZDU0NmY5ODRjNTVkYjgxZWVlOTQ2YiIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.RFnFtTM249761QP0l2GS2ipJkJDGtLcmI9ad4-tdhIo	2025-11-05 07:33:00.180734+00	2025-11-12 07:33:00+00	a0807937-823f-4913-8dce-df36ea89b864	036a5dbb0dd546f984c55db81eee946b
7	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjkzNzkzNCwiaWF0IjoxNzYyMzMzMTM0LCJqdGkiOiI2ZWMyZWQ0YmM3Njg0MzM1OTIzYzIwNzE4OWFiMjVjNyIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.QaSls4wFmkeHtisHGCZCRUfiwZOLTj2YUsZZ7wHquew	2025-11-05 08:58:54.723634+00	2025-11-12 08:58:54+00	a0807937-823f-4913-8dce-df36ea89b864	6ec2ed4bc7684335923c207189ab25c7
8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2Mjk2ODM0MCwiaWF0IjoxNzYyMzYzNTQwLCJqdGkiOiJlMDc1YTlkOWQ2MmU0ODA3ODRkNTkyMzY5YzUyYzYyYyIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.rYW45984umzRWs0h189wvUKKezZQY8lOgkyxeYxIzPs	2025-11-05 17:25:40.205452+00	2025-11-12 17:25:40+00	a0807937-823f-4913-8dce-df36ea89b864	e075a9d9d62e480784d592369c52c62c
9	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2Mjk3MjU3MSwiaWF0IjoxNzYyMzY3NzcxLCJqdGkiOiJlYmFhZGQzOWY1OWE0MjM3ODBkNDJiZTgzZjQ5NzcxZCIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.ePmjX8KB9klkximDXDL5NhXO_WdAoQ9NRjh8jpAGt_Q	2025-11-05 18:36:11.954161+00	2025-11-12 18:36:11+00	a0807937-823f-4913-8dce-df36ea89b864	ebaadd39f59a423780d42be83f49771d
10	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2Mjk3NzQyMCwiaWF0IjoxNzYyMzcyNjIwLCJqdGkiOiIwZDUzMGIyYTc1MDk0ZGI1YWZkYWQ5NzViNzlhMDcxNCIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.9kGbxVnHtFzOQ1aI4sNzZ6-6UV_KjdIq5lU8yD0Vjq8	2025-11-05 19:57:00.66198+00	2025-11-12 19:57:00+00	a0807937-823f-4913-8dce-df36ea89b864	0d530b2a75094db5afdad975b79a0714
11	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2Mjk3ODQ5MCwiaWF0IjoxNzYyMzczNjkwLCJqdGkiOiJlMzllNTI1OTA5N2M0MmIyYjlmNDRjNWU3N2I4ZTNmYSIsInVzZXJfaWQiOiJhMDgwNzkzNy04MjNmLTQ5MTMtOGRjZS1kZjM2ZWE4OWI4NjQifQ.umTZpJgitNvkqI3F5IiPDcu04B-oxYvYEE6trqLYrwM	2025-11-05 20:14:50.790192+00	2025-11-12 20:14:50+00	a0807937-823f-4913-8dce-df36ea89b864	e39e5259097c42b2b9f44c5e77b8e3fa
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (password, id, username, email, first_name, last_name, role, is_active, is_staff, is_superuser, date_joined, last_login, updated_at, phone, dni, profile_image, failed_login_attempts, account_locked_until, password_changed_at, must_change_password) FROM stdin;
pbkdf2_sha256$600000$f183xRtA4dzvjgdH423lOl$45otVMvkGPnDDbMmywt2ozjEinWz13zjLpDP2P3zRGs=	614dda88-105d-4865-bdef-53a10ffcbfa9	admin@traffic.local	admin			admin	t	t	t	2025-11-05 03:01:52.421341+00	2025-11-05 18:34:15.522632+00	2025-11-05 03:01:52.52428+00	\N	\N		0	\N	2025-11-05 03:01:52.421429+00	f
pbkdf2_sha256$600000$HB5xIFD4BZZsYIMyA7p7LO$zHN88m/hrWTXoDM3zyJraRDkiSc2KciJ8zMbb8NCC/Y=	a0807937-823f-4913-8dce-df36ea89b864	admin	admin@traffic.pe	Admin	System	admin	t	t	t	2025-11-05 04:21:24.78085+00	2025-11-05 20:14:50.789325+00	2025-11-05 04:21:25.069212+00	\N	\N		0	\N	2025-11-05 04:21:24.781272+00	f
\.


--
-- Data for Name: users_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: users_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: vehicles_driver; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vehicles_driver (id, document_type, document_number, first_name, last_name, birth_date, phone, email, address, license_number, license_class, license_expiry, is_suspended, suspension_reason, created_at, updated_at, risk_category, risk_score, risk_updated_at) FROM stdin;
e5222de9-aeac-4877-9cb6-beee06f4451d	dni	12345678	Juan	Pérez	1995-11-13	+51987654321	juan.perez@example.com		Q12345678	A-IIIc	2027-11-05	f		2025-11-05 18:06:35.769091+00	2025-11-05 18:18:08.532022+00	critical	0.8421052631578948	2025-11-05 20:27:01.971628+00
\.


--
-- Data for Name: vehicles_vehicle; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vehicles_vehicle (id, license_plate, make, model, year, color, vehicle_type, owner_name, owner_dni, owner_address, registration_date, is_stolen, is_wanted, notes, sunarp_last_updated, created_at, updated_at) FROM stdin;
53e33d52-0e27-4fe8-982f-fe4b68c84239	ABC-123	Toyota	Corolla	2020	silver	car	Juan Pérez	12345678		\N	f	f		\N	2025-11-05 18:07:05.282867+00	2025-11-05 18:07:05.282886+00
2e8ab3f0-0bdc-4485-b5ab-b943f7bf14b6	ABC123	Toyota	Corolla	2020	Azul	car	Juan Pérez	12345678		2025-11-05	f	f		\N	2025-11-05 20:02:37.834583+00	2025-11-05 20:02:37.834595+00
\.


--
-- Data for Name: vehicles_vehicleownership; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vehicles_vehicleownership (id, is_primary_owner, ownership_percentage, start_date, end_date, created_at, updated_at, driver_id, vehicle_id) FROM stdin;
77698f3d-a51c-4a9b-904c-b7cd34fbafd5	t	100.00	2025-11-05	\N	2025-11-05 20:02:51.753494+00	2025-11-05 20:02:51.75351+00	e5222de9-aeac-4877-9cb6-beee06f4451d	2e8ab3f0-0bdc-4485-b5ab-b943f7bf14b6
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 116, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, true);


--
-- Name: django_celery_beat_clockedschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_celery_beat_clockedschedule_id_seq', 1, false);


--
-- Name: django_celery_beat_crontabschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_celery_beat_crontabschedule_id_seq', 5, true);


--
-- Name: django_celery_beat_intervalschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_celery_beat_intervalschedule_id_seq', 1, false);


--
-- Name: django_celery_beat_periodictask_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_celery_beat_periodictask_id_seq', 5, true);


--
-- Name: django_celery_beat_solarschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_celery_beat_solarschedule_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 29, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 60, true);


--
-- Name: infraction_code_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.infraction_code_seq', 1090, true);


--
-- Name: ml_models_mlprediction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ml_models_mlprediction_id_seq', 2, true);


--
-- Name: notifications_notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notifications_notification_id_seq', 1, false);


--
-- Name: token_blacklist_blacklistedtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.token_blacklist_blacklistedtoken_id_seq', 2, true);


--
-- Name: token_blacklist_outstandingtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.token_blacklist_outstandingtoken_id_seq', 11, true);


--
-- Name: users_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_groups_id_seq', 1, false);


--
-- Name: users_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_permissions_id_seq', 1, false);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: devices_device devices_device_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices_device
    ADD CONSTRAINT devices_device_code_key UNIQUE (code);


--
-- Name: devices_device devices_device_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices_device
    ADD CONSTRAINT devices_device_pkey PRIMARY KEY (id);


--
-- Name: devices_deviceevent devices_deviceevent_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices_deviceevent
    ADD CONSTRAINT devices_deviceevent_pkey PRIMARY KEY (id);


--
-- Name: devices_zone devices_zone_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices_zone
    ADD CONSTRAINT devices_zone_code_key UNIQUE (code);


--
-- Name: devices_zone devices_zone_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices_zone
    ADD CONSTRAINT devices_zone_name_key UNIQUE (name);


--
-- Name: devices_zone devices_zone_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices_zone
    ADD CONSTRAINT devices_zone_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_celery_beat_clockedschedule django_celery_beat_clockedschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_clockedschedule
    ADD CONSTRAINT django_celery_beat_clockedschedule_pkey PRIMARY KEY (id);


--
-- Name: django_celery_beat_crontabschedule django_celery_beat_crontabschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_crontabschedule
    ADD CONSTRAINT django_celery_beat_crontabschedule_pkey PRIMARY KEY (id);


--
-- Name: django_celery_beat_intervalschedule django_celery_beat_intervalschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_intervalschedule
    ADD CONSTRAINT django_celery_beat_intervalschedule_pkey PRIMARY KEY (id);


--
-- Name: django_celery_beat_periodictask django_celery_beat_periodictask_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_periodictask
    ADD CONSTRAINT django_celery_beat_periodictask_name_key UNIQUE (name);


--
-- Name: django_celery_beat_periodictask django_celery_beat_periodictask_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_periodictask
    ADD CONSTRAINT django_celery_beat_periodictask_pkey PRIMARY KEY (id);


--
-- Name: django_celery_beat_periodictasks django_celery_beat_periodictasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_periodictasks
    ADD CONSTRAINT django_celery_beat_periodictasks_pkey PRIMARY KEY (ident);


--
-- Name: django_celery_beat_solarschedule django_celery_beat_solar_event_latitude_longitude_ba64999a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_solarschedule
    ADD CONSTRAINT django_celery_beat_solar_event_latitude_longitude_ba64999a_uniq UNIQUE (event, latitude, longitude);


--
-- Name: django_celery_beat_solarschedule django_celery_beat_solarschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_solarschedule
    ADD CONSTRAINT django_celery_beat_solarschedule_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: infractions_appeal infractions_appeal_infraction_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_appeal
    ADD CONSTRAINT infractions_appeal_infraction_id_key UNIQUE (infraction_id);


--
-- Name: infractions_appeal infractions_appeal_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_appeal
    ADD CONSTRAINT infractions_appeal_pkey PRIMARY KEY (id);


--
-- Name: infractions_detectionstatistics infractions_detectionsta_period_type_period_start_b6708d69_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_detectionstatistics
    ADD CONSTRAINT infractions_detectionsta_period_type_period_start_b6708d69_uniq UNIQUE (period_type, period_start, device_id, zone_id);


--
-- Name: infractions_detectionstatistics infractions_detectionstatistics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_detectionstatistics
    ADD CONSTRAINT infractions_detectionstatistics_pkey PRIMARY KEY (id);


--
-- Name: infractions_infraction infractions_infraction_infraction_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infraction
    ADD CONSTRAINT infractions_infraction_infraction_code_key UNIQUE (infraction_code);


--
-- Name: infractions_infraction infractions_infraction_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infraction
    ADD CONSTRAINT infractions_infraction_pkey PRIMARY KEY (id);


--
-- Name: infractions_infractionevent infractions_infractionevent_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infractionevent
    ADD CONSTRAINT infractions_infractionevent_pkey PRIMARY KEY (id);


--
-- Name: infractions_vehicledetection infractions_vehicledetection_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_vehicledetection
    ADD CONSTRAINT infractions_vehicledetection_pkey PRIMARY KEY (id);


--
-- Name: login_history login_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.login_history
    ADD CONSTRAINT login_history_pkey PRIMARY KEY (id);


--
-- Name: ml_models_mlmodel ml_models_mlmodel_model_name_version_c1172b3a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_models_mlmodel
    ADD CONSTRAINT ml_models_mlmodel_model_name_version_c1172b3a_uniq UNIQUE (model_name, version);


--
-- Name: ml_models_mlmodel ml_models_mlmodel_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_models_mlmodel
    ADD CONSTRAINT ml_models_mlmodel_pkey PRIMARY KEY (id);


--
-- Name: ml_models_mlprediction ml_models_mlprediction_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_models_mlprediction
    ADD CONSTRAINT ml_models_mlprediction_pkey PRIMARY KEY (id);


--
-- Name: notifications_notification notifications_notification_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications_notification
    ADD CONSTRAINT notifications_notification_pkey PRIMARY KEY (id);


--
-- Name: token_blacklist_blacklistedtoken token_blacklist_blacklistedtoken_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_blacklistedtoken
    ADD CONSTRAINT token_blacklist_blacklistedtoken_pkey PRIMARY KEY (id);


--
-- Name: token_blacklist_blacklistedtoken token_blacklist_blacklistedtoken_token_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_blacklistedtoken
    ADD CONSTRAINT token_blacklist_blacklistedtoken_token_id_key UNIQUE (token_id);


--
-- Name: token_blacklist_outstandingtoken token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_outstandingtoken
    ADD CONSTRAINT token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq UNIQUE (jti);


--
-- Name: token_blacklist_outstandingtoken token_blacklist_outstandingtoken_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_outstandingtoken
    ADD CONSTRAINT token_blacklist_outstandingtoken_pkey PRIMARY KEY (id);


--
-- Name: users users_dni_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_dni_key UNIQUE (dni);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users_groups users_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_pkey PRIMARY KEY (id);


--
-- Name: users_groups users_groups_user_id_group_id_fc7788e8_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_user_id_group_id_fc7788e8_uniq UNIQUE (user_id, group_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_user_permissions users_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: users_user_permissions users_user_permissions_user_id_permission_id_3b86cbdf_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_user_id_permission_id_3b86cbdf_uniq UNIQUE (user_id, permission_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: vehicles_driver vehicles_driver_document_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles_driver
    ADD CONSTRAINT vehicles_driver_document_number_key UNIQUE (document_number);


--
-- Name: vehicles_driver vehicles_driver_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles_driver
    ADD CONSTRAINT vehicles_driver_pkey PRIMARY KEY (id);


--
-- Name: vehicles_vehicle vehicles_vehicle_license_plate_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles_vehicle
    ADD CONSTRAINT vehicles_vehicle_license_plate_key UNIQUE (license_plate);


--
-- Name: vehicles_vehicle vehicles_vehicle_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles_vehicle
    ADD CONSTRAINT vehicles_vehicle_pkey PRIMARY KEY (id);


--
-- Name: vehicles_vehicleownership vehicles_vehicleownership_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles_vehicleownership
    ADD CONSTRAINT vehicles_vehicleownership_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: devices_dev_code_767230_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_dev_code_767230_idx ON public.devices_device USING btree (code);


--
-- Name: devices_dev_device__0d8d82_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_dev_device__0d8d82_idx ON public.devices_device USING btree (device_type);


--
-- Name: devices_dev_device__5b0de9_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_dev_device__5b0de9_idx ON public.devices_deviceevent USING btree (device_id, "timestamp" DESC);


--
-- Name: devices_dev_event_t_6d20f2_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_dev_event_t_6d20f2_idx ON public.devices_deviceevent USING btree (event_type, "timestamp" DESC);


--
-- Name: devices_dev_status_bbf58f_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_dev_status_bbf58f_idx ON public.devices_device USING btree (status);


--
-- Name: devices_dev_zone_id_926c7c_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_dev_zone_id_926c7c_idx ON public.devices_device USING btree (zone_id);


--
-- Name: devices_device_code_09976111_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_device_code_09976111_like ON public.devices_device USING btree (code varchar_pattern_ops);


--
-- Name: devices_device_zone_id_a6931c33; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_device_zone_id_a6931c33 ON public.devices_device USING btree (zone_id);


--
-- Name: devices_deviceevent_device_id_5294ea65; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_deviceevent_device_id_5294ea65 ON public.devices_deviceevent USING btree (device_id);


--
-- Name: devices_deviceevent_timestamp_21194ee8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_deviceevent_timestamp_21194ee8 ON public.devices_deviceevent USING btree ("timestamp");


--
-- Name: devices_zon_code_729a87_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_zon_code_729a87_idx ON public.devices_zone USING btree (code);


--
-- Name: devices_zon_is_acti_e5a7fc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_zon_is_acti_e5a7fc_idx ON public.devices_zone USING btree (is_active);


--
-- Name: devices_zone_code_f2c56271_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_zone_code_f2c56271_like ON public.devices_zone USING btree (code varchar_pattern_ops);


--
-- Name: devices_zone_name_66174faa_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX devices_zone_name_66174faa_like ON public.devices_zone USING btree (name varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_celery_beat_periodictask_clocked_id_47a69f82; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_celery_beat_periodictask_clocked_id_47a69f82 ON public.django_celery_beat_periodictask USING btree (clocked_id);


--
-- Name: django_celery_beat_periodictask_crontab_id_d3cba168; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_celery_beat_periodictask_crontab_id_d3cba168 ON public.django_celery_beat_periodictask USING btree (crontab_id);


--
-- Name: django_celery_beat_periodictask_interval_id_a8ca27da; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_celery_beat_periodictask_interval_id_a8ca27da ON public.django_celery_beat_periodictask USING btree (interval_id);


--
-- Name: django_celery_beat_periodictask_name_265a36b7_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_celery_beat_periodictask_name_265a36b7_like ON public.django_celery_beat_periodictask USING btree (name varchar_pattern_ops);


--
-- Name: django_celery_beat_periodictask_solar_id_a87ce72c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_celery_beat_periodictask_solar_id_a87ce72c ON public.django_celery_beat_periodictask USING btree (solar_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: infractions_appeal_reviewed_by_id_49a1d0f8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_appeal_reviewed_by_id_49a1d0f8 ON public.infractions_appeal USING btree (reviewed_by_id);


--
-- Name: infractions_appella_1bcf2c_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_appella_1bcf2c_idx ON public.infractions_appeal USING btree (appellant_dni);


--
-- Name: infractions_detectionstatistics_device_id_fed00d97; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_detectionstatistics_device_id_fed00d97 ON public.infractions_detectionstatistics USING btree (device_id);


--
-- Name: infractions_detectionstatistics_period_start_d3e34774; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_detectionstatistics_period_start_d3e34774 ON public.infractions_detectionstatistics USING btree (period_start);


--
-- Name: infractions_detectionstatistics_zone_id_949f69d4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_detectionstatistics_zone_id_949f69d4 ON public.infractions_detectionstatistics USING btree (zone_id);


--
-- Name: infractions_device__696240_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_device__696240_idx ON public.infractions_infraction USING btree (device_id, detected_at DESC);


--
-- Name: infractions_device__b22ab8_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_device__b22ab8_idx ON public.infractions_vehicledetection USING btree (device_id, detected_at DESC);


--
-- Name: infractions_device__fe5c84_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_device__fe5c84_idx ON public.infractions_detectionstatistics USING btree (device_id, period_start DESC);


--
-- Name: infractions_event_t_728a74_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_event_t_728a74_idx ON public.infractions_infractionevent USING btree (event_type, "timestamp" DESC);


--
-- Name: infractions_has_inf_2b770c_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_has_inf_2b770c_idx ON public.infractions_vehicledetection USING btree (has_infraction);


--
-- Name: infractions_infract_089142_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infract_089142_idx ON public.infractions_infractionevent USING btree (infraction_id, "timestamp" DESC);


--
-- Name: infractions_infract_679c79_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infract_679c79_idx ON public.infractions_appeal USING btree (infraction_id);


--
-- Name: infractions_infract_83f8da_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infract_83f8da_idx ON public.infractions_infraction USING btree (infraction_code);


--
-- Name: infractions_infract_ee0e51_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infract_ee0e51_idx ON public.infractions_infraction USING btree (infraction_type, detected_at DESC);


--
-- Name: infractions_infraction_detected_at_cf8801f5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infraction_detected_at_cf8801f5 ON public.infractions_infraction USING btree (detected_at);


--
-- Name: infractions_infraction_device_id_4291d43e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infraction_device_id_4291d43e ON public.infractions_infraction USING btree (device_id);


--
-- Name: infractions_infraction_driver_id_774bc88d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infraction_driver_id_774bc88d ON public.infractions_infraction USING btree (driver_id);


--
-- Name: infractions_infraction_infraction_code_291ce723_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infraction_infraction_code_291ce723_like ON public.infractions_infraction USING btree (infraction_code varchar_pattern_ops);


--
-- Name: infractions_infraction_reviewed_by_id_afcad296; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infraction_reviewed_by_id_afcad296 ON public.infractions_infraction USING btree (reviewed_by_id);


--
-- Name: infractions_infraction_vehicle_id_302a304c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infraction_vehicle_id_302a304c ON public.infractions_infraction USING btree (vehicle_id);


--
-- Name: infractions_infraction_zone_id_1456fb12; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infraction_zone_id_1456fb12 ON public.infractions_infraction USING btree (zone_id);


--
-- Name: infractions_infractionevent_infraction_id_a0f5a29d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infractionevent_infraction_id_a0f5a29d ON public.infractions_infractionevent USING btree (infraction_id);


--
-- Name: infractions_infractionevent_timestamp_529a1bc7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infractionevent_timestamp_529a1bc7 ON public.infractions_infractionevent USING btree ("timestamp");


--
-- Name: infractions_infractionevent_user_id_b557494f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_infractionevent_user_id_b557494f ON public.infractions_infractionevent USING btree (user_id);


--
-- Name: infractions_license_4e6e5c_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_license_4e6e5c_idx ON public.infractions_vehicledetection USING btree (license_plate_detected);


--
-- Name: infractions_license_cd67b1_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_license_cd67b1_idx ON public.infractions_infraction USING btree (license_plate_detected);


--
-- Name: infractions_period__e5d1df_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_period__e5d1df_idx ON public.infractions_detectionstatistics USING btree (period_type, period_start DESC);


--
-- Name: infractions_source_035e58_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_source_035e58_idx ON public.infractions_vehicledetection USING btree (source, detected_at DESC);


--
-- Name: infractions_status_325877_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_status_325877_idx ON public.infractions_appeal USING btree (status);


--
-- Name: infractions_status_f3736a_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_status_f3736a_idx ON public.infractions_infraction USING btree (status);


--
-- Name: infractions_vehicle_bb01cf_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_vehicle_bb01cf_idx ON public.infractions_vehicledetection USING btree (vehicle_type, detected_at DESC);


--
-- Name: infractions_vehicle_dbbc65_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_vehicle_dbbc65_idx ON public.infractions_infraction USING btree (vehicle_id);


--
-- Name: infractions_vehicledetection_detected_at_1274a0a9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_vehicledetection_detected_at_1274a0a9 ON public.infractions_vehicledetection USING btree (detected_at);


--
-- Name: infractions_vehicledetection_device_id_8b59ab3f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_vehicledetection_device_id_8b59ab3f ON public.infractions_vehicledetection USING btree (device_id);


--
-- Name: infractions_vehicledetection_infraction_id_37ea5a19; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_vehicledetection_infraction_id_37ea5a19 ON public.infractions_vehicledetection USING btree (infraction_id);


--
-- Name: infractions_vehicledetection_vehicle_id_ab143c31; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_vehicledetection_vehicle_id_ab143c31 ON public.infractions_vehicledetection USING btree (vehicle_id);


--
-- Name: infractions_vehicledetection_zone_id_9fbd9c83; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_vehicledetection_zone_id_9fbd9c83 ON public.infractions_vehicledetection USING btree (zone_id);


--
-- Name: infractions_zone_id_4187a0_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_zone_id_4187a0_idx ON public.infractions_infraction USING btree (zone_id, detected_at DESC);


--
-- Name: infractions_zone_id_e4f2de_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX infractions_zone_id_e4f2de_idx ON public.infractions_detectionstatistics USING btree (zone_id, period_start DESC);


--
-- Name: login_histo_ip_addr_9672e0_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX login_histo_ip_addr_9672e0_idx ON public.login_history USING btree (ip_address, login_at DESC);


--
-- Name: login_histo_user_id_7d22b5_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX login_histo_user_id_7d22b5_idx ON public.login_history USING btree (user_id, login_at DESC);


--
-- Name: login_history_login_at_5d8b3f90; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX login_history_login_at_5d8b3f90 ON public.login_history USING btree (login_at);


--
-- Name: login_history_user_id_0eeaebb8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX login_history_user_id_0eeaebb8 ON public.login_history USING btree (user_id);


--
-- Name: ml_models_m_deploym_14de3d_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_m_deploym_14de3d_idx ON public.ml_models_mlmodel USING btree (deployment_environment);


--
-- Name: ml_models_m_driver__5f0e92_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_m_driver__5f0e92_idx ON public.ml_models_mlprediction USING btree (driver_id, predicted_at DESC);


--
-- Name: ml_models_m_infract_ed1726_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_m_infract_ed1726_idx ON public.ml_models_mlprediction USING btree (infraction_id);


--
-- Name: ml_models_m_is_acti_afbf29_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_m_is_acti_afbf29_idx ON public.ml_models_mlmodel USING btree (is_active);


--
-- Name: ml_models_m_last_pr_205647_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_m_last_pr_205647_idx ON public.ml_models_mlmodel USING btree (last_prediction_at DESC);


--
-- Name: ml_models_m_model_i_23f478_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_m_model_i_23f478_idx ON public.ml_models_mlprediction USING btree (model_id, predicted_at DESC);


--
-- Name: ml_models_m_model_n_f508f2_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_m_model_n_f508f2_idx ON public.ml_models_mlmodel USING btree (model_name, version);


--
-- Name: ml_models_m_predict_472780_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_m_predict_472780_idx ON public.ml_models_mlprediction USING btree (prediction_type, predicted_at DESC);


--
-- Name: ml_models_mlmodel_created_by_id_f196f145; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_mlmodel_created_by_id_f196f145 ON public.ml_models_mlmodel USING btree (created_by_id);


--
-- Name: ml_models_mlmodel_deployed_by_id_ba48cf24; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_mlmodel_deployed_by_id_ba48cf24 ON public.ml_models_mlmodel USING btree (deployed_by_id);


--
-- Name: ml_models_mlprediction_driver_id_e3b1005b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_mlprediction_driver_id_e3b1005b ON public.ml_models_mlprediction USING btree (driver_id);


--
-- Name: ml_models_mlprediction_infraction_id_bd10a47a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_mlprediction_infraction_id_bd10a47a ON public.ml_models_mlprediction USING btree (infraction_id);


--
-- Name: ml_models_mlprediction_model_id_938225b6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_mlprediction_model_id_938225b6 ON public.ml_models_mlprediction USING btree (model_id);


--
-- Name: ml_models_mlprediction_predicted_at_c74fbb03; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ml_models_mlprediction_predicted_at_c74fbb03 ON public.ml_models_mlprediction USING btree (predicted_at);


--
-- Name: notificatio_created_ae6ed6_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notificatio_created_ae6ed6_idx ON public.notifications_notification USING btree (created_at DESC);


--
-- Name: notificatio_user_id_427e4b_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notificatio_user_id_427e4b_idx ON public.notifications_notification USING btree (user_id, is_read);


--
-- Name: notifications_notification_user_id_b5e8c0ff; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_notification_user_id_b5e8c0ff ON public.notifications_notification USING btree (user_id);


--
-- Name: token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_like ON public.token_blacklist_outstandingtoken USING btree (jti varchar_pattern_ops);


--
-- Name: token_blacklist_outstandingtoken_user_id_83bc629a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX token_blacklist_outstandingtoken_user_id_83bc629a ON public.token_blacklist_outstandingtoken USING btree (user_id);


--
-- Name: users_dni_b6cb98d3_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_dni_b6cb98d3_like ON public.users USING btree (dni varchar_pattern_ops);


--
-- Name: users_email_0ea73cca_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_email_0ea73cca_like ON public.users USING btree (email varchar_pattern_ops);


--
-- Name: users_email_a7cfd1_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_email_a7cfd1_idx ON public.users USING btree (email, is_active);


--
-- Name: users_groups_group_id_2f3517aa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_groups_group_id_2f3517aa ON public.users_groups USING btree (group_id);


--
-- Name: users_groups_user_id_f500bee5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_groups_user_id_f500bee5 ON public.users_groups USING btree (user_id);


--
-- Name: users_role_a8f2ba_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_role_a8f2ba_idx ON public.users USING btree (role, is_active);


--
-- Name: users_role_f0571928; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_role_f0571928 ON public.users USING btree (role);


--
-- Name: users_role_f0571928_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_role_f0571928_like ON public.users USING btree (role varchar_pattern_ops);


--
-- Name: users_user_permissions_permission_id_6d08dcd2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_user_permissions_permission_id_6d08dcd2 ON public.users_user_permissions USING btree (permission_id);


--
-- Name: users_user_permissions_user_id_92473840; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_user_permissions_user_id_92473840 ON public.users_user_permissions USING btree (user_id);


--
-- Name: users_usernam_b4c624_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_usernam_b4c624_idx ON public.users USING btree (username, is_active);


--
-- Name: users_username_e8658fc8_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_username_e8658fc8_like ON public.users USING btree (username varchar_pattern_ops);


--
-- Name: vehicles_dr_documen_45aca3_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_dr_documen_45aca3_idx ON public.vehicles_driver USING btree (document_number);


--
-- Name: vehicles_dr_is_susp_92ae1a_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_dr_is_susp_92ae1a_idx ON public.vehicles_driver USING btree (is_suspended);


--
-- Name: vehicles_dr_license_de2c16_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_dr_license_de2c16_idx ON public.vehicles_driver USING btree (license_number);


--
-- Name: vehicles_driver_document_number_92b72614_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_driver_document_number_92b72614_like ON public.vehicles_driver USING btree (document_number varchar_pattern_ops);


--
-- Name: vehicles_ve_driver__d1090b_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_ve_driver__d1090b_idx ON public.vehicles_vehicleownership USING btree (driver_id);


--
-- Name: vehicles_ve_is_prim_afe9c0_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_ve_is_prim_afe9c0_idx ON public.vehicles_vehicleownership USING btree (is_primary_owner);


--
-- Name: vehicles_ve_is_stol_f22ded_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_ve_is_stol_f22ded_idx ON public.vehicles_vehicle USING btree (is_stolen);


--
-- Name: vehicles_ve_is_want_b9a47b_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_ve_is_want_b9a47b_idx ON public.vehicles_vehicle USING btree (is_wanted);


--
-- Name: vehicles_ve_license_907c55_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_ve_license_907c55_idx ON public.vehicles_vehicle USING btree (license_plate);


--
-- Name: vehicles_ve_owner_d_b3eb80_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_ve_owner_d_b3eb80_idx ON public.vehicles_vehicle USING btree (owner_dni);


--
-- Name: vehicles_ve_vehicle_a3bb7e_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_ve_vehicle_a3bb7e_idx ON public.vehicles_vehicleownership USING btree (vehicle_id);


--
-- Name: vehicles_vehicle_license_plate_9d0c162b_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_vehicle_license_plate_9d0c162b_like ON public.vehicles_vehicle USING btree (license_plate varchar_pattern_ops);


--
-- Name: vehicles_vehicleownership_driver_id_55a24c8f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_vehicleownership_driver_id_55a24c8f ON public.vehicles_vehicleownership USING btree (driver_id);


--
-- Name: vehicles_vehicleownership_vehicle_id_69ab1291; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vehicles_vehicleownership_vehicle_id_69ab1291 ON public.vehicles_vehicleownership USING btree (vehicle_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devices_device devices_device_zone_id_a6931c33_fk_devices_zone_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices_device
    ADD CONSTRAINT devices_device_zone_id_a6931c33_fk_devices_zone_id FOREIGN KEY (zone_id) REFERENCES public.devices_zone(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devices_deviceevent devices_deviceevent_device_id_5294ea65_fk_devices_device_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices_deviceevent
    ADD CONSTRAINT devices_deviceevent_device_id_5294ea65_fk_devices_device_id FOREIGN KEY (device_id) REFERENCES public.devices_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_celery_beat_periodictask django_celery_beat_p_clocked_id_47a69f82_fk_django_ce; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_periodictask
    ADD CONSTRAINT django_celery_beat_p_clocked_id_47a69f82_fk_django_ce FOREIGN KEY (clocked_id) REFERENCES public.django_celery_beat_clockedschedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_celery_beat_periodictask django_celery_beat_p_crontab_id_d3cba168_fk_django_ce; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_periodictask
    ADD CONSTRAINT django_celery_beat_p_crontab_id_d3cba168_fk_django_ce FOREIGN KEY (crontab_id) REFERENCES public.django_celery_beat_crontabschedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_celery_beat_periodictask django_celery_beat_p_interval_id_a8ca27da_fk_django_ce; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_periodictask
    ADD CONSTRAINT django_celery_beat_p_interval_id_a8ca27da_fk_django_ce FOREIGN KEY (interval_id) REFERENCES public.django_celery_beat_intervalschedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_celery_beat_periodictask django_celery_beat_p_solar_id_a87ce72c_fk_django_ce; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_celery_beat_periodictask
    ADD CONSTRAINT django_celery_beat_p_solar_id_a87ce72c_fk_django_ce FOREIGN KEY (solar_id) REFERENCES public.django_celery_beat_solarschedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_appeal infractions_appeal_infraction_id_75273a24_fk_infractio; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_appeal
    ADD CONSTRAINT infractions_appeal_infraction_id_75273a24_fk_infractio FOREIGN KEY (infraction_id) REFERENCES public.infractions_infraction(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_appeal infractions_appeal_reviewed_by_id_49a1d0f8_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_appeal
    ADD CONSTRAINT infractions_appeal_reviewed_by_id_49a1d0f8_fk_users_id FOREIGN KEY (reviewed_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_detectionstatistics infractions_detectio_device_id_fed00d97_fk_devices_d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_detectionstatistics
    ADD CONSTRAINT infractions_detectio_device_id_fed00d97_fk_devices_d FOREIGN KEY (device_id) REFERENCES public.devices_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_detectionstatistics infractions_detectio_zone_id_949f69d4_fk_devices_z; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_detectionstatistics
    ADD CONSTRAINT infractions_detectio_zone_id_949f69d4_fk_devices_z FOREIGN KEY (zone_id) REFERENCES public.devices_zone(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_infractionevent infractions_infracti_infraction_id_a0f5a29d_fk_infractio; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infractionevent
    ADD CONSTRAINT infractions_infracti_infraction_id_a0f5a29d_fk_infractio FOREIGN KEY (infraction_id) REFERENCES public.infractions_infraction(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_infraction infractions_infracti_vehicle_id_302a304c_fk_vehicles_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infraction
    ADD CONSTRAINT infractions_infracti_vehicle_id_302a304c_fk_vehicles_ FOREIGN KEY (vehicle_id) REFERENCES public.vehicles_vehicle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_infraction infractions_infraction_device_id_4291d43e_fk_devices_device_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infraction
    ADD CONSTRAINT infractions_infraction_device_id_4291d43e_fk_devices_device_id FOREIGN KEY (device_id) REFERENCES public.devices_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_infraction infractions_infraction_driver_id_774bc88d_fk_vehicles_driver_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infraction
    ADD CONSTRAINT infractions_infraction_driver_id_774bc88d_fk_vehicles_driver_id FOREIGN KEY (driver_id) REFERENCES public.vehicles_driver(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_infraction infractions_infraction_reviewed_by_id_afcad296_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infraction
    ADD CONSTRAINT infractions_infraction_reviewed_by_id_afcad296_fk_users_id FOREIGN KEY (reviewed_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_infraction infractions_infraction_zone_id_1456fb12_fk_devices_zone_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infraction
    ADD CONSTRAINT infractions_infraction_zone_id_1456fb12_fk_devices_zone_id FOREIGN KEY (zone_id) REFERENCES public.devices_zone(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_infractionevent infractions_infractionevent_user_id_b557494f_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_infractionevent
    ADD CONSTRAINT infractions_infractionevent_user_id_b557494f_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_vehicledetection infractions_vehicled_device_id_8b59ab3f_fk_devices_d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_vehicledetection
    ADD CONSTRAINT infractions_vehicled_device_id_8b59ab3f_fk_devices_d FOREIGN KEY (device_id) REFERENCES public.devices_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_vehicledetection infractions_vehicled_infraction_id_37ea5a19_fk_infractio; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_vehicledetection
    ADD CONSTRAINT infractions_vehicled_infraction_id_37ea5a19_fk_infractio FOREIGN KEY (infraction_id) REFERENCES public.infractions_infraction(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_vehicledetection infractions_vehicled_vehicle_id_ab143c31_fk_vehicles_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_vehicledetection
    ADD CONSTRAINT infractions_vehicled_vehicle_id_ab143c31_fk_vehicles_ FOREIGN KEY (vehicle_id) REFERENCES public.vehicles_vehicle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: infractions_vehicledetection infractions_vehicled_zone_id_9fbd9c83_fk_devices_z; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.infractions_vehicledetection
    ADD CONSTRAINT infractions_vehicled_zone_id_9fbd9c83_fk_devices_z FOREIGN KEY (zone_id) REFERENCES public.devices_zone(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: login_history login_history_user_id_0eeaebb8_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.login_history
    ADD CONSTRAINT login_history_user_id_0eeaebb8_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ml_models_mlmodel ml_models_mlmodel_created_by_id_f196f145_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_models_mlmodel
    ADD CONSTRAINT ml_models_mlmodel_created_by_id_f196f145_fk_users_id FOREIGN KEY (created_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ml_models_mlmodel ml_models_mlmodel_deployed_by_id_ba48cf24_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_models_mlmodel
    ADD CONSTRAINT ml_models_mlmodel_deployed_by_id_ba48cf24_fk_users_id FOREIGN KEY (deployed_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ml_models_mlprediction ml_models_mlpredicti_infraction_id_bd10a47a_fk_infractio; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_models_mlprediction
    ADD CONSTRAINT ml_models_mlpredicti_infraction_id_bd10a47a_fk_infractio FOREIGN KEY (infraction_id) REFERENCES public.infractions_infraction(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ml_models_mlprediction ml_models_mlpredicti_model_id_938225b6_fk_ml_models; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_models_mlprediction
    ADD CONSTRAINT ml_models_mlpredicti_model_id_938225b6_fk_ml_models FOREIGN KEY (model_id) REFERENCES public.ml_models_mlmodel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ml_models_mlprediction ml_models_mlprediction_driver_id_e3b1005b_fk_vehicles_driver_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_models_mlprediction
    ADD CONSTRAINT ml_models_mlprediction_driver_id_e3b1005b_fk_vehicles_driver_id FOREIGN KEY (driver_id) REFERENCES public.vehicles_driver(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: notifications_notification notifications_notification_user_id_b5e8c0ff_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications_notification
    ADD CONSTRAINT notifications_notification_user_id_b5e8c0ff_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: token_blacklist_blacklistedtoken token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_blacklistedtoken
    ADD CONSTRAINT token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk FOREIGN KEY (token_id) REFERENCES public.token_blacklist_outstandingtoken(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: token_blacklist_outstandingtoken token_blacklist_outstandingtoken_user_id_83bc629a_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist_outstandingtoken
    ADD CONSTRAINT token_blacklist_outstandingtoken_user_id_83bc629a_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_groups users_groups_group_id_2f3517aa_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_group_id_2f3517aa_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_groups users_groups_user_id_f500bee5_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_user_id_f500bee5_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_permissions users_user_permissio_permission_id_6d08dcd2_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissio_permission_id_6d08dcd2_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_permissions users_user_permissions_user_id_92473840_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_user_id_92473840_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: vehicles_vehicleownership vehicles_vehicleowne_driver_id_55a24c8f_fk_vehicles_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles_vehicleownership
    ADD CONSTRAINT vehicles_vehicleowne_driver_id_55a24c8f_fk_vehicles_ FOREIGN KEY (driver_id) REFERENCES public.vehicles_driver(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: vehicles_vehicleownership vehicles_vehicleowne_vehicle_id_69ab1291_fk_vehicles_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles_vehicleownership
    ADD CONSTRAINT vehicles_vehicleowne_vehicle_id_69ab1291_fk_vehicles_ FOREIGN KEY (vehicle_id) REFERENCES public.vehicles_vehicle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict r4QjZIlLQRTUcHt0EeRCfKH0vGSJqECEv9XQheO9OmXGQn19Va2Xo1QUFOWnE92

