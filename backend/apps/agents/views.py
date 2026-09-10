from apps.core.viewsets import TenantScopedViewSet

from .models import Agent
from .serializers import AgentSerializer


class AgentViewSet(TenantScopedViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer