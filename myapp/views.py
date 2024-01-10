from django.shortcuts import render
from .spider import NTUSTBulletinScraper,NTUSTLanguageCenterScraper,NTUSTMajorAnnouncementScraper
def index(request):
    data = []
    if request.method == 'POST':
        url = request.POST.get('url')
        scraper = NTUSTBulletinScraper(url)  # 執行爬蟲並獲取結果
        # data.append({'date':date,'publisher':publisher,'title':title,'url':url,'content':content})
        data = scraper.scrape()
    return render(request, 'index.html', {'data': data})
