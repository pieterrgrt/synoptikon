"""Systematiek voor Azië en Oceanië: de hoofdindeling van de burgerlijke wetboeken (of wat het privaatrecht draagt).

JP: gegenereerd uit de geldende tekst van het 民法 bij e-Gov (stand 24-6-2026): 編 › 章, bereik = laagste en
hoogste artikelnummer (geschrapte bereiken zoals 第三十八条から第八十四条まで meegeteld).

TW: gegenereerd uit de geldende tekst van het 民法 bij law.moj.gov.tw (stand 17-8-2026): 編 › 章, in het 債編 ook 節.

HK: geen codificatie; zoals bij EN een eigen indeling in rubrieken met de ordinances eronder, Parts en Chapters uit
de open data van het DoJ (Cap. 26 stand 20-9-2018, Basic Law 1-7-1997). De rest vult de import aan.
"""

JP = [
    ('JP-1', '第一編 · 総則', 'art. 1–174', [
        ('JP-1-1', '第一章 · 通則', 'art. 1–2', []),
        ('JP-1-2', '第二章 · 人', 'art. 3–32の2', []),
        ('JP-1-3', '第三章 · 法人', 'art. 33–84', []),
        ('JP-1-4', '第四章 · 物', 'art. 85–89', []),
        ('JP-1-5', '第五章 · 法律行為', 'art. 90–137', []),
        ('JP-1-6', '第六章 · 期間の計算', 'art. 138–143', []),
        ('JP-1-7', '第七章 · 時効', 'art. 144–174', []),
    ]),
    ('JP-2', '第二編 · 物権', 'art. 175–398の22', [
        ('JP-2-1', '第一章 · 総則', 'art. 175–179', []),
        ('JP-2-2', '第二章 · 占有権', 'art. 180–205', []),
        ('JP-2-3', '第三章 · 所有権', 'art. 206–264の14', []),
        ('JP-2-4', '第四章 · 地上権', 'art. 265–269の2', []),
        ('JP-2-5', '第五章 · 永小作権', 'art. 270–279', []),
        ('JP-2-6', '第六章 · 地役権', 'art. 280–294', []),
        ('JP-2-7', '第七章 · 留置権', 'art. 295–302', []),
        ('JP-2-8', '第八章 · 先取特権', 'art. 303–341', []),
        ('JP-2-9', '第九章 · 質権', 'art. 342–367', []),
        ('JP-2-10', '第十章 · 抵当権', 'art. 369–398の22', []),
    ]),
    ('JP-3', '第三編 · 債権', 'art. 399–724の2', [
        ('JP-3-1', '第一章 · 総則', 'art. 399–520の20', []),
        ('JP-3-2', '第二章 · 契約', 'art. 521–696', []),
        ('JP-3-3', '第三章 · 事務管理', 'art. 697–702', []),
        ('JP-3-4', '第四章 · 不当利得', 'art. 703–708', []),
        ('JP-3-5', '第五章 · 不法行為', 'art. 709–724の2', []),
    ]),
    ('JP-4', '第四編 · 親族', 'art. 725–881', [
        ('JP-4-1', '第一章 · 総則', 'art. 725–730', []),
        ('JP-4-2', '第二章 · 婚姻', 'art. 731–771', []),
        ('JP-4-3', '第三章 · 親子', 'art. 772–817の13', []),
        ('JP-4-4', '第四章 · 親権', 'art. 818–837', []),
        ('JP-4-5', '第五章 · 後見', 'art. 838–875', []),
        ('JP-4-6', '第六章 · 保佐及び補助', 'art. 876–876の10', []),
        ('JP-4-7', '第七章 · 扶養', 'art. 877–881', []),
    ]),
    ('JP-5', '第五編 · 相続', 'art. 882–1050', [
        ('JP-5-1', '第一章 · 総則', 'art. 882–885', []),
        ('JP-5-2', '第二章 · 相続人', 'art. 886–895', []),
        ('JP-5-3', '第三章 · 相続の効力', 'art. 896–914', []),
        ('JP-5-4', '第四章 · 相続の承認及び放棄', 'art. 915–940', []),
        ('JP-5-5', '第五章 · 財産分離', 'art. 941–950', []),
        ('JP-5-6', '第六章 · 相続人の不存在', 'art. 951–959', []),
        ('JP-5-7', '第七章 · 遺言', 'art. 960–1027', []),
        ('JP-5-8', '第八章 · 配偶者の居住の権利', 'art. 1028–1041', []),
        ('JP-5-9', '第九章 · 遺留分', 'art. 1042–1049', []),
        ('JP-5-10', '第十章 · 特別の寄与', 'art. 1050', []),
    ]),
]

