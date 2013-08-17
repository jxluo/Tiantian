#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic.base import View
from django.template import RequestContext, loader

from tiantian.base.util import parseName
from tiantian.data.resultfetcher import getResultFetcher

from entities.name_pb2 import NONE, LOW, HIGH

class SummaryParam:
    # The constants that tell us how common the name is.
    (NEVER_SEEN,
     RARE,
     AVERAGE,
     COMMON,
     VERY_COMMON
    ) = range(0, 5)
   
    xing_ming_text = None
    ming_text = None
    text_hint = None
    num_per_1m_for_xing_ming = 0
    num_per_1m_for_ming = 0
    male_percent = None
    female_percent = None


class XingParam:
    has_info = None
    text = None
    rank = None
    num_per_10k = None


class MingCharParam:
    text = None
    rank = None
    num_per_10k = None
    has_gender_info = False
    male_percent = None
    female_percent = None


class ResultView(View):

    def get(self, request, name):

        parseReulst = parseName(name)
        if not parseReulst:
            print 'not valid'
            return HttpResponse('%s is not a valid Chinese name' % name) 

        xing, ming = parseReulst
        resultData = getResultFetcher().fetchData(name, xing, ming)

        template = loader.get_template('tt/result.tpl')
        context = RequestContext(request, {
            'name': name,
            'summary': self.getSummaryParams(name, ming, resultData),
            'xing': self.getXingParam(xing, resultData.xingInfo),
            'ming_chars': self.getMingCharParams(resultData.mingCharInfoList),
            'data': resultData
        })
        print 'sdfsfsdf'
        return HttpResponse(template.render(context))

    def getMingCharParams(self, mingCharInfoList):
        params = []
        for info in mingCharInfoList:
            p = MingCharParam()
            p.text = info.text
            p.rank = info.rank
            p.num_per_10k = int(info.rate * 10000)
            if info.gender.reliable >= LOW:
                p.male_percent = int(info.gender.male_rate * 100)
                p.female_percent = int(info.gender.female_rate * 100)
                p.has_gender_info = True
            params.append(p)
        return params


    def getXingParam(self, xing, xInfo):
        param = XingParam()
        param.text = xing
        if xInfo:
            param.has_info = True
            param.xing = xInfo.text
            param.rank = xInfo.rank
            param.num_per_10k = int(xInfo.rate * 10000)
        else:
            param.has_info = False
        return param


    def getTextHint(self, sumRate):
        if sumRate < 0.1:
            return SummaryParam.VERY_COMMON
        elif sumRate < 0.2:
            return SummaryParam.COMMON
        elif sumRate < 0.5:
            return SummaryParam.AVERAGE
        elif sumRate < 0.99:
            return SummaryParam.RARE
        else:
            return SummaryParam.NEVER_SEEN

    def getSummaryParams(self, xingMing, ming, data):
        param = SummaryParam()
        param.xing_ming_text = xingMing
        param._ming_text = ming
        
        xmInfo = data.xingMingInfo
        mInfo = data.mingInfo

        param.text_hint = self.getTextHint(data.summarySumRate)
        if xmInfo: param.num_per_1m_for_xing_ming = int(xmInfo.rate * 1000000)
        if mInfo: param.num_per_1m_for_ming = int(mInfo.rate * 1000000)
        param.male_rate = param.female_rate = 0
        if data.hasGenderInfo:
            param.male_percent = int(data.summaryMaleRate * 100)
            param.female_percent = int(data.summaryFemaleRate * 100)

        return param


