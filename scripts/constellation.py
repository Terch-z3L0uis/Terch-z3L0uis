from datetime import date, timedelta
from pathlib import Path
import json
import math
import os
import urllib.request
from xml.sax.saxutils import escape

USERNAME = os.environ.get('GITHUB_USER', 'Terch-z3L0uis')
TOKEN = os.environ.get('GH_TOKEN', '')
DAYS = 90

query = '''query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}'''

def get_activity():
    if not TOKEN:
        raise RuntimeError('GH_TOKEN is missing. Check workflow env settings.')
    today = date.today()
    start = today - timedelta(days=DAYS - 1)
    variables = {'login': USERNAME, 'from': start.isoformat() + 'T00:00:00Z', 'to': today.isoformat() + 'T23:59:59Z'}
    request = urllib.request.Request('https://api.github.com/graphql', data=json.dumps({'query': query, 'variables': variables}).encode(), headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json', 'User-Agent': 'observer-constellation'})
    with urllib.request.urlopen(request, timeout=25) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError('GitHub API error: ' + str(result['errors']))
    user = result.get('data', {}).get('user')
    if user is None:
        raise RuntimeError('GitHub user not found: ' + USERNAME)
    days = user['contributionsCollection']['contributionCalendar']['weeks']
    counts = {item['date']: item['contributionCount'] for week in days for item in week['contributionDays']}
    return [(start + timedelta(days=i), counts.get((start + timedelta(days=i)).isoformat(), 0)) for i in range(DAYS)]

def make_svg(activity):
    width, height = 840, 350
    active = [(day, count, i) for i, (day, count) in enumerate(activity) if count > 0]
    total = sum(count for _, count in activity)
    stars = []
    for day, count, i in active:
        x = 38 + (i * 73 + 17) % 765
        y = 86 + (i * 47 + 11) % 175
        radius = min(6, 1.8 + math.log2(count + 1) * 1.1)
        opacity = min(1, 0.55 + math.log2(count + 1) * 0.12)
        stars.append((x, y, radius, opacity, day, count))
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="840" height="350" rx="18" fill="#101521"/>', '<rect x="2" y="2" width="836" height="346" rx="16" fill="none" stroke="#76654e" stroke-width="2"/>', '<text x="420" y="48" text-anchor="middle" fill="#e8c99a" font-family="monospace" font-size="24">THE OBSERVER&#39;S SKY</text>']
    for a, b in zip(stars, stars[1:]):
        pieces.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#bba37c" stroke-width="0.7" opacity="0.28"/>')
    for i, (x, y, r, opacity, day, count) in enumerate(stars):
        # Each star has its own twinkle speed and delay.
        # The static circle remains visible if SVG animation is unsupported.
        low = max(0.25, opacity * 0.55)
        high = min(1.0, opacity + 0.12)
        duration = 2.8 + (i % 7) * 0.45
        delay = -((i * 1.37) % duration)
        pieces.append(
            f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#f5dbac" opacity="{opacity:.2f}">'
            f'<title>{escape(day.isoformat())}: {count} contributions</title>'
            f'<animate attributeName="opacity" values="{low:.2f};{high:.2f};{low:.2f}" '
            f'dur="{duration:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    if not stars:
        pieces.append('<text x="420" y="165" text-anchor="middle" fill="#c6b393" font-family="monospace" font-size="18">The sky awaits its first star...</text>')
    pieces.extend([f'<text x="420" y="304" text-anchor="middle" fill="#d4bd98" font-family="monospace" font-size="15">{total} contributions &#183; {len(stars)} active days &#183; last {DAYS} days</text>', '<text x="420" y="328" text-anchor="middle" fill="#958875" font-family="monospace" font-size="12">Every star holds a little memory.</text>', '</svg>'])
    return '\n'.join(pieces)

if __name__ == '__main__':
    activity = get_activity()
    path = Path('assets/constellation.svg')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(make_svg(activity), encoding='utf-8')
    print('Generated', path)
