from django.urls import path
from . import views
#導航到app.urls的末肉顯示views.index 
# 會從views.py的檔案中找到對應的函數顯示
urlpatterns = [
    path('', views.index, name="Index")
]