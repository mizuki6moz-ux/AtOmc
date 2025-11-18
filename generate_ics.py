import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# =========================
# AtCoder
# =========================
ATCODER_URL = "https://atcoder.jp/contests/?lang=ja"

def fetch_atcoder_contests():
    html = requests.get(ATCODER_URL).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("div", {"id": "contest-table-upcoming"})
    if not table:
        return []
    rows = table.find("tr").find_all_next("tr")

    contests = []
    for r in rows:
        cols = r.find_all("td")
        if len(cols) < 3:
            continue
        date_str = cols[0].text.strip()
        title = cols[1].text.strip()
        link = "https://atcoder.jp" + cols[1].find("a")["href"]

        start = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        start = start.replace(tzinfo=timezone(timedelta(hours=9)))

        duration_str = cols[2].text.strip()
        try:
            h, m = map(int, duration_str.split(":"))
        except:
            h, m = 2, 0
        end = start + timedelta(hours=h, minutes=m)

        contests.append({
            "title": title,
            "start": start,
            "end": end,
            "url": link,
        })
    return contests

# =========================
# OnlineMathContest (OMC)
# =========================
OMC_URL = "https://onlinemathcontest.com/contests/"

def fetch_omc_contests():
    html = requests.get(OMC_URL).text
    soup = BeautifulSoup(html, "html.parser")
    contests_div = soup.find_all("div", class_="contest-item")
    contests = []

    for c in contests_div:
        title_tag = c.find("h3")
        if not title_tag:
            continue
        title = title_tag.text.strip()

        date_tag = c.find("p", class_="contest-date")
        if not date_tag:
            continue
        date_text = date_tag.text.strip()  # e.g. "Nov 22, 2025 18:00 UTC"
        try:
            start = datetime.strptime(date_text, "%b %d, %Y %H:%M %Z")
        except:
            continue
        start = start.replace(tzinfo=timezone.utc)

        duration_tag = c.find("p", class_="contest-duration")
        if duration_tag:
            dur_text = duration_tag.text.strip()  # e.g. "Duration: 2 hours"
            try:
                hours = int(dur_text.split()[1])
            except:
                hours = 2
        else:
            hours = 2
        end = start + timedelta(hours=hours)

        link_tag = c.find("a", href=True)
        link = link_tag["href"] if link_tag else OMC_URL

        contests.append({
            "title": title,
            "start": start,
            "end": end,
            "url": link,
        })
    return contests

# =========================
# ICS 生成
# =========================
def make_ics(contests, filename="contest.ics"):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AtCoder+OMC ICS//EN"]

    for c in contests:
        uid = c['url'].split("/")[-1] + "@combined-contest.com"
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"SUMMARY:{c['title']}",
            f"DTSTART:{c['start'].strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{c['end'].strftime('%Y%m%dT%H%M%SZ')}",
            f"DESCRIPTION:{c['url']}",
            f"URL:{c['url']}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✔ {filename} を生成しました")

# =========================
# メイン
# =========================
if __name__ == "__main__":
    atcoder = fetch_atcoder_contests()
    omc = fetch_omc_contests()
    all_contests = atcoder + omc
    make_ics(all_contests)

