-- =========================================================================
-- MODULE: Administration Oracle et Intelligence Artificielle
-- MINI-PROJET: Maintenance Prédictive des Tablespaces
-- SCRIPT CORRIGÉ: Compatible Oracle 11g / 12c+ (Sequence & Trigger)
-- =========================================================================

-- 1. Donner le quota à SYSTEM sur le tablespace
ALTER USER SYSTEM QUOTA UNLIMITED ON TS_ADMIN_IA;

-- 2. Supprimer l'ancienne table si elle existe
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE ts_space_history CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

-- 3. Supprimer l'ancienne séquence si elle existe
BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE seq_ts_space_history';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -2289 THEN
         RAISE;
      END IF;
END;
/

-- 4. Création de la table SANS IDENTITY
CREATE TABLE ts_space_history (
    id_mesure NUMBER NOT NULL,
    date_mesure DATE DEFAULT SYSDATE,
    tablespace_name VARCHAR2(30),
    used_space_mb NUMBER(10, 2),
    max_space_mb NUMBER(10, 2),
    pct_used NUMBER(5, 2),
    CONSTRAINT pk_ts_space_history PRIMARY KEY (id_mesure)
) TABLESPACE TS_ADMIN_IA;

-- 5. Création de la séquence pour générer automatiquement les ID
CREATE SEQUENCE seq_ts_space_history
START WITH 1
INCREMENT BY 1
NOCACHE;

-- 6. Trigger pour remplir id_mesure automatiquement
CREATE OR REPLACE TRIGGER trg_ts_space_history_bi
BEFORE INSERT ON ts_space_history
FOR EACH ROW
BEGIN
   IF :NEW.id_mesure IS NULL THEN
      SELECT seq_ts_space_history.NEXTVAL
      INTO :NEW.id_mesure
      FROM dual;
   END IF;
END;
/

-- 7. Insertion de données simulées réalistes
INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-05-28', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 5.20, 50.00, 10.40);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-05-29', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 8.70, 50.00, 17.40);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-05-30', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 12.10, 50.00, 24.20);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-05-31', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 14.80, 50.00, 29.60);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-06-01', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 19.30, 50.00, 38.60);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-06-02', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 22.10, 50.00, 44.20);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-06-03', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 26.50, 50.00, 53.00);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-06-04', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 31.00, 50.00, 62.00);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-06-05', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 33.40, 50.00, 66.80);

INSERT INTO ts_space_history (date_mesure, tablespace_name, used_space_mb, max_space_mb, pct_used)
VALUES (TO_DATE('2026-06-06', 'YYYY-MM-DD'), 'TS_ADMIN_IA', 38.20, 50.00, 76.40);

COMMIT;

-- 8. Vérification
SELECT 
    TO_CHAR(date_mesure, 'YYYY-MM-DD') AS jour,
    used_space_mb,
    max_space_mb,
    pct_used
FROM ts_space_history
WHERE tablespace_name = 'TS_ADMIN_IA'
ORDER BY date_mesure ASC;