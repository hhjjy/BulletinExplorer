from django.shortcuts import render
from .spider import NTUSTBulletinScraper,NTUSTLanguageCenterScraper,NTUSTMajorAnnouncementScraper,ScraperFactory
def index(request):
    data = []
    if request.method == 'POST':
        url = request.POST.get('website')
        scraper = ScraperFactory.get_scraper(url)
  
        # data.append({'date':date,'publisher':publisher,'title':title,'url':url,'content':content})
        data = scraper.scrape()
    return render(request, 'index.html', {'data': data})
