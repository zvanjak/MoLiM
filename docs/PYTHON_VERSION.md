# Python Version

MoLiM requires **Python 3.11 or newer**. CI runs on 3.11 and 3.12;
3.13 and 3.14 are also supported.

The historical 3.11 ceiling existed because the legacy `cinemagoer`
dependency used `pkgutil.find_loader`, removed in Python 3.14. After
the MoLiM-02x migration the IMDb data layer is a pure-`requests` OMDb +
TMDb hybrid and that constraint is gone.

## Checking Your Python Version

```powershell
py --list           # Windows: list installed Pythons
py -3.12 --version  # check a specific one
```

```bash
python3 --version   # Linux/macOS
```

## Using a Specific Version

The setup script picks the newest `>= 3.11` automatically:

```powershell
.\setup.ps1                # auto-pick
.\setup.ps1 -PythonVersion 3.12   # force 3.12
```

```bash
./setup.sh
```
