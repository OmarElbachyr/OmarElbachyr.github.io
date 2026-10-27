# Omar El Bachyr — Personal Website

My academic website, featuring my research, publications, projects, and CV.

**Visit:** [omarelbachyr.github.io](https://omarelbachyr.github.io/)

I am a PhD researcher at the University of Luxembourg, working on information retrieval, multimodal document understanding, and retrieval-augmented generation.

Built with [Jekyll](https://jekyllrb.com/) and the [al-folio](https://github.com/alshedivat/al-folio) starter. Hosted on GitHub Pages.

## Updating the site

- **About:** [`_pages/about.md`](_pages/about.md)
- **Publications:** [`_bibliography/papers.bib`](_bibliography/papers.bib)
- **Projects:** [`_projects/`](_projects/)
- **CV and social links:** [`_data/`](_data/)
- **Site settings:** [`_config.yml`](_config.yml)

Google Scholar publications and citation counts sync automatically through GitHub Actions. See the [sync documentation](docs/CUSTOMIZE.md#automatic-google-scholar-citation-updates).

## Local preview

```bash
docker compose up -d
```

Open [localhost:8080](http://localhost:8080/). To stop the preview:

```bash
docker compose down
```

Changes pushed to `main` deploy automatically through GitHub Actions.

For further setup and customization, see the [documentation](docs/README.md).
