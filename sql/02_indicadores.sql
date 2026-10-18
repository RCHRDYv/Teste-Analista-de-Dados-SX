-- Indicadores do teste, calculados sobre o esquema estrela.
-- As definições estão no ADR-0006 (docs/adr/0006-definicoes-das-metricas.md).
-- Cada consulta começa com uma linha "-- name: <nome>", usada pelo script
-- src/analise/indicadores_sql.py para executar e nomear o resultado.

-- name: q1_escola_maior_media
-- Pergunta 1. Sem CO_ESCOLA (ADR-0005), o nível mais fino é o grupo
-- município da escola x dependência administrativa x localização, com
-- pelo menos 30 participantes presentes nas quatro provas.
SELECT
    e.no_municipio_esc            AS municipio_escola,
    e.sg_uf_esc                   AS uf_escola,
    e.ds_dependencia_adm_esc      AS dependencia_adm,
    e.ds_localizacao_esc          AS localizacao,
    COUNT(*)                      AS participantes,
    ROUND(AVG(f.nu_media_objetivas), 2) AS media
FROM fato_participacao f
JOIN dim_escola e ON e.sk_escola = f.sk_escola
WHERE f.sk_escola <> 0
  AND f.nu_media_objetivas IS NOT NULL
GROUP BY e.co_municipio_esc, e.no_municipio_esc, e.sg_uf_esc,
         e.tp_dependencia_adm_esc, e.ds_dependencia_adm_esc,
         e.tp_localizacao_esc, e.ds_localizacao_esc
HAVING COUNT(*) >= 30
ORDER BY media DESC
LIMIT 10;

-- name: q2_aluno_maior_media
-- Pergunta 2. Lista todas as inscrições empatadas na maior média.
SELECT
    f.nu_inscricao,
    f.nu_media_objetivas AS media,
    f.nu_nota_cn, f.nu_nota_ch, f.nu_nota_lc, f.nu_nota_mt
FROM fato_participacao f
WHERE f.nu_media_objetivas = (SELECT MAX(nu_media_objetivas) FROM fato_participacao)
ORDER BY f.nu_inscricao;

-- name: q3_media_geral
-- Pergunta 3. Média das médias dos participantes presentes nas quatro
-- provas e, ao lado, a média simples de todas as notas objetivas.
SELECT
    ROUND(AVG(nu_media_objetivas), 2) AS media_das_medias,
    COUNT(nu_media_objetivas)         AS participantes_quatro_provas,
    ROUND(
        (SUM(nu_nota_cn) + SUM(nu_nota_ch) + SUM(nu_nota_lc) + SUM(nu_nota_mt))
        / (COUNT(nu_nota_cn) + COUNT(nu_nota_ch) + COUNT(nu_nota_lc) + COUNT(nu_nota_mt)),
        2
    ) AS media_de_todas_as_notas
FROM fato_participacao;

-- name: q4_percentual_ausentes
-- Pergunta 4. Ausente = faltou (código 0). Eliminado (código 2) não conta.
-- Dia 1: LC, CH e redação. Dia 2: CN e MT.
SELECT
    ROUND(100 * AVG(tp_presenca_lc = 0 OR tp_presenca_ch = 0
                 OR tp_presenca_cn = 0 OR tp_presenca_mt = 0), 2) AS pct_ausente_algum_dia,
    ROUND(100 * AVG(tp_presenca_lc = 0 OR tp_presenca_ch = 0), 2) AS pct_ausente_dia_1,
    ROUND(100 * AVG(tp_presenca_cn = 0 OR tp_presenca_mt = 0), 2) AS pct_ausente_dia_2,
    ROUND(100 * AVG(tp_presenca_lc = 0 AND tp_presenca_ch = 0
                 AND tp_presenca_cn = 0 AND tp_presenca_mt = 0), 2) AS pct_ausente_dois_dias,
    ROUND(100 * AVG(tp_presenca_cn = 0), 2) AS pct_ausente_cn,
    ROUND(100 * AVG(tp_presenca_ch = 0), 2) AS pct_ausente_ch,
    ROUND(100 * AVG(tp_presenca_lc = 0), 2) AS pct_ausente_lc,
    ROUND(100 * AVG(tp_presenca_mt = 0), 2) AS pct_ausente_mt
FROM fato_participacao;

-- name: q5_total_inscritos
-- Pergunta 5. Uma linha por inscrição.
SELECT COUNT(*) AS total_inscritos
FROM fato_participacao;

-- name: q6_media_por_disciplina
-- Pergunta 6. Média de cada prova entre os presentes naquela prova.
-- A redação considera quem teve redação corrigida (status diferente de 0),
-- incluindo as notas zero de redações anuladas ou em branco.
SELECT 'Ciências da Natureza' AS disciplina, ROUND(AVG(nu_nota_cn), 2) AS media,
       COUNT(nu_nota_cn) AS participantes
FROM fato_participacao WHERE tp_presenca_cn = 1
UNION ALL
SELECT 'Ciências Humanas', ROUND(AVG(nu_nota_ch), 2), COUNT(nu_nota_ch)
FROM fato_participacao WHERE tp_presenca_ch = 1
UNION ALL
SELECT 'Linguagens e Códigos', ROUND(AVG(nu_nota_lc), 2), COUNT(nu_nota_lc)
FROM fato_participacao WHERE tp_presenca_lc = 1
UNION ALL
SELECT 'Matemática', ROUND(AVG(nu_nota_mt), 2), COUNT(nu_nota_mt)
FROM fato_participacao WHERE tp_presenca_mt = 1
UNION ALL
SELECT 'Redação', ROUND(AVG(nu_nota_redacao), 2), COUNT(nu_nota_redacao)
FROM fato_participacao WHERE tp_status_redacao <> 0;

-- name: q7_media_por_sexo
-- Pergunta 7. Média do participante (quatro provas objetivas) por sexo.
SELECT
    p.ds_sexo                          AS sexo,
    COUNT(*)                           AS participantes,
    ROUND(AVG(f.nu_media_objetivas), 2) AS media
FROM fato_participacao f
JOIN dim_perfil p ON p.sk_perfil = f.sk_perfil
WHERE f.nu_media_objetivas IS NOT NULL
GROUP BY p.tp_sexo, p.ds_sexo
ORDER BY media DESC;

-- name: q8_media_por_cor_raca
-- Pergunta 8. Média do participante por cor/raça (a "etnia" do enunciado).
SELECT
    p.ds_cor_raca                      AS cor_raca,
    COUNT(*)                           AS participantes,
    ROUND(AVG(f.nu_media_objetivas), 2) AS media
FROM fato_participacao f
JOIN dim_perfil p ON p.sk_perfil = f.sk_perfil
WHERE f.nu_media_objetivas IS NOT NULL
GROUP BY p.tp_cor_raca, p.ds_cor_raca
ORDER BY media DESC;
