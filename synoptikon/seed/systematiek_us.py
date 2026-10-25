"""Systematiek voor de Verenigde Staten: privaatrecht is statelijk recht.

Wat uniform is, komt uit drie hoeken: de Uniform Commercial Code (door alle
staten ingevoerd), de Restatements van het American Law Institute (geen wet,
maar gezaghebbende herformulering van de common law) en andere uniforme
wetten. Daarnaast twee statelijke wetboeken als voorbeeld, waaronder de
Louisiana Civil Code (civil law-traditie, gemengd stelsel).

UCC-indeling (Articles en Parts) uit Cornell LII (officiële tekst van ALI/ULC);
de hoofdstukken van de Restatement (Second) of Contracts zijn die van de
uitgave van 1981 (niet online gecontroleerd). Knopen zonder bereik bevatten
elke section van hun wet.
"""

US = [
    ('US-UCC', 'Uniform Commercial Code (ALI/ULC; in alle staten ingevoerd, Louisiana deels)', '', [
        ('US-UCC-1', 'Article 1 · General Provisions', '§§ 1-101–1-310', [
            ('US-UCC-1-1', 'Part 1 · General Provisions', '§§ 1-101–1-108', []),
            ('US-UCC-1-2', 'Part 2 · General Definitions and Principles of Interpretation', '§§ 1-201–1-206', []),
            ('US-UCC-1-3', 'Part 3 · Territorial Applicability and General Rules', '§§ 1-301–1-310', []),
        ]),
        ('US-UCC-2', 'Article 2 · Sales', '§§ 2-101–2-725', [
            ('US-UCC-2-1', 'Part 1 · Short Title, General Construction and Subject Matter', '§§ 2-101–2-107', []),
            ('US-UCC-2-2', 'Part 2 · Form, Formation and Readjustment of Contract', '§§ 2-201–2-210', []),
            ('US-UCC-2-3', 'Part 3 · General Obligation and Construction of Contract', '§§ 2-301–2-328', []),
            ('US-UCC-2-4', 'Part 4 · Title, Creditors and Good Faith Purchasers', '§§ 2-401–2-403', []),
            ('US-UCC-2-5', 'Part 5 · Performance', '§§ 2-501–2-515', []),
            ('US-UCC-2-6', 'Part 6 · Breach, Repudiation and Excuse', '§§ 2-601–2-616', []),
            ('US-UCC-2-7', 'Part 7 · Remedies', '§§ 2-701–2-725', []),
        ]),
        ('US-UCC-3', 'Article 3 · Negotiable Instruments', '§§ 3-101–3-605', [
            ('US-UCC-3-1', 'Part 1 · General Provisions and Definitions', '§§ 3-101–3-119', []),
            ('US-UCC-3-2', 'Part 2 · Negotiation, Transfer, and Indorsement', '§§ 3-201–3-207', []),
            ('US-UCC-3-3', 'Part 3 · Enforcement of Instruments', '§§ 3-301–3-312', []),
            ('US-UCC-3-4', 'Part 4 · Liability of Parties', '§§ 3-401–3-420', []),
            ('US-UCC-3-5', 'Part 5 · Dishonor', '§§ 3-501–3-505', []),
            ('US-UCC-3-6', 'Part 6 · Discharge and Payment', '§§ 3-601–3-605', []),
        ]),
        ('US-UCC-9', 'Article 9 · Secured Transactions', '§§ 9-101–9-709', [
            ('US-UCC-9-1', 'Part 1 · General Provisions', '§§ 9-101–9-110', []),
            ('US-UCC-9-2', 'Part 2 · Effectiveness of Security Agreement; Attachment of Security Interest; Rights of Parties to Security Agreement', '§§ 9-201–9-210', []),
            ('US-UCC-9-3', 'Part 3 · Perfection and Priority', '§§ 9-301–9-342', []),
            ('US-UCC-9-4', 'Part 4 · Rights of Third Parties', '§§ 9-401–9-409', []),
            ('US-UCC-9-5', 'Part 5 · Filing', '§§ 9-501–9-527', []),
            ('US-UCC-9-6', 'Part 6 · Default', '§§ 9-601–9-628', []),
            ('US-UCC-9-7', 'Part 7 · Transition', '§§ 9-701–9-709', []),
        ]),
    ], 'UCC'),
    ('US-REST', 'Restatements of the Law (American Law Institute)', '', [
        ('US-REST2K', 'Restatement (Second) of Contracts (1981)', '§§ 1–385', [
            ('US-REST2K-1', 'Chapter 1 · Meaning of Terms', '§§ 1–8', []),
            ('US-REST2K-2', 'Chapter 2 · Formation of Contracts—Parties and Capacity', '§§ 9–16', []),
            ('US-REST2K-3', 'Chapter 3 · Formation of Contracts—Mutual Assent', '§§ 17–70', []),
            ('US-REST2K-4', 'Chapter 4 · Formation of Contracts—Consideration', '§§ 71–109', []),
            ('US-REST2K-5', 'Chapter 5 · The Statute of Frauds', '§§ 110–150', []),
            ('US-REST2K-6', 'Chapter 6 · Mistake', '§§ 151–158', []),
            ('US-REST2K-7', 'Chapter 7 · Misrepresentation, Duress and Undue Influence', '§§ 159–177', []),
            ('US-REST2K-8', 'Chapter 8 · Unenforceability on Grounds of Public Policy', '§§ 178–199', []),
            ('US-REST2K-9', 'Chapter 9 · The Scope of Contractual Obligations', '§§ 200–230', []),
            ('US-REST2K-10', 'Chapter 10 · Performance and Non-Performance', '§§ 231–260', []),
            ('US-REST2K-11', 'Chapter 11 · Impracticability of Performance and Frustration of Purpose', '§§ 261–272', []),
            ('US-REST2K-12', 'Chapter 12 · Discharge by Assent or Alteration', '§§ 273–287', []),
            ('US-REST2K-13', 'Chapter 13 · Joint and Several Promisors and Promisees', '§§ 288–301', []),
            ('US-REST2K-14', 'Chapter 14 · Contract Beneficiaries', '§§ 302–315', []),
            ('US-REST2K-15', 'Chapter 15 · Assignment and Delegation', '§§ 316–343', []),
            ('US-REST2K-16', 'Chapter 16 · Remedies', '§§ 344–385', []),
        ], 'Rest. 2d Contracts'),
        ('US-REST2T', 'Restatement (Second) of Torts (1965–1979)', '', [], 'Rest. 2d Torts'),
        ('US-REST3PEH', 'Restatement (Third) of Torts: Liability for Physical and Emotional Harm', '', [], 'Rest. 3d Torts: PEH'),
        ('US-REST3PL', 'Restatement (Third) of Torts: Products Liability (1998)', '', [], 'Rest. 3d Torts: Prod. Liab.'),
        ('US-REST3AP', 'Restatement (Third) of Torts: Apportionment of Liability (2000)', '', [], 'Rest. 3d Torts: Apport.'),
        ('US-REST3R', 'Restatement (Third) of Restitution and Unjust Enrichment (2011)', '', [], 'Rest. 3d Restitution'),
        ('US-REST3AG', 'Restatement (Third) of Agency (2006)', '', [], 'Rest. 3d Agency'),
        ('US-REST3W', 'Restatement (Third) of Property: Wills and Other Donative Transfers', '', [], 'Rest. 3d Property: Wills'),
        ('US-REST3TR', 'Restatement (Third) of Trusts', '', [], 'Rest. 3d Trusts'),
    ]),
    ('US-UNIFORM', 'Andere uniforme wetten (Uniform Law Commission)', '', [
        ('US-UPC', 'Uniform Probate Code', '', [], 'UPC'),
        ('US-UMDA', 'Uniform Marriage and Divorce Act', '', [], 'UMDA'),
        ('US-UPA', 'Uniform Parentage Act (2017)', '', [], 'UPA 2017'),
        ('US-RUPA', 'Revised Uniform Partnership Act', '', [], 'RUPA'),
        ('US-RULLCA', 'Revised Uniform Limited Liability Company Act', '', [], 'RULLCA'),
    ]),
    ('US-STATE', 'Statelijke codificaties (voorbeelden)', '', [
        ('US-CALCIV', 'California Civil Code (1872, Field Code)', '', [], 'Cal. Civ. Code'),
        ('US-CALFAM', 'California Family Code', '', [], 'Cal. Fam. Code'),
        ('US-LACC', 'Louisiana Civil Code (gemengd stelsel, civil law-traditie)', '', [], 'La. C.C.'),
    ]),
    ('US-FED', 'Federaal recht (U.S. Code)', '', [
        ('US-USC11', 'Title 11 · Bankruptcy', '', [], '11 U.S.C.'),
        ('US-USC15', 'Title 15 · Commerce and Trade (o.a. Magnuson-Moss Warranty Act)', '', [], '15 U.S.C.'),
    ]),
]
