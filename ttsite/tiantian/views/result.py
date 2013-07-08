#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View

class ResultView(View):
    def get(self, request):
        # <view logic>
        return HttpResponse('Result View')
