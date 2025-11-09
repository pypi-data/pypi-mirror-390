# CLI Syntax Update Summary

**Date:** November 8, 2025  
**Change:** Simplified CLI syntax from verbose flags to positional arguments

---

## What Changed

### Old Syntax (Deprecated)
```bash
# Create room
mact create --project MyProject --subdomain dev-alice-myproject --local-port 3000

# Join room
mact join --room MyProject --subdomain dev-bob-myproject --local-port 3001
```

### New Syntax (Current)
```bash
# Create room (subdomain auto-generated)
mact create MyProject -port 3000

# Join room (subdomain auto-generated)
mact join MyProject -port 3001
```

---

## Key Improvements

1. **Positional project name** - No more `--project` or `--room` flag
2. **Shorter port syntax** - `-port 3000` instead of `--local-port 3000`
3. **Auto-generated subdomains** - Format: `dev-{developer}-{project}`
4. **Backward compatible** - Old flags still work (for now)

---

## Auto-Generated Subdomains

The CLI now automatically generates subdomains based on:
- Developer name (from `mact init --name`)
- Project name (from create/join command)

**Format:** `dev-{developer}-{project}`

**Examples:**
```bash
# Alice creates "TelegramBot"
mact init --name alice
mact create TelegramBot -port 3000
# Subdomain: dev-alice-telegrambot

# Bob joins "TelegramBot"
mact init --name bob
mact join TelegramBot -port 3001
# Subdomain: dev-bob-telegrambot
```

---

## Migration Guide

### For Users
No action needed. Old syntax still works:
```bash
# Still works (backward compatible)
mact create --project MyProject --local-port 3000
```

But we recommend switching to new syntax:
```bash
# Preferred (simpler)
mact create MyProject -port 3000
```

### For Scripts/Documentation
Update any automated scripts or docs:

**Before:**
```bash
mact create --project "$PROJECT" --subdomain "$SUBDOMAIN" --local-port $PORT
```

**After:**
```bash
mact create "$PROJECT" -port $PORT
# Subdomain auto-calculated from developer + project name
```

---

## Files Updated

✅ `cli/cli.py` - Argument parsing updated  
✅ `scripts/e2e_with_tunnels.sh` - Test script updated  
✅ `README.md` - Examples updated  
✅ `.docs/QUICK_START.md` - Usage examples updated  

---

## Testing

Run the E2E test to verify everything works:
```bash
./scripts/e2e_with_tunnels.sh
```

Expected behavior:
- User1 creates room with `mact create mact-demo-e2e -port 3000`
- Subdomain auto-generated: `dev-rahbar-mact-demo-e2e`
- User2 joins with `mact join mact-demo-e2e -port 3001`
- Subdomain auto-generated: `dev-sanaullah-mact-demo-e2e`

---

## Troubleshooting

### Error: "unrecognized arguments: --project"
**Cause:** Using old syntax with updated CLI

**Fix:** Update to new syntax:
```bash
# Old (broken)
mact create --project MyProject --local-port 3000

# New (works)
mact create MyProject -port 3000
```

### Error: Subdomain mismatch
**Cause:** Scripts using hardcoded old subdomain format

**Fix:** Update subdomain variables in scripts:
```bash
# Old
USER_SUBDOMAIN="dev-alice-e2e"

# New (matches auto-generation)
USER_SUBDOMAIN="dev-alice-projectname"
```

---

## Related Documentation

- [QUICK_START.md](.docs/QUICK_START.md) - Updated examples
- [CLI_COMPARISON.md](.docs/CLI_COMPARISON.md) - Client vs Admin CLI
- [CLIENT_INSTALLATION_GUIDE.md](.docs/CLIENT_INSTALLATION_GUIDE.md) - Installation guide
