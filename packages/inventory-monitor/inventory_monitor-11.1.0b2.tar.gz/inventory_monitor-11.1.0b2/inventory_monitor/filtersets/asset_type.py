import django_filters
from netbox.filtersets import NetBoxModelFilterSet

from inventory_monitor.models import AssetType


class AssetTypeFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AssetType
        fields = ["id", "name", "slug", "description", "color"]

    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="iexact")
