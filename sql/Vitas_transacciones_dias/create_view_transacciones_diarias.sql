CREATE OR REPLACE VIEW transacciones_diarias AS
SELECT
    c.id AS company_id,
    c.company_name,
    ch.updated_at::DATE AS fecha_pago,
    ROUND(SUM(ch.amount::numeric), 2) AS monto_total
FROM
    charges ch
JOIN
    companies c ON ch.company_id = c.id
WHERE
    ch.updated_at IS NOT NULL
    AND ch.status = 'paid'
GROUP BY
    c.id, c.company_name, ch.updated_at::DATE
ORDER BY
    fecha_pago DESC;
