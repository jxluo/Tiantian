<html>
  <head>
    <title>{% block title %} Tiantian Site {% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" type="text/css"
      href="{% static "tt/css/base.css" %}"></link>
    <script type="text/javascript" src="{% static "tt/js/base.js" %}"></script>
  </head>
  <body>
    {% block viewContent %}
      Base Tempalte
    {% endblock %}
  </body>
</html>
