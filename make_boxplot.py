import csv
from collections import defaultdict
from pathlib import Path


source = Path("AmesHousing-cleaned.csv")
output = Path("saleprice_by_rooms_boxplot.svg")
groups = defaultdict(list)
with source.open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        try:
            groups[int(row["TotRms AbvGrd"])].append(float(row["SalePrice"]))
        except (ValueError, KeyError):
            continue


def quantile(values, p):
    values = sorted(values)
    pos = (len(values) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(values) - 1)
    return values[lo] * (hi - pos) + values[hi] * (pos - lo)


width, height = 1050, 650
left, right, top, bottom = 90, 30, 65, 105
plot_w, plot_h = width - left - right, height - top - bottom
ymax = 800000
def y(value):
    return top + plot_h * (1 - value / ymax)

items = [(rooms, prices) for rooms, prices in sorted(groups.items()) if len(prices) >= 5]
spacing = plot_w / len(items)
box_w = min(42, spacing * 0.55)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
       '<rect width="100%" height="100%" fill="white"/>',
       '<style>text{font-family:Arial,sans-serif;fill:#263238}.grid{stroke:#e2e8f0}.axis{stroke:#475569}.box{fill:#c7e9f1;stroke:#187a91;stroke-width:2}.med{stroke:#c2410c;stroke-width:3}.whisk{stroke:#187a91;stroke-width:2}</style>',
       '<text x="525" y="30" font-size="21" font-weight="bold" text-anchor="middle">Sale Price by Total Rooms Above Ground</text>',
       '<text x="525" y="52" font-size="12" text-anchor="middle">AmesHousing • box shows Q1–Q3; whiskers extend to 1.5×IQR; points are outliers</text>']
for tick in range(0, 800001, 100000):
    yy = y(tick)
    svg.append(f'<line class="grid" x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}"/>')
    svg.append(f'<text x="{left-12}" y="{yy+4:.1f}" font-size="11" text-anchor="end">${tick//1000}k</text>')
svg.extend([f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}"/>',
            f'<line class="axis" x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}"/>',
            f'<text x="22" y="{top+plot_h/2}" font-size="13" text-anchor="middle" transform="rotate(-90 22 {top+plot_h/2})">Sale Price (USD)</text>',
            f'<text x="{left+plot_w/2}" y="{height-25}" font-size="13" text-anchor="middle">Total Rooms Above Ground</text>'])
for i, (rooms, prices) in enumerate(items):
    x = left + spacing * (i + 0.5)
    q1, med, q3 = (quantile(prices, p) for p in (0.25, 0.5, 0.75))
    iqr = q3 - q1
    low = min(v for v in prices if v >= q1 - 1.5 * iqr)
    high = max(v for v in prices if v <= q3 + 1.5 * iqr)
    svg.append(f'<line class="whisk" x1="{x:.1f}" y1="{y(high):.1f}" x2="{x:.1f}" y2="{y(q3):.1f}"/><line class="whisk" x1="{x-box_w/3:.1f}" y1="{y(high):.1f}" x2="{x+box_w/3:.1f}" y2="{y(high):.1f}"/>')
    svg.append(f'<line class="whisk" x1="{x:.1f}" y1="{y(q1):.1f}" x2="{x:.1f}" y2="{y(low):.1f}"/><line class="whisk" x1="{x-box_w/3:.1f}" y1="{y(low):.1f}" x2="{x+box_w/3:.1f}" y2="{y(low):.1f}"/>')
    svg.append(f'<rect class="box" x="{x-box_w/2:.1f}" y="{y(q3):.1f}" width="{box_w:.1f}" height="{max(1,y(q1)-y(q3)):.1f}"/>')
    svg.append(f'<line class="med" x1="{x-box_w/2:.1f}" y1="{y(med):.1f}" x2="{x+box_w/2:.1f}" y2="{y(med):.1f}"/>')
    for value in prices:
        if value < low or value > high:
            svg.append(f'<circle cx="{x:.1f}" cy="{y(value):.1f}" r="2" fill="#64748b" opacity=".5"/>')
    svg.append(f'<text x="{x:.1f}" y="{height-bottom+20}" font-size="11" text-anchor="middle">{rooms}</text>')
svg.append("</svg>")
output.write_text("\n".join(svg), encoding="utf-8")
print(f"Saved {output}; included groups with at least 5 observations.")
