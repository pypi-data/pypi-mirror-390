from extractors.deterministic_extractor import DeterministicLinkExtractor

sample_html = """
<a href="/about">About Us</a>
<link rel="canonical" href="https://example.com/home" />
<meta property="og:url" content="https://example.com/page" />
<div data-href="/contact">Get in Touch</div>
"""

links = DeterministicLinkExtractor.extract(sample_html, "https://example.com")
for link in links:
    print(link)
