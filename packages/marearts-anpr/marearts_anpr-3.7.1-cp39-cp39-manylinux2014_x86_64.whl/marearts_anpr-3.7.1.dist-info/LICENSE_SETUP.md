# MareArts ANPR License Configuration Guide

## Overview
This guide explains how to configure your MareArts ANPR license for building and testing wheels.

## License Types

### V1 License (Legacy)
- **Key Format**: Regular encrypted string
- **Files Required**:
  - `.license_email.txt` - Your email
  - `.license_key.txt` - Your V1 license key
- **Supported Models**: V10, V11, V13

### V2 License (Current)
- **Key Format**: Starts with `MAEV2:`
- **Files Required**:
  - `.license_email.txt` - Your email
  - `.license_key.txt` - Your V2 license key
  - `.license_signature.txt` - Digital signature (16 hex characters)
- **Supported Models**: V10, V11, V13, V14 (all models)
- **Additional Features**: TensorRT support, V14 models

## Setup Instructions

### 1. Automatic Setup (Recommended)
```bash
cd /media/m2/dev2/marearts-anpr-main/marearts-anpr-pypi
./scripts/setup_license_env.sh
```

This will prompt you to enter:
1. Your email address
2. Your license key
3. Your signature (for V2 licenses)

### 2. Manual Setup

#### For V2 License:
```bash
cd /media/m2/dev2/marearts-anpr-main/marearts-anpr-pypi/scripts

# Create license files
echo "your-email@domain.com" > .license_email.txt
echo "MAEV2:your-encrypted-key-here" > .license_key.txt
echo "your-16-char-hex" > .license_signature.txt

# Set permissions
chmod 600 .license_*.txt
```

#### For V1 License:
```bash
cd /media/m2/dev2/marearts-anpr-main/marearts-anpr-pypi/scripts

# Create license files
echo "your-email@domain.com" > .license_email.txt
echo "your-v1-license-key" > .license_key.txt

# Set permissions
chmod 600 .license_*.txt
```

## File Locations

License files should be stored in the `scripts/` directory:
```
/media/m2/dev2/marearts-anpr-main/marearts-anpr-pypi/scripts/
├── .license_email.txt      # Your email
├── .license_key.txt        # Your license key
└── .license_signature.txt  # V2 signature (optional for V1)
```

**Important**: These files are automatically copied to the appropriate locations during build and test processes.

## Environment Variables

You can also use environment variables instead of files:
```bash
export MAREARTS_ANPR_USERNAME="your-email@domain.com"
export MAREARTS_ANPR_SERIAL_KEY="MAEV2:your-key"
export MAREARTS_ANPR_SIGNATURE="your-signature"  # V2 only
```

## Verification

### Check License Status
```bash
# After setting up license files
cd /media/m2/dev2/marearts-anpr-main/marearts-anpr-pypi
./scripts/building_wheels.sh

# The script will validate your license before building
```

### Manual Validation
```bash
# Install the package first
pip install marearts-anpr

# Then validate
export MAREARTS_ANPR_USERNAME=$(cat scripts/.license_email.txt)
export MAREARTS_ANPR_SERIAL_KEY=$(cat scripts/.license_key.txt)
export MAREARTS_ANPR_SIGNATURE=$(cat scripts/.license_signature.txt)  # V2 only

ma-anpr validate
```

## Security Notes

1. **Never commit license files to git**
   - The `.gitignore` already excludes `.license_*` files
   - Always check before committing

2. **File Permissions**
   - License files should have restricted permissions (600)
   - Only the owner should be able to read them

3. **CI/CD Usage**
   - Use GitHub Secrets or environment variables
   - Never hardcode licenses in scripts

## Troubleshooting

### "License validation failed"
- Check email is correct
- Verify license key is complete
- For V2: Ensure signature file exists

### "Model access denied"
- V14 models require V2 license with signature
- Check signature is exactly 16 hex characters
- Verify license hasn't expired

### "No credentials found"
- Ensure files are in `scripts/` directory
- Check file names start with dot (`.license_`)
- Verify files are not empty

## Getting a License

To obtain a MareArts ANPR license:
1. Visit: https://marearts.com
2. Contact: support@marearts.com
3. Request V2 license for full feature access

## License Features Comparison

| Feature | V1 License | V2 License |
|---------|------------|------------|
| V13 Models | ✅ | ✅ |
| V14 Models | ❌ | ✅ |
| TensorRT | ❌ | ✅ |
| API Access | ✅ | ✅ |
| CLI Tools | ✅ | ✅ |
| Commercial Use | ✅ | ✅ |