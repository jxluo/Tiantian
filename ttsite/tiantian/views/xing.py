#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View

class XingView(View):
    def get(self, request):
        # <view logic>
        return HttpResponse('Xing View')
