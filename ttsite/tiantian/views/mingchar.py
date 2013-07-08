#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View

class MingCharView(View):
    def get(self, request):
        # <view logic>
        return HttpResponse('Ming Char View')
