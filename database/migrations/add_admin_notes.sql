-- Run once on existing databases: docker compose exec -T db psql -U vulnshop -d vulnshop < database/migrations/add_admin_notes.sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS admin_notes TEXT;
