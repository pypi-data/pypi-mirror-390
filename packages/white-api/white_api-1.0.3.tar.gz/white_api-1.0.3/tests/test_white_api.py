from white_api import WhiteAPI

# Инициализация API
api = WhiteAPI(api_key="your_api_key")

# Работа с подарками
gifts = api.gift.floor_gift_all()
print(gifts)

# Работа со стикерами
stickers = api.sticker.get_floor_sticker(collection="Not Pixel")
print(stickers)

# Работа с Stickertools
stats = api.stickertools.total_stats()
print(stats)