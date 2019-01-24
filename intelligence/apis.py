from rest_framework.routers import DefaultRouter
from apps.reputation.api import blViewSet
from apps.twitter.api import twViewSet
from apps.exploit.api import exViewSet
from apps.threat.api import threatEventViewSet, threatAttrViewSet

router = DefaultRouter(trailing_slash=False)
router.register('reputation', blViewSet)
router.register('twitter', twViewSet)
router.register('exploit', exViewSet)
router.register('threatEvent', threatEventViewSet)
router.register('threatAttribute', threatAttrViewSet)

