{{info.text}}
rate: {{info.rate|floatformat:6}}
&nbsp;&nbsp;&nbsp;&nbsp;
rank: {{info.rank}}
&nbsp;&nbsp;&nbsp;&nbsp;
rank_rate: {{info.rank_rate|floatformat:6}}
&nbsp;&nbsp;&nbsp;&nbsp;
sum_rate: {{info.sum_rate|floatformat:6}}
&nbsp;&nbsp;&nbsp;&nbsp;
male_rate: {{ info.gender.male_rate|floatformat:2 }}
&nbsp;&nbsp;&nbsp;&nbsp;
female_rate: {{ info.gender.female_rate|floatformat:2 }}
&nbsp;&nbsp;&nbsp;&nbsp;
genderInfoReliable: {{ info.gender.reliable|floatformat:2 }}
&nbsp;&nbsp;&nbsp;&nbsp;
InfoReliable: {{ info.reliable|floatformat:2 }}
{% if info.raw_info%}
&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;
count: {{ info.raw_info.count }}
&nbsp;&nbsp;&nbsp;&nbsp;
male count: {{ info.raw_info.male_count }}
&nbsp;&nbsp;&nbsp;&nbsp;
female count: {{ info.raw_info.female_count }}
{% endif %}