TW = [
    ('TW-1', '第一編 · 總則', 'art. 1–152', [
        ('TW-1-1', '第一章 · 法例', 'art. 1–5', []),
        ('TW-1-2', '第二章 · 人', 'art. 6–65', []),
        ('TW-1-3', '第三章 · 物', 'art. 66–70', []),
        ('TW-1-4', '第四章 · 法律行為', 'art. 71–118', []),
        ('TW-1-5', '第五章 · 期日及期間', 'art. 119–124', []),
        ('TW-1-6', '第六章 · 消滅時效', 'art. 125–147', []),
        ('TW-1-7', '第七章 · 權利之行使', 'art. 148–152', []),
    ]),
    ('TW-2', '第二編 · 債', 'art. 153–756-9', [
        ('TW-2-1', '第一章 · 通則', 'art. 153–344', [
            ('TW-2-1-1', '第一節 · 債之發生', 'art. 153–198', []),
            ('TW-2-1-2', '第二節 · 債之標的', 'art. 199–218-1', []),
            ('TW-2-1-3', '第三節 · 債之效力', 'art. 219–270', []),
            ('TW-2-1-4', '第四節 · 多數債務人及債權人', 'art. 271–293', []),
            ('TW-2-1-5', '第五節 · 債之移轉', 'art. 294–306', []),
            ('TW-2-1-6', '第六節 · 債之消滅', 'art. 307–344', []),
        ]),
        ('TW-2-2', '第二章 · 各種之債', 'art. 345–756-9', [
            ('TW-2-2-1', '第一節 · 買賣', 'art. 345–397', []),
            ('TW-2-2-2', '第二節 · 互易', 'art. 398–399', []),
            ('TW-2-2-3', '第三節 · 交互計算', 'art. 400–405', []),
            ('TW-2-2-4', '第四節 · 贈與', 'art. 406–420', []),
            ('TW-2-2-5', '第五節 · 租賃', 'art. 421–463-1', []),
            ('TW-2-2-6', '第六節 · 借貸', 'art. 464–481', []),
            ('TW-2-2-7', '第七節 · 僱傭', 'art. 482–489', []),
            ('TW-2-2-8', '第八節 · 承攬', 'art. 490–514', []),
            ('TW-2-2-9', '第八節之一 · 旅遊', 'art. 514-1–514-12', []),
            ('TW-2-2-10', '第九節 · 出版', 'art. 515–527', []),
            ('TW-2-2-11', '第十節 · 委任', 'art. 528–552', []),
            ('TW-2-2-12', '第十一節 · 經理人及代辦商', 'art. 553–564', []),
            ('TW-2-2-13', '第十二節 · 居間', 'art. 565–575', []),
            ('TW-2-2-14', '第十三節 · 行紀', 'art. 576–588', []),
            ('TW-2-2-15', '第十四節 · 寄託', 'art. 589–612', []),
            ('TW-2-2-16', '第十五節 · 倉庫', 'art. 613–621', []),
            ('TW-2-2-17', '第十六節 · 運送', 'art. 622–659', []),
            ('TW-2-2-18', '第十七節 · 承攬運送', 'art. 660–666', []),
            ('TW-2-2-19', '第十八節 · 合夥', 'art. 667–699', []),
            ('TW-2-2-20', '第十九節 · 隱名合夥', 'art. 700–709', []),
            ('TW-2-2-21', '第十九節之一 · 合會', 'art. 709-1–709-9', []),
            ('TW-2-2-22', '第二十節 · 指示證券', 'art. 710–718', []),
            ('TW-2-2-23', '第二十一節 · 無記名證券', 'art. 719–728', []),
            ('TW-2-2-24', '第二十二節 · 終身定期金', 'art. 729–735', []),
            ('TW-2-2-25', '第二十三節 · 和解', 'art. 736–738', []),
            ('TW-2-2-26', '第二十四節 · 保證', 'art. 739–756', []),
            ('TW-2-2-27', '第二十四節之一 · 人事保證', 'art. 756-1–756-9', []),
        ]),
    ]),
    ('TW-3', '第三編 · 物權', 'art. 757–966', [
        ('TW-3-1', '第一章 · 通則', 'art. 757–764', []),
        ('TW-3-2', '第二章 · 所有權', 'art. 765–831', []),
        ('TW-3-3', '第三章 · 地上權', 'art. 832–841-6', []),
        ('TW-3-4', '第四章 · （刪除）', 'art. 842–850', []),
        ('TW-3-5', '第四章之一 · 農育權', 'art. 850-1–850-9', []),
        ('TW-3-6', '第五章 · 不動產役權', 'art. 851–859-5', []),
        ('TW-3-7', '第六章 · 抵押權', 'art. 860–883', []),
        ('TW-3-8', '第七章 · 質權', 'art. 884–910', []),
        ('TW-3-9', '第八章 · 典權', 'art. 911–927', []),
        ('TW-3-10', '第九章 · 留置權', 'art. 928–939', []),
        ('TW-3-11', '第十章 · 占有', 'art. 940–966', []),
    ]),
    ('TW-4', '第四編 · 親屬', 'art. 967–1137', [
        ('TW-4-1', '第一章 · 通則', 'art. 967–971', []),
        ('TW-4-2', '第二章 · 婚姻', 'art. 972–1058', []),
        ('TW-4-3', '第三章 · 父母子女', 'art. 1059–1090', []),
        ('TW-4-4', '第四章 · 監護', 'art. 1091–1113-10', []),
        ('TW-4-5', '第五章 · 扶養', 'art. 1114–1121', []),
        ('TW-4-6', '第六章 · 家', 'art. 1122–1128', []),
        ('TW-4-7', '第七章 · 親屬會議', 'art. 1129–1137', []),
    ]),
    ('TW-5', '第五編 · 繼承', 'art. 1138–1225', [
        ('TW-5-1', '第一章 · 遺產繼承人', 'art. 1138–1146', []),
        ('TW-5-2', '第二章 · 遺產之繼承', 'art. 1147–1185', []),
        ('TW-5-3', '第三章 · 遺囑', 'art. 1186–1225', []),
    ]),
]


