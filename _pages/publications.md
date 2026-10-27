---
layout: page
permalink: /publications/
title: Publications
description: Research publications and preprints by Omar El Bachyr, in reverse chronological order.
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

{% assign total_citations = 0 %}
{% assign tracked_publications = 0 %}
{% for paper in site.data.citations.papers %}
  {% assign paper_key = paper[0] %}
  {% if paper_key contains 'k9z_ASsAAAAJ:' %}
    {% assign total_citations = total_citations | plus: paper[1].citations %}
    {% assign tracked_publications = tracked_publications | plus: 1 %}
  {% endif %}
{% endfor %}
<a class="citation-summary" href="https://scholar.google.com/citations?user=k9z_ASsAAAAJ&hl=en" aria-label="{{ total_citations }} Google Scholar citations across {{ tracked_publications }} tracked publications">
  <span class="citation-summary__value">{{ total_citations }}</span>
  <span class="citation-summary__label">Google Scholar citations</span>
  <span class="citation-summary__detail">across {{ tracked_publications }} tracked publications</span>
</a>

See my [Google Scholar profile](https://scholar.google.com/citations?user=k9z_ASsAAAAJ&hl=en) for citation metrics.

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

{% capture publication_list %}
{% bibliography %}
{% endcapture %}
{{ publication_list | replace: '>Abs</a>', '>Abstract</a>' }}

</div>
