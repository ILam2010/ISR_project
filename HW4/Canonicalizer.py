"""
 Written by Vinod Vishwanath
 Adapted for Python 3
"""

from urllib.parse import urlparse


class Canonicalizer:

    @staticmethod
    def get_domain(url, include_scheme=True):
        parse = urlparse(url)

        # Force scheme to http and normalize
        parse = parse._replace(scheme='http')
        scheme = parse.scheme.lower()
        domain = parse.netloc.lower()

        clean_domain = Canonicalizer.clean_domain(domain, scheme)

        if include_scheme:
            return f"{scheme}://{clean_domain}"
        else:
            return clean_domain

    @staticmethod
    def is_relative_url(url):
        parse = urlparse(url)
        return parse.netloc == ''

    @staticmethod
    def canonicalize(url, domain=None):

        # Handle relative URLs
        if domain is not None:
            url = domain.rstrip('/') + '/' + url.lstrip('/')

        parse = urlparse(url)

        # Normalize scheme
        parse = parse._replace(scheme='http')

        output = f"{parse.scheme.lower()}://"
        output += Canonicalizer.clean_domain(
            parse.netloc.lower(),
            parse.scheme.lower()
        )

        if parse.path:
            output += Canonicalizer.clean_path(parse.path)

        return output

    @staticmethod
    def clean_domain(domain, scheme):

        if scheme == 'http':
            return rchop(domain, ':80')
        elif scheme == 'https':
            return rchop(domain, ':443')

        return domain

    @staticmethod
    def clean_path(path):

        comps = path.split('/')
        output = ''

        for cmp in comps:
            if cmp and cmp != '/':
                output += '/' + cmp

        return output


def rchop(string, ending):
    if string.endswith(ending):
        return string[:-len(ending)]
    return string


# Test
print(Canonicalizer.get_domain("https://www.en.wikipedia.org/wiki/World_War_II"))
