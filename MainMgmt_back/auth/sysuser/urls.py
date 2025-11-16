from django.urls import path
from .views import *
# from .captchaView import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename='user')

app_name = 'sysuser'
urlpatterns = [
    path('login', LoginView.as_view(), name='login'),   # 登录

    # path('slider-captcha', SliderCaptchaView.as_view(), name='slider-captcha'),
    # path('slider-verify', SliderCaptchaVerifyView.as_view(), name='slider-verify'),

    #path('pwd', ResetPasswordView.as_view(), name='pwd'),   # 修改密码
    # 管理员重置密码2025-10-19thon
    #path('admin-reset-password', AdminResetPasswordView.as_view(), name='admin-reset-password'),
    path('change_password', ChangePasswordView.as_view(), name='change-pwd'),

    path('contact', UpdateContactInfoView.as_view(), name='contact-info'),   # 修改用户信息
    path('uploadImage', ImageView.as_view(), name='uploadImage'),  # 头像上传
    path('request_logs', RequestLogSearchView.as_view(), name='request_logs'),  # 审计日志
]
urlpatterns += router.urls