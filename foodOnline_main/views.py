from django.shortcuts import render
from django.http import HttpResponse
from vendor.models import Vendor
from menu.models import Category

from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance


def home(request):
    if 'lat' in request.GET:
        lat = reqeust.GET.get('lat')
        lng = reqeust.GET.get('lng')
        radius = 100

        pnt = GEOSGeometry('POINT(%s %s)' % (lng, lat))

        vendors = Vendor.objects.filter(
            Q(id__in=fetch_vendors_by_fooditems) |
            Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
            user_profile__location__distance_lte=(pnt, D(km=radius))
        ).annotate(distance=Distance("user_profile__location", pnt)).order_by('distance')

        for v in vendors:
            v.kms = round(v.distance.km, 1)

    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    categories = Category.objects.all()
    context = {
        'vendors': vendors,
        'categories': categories,
    }
    return render(request, 'home.html', context)