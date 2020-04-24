import pandas as pd
import numpy as np
import requests
import json
  
class WavveParser:
     
    def __init__(self, datetime, apikey):
        self.apikey = apikey
        contents_id = self.getPopularId()
        self.contents_id_dfs = pd.concat(contents_id, ignore_index=True)
        self.contents_info = self.getDetailInfo()
        category_df, categories = self.ParseDetailInfo()
        category_df['category'] = np.where(category_df['broadcast'].isin(
            categories['지상파']), '지상파', np.where(category_df['broadcast'].isin(categories['종편']), '종편', '케이블'))
        category_df['rank'] = category_df.reset_index()["index"]+1
        category_df['DateTime'] = datetime
        self.category_df = category_df.reindex(columns = ['rank','title','broadcast','episode', 'date', 'genre', 'category','DateTime'])
        
    
    def getPopularId(self):

        popular_urls = []
        contents_id = []

        genres = {

            'all': '전체',
            '01': "드라마",
            '02': "예능",

        }

        for genre in genres:
            for page in range(1, 6):
                offset = (page-1) * 20
                item_url = f'https://apis.pooq.co.kr/cf/vod/popularcontents?WeekDay=all&broadcastid=6339&came=broadcast&contenttype=vod&genre={genre}&limit=20&offset={offset}&orderby=viewtime&page={page}&uiparent=GN2-VN2&uirank=2&uitype=VN2&apikey={self.apikey}&credential=none&device=pc&drm=wm&partner=pooq&pooqzone=none&region=kor&targetage=auto'
                popular_urls.append(item_url)

        for popular_url in popular_urls:
            req = requests.get(popular_url)
            data = json.loads(req.text)
            item_ids = [item['event_list'][0]['bodylist'][3].split(
                ':')[1] for item in data['cell_toplist']['celllist']]
            contents_id.append(pd.DataFrame({'id': item_ids}))

        return contents_id
    
    def getDetailInfo(self):

        detail_info = []

        for content_id in self.contents_id_dfs['id']:
            detail_url = f'https://apis.pooq.co.kr/vod/contents/{content_id}?device=pc&partner=pooq&pooqzone=none&region=kor&drm=wm&targetage=auto&apikey={self.apikey}&credential=gnay3eDqvjaYTaFwZFAJ57u0nvz33CA2FoHsr5NsY8OCv2wWeu3ZRgaY9Ci2CjRlAd03D4A%2BIdixX2iwjy6jRFjRGc9qw%2BSkVjGFCJxuSRe86SSYVVK953HfiFKuKb6A3nNVJoHyY6gvgpSgRpyNNeZOzMNkqmc2RcGu%2FWrnAXFDATjT2IpHfym9Ng6rPXCbvkd9q3Y%2FsfQrOSB%2BLRTp4IL6AnvszoJi8ccV9AJhR37vOmwOwiV76z7QJexM054Dhp04KJCHm8HmpZANhV1iOw%3D%3D'
            req = requests.get(detail_url)
            data = json.loads(req.text)
            detail_info.append(data)

        return detail_info
    
    def ParseDetailInfo(self):

        wavve_list = []

        categories = {

            '지상파': ['MBC', 'SBS', 'KBS 2TV', 'KBS 1TV', 'KBS'],
            '종편': ['MBN', '채널A', 'TV조선', 'TV CHOSUN'],
            '케이블': ['MBC Every1', 'KBS JOY', 'OCN', 'YTN', '연합뉴스TV', 'KTH PLAYY', 'SBS Fil']
        }

        for content_info in self.contents_info:

            wavve_list.append({
                'title': content_info['programtitle'],
                'broadcast': content_info['channelname'],
                'episode': content_info['episodenumber'],
                'date': content_info['releasedate']+"("+content_info['releaseweekday']+")",
                'genre': content_info['genretext'],

            })

        return pd.DataFrame(wavve_list), categories
