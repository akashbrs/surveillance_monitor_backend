from django.urls import path
from .views import GoogleLoginView, LoginView, SignupView, SendOTPView, VerifyOTPView, LogoutView

urlpatterns = [
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
