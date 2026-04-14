import urllib.request
url = "https://mytimetable.gift.edu.in/mytimetable.php?t=r&id=17632"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    with open("timetable_17632.html", "w") as f:
        f.write(html)
    print("HTML saved to timetable_17632.html")
except Exception as e:
    print(f"Error: {e}")
