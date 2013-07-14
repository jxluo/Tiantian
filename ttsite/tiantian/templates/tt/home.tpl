{% extends "tt/base.tpl" %}


{% block title %}
  试试你的名字
{% endblock %}

{% block viewExtendHead %}
  {% load static %}
  <link rel="stylesheet" type="text/css"
    href="{% static "tt/css/home.css" %}"></link>
  <script type="text/javascript" src="{% static "tt/js/home.js" %}"></script>
{% endblock %}

{% block bodyLoadedScript %}
  startScript();
{% endblock %}

{% block viewContent %}
  <div class="home-content-container">
    <div class="home-logo-card">
    </div>
    <div class="home-input-container">
      <input id="input" type="text" class="home-input-text">
      <div class="home-input-button" onClick="home.handleInputButtonClick()">
        我输入好啦
      </div>
    </div>
    <div class="home-input-invalid-hint">
    </div>
  </div>
{% endblock %}
