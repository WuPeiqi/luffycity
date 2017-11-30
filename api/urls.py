from django.conf.urls import url
from .views import auth
from .views import course
from .views import shopping_car
from .views import payment
from .views import order
from .views import alipay

urlpatterns = [
    url(r'^auth/$', auth.AuthView.as_view()),
    url(r'^courses/$', course.CourseView.as_view()),
    url(r'^courses/(?P<pk>\d+)/$', course.CourseView.as_view()),
    url(r'^price_policy/(?P<course_id>\d+)/$', course.PricePolicyView.as_view()),
    url(r'^shop_car/$', shopping_car.ShoppingCarView.as_view({'get': 'get', 'post': 'post'})),
    url(r'^shop_car/(?P<pk>\d+)/$', shopping_car.ShoppingCarView.as_view({'delete': 'delete', 'put': "put"})),
    url(r'^payment/$', payment.PaymentView.as_view()),
    url(r'^order/$', order.PayOrderView.as_view()),
    url(r'^alipay/$', alipay.AlipayView.as_view()),
]
