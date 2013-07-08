#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View
from django.template import RequestContext, loader

class HomeView(View):
    """The view show home page of the site."""

    def get(self, request):
        helloString = 'Hello world!'
        template = loader.get_template('tiantian/home.html')
        context = RequestContext(request, {
            'helloString': helloString,
        })
        return HttpResponse(template.render(context))
