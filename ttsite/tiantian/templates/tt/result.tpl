{% extends "tt/base.tpl" %}

{% block viewExtendHead %}
  {% load static %}
  <link rel="stylesheet" type="text/css"
    href="{% static "tt/css/result.css" %}"></link>
  <script type="text/javascript" src="{% static "tt/js/result.js" %}"></script>
{% endblock %}


{% block viewContent %}
  <div class="result-top-bar">
    <div class="result-embedded-search-box">
      <div class="result-mini-logo">
      </div>
      <input id="input" type="text"class="result-search-input">
      <div class="result-search-button">
        OK
      </div>
    </div>
  </div>
  <div class="result-content-container">
    <div class="result-content-summary">
    </div>
    <div class="result-content-detail">
      <div class="result-content-detail-xing">
      </div>
      <div class="result-content-detail-mingchar">
      </div>
    </div>
  </div>


  <div class="result-debug-info">
    姓名: {{ name }} <br>
    姓: {% include "tt/common/info.tpl" with info=data.xingInfo only %}<br>
    名: {% include "tt/common/info.tpl" with info=data.mingInfo only %}<br>
    字：<br>
    {% for info in data.mingCharInfoList %}
      &nbsp;&nbsp;&nbsp;&nbsp;
      {% include "tt/common/info.tpl" with info=info only %}<br>
    {% endfor %}
    Estimated Male Rate:
        {{data.estimatedMaleRate|floatformat:2}}
        &nbsp;&nbsp;&nbsp;&nbsp;
    Estimated Female Rate:
        {{data.estimatedFemaleRate|floatformat:2}}
        &nbsp;&nbsp;&nbsp;&nbsp;
    Estimated GenderInfo Reliability:
        {{data.estimatedGenderReliability|floatformat:2}}
  </div>
{% endblock %}
