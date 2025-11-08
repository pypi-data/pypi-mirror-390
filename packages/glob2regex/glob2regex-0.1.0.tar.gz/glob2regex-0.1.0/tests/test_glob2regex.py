"""Basic glob2regex tests."""
from glob2regex import glob2regex


def test_normal() -> None:
    """Test default settings."""
    search_list = {
        "Sociální služby/*/ST-*/*.pdf": "^Sociální služby\\/.*\\/ST-.*\\/.*\\.pdf$",
        "Sociální služby/*/ST-*/q[01-10]*.pdf": "^Sociální služby\\/.*\\/ST-.*\\/q01-10.*\\.pdf$",
        "Soubory společné/M-Směrnice organizačně právní/*/Směrnice/*.pdf": "^Soubory společné\\/M-Směrnice organizačně právní\\/.*\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/E-Ekonomické směrnice/*/Směrnice/*.pdf": "^Soubory společné\\/E-Ekonomické směrnice\\/.*\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/I-Přístup k informacím/Směrnice/*.pdf": "^Soubory společné\\/I-Přístup k informacím\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/Z-Zdravotní úsek/*.pdf": "^Soubory společné\\/Z-Zdravotní úsek\\/.*\\.pdf$",
        "Soubory společné/P-Personální úsek/Směrnice/*.pdf": "^Soubory společné\\/P-Personální úsek\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/S-Sociální úsek/Směrnice/*.pdf": "^Soubory společné\\/S-Sociální úsek\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/T-Provozní úsek/Směrnice/*.pdf": "^Soubory společné\\/T-Provozní úsek\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/Pokyny ředitele/*/*.pdf": "^Soubory společné\\/Pokyny ředitele\\/.*\\/.*\\.pdf$",
        "Soubory společné/Řády/*/Směrnice/*.pdf": "^Soubory společné\\/Řády\\/.*\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/EU-GDPR/*/*.pdf": "^Soubory společné\\/EU-GDPR\\/.*\\/.*\\.pdf$",
    }

    for glob, regex in search_list.items():
        assert regex == glob2regex(glob)


def test_extended() -> None:
    """Test extended option True."""
    search_list = {
        "Sociální služby/*/ST-*/*.pdf": "^Sociální služby\\/.*\\/ST-.*\\/.*\\.pdf$",
        "Sociální služby/*/ST-*/q[01-10]*.pdf": "^Sociální služby\\/.*\\/ST-.*\\/q[01-10].*\\.pdf$",
        "Soubory společné/M-Směrnice organizačně právní/*/Směrnice/*.pdf": "^Soubory společné\\/M-Směrnice organizačně právní\\/.*\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/E-Ekonomické směrnice/*/Směrnice/*.pdf": "^Soubory společné\\/E-Ekonomické směrnice\\/.*\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/I-Přístup k informacím/Směrnice/*.pdf": "^Soubory společné\\/I-Přístup k informacím\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/Z-Zdravotní úsek/*.pdf": "^Soubory společné\\/Z-Zdravotní úsek\\/.*\\.pdf$",
        "Soubory společné/P-Personální úsek/Směrnice/*.pdf": "^Soubory společné\\/P-Personální úsek\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/S-Sociální úsek/Směrnice/*.pdf": "^Soubory společné\\/S-Sociální úsek\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/T-Provozní úsek/Směrnice/*.pdf": "^Soubory společné\\/T-Provozní úsek\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/Pokyny ředitele/*/*.pdf": "^Soubory společné\\/Pokyny ředitele\\/.*\\/.*\\.pdf$",
        "Soubory společné/Řády/*/Směrnice/*.pdf": "^Soubory společné\\/Řády\\/.*\\/Směrnice\\/.*\\.pdf$",
        "Soubory společné/EU-GDPR/*/*.pdf": "^Soubory společné\\/EU-GDPR\\/.*\\/.*\\.pdf$",
    }

    for glob, regex in search_list.items():
        assert regex == glob2regex(glob, extended=True)


def test_glob_star() -> None:
    """Test glob_star option True."""
    search_list = {
        "Sociální služby/*/ST-*/*.pdf": "^Sociální služby\\/([^/]*)\\/ST-([^/]*)\\/([^/]*)\\.pdf$",
        "Sociální služby/*/ST-*/q[01-10]*.pdf": "^Sociální služby\\/([^/]*)\\/ST-([^/]*)\\/q01-10([^/]*)\\.pdf$",
        "Soubory společné/M-Směrnice organizačně právní/*/Směrnice/*.pdf": "^Soubory společné\\/M-Směrnice organizačně právní\\/([^/]*)\\/Směrnice\\/([^/]*)\\.pdf$",
        "Soubory společné/E-Ekonomické směrnice/*/Směrnice/*.pdf": "^Soubory společné\\/E-Ekonomické směrnice\\/([^/]*)\\/Směrnice\\/([^/]*)\\.pdf$",
        "Soubory společné/I-Přístup k informacím/Směrnice/*.pdf": "^Soubory společné\\/I-Přístup k informacím\\/Směrnice\\/([^/]*)\\.pdf$",
        "Soubory společné/Z-Zdravotní úsek/*.pdf": "^Soubory společné\\/Z-Zdravotní úsek\\/([^/]*)\\.pdf$",
        "Soubory společné/P-Personální úsek/Směrnice/*.pdf": "^Soubory společné\\/P-Personální úsek\\/Směrnice\\/([^/]*)\\.pdf$",
        "Soubory společné/S-Sociální úsek/Směrnice/*.pdf": "^Soubory společné\\/S-Sociální úsek\\/Směrnice\\/([^/]*)\\.pdf$",
        "Soubory společné/T-Provozní úsek/Směrnice/*.pdf": "^Soubory společné\\/T-Provozní úsek\\/Směrnice\\/([^/]*)\\.pdf$",
        "Soubory společné/Pokyny ředitele/*/*.pdf": "^Soubory společné\\/Pokyny ředitele\\/([^/]*)\\/([^/]*)\\.pdf$",
        "Soubory společné/Řády/*/Směrnice/*.pdf": "^Soubory společné\\/Řády\\/([^/]*)\\/Směrnice\\/([^/]*)\\.pdf$",
        "Soubory společné/EU-GDPR/*/*.pdf": "^Soubory společné\\/EU-GDPR\\/([^/]*)\\/([^/]*)\\.pdf$",
    }

    for glob, regex in search_list.items():
        assert regex == glob2regex(glob, glob_star=True)
