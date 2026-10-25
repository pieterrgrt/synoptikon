"""Systematiek voor Australië: federaal (Commonwealth) en statelijk recht.

Common law met Engelse wortels; contract en tort zijn grotendeels
rechtersrecht. De Australian Consumer Law (sch 2 bij de Competition and
Consumer Act 2010) is één federale wet die in alle staten geldt; Chapters en
Parts komen uit de inhoudsopgave van de geldende compilatie op
legislation.gov.au (C2026C00405, stand 16-9-2026). Goederen-, erf- en
aansprakelijkheidsrecht verschillen per staat; New South Wales staat hier
als voorbeeld. Knopen zonder bereik bevatten elke section van hun wet.
"""

AU = [
    ('AU-ACL', 'Australian Consumer Law (Competition and Consumer Act 2010 (Cth) sch 2)', 'ss 1–310', [
        ('AU-ACL-1', 'Chapter 1 · Introduction', 'ss 1–17', []),
        ('AU-ACL-2', 'Chapter 2 · General protections', 'ss 18–28A', [
            ('AU-ACL-2-1', 'Part 2-1 · Misleading or deceptive conduct', 'ss 18–19', []),
            ('AU-ACL-2-2', 'Part 2-2 · Unconscionable conduct', 'ss 20–22A', []),
            ('AU-ACL-2-3', 'Part 2-3 · Unfair contract terms', 'ss 23–28A', []),
        ]),
        ('AU-ACL-3', 'Chapter 3 · Specific protections', 'ss 29–150', [
            ('AU-ACL-3-1', 'Part 3-1 · Unfair practices', 'ss 29–50', []),
            ('AU-ACL-3-2', 'Part 3-2 · Consumer transactions', 'ss 51–103', []),
            ('AU-ACL-3-3', 'Part 3-3 · Safety of consumer goods and product related services', 'ss 104–133', []),
            ('AU-ACL-3-4', 'Part 3-4 · Information standards', 'ss 134–137B', []),
            ('AU-ACL-3-5', 'Part 3-5 · Liability of manufacturers for goods with safety defects', 'ss 138–150', []),
        ]),
        ('AU-ACL-4', 'Chapter 4 · Offences', 'ss 151–217', [
            ('AU-ACL-4-1', 'Part 4-1 · Offences relating to unfair practices', 'ss 151–168', []),
            ('AU-ACL-4-2', 'Part 4-2 · Offences relating to consumer transactions', 'ss 169–193', []),
            ('AU-ACL-4-3', 'Part 4-3 · Offences relating to safety of consumer goods and product related services', 'ss 194–202', []),
            ('AU-ACL-4-4', 'Part 4-4 · Offences relating to information standards', 'ss 203–204', []),
            ('AU-ACL-4-5', 'Part 4-5 · Offences relating to substantiation notices', 'ss 205–206', []),
            ('AU-ACL-4-6', 'Part 4-6 · Defences', 'ss 207–211', []),
            ('AU-ACL-4-7', 'Part 4-7 · Miscellaneous', 'ss 212–217', []),
        ]),
        ('AU-ACL-5', 'Chapter 5 · Enforcement and remedies', 'ss 218–287', [
            ('AU-ACL-5-1', 'Part 5-1 · Enforcement', 'ss 218–223', []),
            ('AU-ACL-5-2', 'Part 5-2 · Remedies', 'ss 224–253', []),
            ('AU-ACL-5-3', 'Part 5-3 · Country of origin representations', 'ss 254–258', []),
            ('AU-ACL-5-4', 'Part 5-4 · Remedies relating to guarantees', 'ss 259–277', []),
            ('AU-ACL-5-5', 'Part 5-5 · Liability of suppliers and credit providers', 'ss 278–287', []),
        ]),
        ('AU-ACL-6', 'Chapter 6 · Application and transitional provisions', 'ss 288–310', []),
    ], 'ACL'),
    ('AU-CTH', 'Commonwealth', '', [
        ('AU-CCA', 'Competition and Consumer Act 2010 (Cth)', '', [], 'CCA 2010 (Cth)'),
        ('AU-CORP', 'Corporations Act 2001 (Cth)', '', [], 'Corporations Act 2001 (Cth)'),
        ('AU-PPSA', 'Personal Property Securities Act 2009 (Cth)', '', [], 'PPSA 2009 (Cth)'),
        ('AU-FLA', 'Family Law Act 1975 (Cth)', '', [], 'Family Law Act 1975 (Cth)'),
        ('AU-BANKR', 'Bankruptcy Act 1966 (Cth)', '', [], 'Bankruptcy Act 1966 (Cth)'),
    ]),
    ('AU-NSW', 'New South Wales (als voorbeeld van een staat)', '', [
        ('AU-NSW-SGA', 'Sale of Goods Act 1923 (NSW)', '', [], 'Sale of Goods Act 1923 (NSW)'),
        ('AU-NSW-FCA', 'Frustrated Contracts Act 1978 (NSW)', '', [], 'Frustrated Contracts Act 1978 (NSW)'),
        ('AU-NSW-MPCA', 'Minors (Property and Contracts) Act 1970 (NSW)', '', [], 'Minors (Property and Contracts) Act 1970 (NSW)'),
        ('AU-NSW-CLA', 'Civil Liability Act 2002 (NSW)', '', [], 'Civil Liability Act 2002 (NSW)'),
        ('AU-NSW-LRMPA', 'Law Reform (Miscellaneous Provisions) Act 1965 (NSW)', '', [], 'Law Reform (Miscellaneous Provisions) Act 1965 (NSW)'),
        ('AU-NSW-LA', 'Limitation Act 1969 (NSW)', '', [], 'Limitation Act 1969 (NSW)'),
        ('AU-NSW-CONV', 'Conveyancing Act 1919 (NSW)', '', [], 'Conveyancing Act 1919 (NSW)'),
        ('AU-NSW-RPA', 'Real Property Act 1900 (NSW) · Torrens-registratie', '', [], 'Real Property Act 1900 (NSW)'),
        ('AU-NSW-SUCC', 'Succession Act 2006 (NSW)', '', [], 'Succession Act 2006 (NSW)'),
        ('AU-NSW-ADOPT', 'Adoption Act 2000 (NSW)', '', [], 'Adoption Act 2000 (NSW)'),
    ]),
]
