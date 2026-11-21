# plglegal.com

Website for Prospect Law Group, PC.

- `content/`: every page, as Markdown with a short header (title, description, URL). Edit text here.
- `public/`: images, video, CSS, JavaScript.
- `templates/`: page layout and the contact form.
- `build.py`: turns content into the finished site in `dist/`. Run `python3 build.py` after editing (needs `pip install markdown pyyaml jinja2`; `pillow` is optional and makes smaller image copies for faster pages).
- `dist/`: the finished site. DigitalOcean serves this folder as-is.

Contact form submissions go to contact@plglegal.com through FormSubmit.

To add Google Analytics or Google Ads tracking, set `GA_ID` / `ADS_ID` at the top of `build.py` and rebuild.
