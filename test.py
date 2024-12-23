# from scrapfly import ScrapflyClient, ScrapeConfig

# client = ScrapflyClient(key="scp-live-c801560fbb5840618208b8a8f02515d7")
# result = client.scrape(ScrapeConfig(
#     url="https://www.tripadvisor.com//Hotel_Review-g297930-d315568-Reviews-Phuket_Marriott_Resort_Spa_Merlin_Beach-Patong_Kathu_Phuket.html",
#     asp=True, # enable Anti Scraping Protection
#     country="US", # select a specific country location
#     render_js=True # enable JavaScript rendering if needed, similar to headless browsers
# ))

# html = result.content  # get the page HTML
# selector = result.selector

# print(html)
# print(selector)