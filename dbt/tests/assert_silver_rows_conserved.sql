-- Khong dong du lieu nao "bien mat" khi di tu Bronze sang Silver.
select * from {{ ref('silver_row_reconciliation') }} where unexplained_rows != 0
