-- Migration: Add status column to device_codes table for dashboard code flow
-- Date: 2025-11-07
-- Description: Adds missing 'status' column needed for the new dashboard-code authentication flow

-- Step 1: Add the status column if it doesn't exist
ALTER TABLE device_codes
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending';

-- Step 2: Create index on status for performance
CREATE INDEX IF NOT EXISTS idx_device_codes_status ON device_codes(status);

-- Step 3: Update existing records to have 'pending' status if null
UPDATE device_codes
SET status = 'pending'
WHERE status IS NULL;

-- Step 4: Add constraint to ensure status has valid values
ALTER TABLE device_codes
ADD CONSTRAINT IF NOT EXISTS chk_device_codes_status
CHECK (status IN ('pending', 'authorized', 'expired', 'used'));

-- Verify the migration
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'device_codes'
ORDER BY ordinal_position;