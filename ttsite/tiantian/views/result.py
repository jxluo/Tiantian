#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View
from django.template import RequestContext, loader

from tiantian.base.util import parseName
from tiantian.data.resultfetcher import getResultFetcher

class ResultView(View):

    def get(self, request, name):

        parseReulst = parseName(name)
        if not parseReulst:
            print 'not valid'
            return HttpResponse('%s is not a valid Chinese name' % name) 

        xing, ming = parseReulst
        resultData = getResultFetcher().fetchData(name, xing, ming)
        print resultData.xingInfo

        template = loader.get_template('tt/result.tpl')
        context = RequestContext(request, {
            'name': name,
            'data': resultData
        })
        print 'sdfsfsdf'
        return HttpResponse(template.render(context))
