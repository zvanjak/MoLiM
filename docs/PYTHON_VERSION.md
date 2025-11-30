# Python Version Requirements

## Why Python 3.11?

This project uses the `cinemagoer` library for IMDb data fetching. This library has a known incompatibility with Python 3.14:

- **Issue**: Uses `pkgutil.find_loader` which was removed in Python 3.14
- **Error**: `ImportError: cannot import name 'find_loader' from 'pkgutil'`
- **Solution**: Use Python 3.11

## Checking Your Python Version
