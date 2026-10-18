-- Esquema estrela dos microdados do ENEM 2020 (ADR-0002).
-- Grão do fato: uma linha por inscrição.
-- Executado automaticamente pelo MySQL na primeira subida do container,
-- dentro do banco definido em MYSQL_DATABASE.

-- ---------------------------------------------------------------------------
-- Dimensões
-- ---------------------------------------------------------------------------

-- Perfil do participante: dimensão junk com atributos de baixa cardinalidade.
CREATE TABLE dim_perfil (
    sk_perfil          INT          NOT NULL,
    tp_faixa_etaria    TINYINT      NOT NULL,
    ds_faixa_etaria    VARCHAR(30)  NOT NULL,
    tp_sexo            CHAR(1)      NOT NULL,
    ds_sexo            VARCHAR(10)  NOT NULL,
    tp_estado_civil    TINYINT      NOT NULL,
    ds_estado_civil    VARCHAR(40)  NOT NULL,
    tp_cor_raca        TINYINT      NOT NULL,
    ds_cor_raca        VARCHAR(20)  NOT NULL,
    tp_nacionalidade   TINYINT      NOT NULL,
    ds_nacionalidade   VARCHAR(50)  NOT NULL,
    tp_st_conclusao    TINYINT      NOT NULL,
    ds_st_conclusao    VARCHAR(60)  NOT NULL,
    tp_escola          TINYINT      NOT NULL,
    ds_escola          VARCHAR(20)  NOT NULL,
    in_treineiro       TINYINT      NOT NULL,
    ds_treineiro       VARCHAR(5)   NOT NULL,
    tp_lingua          TINYINT      NOT NULL,
    ds_lingua          VARCHAR(10)  NOT NULL,
    PRIMARY KEY (sk_perfil)
) ENGINE=InnoDB COMMENT='Perfil do participante (dimensão junk)';

-- Escola declarada pelo participante. O Inep não publica CO_ESCOLA desde 2020
-- (ADR-0005), então a dimensão guarda os atributos disponíveis da escola.
-- A linha sk_escola = 0 representa "escola não informada".
CREATE TABLE dim_escola (
    sk_escola               INT          NOT NULL,
    co_municipio_esc        INT          NULL,
    no_municipio_esc        VARCHAR(150) NOT NULL,
    co_uf_esc               TINYINT      NULL,
    sg_uf_esc               CHAR(2)      NULL,
    tp_dependencia_adm_esc  TINYINT      NULL,
    ds_dependencia_adm_esc  VARCHAR(20)  NOT NULL,
    tp_localizacao_esc      TINYINT      NULL,
    ds_localizacao_esc      VARCHAR(20)  NOT NULL,
    tp_sit_func_esc         TINYINT      NULL,
    ds_sit_func_esc         VARCHAR(40)  NOT NULL,
    PRIMARY KEY (sk_escola)
) ENGINE=InnoDB COMMENT='Escola declarada (sem CO_ESCOLA)';

-- Município de aplicação da prova.
CREATE TABLE dim_local_prova (
    sk_local_prova      INT          NOT NULL,
    co_municipio_prova  INT          NOT NULL,
    no_municipio_prova  VARCHAR(150) NOT NULL,
    co_uf_prova         TINYINT      NOT NULL,
    sg_uf_prova         CHAR(2)      NOT NULL,
    PRIMARY KEY (sk_local_prova)
) ENGINE=InnoDB COMMENT='Local de aplicação da prova';

-- Situação da redação, decodificada a partir do dicionário do Inep.
-- A linha tp_status_redacao = 0 representa "sem redação" (faltou ao dia 1).
CREATE TABLE dim_status_redacao (
    tp_status_redacao  TINYINT     NOT NULL,
    ds_status_redacao  VARCHAR(40) NOT NULL,
    PRIMARY KEY (tp_status_redacao)
) ENGINE=InnoDB COMMENT='Situação da redação';

-- Questionário socioeconômico: mini-dimensão 1:1 com o fato.
CREATE TABLE dim_questionario (
    nu_inscricao  BIGINT     NOT NULL,
    q001 CHAR(1) NULL, q002 CHAR(1) NULL, q003 CHAR(1) NULL, q004 CHAR(1) NULL,
    q005 TINYINT NULL,
    q006 CHAR(1) NULL, q007 CHAR(1) NULL, q008 CHAR(1) NULL, q009 CHAR(1) NULL,
    q010 CHAR(1) NULL, q011 CHAR(1) NULL, q012 CHAR(1) NULL, q013 CHAR(1) NULL,
    q014 CHAR(1) NULL, q015 CHAR(1) NULL, q016 CHAR(1) NULL, q017 CHAR(1) NULL,
    q018 CHAR(1) NULL, q019 CHAR(1) NULL, q020 CHAR(1) NULL, q021 CHAR(1) NULL,
    q022 CHAR(1) NULL, q023 CHAR(1) NULL, q024 CHAR(1) NULL, q025 CHAR(1) NULL,
    PRIMARY KEY (nu_inscricao)
) ENGINE=InnoDB COMMENT='Questionário socioeconômico (Q001 a Q025)';

-- ---------------------------------------------------------------------------
-- Fato
-- ---------------------------------------------------------------------------

-- Presença: 0 = faltou, 1 = presente, 2 = eliminado (dicionário do Inep).
-- nu_media_objetivas: média das quatro provas objetivas, preenchida só para
-- quem esteve presente nas quatro (ADR-0006).
CREATE TABLE fato_participacao (
    nu_inscricao        BIGINT       NOT NULL,
    sk_perfil           INT          NOT NULL,
    sk_escola           INT          NOT NULL,
    sk_local_prova      INT          NOT NULL,
    tp_status_redacao   TINYINT      NOT NULL,
    tp_presenca_cn      TINYINT      NOT NULL,
    tp_presenca_ch      TINYINT      NOT NULL,
    tp_presenca_lc      TINYINT      NOT NULL,
    tp_presenca_mt      TINYINT      NOT NULL,
    nu_nota_cn          DECIMAL(5,1) NULL,
    nu_nota_ch          DECIMAL(5,1) NULL,
    nu_nota_lc          DECIMAL(5,1) NULL,
    nu_nota_mt          DECIMAL(5,1) NULL,
    nu_nota_comp1       SMALLINT     NULL,
    nu_nota_comp2       SMALLINT     NULL,
    nu_nota_comp3       SMALLINT     NULL,
    nu_nota_comp4       SMALLINT     NULL,
    nu_nota_comp5       SMALLINT     NULL,
    nu_nota_redacao     SMALLINT     NULL,
    nu_media_objetivas  DECIMAL(7,3) NULL,
    PRIMARY KEY (nu_inscricao),
    CONSTRAINT fk_fato_perfil   FOREIGN KEY (sk_perfil)         REFERENCES dim_perfil (sk_perfil),
    CONSTRAINT fk_fato_escola   FOREIGN KEY (sk_escola)         REFERENCES dim_escola (sk_escola),
    CONSTRAINT fk_fato_local    FOREIGN KEY (sk_local_prova)    REFERENCES dim_local_prova (sk_local_prova),
    CONSTRAINT fk_fato_redacao  FOREIGN KEY (tp_status_redacao) REFERENCES dim_status_redacao (tp_status_redacao),
    CONSTRAINT fk_fato_quest    FOREIGN KEY (nu_inscricao)      REFERENCES dim_questionario (nu_inscricao)
) ENGINE=InnoDB COMMENT='Participação no ENEM 2020, uma linha por inscrição';
