# WORKFLOW DỮ LIỆU — từ file gốc đến kho dữ liệu truy vấn được

> Dùng để trình bày "sản phẩm nhập dữ liệu thế nào" trước hội đồng. Mọi số liệu dưới đây lấy từ máy thật, không phải lý thuyết.

## 1. Data gốc nằm ở đâu — trả lời thẳng

```
D:\khoaluan\data\calibration\source_systems\      <- DATA GỐC, file thật, đọc được bằng Excel/VS Code
  ├── pos\              2.013 file JSON   (11 chi nhánh × ~183 ngày)
  │     └── POS-01\pos_export_2024-03-11.json
  ├── owned_app\          183 file JSON   (1 file/ngày, gộp 11 chi nhánh)
  ├── grabfood\            26 file CSV    (1 file/tuần)
  ├── shopeefood\          26 file Excel  (1 file/tuần)
  ├── warehouse_receipts\ 1.710 file Excel (phiếu nhập kho, 2 mẫu khác nhau)
  │     └── CN01\NhapKho_CN01_20240313.xlsx
  ├── stock_counts\        143 file Excel (phiếu kiểm kê, 2 tuần/lần)
  ├── timekeeping\        2.013 file CSV  (log chấm công)
  ├── external\             183 file JSON (thời tiết)
  └── master_data\           11 file CSV  (danh mục: chi nhánh, món, nhân viên...)
```

Đây là **dữ liệu thô 100% chưa qua xử lý** — mở thẳng bằng Excel hoặc trong trang "File nguồn" (localhost:8503) là thấy nguyên bản.

## 2. Workflow nhập dữ liệu — đúng những gì đang chạy thật

```
BƯỚC 1: file thô nằm trên đĩa (source_systems/)
            │
            │  lệnh: python -m pipeline.ingest --profile calibration
            ▼
BƯỚC 2: pipeline/ingest.py đọc từng file, GIỮ NGUYÊN giá trị gốc,
         chỉ thêm thông tin truy vết (file nào, dòng nào, lúc nào nạp)
            │
            ▼
BƯỚC 3: ghi vào fastfat.duckdb, schema "bronze"
         (data\calibration\warehouse\fastfat.duckdb — 1 file duy nhất, 324 MB)
            │
            │  lệnh: python -m pipeline.run_dbt --profile calibration build
            ▼
BƯỚC 4: dbt đọc schema "bronze", làm sạch + chuẩn hóa
            │
            ▼
BƯỚC 5: ghi kết quả vào CÙNG FILE fastfat.duckdb, schema "silver"
            │
            ▼
(sắp làm) BƯỚC 6: dbt tổ chức lại thành schema "gold" — kho dữ liệu hình sao
```

**Điểm quan trọng khi trình bày:** Bronze và Silver không phải 2 nơi khác nhau — chúng là **2 schema trong cùng 1 file `fastfat.duckdb`**, giống như 2 "ngăn" trong cùng 1 tủ. Gold sắp tới cũng sẽ là ngăn thứ 3 trong chính file đó.

## 3. Cách mở kho dữ liệu để truy vấn (giống một CSDL thật)

```
powershell -File tools\open_warehouse.ps1 calibration
```

Lệnh này mở **Harlequin** — một IDE SQL chạy trong terminal, có cây schema/bảng bên trái, ô gõ SQL, bảng kết quả bên phải — đúng trải nghiệm "kết nối và truy vấn kho dữ liệu" mà một CSDL thật (Postgres, Snowflake...) mang lại, chỉ khác là không cần server, không cần mật khẩu, vì DuckDB là CSDL nhúng (embedded) chạy ngay trong tiến trình, không phải là một dịch vụ mạng.

Khi mở lên, gõ thử để demo:
```sql
show all tables;                              -- liệt kê toàn bộ bảng trong bronze + silver
select * from silver.silver_row_reconciliation;  -- bảng đối soát số dòng
select * from bronze.pos_receipts limit 5;    -- dữ liệu Bronze thô
select * from silver.stg_pos__receipts limit 5; -- dữ liệu Silver đã sạch
```

## 4. Vì sao chọn kiến trúc này (nếu bị hỏi)

> "Em dùng DuckDB — một cơ sở dữ liệu phân tích dạng nhúng, không chạy server riêng, toàn bộ kho nằm trong 1 file. Vì quy mô dữ liệu của em chỉ khoảng 600MB–1GB, dùng Postgres hay cụm Spark sẽ là chồng công nghệ không cần thiết. Khi triển khai thật với dữ liệu lớn hơn, kiến trúc Medallion (Bronze/Silver/Gold) này có thể chuyển sang Postgres hoặc Snowflake mà không phải viết lại logic, vì toàn bộ xử lý đã viết bằng SQL chuẩn qua dbt."
