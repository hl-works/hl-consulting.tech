#!/usr/bin/env python3
"""Pochettes mensuelles du Podcast iA (une par format, valables tout le mois).

Demande de Hugo (17 novembre 2026) : la pochette change une fois par mois,
avec le portrait d'iAstro du mois (tenue du mois). Même mise en page que le
site (masthead « Podcast iA », portrait, étiquette du format, pied de page),
mais le pied affiche le mois au lieu de la date et de la durée, déjà données
par les plateformes.

Composition Pillow, sans navigateur : robuste dans les jobs automatiques.
Sortie : assets/podcast/art/cover-AAAA-MM-{short,full}-v1.jpg et show-cover-AAAA-MM.jpg
(image générale de l'émission, tenue du mois), 3000 × 3000.
Ne réécrit jamais une pochette existante.

    python3 scripts/build_monthly_podcast_covers.py --month 2026-11
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/podcast/art'
SIZE = 3000
IVORY, INK = (255, 252, 248), (12, 12, 12)
ACCENT = {'short': (198, 18, 31), 'full': (57, 53, 158)}
LABEL = {'short': 'LE FLASH', 'full': 'LE DÉBRIEF'}
MONTHS = ['JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOÛT',
          'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']
FONTS = ['/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
MONO = ['/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf']


def font(candidates, size):
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    raise RuntimeError('Aucune police système trouvée')


def fit(draw, text, candidates, size, max_width):
    while size > 20:
        f = font(candidates, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 10
    return font(candidates, size)


def compose(year, month, kind):
    portrait = Image.open(ART / f'iastro-{month:02d}-v1.png').convert('RGB')
    img = Image.new('RGB', (SIZE, SIZE), IVORY)
    d = ImageDraw.Draw(img)
    accent = ACCENT[kind]
    head, foot = int(SIZE * .17), int(SIZE * .17)
    # Portrait (contain) dans la zone centrale.
    area = SIZE - head - foot
    p = portrait.resize((area, area), Image.LANCZOS)
    img.paste(p, ((SIZE - area) // 2, head))
    # Masthead.
    d.rectangle([0, 0, SIZE, head], fill=IVORY)
    d.line([0, head, SIZE, head], fill=INK, width=4)
    brand = font(FONTS, 240)
    x, y = int(SIZE * .06), head // 2
    d.text((x, y), 'PODCAST ', font=brand, fill=INK, anchor='lm')
    d.text((x + d.textlength('PODCAST ', font=brand), y), 'iA', font=brand, fill=accent, anchor='lm')
    d.text((SIZE - int(SIZE * .06), y), ')))', font=font(MONO, 120), fill=accent, anchor='rm')
    # Étiquette du format.
    label = font(FONTS, 111)
    lx, ly = int(SIZE * .05), int(SIZE * .21)
    w = d.textlength(LABEL[kind], font=label)
    d.rectangle([lx, ly, lx + w + 156, ly + 190], fill=accent)
    d.text((lx + 78, ly + 95), LABEL[kind], font=label, fill='white', anchor='lm')
    # Pied : mois + bloc couleur.
    top = SIZE - foot
    d.rectangle([0, top, SIZE, SIZE], fill=IVORY)
    d.line([0, top, SIZE, top], fill=INK, width=4)
    pad = int(SIZE * .04)
    split = int(SIZE * .56)
    month_text = f'{MONTHS[month - 1]} {year}'
    d.text((pad, top + foot // 2), month_text, font=fit(d, month_text, FONTS, 230, split - 2 * pad),
           fill=INK, anchor='lm')
    d.rectangle([split, top + int(foot * .15), SIZE - pad, SIZE - int(foot * .15)], fill=accent)
    d.text(((split + SIZE - pad) // 2, top + foot // 2), 'iAstro', font=fit(d, 'iAstro', FONTS, 230, SIZE - pad - split - 80),
           fill='white', anchor='mm')
    d.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=INK, width=4)
    return img


def compose_show(month):
    """Image générale de l'émission, même style que show-cover-v1, tenue du mois."""
    violet = ACCENT['full']
    portrait = Image.open(ART / f'iastro-{month:02d}-v1.png').convert('RGB')
    img = Image.new('RGB', (SIZE, SIZE), IVORY)
    d = ImageDraw.Draw(img)
    head, foot = int(SIZE * .18), int(SIZE * .10)
    margin = int(SIZE * .055)
    title = font(FONTS, 330)
    y = head // 2 + 30
    d.text((margin, y), 'LE PODCAST ', font=title, fill=INK, anchor='lm')
    d.text((margin + d.textlength('LE PODCAST ', font=title), y), 'IA', font=title, fill=violet, anchor='lm')
    d.line([margin, head, SIZE - margin, head], fill=INK, width=6)
    area = SIZE - head - foot - 40
    img.paste(portrait.resize((area, area), Image.LANCZOS), ((SIZE - area) // 2, head + 20))
    top = SIZE - foot
    d.rectangle([0, top, SIZE, SIZE], fill=IVORY)
    d.line([margin, top, SIZE - margin, top], fill=INK, width=6)
    small = font(FONTS, 130)
    d.text((margin, top + foot // 2), 'Hugo LaHutte', font=small, fill=INK, anchor='lm')
    d.text((SIZE - margin, top + foot // 2), 'iAstro', font=small, fill=violet, anchor='rm')
    return img


def build(year, month):
    made = []
    show = ART / f'show-cover-{year}-{month:02d}.jpg'
    if not show.exists():
        compose_show(month).save(show, 'JPEG', quality=92)
        made.append(show)
    for kind in ('short', 'full'):
        dest = ART / f'cover-{year}-{month:02d}-{kind}-v1.jpg'
        if dest.exists():
            continue
        compose(year, month, kind).save(dest, 'JPEG', quality=92)
        made.append(dest)
    return made


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--month', required=True, help='AAAA-MM')
    args = ap.parse_args()
    y, m = map(int, args.month.split('-'))
    for path in build(y, m):
        print('Pochette créée :', path.relative_to(ROOT))