HK = [
    ('HK-GRONDWET', 'Grondwet', '', [
        ('HK-BL', 'Basic Law', 'art. 1–160', [
            ('HK-BL-I', 'Chapter I · General Principles', 'art. 1–11', []),
            ('HK-BL-II', 'Chapter II · Relationship between the Central Authorities and the HKSAR', 'art. 12–23', []),
            ('HK-BL-III', 'Chapter III · Fundamental Rights and Duties of the Residents', 'art. 24–42', []),
            ('HK-BL-IV', 'Chapter IV · Political Structure', 'art. 43–104', []),
            ('HK-BL-V', 'Chapter V · Economy', 'art. 105–135', []),
            ('HK-BL-VI', 'Chapter VI · Education, Science, Culture, Sports, Religion, Labour and Social Services', 'art. 136–149', []),
            ('HK-BL-VII', 'Chapter VII · External Affairs', 'art. 150–157', []),
            ('HK-BL-VIII', 'Chapter VIII · Interpretation and Amendment of the Basic Law', 'art. 158–159', []),
            ('HK-BL-IX', 'Chapter IX · Supplementary Provisions', 'art. 160', []),
        ], 'BL'),
    ]),
    ('HK-CONTRACT', 'Contract en koop', '', [
        ('HK-CAP26', 'Sale of Goods Ordinance (Cap. 26)', 'ss 1–62', [
            ('HK-CAP26-I', 'Part I · Formation of the Contract', 'ss 3–17', []),
            ('HK-CAP26-II', 'Part II · Effects of the Contract', 'ss 18–28', []),
            ('HK-CAP26-III', 'Part III · Performance of the Contract', 'ss 29–39', []),
            ('HK-CAP26-IV', 'Part IV · Rights of Unpaid Seller against the Goods', 'ss 40–50', []),
            ('HK-CAP26-V', 'Part V · Actions for Breach of the Contract', 'ss 51–56', []),
            ('HK-CAP26-VI', 'Part VI · Supplementary', 'ss 57–62', []),
        ], 'Cap. 26'),
        ('HK-CAP71', 'Control of Exemption Clauses Ordinance (Cap. 71)', '', [], 'Cap. 71'),
        ('HK-CAP284', 'Misrepresentation Ordinance (Cap. 284)', '', [], 'Cap. 284'),
        ('HK-CAP457', 'Supply of Services (Implied Terms) Ordinance (Cap. 457)', '', [], 'Cap. 457'),
        ('HK-CAP623', 'Contracts (Rights of Third Parties) Ordinance (Cap. 623)', '', [], 'Cap. 623'),
        ('HK-CAP347', 'Limitation Ordinance (Cap. 347)', '', [], 'Cap. 347'),
    ]),
    ('HK-VENNOOTSCHAP', 'Vennootschappen', '', [
        ('HK-CAP622', 'Companies Ordinance (Cap. 622)', '', [], 'Cap. 622'),
    ]),
    ('HK-STRAF', 'Strafrecht', '', [
        ('HK-CAP200', 'Crimes Ordinance (Cap. 200)', '', [], 'Cap. 200'),
    ]),
]
