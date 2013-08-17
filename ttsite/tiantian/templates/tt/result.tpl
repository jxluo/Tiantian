{% extends "tt/base.tpl" %}

{% block viewExtendHead %}
  {% load static %}
  <link rel="stylesheet" type="text/css"
    href="{% static "tt/css/result.css" %}"></link>
  <script type="text/javascript" src="{% static "tt/js/result.js" %}"></script>
{% endblock %}

{% block bodyLoadedScript %}
  startScript();
{% endblock %}

{% comment %}
  @param name: string,
  @param summary: SummaryParam,
  @param xing: XingParam,
  @param ming_chars: [MingCharParam],
  @param data: ResultData
{% endcomment %}
{% block viewContent %}
  <div class="result-top-bar">
    <div class="result-embedded-search-box">
      <div class="result-mini-logo">
      </div>
      <input id="search-input" type="text"
          class="base-search-input result-search-input"
          value="{{name}}">
      <div class="base-search-button result-search-button"
          onClick="base.handleInputButtonClick()">
        OK
      </div>
    </div>
  </div>
  <div class="result-content-container">
    <div class="result-content-summary
        {% if summary.male_percent > 50 %}
          result-male-style
        {% elif summary.female_percent > 50 %}
          result-female-style
        {% else %}
          result-no-gender-style
        {% endif %}">
      {{name}}这个名字
      {% if summary.text_hint == summary.VERY_COMMON %}
        非常非常常见哦。
      {% elif summary.text_hint == summary.COMMON %}
        很常见哦。
      {% elif summary.text_hint == summary.AVERAGE %}
        很普通哦。
      {% elif summary.text_hint == summary.RARE %}
        很罕见哦。
      {% else %}
        从来没见过，真的是人的名字吗？
      {% endif %}
      <br/>
      一百万个人中，
        跟你同名同姓的人约有{{summary.num_per_1m_for_xing_ming}}个,
        跟你同名的人约有{{summary.num_per_1m_for_ming}}个。
      <br/>
      {{name}}是：
      <br/>
      男生名字的可能性：{{summary.male_percent}}%
      <br/>
      女生名字的可能性：{{summary.female_percent}}%
    </div>
    <div class="result-content-detail-separator"></div>
    <div class="result-content-detail">
      <div class="result-content-detail-xing">
        <div class="result-content-detail-xing-title">
          {{xing.text}}
        </div>
        <div class="result-content-detail-xing-info">
          {% if xing.has_info %}
            在百家姓中，{{xing.text}}姓的排第{{xing.rank}}位，
            一万人中约有{{xing.num_per_10k}}人姓{{xing.text}}。
          {% else %}
            木有听说过有姓这个的。
          {% endif %}
        </div>
      </div>
      <div class="result-content-detail-separator"></div>
      <div class="result-content-detail-mingchar">
        {% for char in ming_chars %}
          {% if not forloop.first %}
            <div class="result-content-detail-separator"></div>
          {% endif %}
          <div class="result-content-detail-char
            {% if char.male_percent > 50 %}
              result-male-style
            {% elif char.female_percent > 50 %}
              result-female-style
            {% else %}
              result-no-gender-style
            {% endif %}">
            <div class="result-content-detail-char-title">
              {{char.text}}
            </div>
            <div class="result-content-detail-char-info">
              名字里有{{char.text}}字的人一万人中约有{{char.num_per_10k}}个，
              排第{{char.rank}}位。
              <br/>
              其中，{{char.male_percent}}%是男生，{{char.female_percent}}%是女生。
            </div>
          </div>
        {% endfor %}
      </div>
    </div>
  </div>

  {% if debugMode %}
    <div class="base-debug-info">
      姓名: {% include "tt/common/info.tpl" with info=data.xingMingInfo only %}<br>
      姓: {% include "tt/common/info.tpl" with info=data.xingInfo only %}<br>
      名: {% include "tt/common/info.tpl" with info=data.mingInfo only %}<br>
      字：<br>
      {% for info in data.mingCharInfoList %}
        &nbsp;&nbsp;&nbsp;&nbsp;
        {% include "tt/common/info.tpl" with info=info only %}<br> {% endfor %}
      Summary Male Rate:
          {{data.summaryMaleRate|floatformat:2}}
          &nbsp;&nbsp;&nbsp;&nbsp;
      Summary Female Rate:
          {{data.summaryFemaleRate|floatformat:2}}
          &nbsp;&nbsp;&nbsp;&nbsp;
      Summary sum Rate:
          {{data.summarySumRate|floatformat:2}}
          &nbsp;&nbsp;&nbsp;&nbsp;
    </div>
  {% endif %}
{% endblock %}
