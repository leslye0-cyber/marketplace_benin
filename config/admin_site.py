# config/admin_site.py

from django.contrib.admin import AdminSite

class MarketPlaceAdminSite(AdminSite):
    site_header = '🛍️ MarketPlace Bénin — Administration'
    site_title = 'MarketPlace Bénin Admin'
    index_title = 'Tableau de bord administrateur'