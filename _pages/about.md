---
layout: about
title: About
permalink: /
nav: false
nav_order: 1
subtitle: PhD Researcher · <a href="https://www.uni.lu/">University of Luxembourg</a>
profile:
  align: right
  image: omar-el-bachyr.jpg
  image_circular: false
  more_info: >
    <p>TruX Research Group</p>
    <p>SnT, University of Luxembourg</p>
selected_papers: false # Rendered below to expand the abstract button label.
social: true
announcements:
  enabled: false
latest_posts:
  enabled: false
---

<link rel="stylesheet" href="{{ '/assets/css/site.css' | relative_url }}">

I am a PhD Researcher in the [Trustworthy Software (TruX) group](https://www.uni.lu/snt-en/people/omar-el-bachyr/) at the [Interdisciplinary Centre for Security, Reliability and Trust (SnT)](https://www.uni.lu/snt-en/), University of Luxembourg.

My research focuses on information retrieval, multimodal retrieval, visually rich documents, retrieval-augmented generation, and multilingual information retrieval. I study how document processing and retrieval methods support question answering over complex documents, including financial reports and Luxembourgish documents.

You can find my work on the [Publications page]({{ '/publications/' | relative_url }}) and my academic background on the [CV page]({{ '/cv/' | relative_url }}).

<h2>
  <a href="{{ '/publications/' | relative_url }}" style="color: inherit">Selected Publications</a>
</h2>

{% capture selected_publications %}
{% include selected_papers.liquid %}
{% endcapture %}
{{ selected_publications | replace: '>Abs</a>', '>Abstract</a>' }}
