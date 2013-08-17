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
    <div class="home-search-container">
      <input id="search-input" type="text" class="base-search-input home-search-input">
      <div class="base-search-button home-search-button"
          onClick="base.handleInputButtonClick()">
        我输入好啦
      </div>
    </div>
    <div class="home-search-invalid-hint">
    </div>
  </div>
{% endblock %}
