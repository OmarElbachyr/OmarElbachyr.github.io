---
layout: page
permalink: /publications/
title: Publications
description: Research publications and preprints by Omar El Bachyr, in reverse chronological order.
nav: true
nav_order: 2
---

<link rel="stylesheet" href="{{ '/assets/css/site.css' | relative_url }}">

<!-- _pages/publications.md -->

See my [Google Scholar profile](https://scholar.google.com/citations?user=k9z_ASsAAAAJ&hl=en) for citation metrics.

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

{% capture publication_list %}
{% bibliography %}
{% endcapture %}
{{ publication_list | replace: '>Abs</a>', '>Abstract</a>' }}

</div>
