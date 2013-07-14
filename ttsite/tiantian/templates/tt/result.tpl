{% extends "tt/base.tpl" %}

{% block viewContent %}
  姓名: {{ name }} <br>
  姓: {% include "tt/common/info.tpl" with info=data.xingInfo only %}<br>
  名: {% include "tt/common/info.tpl" with info=data.mingInfo only %}<br>
  字：<br>
  {% for info in data.mingCharInfoList %}
    &nbsp;&nbsp;&nbsp;&nbsp;
    {% include "tt/common/info.tpl" with info=info only %}<br>
  {% endfor %}
{% endblock %}
