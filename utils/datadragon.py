from riotwatcher import LolWatcher, ApiError
import os


class DataDragon():

    watcher = LolWatcher(os.getenv("LEAGUE_TOKEN"))

    def __init__(self, client):
        
        self.champions = {}
        self.summoners = {}
        self.items = {}
        self.runes = {}
        # all types ['item', 'rune', 'mastery', 'summoner', 'champion', 'profileicon', 'map', 'language', 'sticker']

        types = ["champion", "summoner", "rune"]
        version_dict = self.watcher.data_dragon.versions_for_region(client.config["region"])["n"]

        for data_type in types:            
            # get league's latest version
            latest = version_dict[data_type]

            # get info
            info = None
            if data_type == "champion":
                info = self.watcher.data_dragon.champions(latest, False, 'en_US')
                for key in info['data']:
                    self.champions[int(info['data'][key]['key'])] = info['data'][key]
            elif data_type == "summoner":
                info = self.watcher.data_dragon.summoner_spells(latest, 'en_US')
                for key in info['data']:
                    self.summoners[int(info['data'][key]['key'])] = info['data'][key]
            elif data_type == "rune":
                latest = version_dict["champion"] # riot fucked this up in /realms/na.json
                info = self.watcher.data_dragon.runes_reforged(latest, 'en_US')
                for rune_category in info:
                    current_runes = {}
                    for rune in rune_category['slots'][0]['runes']:
                        current_runes[int(rune['id'])] = rune['name']
                    self.runes[int(rune_category['id'])] = current_runes

            

    