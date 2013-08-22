<html>
  <head>
    <title>{% block title %} Tiantian Site {% endblock %}</title>
    {% load static %}
    <script>
      // Google Analytic code.
      (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
      (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
      m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
      })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

      ga('create', 'UA-43328182-1', 'tiant.me');
      ga('send', 'pageview');
    </script>
    <link rel="stylesheet" type="text/css"
      href="{% static "tt/css/base.css" %}"></link>
    <script type="text/javascript" src="{% static "tt/js/base.js" %}"></script>
    {% block viewExtendHead %}{% endblock %}
  </head>
  <body onload="{% block bodyLoadedScript %}{% endblock %}">
    {% block viewContent %}
      Base Tempalte
    {% endblock %}
  </body>
</html>
