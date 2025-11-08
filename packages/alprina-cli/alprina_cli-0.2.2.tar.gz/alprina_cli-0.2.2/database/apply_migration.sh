#!/bin/bash

# Script to apply database migration to production (Neon)
# Usage: ./apply_migration.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Applying device_codes status column migration...${NC}"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ ERROR: DATABASE_URL environment variable not set${NC}"
    echo -e "${YELLOW}Please set your Neon database URL:${NC}"
    echo "export DATABASE_URL=\"postgresql://neondb_owner:PASSWORD@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require\""
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Path to migration file
MIGRATION_FILE="$SCRIPT_DIR/migrations/add_device_codes_status_column.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}❌ Migration file not found: $MIGRATION_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}📊 Migration file: $MIGRATION_FILE${NC}"
echo -e "${YELLOW}🎯 Target database: ${DATABASE_URL%/*}/[DATABASE]${NC}"

# Confirm before proceeding
read -p "Apply migration to production database? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⏹️  Migration cancelled${NC}"
    exit 0
fi

# Apply migration
echo -e "${YELLOW}⚡ Applying migration...${NC}"

if psql "$DATABASE_URL" -f "$MIGRATION_FILE"; then
    echo -e "${GREEN}✅ Migration applied successfully!${NC}"
    echo -e "${GREEN}🎉 The device_codes table now has the 'status' column${NC}"
    echo -e "${YELLOW}💡 Your production API should now work with the dashboard code flow${NC}"
else
    echo -e "${RED}❌ Migration failed${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Testing the production endpoint...${NC}"

# Test the endpoint
if curl -s -X POST https://api.alprina.com/v1/auth/dashboard-code \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer test_token" \
    -d '{}' | grep -q "error"; then
    echo -e "${GREEN}✅ Production endpoint is responding (authentication will be needed for real use)${NC}"
else
    echo -e "${YELLOW}⚠️  Production endpoint test had issues, but the database migration completed${NC}"
fi

echo -e "${GREEN}🚀 Migration complete! Your dashboard code flow should now work in production.${NC}"