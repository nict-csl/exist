from rest_framework.routers import DefaultRouter
from reputation.api import blViewSet
from twitter.api import twViewSet
from exploit.api import exViewSet
from threat.api import threatEventViewSet, threatAttrViewSet
from vuln.api import vulnViewSet

router = DefaultRouter(trailing_slash=False)
router.register('reputation', blViewSet)
router.register('twitter', twViewSet)
router.register('exploit', exViewSet)
router.register('threatEvent', threatEventViewSet)
router.register('threatAttribute', threatAttrViewSet)
router.register('vuln', vulnViewSet)

