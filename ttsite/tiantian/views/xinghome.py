#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View

class XingHomeView(View):
    def get(self, request):
        # <view logic>
        return HttpResponse('Xing Home View')
