#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View
from django.template import RequestContext, loader

class MingView(View):
    def get(self, request):
        template = loader.get_template('tt/ming.tpl')
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))
