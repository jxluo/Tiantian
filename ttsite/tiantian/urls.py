from django.conf.urls import patterns, url

from tiantian.views.home import HomeView
from tiantian.views.result import ResultView
from tiantian.views.xing import XingView
from tiantian.views.xinghome import XingHomeView
from tiantian.views.ming import MingView
from tiantian.views.mingchar import MingCharView
from tiantian.views.minghome import MingHomeView


urlpatterns = patterns('',
    url(r'^result/([^/]+)/?$', ResultView.as_view(), name='result'),
    url(r'^xing/?$', XingView.as_view(), name='xing'),
    url(r'^xinghome/?$', XingHomeView.as_view(), name='xing_home'),
    url(r'^ming/?$', MingView.as_view(), name='ming'),
    url(r'^mingchar/?$', MingCharView.as_view(), name='ming_char'),
    url(r'^minghome/?$', MingHomeView.as_view(), name='ming_home'),
    # Default
    url(r'', HomeView.as_view(), name='home'),
)
