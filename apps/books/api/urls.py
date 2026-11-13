from rest_framework.routers import SimpleRouter

from .views import BookViewSet, CategoryViewSet


class OptionalSlashRouter(SimpleRouter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'


router = OptionalSlashRouter()
router.register('books', BookViewSet, basename='book')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = router.urls
