-- Gold: chieu kenh ban. Kenh san (Grab/Shopee) duoc ghi vao POS khi cua hang nhan don,
-- con so don hoan thanh/hoa hong lay tu bao cao doi soat hang tuan cua san.
select * from (values
    ('WALKIN',     'Tai quay',   'IN_STORE',    'POS',                   false),
    ('APP',        'App rieng',  'OWNED_APP',   'App',                   false),
    ('GRABFOOD',   'GrabFood',   'MARKETPLACE', 'POS + doi soat Grab',   true),
    ('SHOPEEFOOD', 'ShopeeFood', 'MARKETPLACE', 'POS + doi soat Shopee', true)
) as t(channel, channel_name, channel_group, source_systems, has_commission)
