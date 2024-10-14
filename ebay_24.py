import os
import datetime
import sys
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection as finding
from models import Item

from dotenv import load_dotenv
load_dotenv()
API_KEY=os.getenv('api_key')

class Ebay_24(object):
    def __init__(self, API_KEY, st):
        self.api_key = API_KEY
        self.st = st

    
    def fetch(self):
        try:
            api = finding(appid=self.api_key, config_file=None)
            response = api.execute('findItemsAdvanced', {'keywords': self.st,
                                                         'outputSelector': ['GalleryInfo', 'PictureURLLarge']})
            
            items = []
            for item in response.reply.searchResult.item:
                if len(items) >= 10:  # Limit the items list to 10
                    break
                
                title = item.title
                condition = item.condition.conditionDisplayName if hasattr(item, 'condition') else None
                # Try multiple image sources
                image_url = None
                if hasattr(item, 'galleryURL'):
                    image_url = item.galleryURL
                elif hasattr(item, 'galleryInfoContainer') and hasattr(item.galleryInfoContainer, 'galleryURL'):
                    image_url = item.galleryInfoContainer.galleryURL[0]  # Use the first URL in the list
                elif hasattr(item, 'pictureURLLarge'):
                    image_url = item.pictureURLLarge
                
                # Check if the item already exists in the database
                existing_item = Item.query.filter_by(title=title, condition=condition).first()
                if not existing_item:
                    if image_url:
                        items.append({
                            'title': title,
                            'condition': condition,
                            'image_url': image_url
                        })

            return items
                
        except ConnectionError as e:
            print(e)
            print(e.response.dict())

    def parse(self):
        pass

# main driver

if __name__=='__main__':
    st = sys.argv[1]
    e = Ebay_24(API_KEY, st)
    e.fetch()
    e.parse()