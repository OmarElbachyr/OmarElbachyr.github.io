---
layout: about
title: About
permalink: /
nav: false
nav_order: 1
subtitle: PhD Researcher · <a href="https://www.uni.lu/">University of Luxembourg</a>
profile:
  align: right
  image: omar-el-bachyr.jpeg
  image_circular: false
  more_info: >
    <p>TruX Research Group</p>
    <p>SnT, University of Luxembourg</p>
selected_papers: false # Rendered below to expand the abstract button label.
social: false
announcements:
  enabled: false
latest_posts:
  enabled: false
---

I work in the [TruX Research Group](https://www.uni.lu/snt-en/research-groups/trux/), supervised by [Prof. Jacques Klein]({{ site.data.coauthors.klein[0].url }}), with guidance from [Prof. Tegawendé F. Bissyandé]({{ site.data.coauthors.bissyande[0].url }}) and [Prof. Saad Ezzini]({{ site.data.coauthors.ezzini[0].url }}), in collaboration with BGL BNP Paribas.

My research focuses on information retrieval (IR), multimodal document understanding, and retrieval-augmented generation (RAG) over visually rich documents.

I am also interested in multilingual and low-resource retrieval and RAG, particularly for Luxembourgish.

#### Research Interests

- Information Retrieval (IR) & Multimodal Retrieval
- Retrieval-Augmented Generation (RAG)
- Multilingual & Low-Resource Natural Language Processing (NLP)

[Google Scholar](https://scholar.google.com/citations?user={{ site.data.socials.scholar_userid }}) · [GitHub](https://github.com/{{ site.data.socials.github_username }}) · [ORCID](https://orcid.org/{{ site.data.socials.orcid_id }}) · [Email](mailto:{{ site.data.socials.email }}) · [X](https://x.com/{{ site.data.socials.x_username }})

<h2 id="selected-publications">
  <a href="{{ '/publications/' | relative_url }}" style="color: inherit">Selected Publications</a>
</h2>

{% capture selected_publications %}
{% include selected_papers.liquid %}
{% endcapture %}
{{ selected_publications | replace: '>Abs</a>', '>Abstract</a>' }}
