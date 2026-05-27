# Indoor Tracking (Prototype)

Prototip monocular pentru detectarea unui LED IR folosind OpenCV.

## Cerințe
- Python 3.10+
- Windows recomandat (ex: folosește `cv2.CAP_DSHOW` pentru camere)

## Instalare

```
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

## Rulare

```
python tracking_2d.py
```

### Prototip rapid IR

```
python tracking_ir.py --show
```

Acest script rulează o detecție rapidă a unui LED sau punct luminos și afișează coordonatele X/Y.

### Rulează cu OSC

```
python tracking_2d.py --osc-host 127.0.0.1 --osc-port 8000
```

Parametri utili:
- `--device 0` - indexul camerei
- `--threshold 240` - pragul de detecție al LED-ului IR
- `--osc-path /tracker/position` - adresă OSC pentru poziție
- `--osc-status-path /tracker/status` - adresă OSC pentru stare LED
- `--no-osc` - dezactivează trimiterea OSC

Apasă `q` pentru a închide.

## Test OSC local

1. Pornește receptorul OSC într-un terminal:

```
python osc_receiver.py
```

2. Rulează trackerul:

```
python tracking_2d.py --osc-host 127.0.0.1 --osc-port 8000
```

3. Verifică în terminalul receptorului dacă apar mesaje `/tracker/position`.

## Următorii pași
- Ajustează `THRESHOLD` din `tracking_2d.py` pentru LED-ul tău IR
- Extinde la două camere pentru triangulare 3D
- Integrează OSC cu TouchDesigner / consola ta de lumini
