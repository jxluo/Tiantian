#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View
from django.template import RequestContext, loader

class XingView(View):
    
    def get(self, request):
        template = loader.get_template('tt/xing.tpl')
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))
