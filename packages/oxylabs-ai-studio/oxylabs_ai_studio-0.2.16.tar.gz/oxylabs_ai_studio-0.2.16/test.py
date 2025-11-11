from pydantic import BaseModel
from oxylabs_ai_studio.apps.ai_scraper import AiScraper

scraper = AiScraper(api_key="Q1zriEzlRW5euISZqGipa1M6A8zL9fns2pPse2aB")

payload = {
    "url": "https://www.oxylabs.io",
    "output_format": "screenshot",
    "render_javascript": True
}
result = scraper.scrape(**payload)
print(result.data)
