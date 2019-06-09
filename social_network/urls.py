from rest_framework.routers import SimpleRouter
from social_network.views import PostViewSet, UserViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('posts', PostViewSet)

urlpatterns = router.urls
