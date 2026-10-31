"""Datamodel van Synoptikon.

Keuzes, kort gemotiveerd:

* **Vraag** is het tertium comparationis en de spil van alles. Een Vraag
  heeft per Stelsel precies één **Antwoord** (mijn analyse). Bronnen hangen
  niet rechtstreeks aan de Vraag maar aan het Antwoord (`AntwoordBron`), met
  een volgorde en een korte rol ("hoofdregel", "uitzondering", "rechtspraak").
  Zo kan dezelfde Bron (bijv. § 242 BGB) bij veel vragen een andere functie
  vervullen; dat is precies het functionele uitgangspunt.

* **Bron** is bewust één tabel voor wetsartikel, arrest en literatuur, met een
  `soort`-veld. De velden die alleen voor een soort gelden (ECLI, CELEX, …)
  zitten in `vindplaats` als vrije tekst plus `vindplaats_type`. Aparte
  tabellen per soort zouden elke weergave en de zoekfunctie drie keer zo
  ingewikkeld maken, terwijl de verschillen klein zijn.

* **Vertaling** staat los van Bron, zodat een tekst meerdere vertalingen kan
  hebben (eigen, officieel, DCFR-vertaling) en de synopse er één kan kiezen.

* **Begrip** hoort bij één Stelsel; verwantschap tussen begrippen zit in
  **BegripRelatie** met een getypeerde relatie. Relaties zijn gericht (a → b)
  maar worden in de kaart ongericht getoond; `faux_ami` en `geen_equivalent`
  krijgen daar een afwijkende lijnstijl.

* **Systematiek** is een boom per Stelsel (Boek → Titel → Afdeling, Buch →
  Abschnitt → Titel, Livre → Titre → Chapitre). Een Bron van het soort `wet`
  wijst naar een knoop. De Stelselweergave is niets anders dan deze boom met
  de bronnen van een Vraag erin gemarkeerd.

* **Wettekst / WettekstArtikel** zijn de lokale kopie van geïmporteerde
  wetten, met versiedatum en herkomst. Een Bron kan naar een artikel wijzen,
  maar hoeft dat niet: handmatig ingevoerde teksten blijven mogelijk. Lezen
  gaat altijd uit de database, nooit live.

* **Concordantie** koppelt oude aan nieuwe nummering, met datum en grond.

* **EuHandeling** is de catalogus van het geldende afgeleide Unierecht
  (verordeningen en richtlijnen, ook uitvoerings- en gedelegeerde), uit de
  Cellar van het Publicatiebureau, ingedeeld naar het repertorium
  (**EuRepertorium**). **EuNim** zijn de nationale uitvoeringsmaatregelen
  zoals de lidstaten ze bij de Commissie hebben gemeld; **Omzetting** is
  mijn eigen koppeling op artikelniveau: welk artikel van welke nationale wet
  welk artikel van de handeling omzet of uitvoert. Omzetting gebruikt
  dezelfde (stelsel, wet, nummer[, tot])-vorm als Correspondentie, zodat de
  artikelpagina beide kanten op kan wijzen.

* **Correspondentie** is een thema ("vereisten voor overdracht") met per
  stelsel de artikelen die die functie vervullen (`CorrespondentieArtikel`).
  Groepen in plaats van paren: drie stelsels geven anders drie paren per
  thema, en bij een vierde stelsel zes. Een artikel kan in meerdere thema's
  staan; een lid zonder nummer betekent "geen wettelijke regeling". Artikelen
  worden niet als Bron opgeslagen maar als (stelsel, wet, nummer), zodat ook
  artikelen zonder ingevoerde tekst kunnen corresponderen; de plaats in de
  systematiek volgt uit het nummer (`services/artikelen.py`).
"""
from __future__ import annotations

import re
from datetime import date, datetime, timezone

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .i18n import _


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


class Base(DeclarativeBase):
    pass


# Rechtsfamilies (naar Zweigert/Kötz, met de gebruikelijke correcties): sleutel → (naam, kenmerk).
# De volgorde is die van de kolommen: eerst de civil law, dan de common law, dan het eenvormige recht.
RECHTSFAMILIES: dict[str, tuple[str, str]] = {
    "romaans": ("Romaanse rechtsfamilie", "Code civil-traditie: causaal stelsel, consensualisme, de wet als hoofdbron"),
    "germaans": ("Germaanse rechtsfamilie", "Pandektistiek: Allgemeiner Teil, abstracte begrippen, Trennungs- en Abstraktionsprinzip"),
    "nordisch": ("Nordische rechtsfamilie", "Scandinavisch recht: pragmatisch, weinig codificatie van het algemene deel"),
    "gemengd": ("Gemengde stelsels", "Civil law-kern met common law-bovenbouw: Louisiana, Québec, Schotland, Zuid-Afrika"),
    "common_law": ("Common law", "Rechtersrecht en precedent; statutes vullen aan en worden restrictief uitgelegd"),
    "post_sovjet": ("Post-Sovjetstelsels", "Rusland en de GOS: civil law naar Duits-Nederlands model, met Sovjeterfgoed in uitvoering en rechtspraak"),
    "islamitisch": ("Islamitisch en gemengd-islamitisch recht", "Sharia als bron naast een Frans of Egyptisch geïnspireerd burgerlijk wetboek"),
    "oost_aziatisch": ("Oost-Aziatische stelsels", "Receptie van Duits en Frans civil law (Japan, Korea, Taiwan) en het Chinese socialistische recht"),
    "supranationaal": ("Europees en eenvormig recht", "EU-recht, verdragen en soft law (CISG, PECL, DCFR) als gemeenschappelijke maatstaf"),
}


class Stelsel(Base):
    __tablename__ = "stelsel"

    code: Mapped[str] = mapped_column(String(8), primary_key=True)  # NL, DE, FR, EU, IT, EN …
    naam: Mapped[str] = mapped_column(String(80))
    familie: Mapped[str | None] = mapped_column(String(20))  # sleutel uit RECHTSFAMILIES
    taal: Mapped[str] = mapped_column(String(5))  # hoofdtaal van de wetteksten
    volgorde: Mapped[int] = mapped_column(Integer, default=0)
    actief: Mapped[bool] = mapped_column(default=True)
    toelichting: Mapped[str | None] = mapped_column(Text)

    bronnen: Mapped[list["Bron"]] = relationship(back_populates="stelsel")
    begrippen: Mapped[list["Begrip"]] = relationship(back_populates="stelsel")
    systematiek: Mapped[list["Systematiek"]] = relationship(back_populates="stelsel")

    @property
    def familie_naam(self) -> str:
        return _(RECHTSFAMILIES.get(self.familie or "", ("Overig", ""))[0])


class Vraag(Base):
    __tablename__ = "vraag"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    titel: Mapped[str] = mapped_column(String(300))
    omschrijving: Mapped[str | None] = mapped_column(Text)  # markdown
    rechtsgebied: Mapped[str | None] = mapped_column(String(120))
    tags: Mapped[str | None] = mapped_column(String(300))  # kommagescheiden
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)
    gewijzigd: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    antwoorden: Mapped[list["Antwoord"]] = relationship(
        back_populates="vraag", cascade="all, delete-orphan", order_by="Antwoord.stelsel_code"
    )
    begrippen: Mapped[list["VraagBegrip"]] = relationship(back_populates="vraag", cascade="all, delete-orphan")
    notities: Mapped[list["Notitie"]] = relationship(
        back_populates="vraag", cascade="all, delete-orphan", order_by="Notitie.aangemaakt.desc()"
    )

    @property
    def tag_list(self) -> list[str]:
        return [t.strip() for t in (self.tags or "").split(",") if t.strip()]

    def antwoord_voor(self, code: str) -> "Antwoord | None":
        return next((a for a in self.antwoorden if a.stelsel_code == code), None)


class Antwoord(Base):
    """Mijn analyse voor één Vraag in één Stelsel."""

    __tablename__ = "antwoord"
    __table_args__ = (UniqueConstraint("vraag_id", "stelsel_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    vraag_id: Mapped[int] = mapped_column(ForeignKey("vraag.id", ondelete="CASCADE"))
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    analyse: Mapped[str | None] = mapped_column(Text)  # markdown
    kern: Mapped[str | None] = mapped_column(String(400))  # één zin, bovenaan de kolom
    gewijzigd: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    vraag: Mapped[Vraag] = relationship(back_populates="antwoorden")
    stelsel: Mapped[Stelsel] = relationship()
    bronnen: Mapped[list["AntwoordBron"]] = relationship(
        back_populates="antwoord", cascade="all, delete-orphan", order_by="AntwoordBron.volgorde"
    )


class Bron(Base):
    __tablename__ = "bron"

    id: Mapped[int] = mapped_column(primary_key=True)
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    soort: Mapped[str] = mapped_column(String(16))  # wet | rechtspraak | literatuur | softlaw
    citeertitel: Mapped[str] = mapped_column(String(200))  # "art. 3:84 BW", "§ 929 BGB", "HR 18 juni 1982 (Plas/Valburg)"
    titel: Mapped[str | None] = mapped_column(String(300))  # opschrift / zaaknaam / titel van het werk
    tekst: Mapped[str | None] = mapped_column(Text)  # originele tekst (of kernoverweging)
    taal: Mapped[str] = mapped_column(String(5))
    vindplaats_type: Mapped[str | None] = mapped_column(String(20))  # ECLI | BeckRS | LEGIARTI | CELEX | NJ | …
    vindplaats: Mapped[str | None] = mapped_column(String(200))
    url: Mapped[str | None] = mapped_column(String(500))
    geldig_van: Mapped[date | None] = mapped_column(Date)
    geldig_tot: Mapped[date | None] = mapped_column(Date)
    opmerking: Mapped[str | None] = mapped_column(Text)  # bijv. "tekst ingekort tot de kernoverweging"
    systematiek_id: Mapped[int | None] = mapped_column(ForeignKey("systematiek.id", ondelete="SET NULL"))
    wettekst_artikel_id: Mapped[int | None] = mapped_column(ForeignKey("wettekst_artikel.id", ondelete="SET NULL"))
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)
    gewijzigd: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    stelsel: Mapped[Stelsel] = relationship(back_populates="bronnen")
    systematiek: Mapped["Systematiek | None"] = relationship(back_populates="bronnen")
    wettekst_artikel: Mapped["WettekstArtikel | None"] = relationship()
    vertalingen: Mapped[list["Vertaling"]] = relationship(back_populates="bron", cascade="all, delete-orphan")
    antwoorden: Mapped[list["AntwoordBron"]] = relationship(back_populates="bron", cascade="all, delete-orphan")

    def vertaling(self, taal: str) -> "Vertaling | None":
        return next((v for v in self.vertalingen if v.taal == taal), None)

    @property
    def is_geldig(self) -> bool:
        vandaag = date.today()
        if self.geldig_van and self.geldig_van > vandaag:
            return False
        if self.geldig_tot and self.geldig_tot < vandaag:
            return False
        return True


class Vertaling(Base):
    __tablename__ = "vertaling"
    __table_args__ = (UniqueConstraint("bron_id", "taal"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    bron_id: Mapped[int] = mapped_column(ForeignKey("bron.id", ondelete="CASCADE"))
    taal: Mapped[str] = mapped_column(String(5))
    tekst: Mapped[str] = mapped_column(Text)
    herkomst: Mapped[str] = mapped_column(String(20), default="eigen")  # eigen | officieel | literatuur

    bron: Mapped[Bron] = relationship(back_populates="vertalingen")


class AntwoordBron(Base):
    __tablename__ = "antwoord_bron"
    __table_args__ = (UniqueConstraint("antwoord_id", "bron_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    antwoord_id: Mapped[int] = mapped_column(ForeignKey("antwoord.id", ondelete="CASCADE"))
    bron_id: Mapped[int] = mapped_column(ForeignKey("bron.id", ondelete="CASCADE"))
    volgorde: Mapped[int] = mapped_column(Integer, default=0)
    rol: Mapped[str | None] = mapped_column(String(60))  # hoofdregel | uitzondering | rechtspraak | literatuur | …
    notitie: Mapped[str | None] = mapped_column(Text)  # korte annotatie bij deze bron in deze context (markdown)

    antwoord: Mapped[Antwoord] = relationship(back_populates="bronnen")
    bron: Mapped[Bron] = relationship(back_populates="antwoorden")


class Begrip(Base):
    __tablename__ = "begrip"
    __table_args__ = (UniqueConstraint("stelsel_code", "term"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    term: Mapped[str] = mapped_column(String(120))
    taal: Mapped[str] = mapped_column(String(5))
    definitie: Mapped[str | None] = mapped_column(Text)  # markdown
    vindplaats: Mapped[str | None] = mapped_column(String(200))  # waar het begrip wettelijk verankerd is
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)

    stelsel: Mapped[Stelsel] = relationship(back_populates="begrippen")
    relaties_uit: Mapped[list["BegripRelatie"]] = relationship(
        back_populates="van", foreign_keys="BegripRelatie.van_id", cascade="all, delete-orphan"
    )
    relaties_in: Mapped[list["BegripRelatie"]] = relationship(
        back_populates="naar", foreign_keys="BegripRelatie.naar_id", cascade="all, delete-orphan"
    )
    vragen: Mapped[list["VraagBegrip"]] = relationship(back_populates="begrip", cascade="all, delete-orphan")

    @property
    def relaties(self) -> list["BegripRelatie"]:
        return [*self.relaties_uit, *self.relaties_in]


RELATIE_TYPES: dict[str, str] = {
    "equivalent": "equivalent",
    "deels": "deels overlappend",
    "faux_ami": "faux ami",
    "geen": "geen equivalent",
}


class BegripRelatie(Base):
    __tablename__ = "begrip_relatie"
    __table_args__ = (UniqueConstraint("van_id", "naar_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    van_id: Mapped[int] = mapped_column(ForeignKey("begrip.id", ondelete="CASCADE"))
    naar_id: Mapped[int] = mapped_column(ForeignKey("begrip.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(16))  # sleutel uit RELATIE_TYPES
    toelichting: Mapped[str | None] = mapped_column(Text)

    van: Mapped[Begrip] = relationship(back_populates="relaties_uit", foreign_keys=[van_id])
    naar: Mapped[Begrip] = relationship(back_populates="relaties_in", foreign_keys=[naar_id])

    @property
    def type_label(self) -> str:
        return _(RELATIE_TYPES.get(self.type, self.type))

    def andere(self, begrip: Begrip) -> Begrip:
        return self.naar if self.van_id == begrip.id else self.van


class VraagBegrip(Base):
    __tablename__ = "vraag_begrip"
    __table_args__ = (UniqueConstraint("vraag_id", "begrip_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    vraag_id: Mapped[int] = mapped_column(ForeignKey("vraag.id", ondelete="CASCADE"))
    begrip_id: Mapped[int] = mapped_column(ForeignKey("begrip.id", ondelete="CASCADE"))

    vraag: Mapped[Vraag] = relationship(back_populates="begrippen")
    begrip: Mapped[Begrip] = relationship(back_populates="vragen")


class Notitie(Base):
    """Losse notitie bij een Vraag, al dan niet voor één Stelsel (snel invoeren)."""

    __tablename__ = "notitie"

    id: Mapped[int] = mapped_column(primary_key=True)
    vraag_id: Mapped[int] = mapped_column(ForeignKey("vraag.id", ondelete="CASCADE"))
    stelsel_code: Mapped[str | None] = mapped_column(ForeignKey("stelsel.code"))
    tekst: Mapped[str] = mapped_column(Text)  # markdown
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)

    vraag: Mapped[Vraag] = relationship(back_populates="notities")
    stelsel: Mapped[Stelsel | None] = relationship()


class Systematiek(Base):
    """Boom van de wettelijke systematiek per stelsel."""

    __tablename__ = "systematiek"

    id: Mapped[int] = mapped_column(primary_key=True)
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("systematiek.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(60))  # bijv. "BW-3-4-2", "BGB-3-3-1", "CC-III-I-1-2"
    wet: Mapped[str | None] = mapped_column(String(60))  # None = hoofdcodificatie; anders "OR", "UCC", "SGA 1979"
    label: Mapped[str] = mapped_column(String(200))  # "Boek 3", "Titel 4 Verkrijging en verlies van goederen"
    bereik: Mapped[str | None] = mapped_column(String(80))  # "art. 3:83–3:98", "§§ 929–936"
    volgorde: Mapped[int] = mapped_column(Integer, default=0)

    stelsel: Mapped[Stelsel] = relationship(back_populates="systematiek")
    parent: Mapped["Systematiek | None"] = relationship(back_populates="kinderen", remote_side=[id])
    kinderen: Mapped[list["Systematiek"]] = relationship(back_populates="parent", order_by="Systematiek.volgorde")
    bronnen: Mapped[list[Bron]] = relationship(back_populates="systematiek")

    def pad(self) -> list["Systematiek"]:
        knoop, pad = self, []
        while knoop is not None:
            pad.append(knoop)
            knoop = knoop.parent
        return list(reversed(pad))


class Concordantie(Base):
    __tablename__ = "concordantie"

    id: Mapped[int] = mapped_column(primary_key=True)
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    wet: Mapped[str] = mapped_column(String(80))  # "C. civ.", "BW"
    oud: Mapped[str] = mapped_column(String(80))  # "art. 1382"
    nieuw: Mapped[str | None] = mapped_column(String(80))  # "art. 1240"; None = vervallen zonder opvolger
    datum: Mapped[date | None] = mapped_column(Date)
    grond: Mapped[str | None] = mapped_column(String(300))  # "Ordonnance n° 2016-131 du 10 février 2016"
    toelichting: Mapped[str | None] = mapped_column(Text)

    stelsel: Mapped[Stelsel] = relationship()


class Correspondentie(Base):
    """Thema waarbinnen artikelen uit verschillende stelsels functioneel overeenkomen."""

    __tablename__ = "correspondentie"

    id: Mapped[int] = mapped_column(primary_key=True)
    titel: Mapped[str] = mapped_column(String(200), unique=True)
    rechtsgebied: Mapped[str | None] = mapped_column(String(120))
    toelichting: Mapped[str | None] = mapped_column(Text)  # markdown
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)

    artikelen: Mapped[list["CorrespondentieArtikel"]] = relationship(
        back_populates="correspondentie", cascade="all, delete-orphan", order_by="CorrespondentieArtikel.volgorde"
    )

    def voor(self, stelsel: str) -> list["CorrespondentieArtikel"]:
        return [a for a in self.artikelen if a.stelsel_code == stelsel]


class CorrespondentieArtikel(Base):
    __tablename__ = "correspondentie_artikel"

    id: Mapped[int] = mapped_column(primary_key=True)
    correspondentie_id: Mapped[int] = mapped_column(ForeignKey("correspondentie.id", ondelete="CASCADE"))
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    wet: Mapped[str | None] = mapped_column(String(40))  # None = hoofdwet (BW, BGB, C. civ.)
    nummer: Mapped[str | None] = mapped_column(String(40))  # "3:84", "929", "1112-1"; None = geen regeling
    tot: Mapped[str | None] = mapped_column(String(40))  # einde van een bereik ("1136" bij 1132–1136)
    detail: Mapped[str | None] = mapped_column(String(60))  # "lid 3", "Abs. 2", "al. 5"
    rol: Mapped[str | None] = mapped_column(String(80))  # "hoofdregel", "deels", "faux ami", …
    opmerking: Mapped[str | None] = mapped_column(Text)
    volgorde: Mapped[int] = mapped_column(Integer, default=0)

    correspondentie: Mapped[Correspondentie] = relationship(back_populates="artikelen")
    stelsel: Mapped[Stelsel] = relationship()

    @property
    def ref(self):
        from .services.artikelen import Ref

        return Ref(self.stelsel_code, self.nummer, self.wet, self.tot, self.detail)


class Wettekst(Base):
    """Eén geïmporteerde versie van één wet, lokaal opgeslagen."""

    __tablename__ = "wettekst"
    __table_args__ = (UniqueConstraint("stelsel_code", "wet_id", "versie"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    wet_id: Mapped[str] = mapped_column(String(80))  # BWBR0005291 | bgb | LEGITEXT000006070721 | 32007R0864
    wet: Mapped[str | None] = mapped_column(String(60))  # citeerafkorting ("OR", "C. consom."); None = hoofdcodificatie
    titel: Mapped[str] = mapped_column(String(300))
    versie: Mapped[str] = mapped_column(String(40))  # geldigheidsdatum of versielabel van de bron
    bron_url: Mapped[str | None] = mapped_column(String(500))
    bestand: Mapped[str | None] = mapped_column(String(300))  # relatief pad onder data/wetteksten
    opgehaald: Mapped[datetime] = mapped_column(DateTime, default=now)
    taal: Mapped[str | None] = mapped_column(String(5))  # taal van de tekst als het stelsel er meer heeft (EU); None = de taal van het stelsel
    kern: Mapped[bool] = mapped_column(default=True)  # uit het register (systematiek, overzicht); False = bulkimport (alle wetten)
    stijl: Mapped[str | None] = mapped_column(String(8))  # citeerwijze als die afwijkt van het stelsel: "Art" (GG, EGBGB)
    # Voor `synoptikon bijwerken`: sha256 over de artikelen (store.inhoud_hash), wanneer laatst met de bron vergeleken,
    # en aantal artikelen en tekens (zodat /wetteksten de opslag per stelsel toont zonder alle teksten te tellen).
    hash: Mapped[str | None] = mapped_column(String(64))
    gecontroleerd: Mapped[datetime | None] = mapped_column(DateTime)
    aantal: Mapped[int | None] = mapped_column(Integer)
    grootte: Mapped[int | None] = mapped_column(Integer)

    artikelen: Mapped[list["WettekstArtikel"]] = relationship(
        back_populates="wettekst", cascade="all, delete-orphan", order_by="WettekstArtikel.volgorde"
    )


class WettekstArtikel(Base):
    __tablename__ = "wettekst_artikel"
    __table_args__ = (UniqueConstraint("wettekst_id", "nummer"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    wettekst_id: Mapped[int] = mapped_column(ForeignKey("wettekst.id", ondelete="CASCADE"))
    nummer: Mapped[str] = mapped_column(String(40))  # "3:84", "929", "1196", "12"
    opschrift: Mapped[str | None] = mapped_column(String(300))
    tekst: Mapped[str] = mapped_column(Text)
    pad: Mapped[str | None] = mapped_column(String(400))  # "Boek 3 › Titel 4 › Afdeling 2"
    volgorde: Mapped[int] = mapped_column(Integer, default=0)

    wettekst: Mapped[Wettekst] = relationship(back_populates="artikelen")


class Bijwerking(Base):
    """Logboek van `synoptikon bijwerken`: één regel per bron (en stelsel) per ronde."""

    __tablename__ = "bijwerking"

    id: Mapped[int] = mapped_column(primary_key=True)
    begin: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    bron: Mapped[str] = mapped_column(String(20))  # register · de · nl · fr · eu · eu-catalogus
    stelsel: Mapped[str | None] = mapped_column(String(8))
    gecontroleerd: Mapped[int] = mapped_column(Integer, default=0)
    gewijzigd: Mapped[int] = mapped_column(Integer, default=0)
    nieuw: Mapped[int] = mapped_column(Integer, default=0)
    fouten: Mapped[int] = mapped_column(Integer, default=0)
    duur: Mapped[float] = mapped_column(Float, default=0.0)  # seconden
    melding: Mapped[str | None] = mapped_column(Text)  # waarom gestopt, en de eerste fouten


# --- Unierecht -----------------------------------------------------------------

# Soorten handelingen (art. 288–291 VWEU): sleutel → (enkelvoud, meervoud).
EU_SOORTEN: dict[str, tuple[str, str]] = {
    "verordening": ("verordening", "verordeningen"),
    "richtlijn": ("richtlijn", "richtlijnen"),
    "kaderbesluit": ("kaderbesluit", "kaderbesluiten"),
}
# Variant: basishandeling (wetgevingshandeling of Raad/Commissie op verdragsgrondslag),
# gedelegeerde handeling (art. 290 VWEU) of uitvoeringshandeling (art. 291 VWEU).
EU_VARIANTEN: dict[str, str] = {"basis": "basishandeling", "gedelegeerd": "gedelegeerd (art. 290 VWEU)", "uitvoering": "uitvoering (art. 291 VWEU)"}


class EuRepertorium(Base):
    """Rubriek van het repertorium van de geldende wetgeving van de Unie ("13.30.10")."""

    __tablename__ = "eu_repertorium"

    code: Mapped[str] = mapped_column(String(20), primary_key=True)  # "13.30.10"
    label: Mapped[str] = mapped_column(String(300))
    ouder_code: Mapped[str | None] = mapped_column(String(20))
    niveau: Mapped[int] = mapped_column(Integer, default=1)

    @property
    def toon_label(self) -> str:
        """Rubrieknaam in de taal van het verzoek (zie `services.eu.rubrieklabels`)."""
        from .i18n import taal

        from .services.eu import rubrieklabel

        return rubrieklabel(self.code, taal()) or self.label


class EuHandeling(Base):
    __tablename__ = "eu_handeling"

    celex: Mapped[str] = mapped_column(String(20), primary_key=True)  # 32016R0679
    soort: Mapped[str] = mapped_column(String(16))  # sleutel uit EU_SOORTEN
    variant: Mapped[str] = mapped_column(String(12), default="basis")  # sleutel uit EU_VARIANTEN
    nummer: Mapped[str | None] = mapped_column(String(20))  # "2016/679"
    titel: Mapped[str] = mapped_column(Text)  # volledige titel in het Nederlands
    roepnaam: Mapped[str | None] = mapped_column(String(120))  # "AVG", "AI-verordening"
    datum: Mapped[date | None] = mapped_column(Date)  # datum van de handeling
    in_werking: Mapped[date | None] = mapped_column(Date)  # eerste datum van inwerkingtreding
    toepassing: Mapped[date | None] = mapped_column(Date)  # latere datum van toepassing, als die er is
    geldig_tot: Mapped[date | None] = mapped_column(Date)  # None = onbepaald
    omzettingstermijn: Mapped[date | None] = mapped_column(Date)  # alleen richtlijnen en kaderbesluiten
    eer: Mapped[bool] = mapped_column(default=False)  # relevant voor de EER
    eli: Mapped[str | None] = mapped_column(String(200))
    repertorium: Mapped[str | None] = mapped_column(String(200))  # kommagescheiden codes
    bijgewerkt: Mapped[datetime] = mapped_column(DateTime, default=now)

    nims: Mapped[list["EuNim"]] = relationship(back_populates="handeling", cascade="all, delete-orphan", order_by="EuNim.datum")
    omzettingen: Mapped[list["Omzetting"]] = relationship(back_populates="handeling", cascade="all, delete-orphan", order_by="Omzetting.volgorde")

    @property
    def soort_label(self) -> str:
        return _(EU_SOORTEN.get(self.soort, (self.soort, ""))[0])

    @property
    def toon_titel(self) -> str:
        """Officiële titel in de taal van het verzoek, als `services.eu.met_titels` die heeft opgehaald."""
        return getattr(self, "_titel_vertaald", None) or self.titel

    @property
    def citeer(self) -> str:
        """'Verordening (EU) 2016/679' — kort, zonder de rest van de titel."""
        m = re.match(r"^(.*?\d{2,4}/\d+(?:/\w+)?)", self.toon_titel or "")
        return m.group(1) if m else f"{self.soort_label.capitalize()} {self.nummer or self.celex}"

    @property
    def rep_codes(self) -> list[str]:
        return [c for c in (self.repertorium or "").split(",") if c]

    @property
    def eurlex(self) -> str:
        from .i18n import taal

        return f"https://eur-lex.europa.eu/legal-content/{taal().upper()}/TXT/?uri=CELEX:{self.celex}"


class EuNim(Base):
    """Nationale uitvoeringsmaatregel zoals gemeld aan de Commissie (Cellar, sector 7)."""

    __tablename__ = "eu_nim"
    __table_args__ = (UniqueConstraint("celex", "nim_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    celex: Mapped[str] = mapped_column(ForeignKey("eu_handeling.celex", ondelete="CASCADE"))
    land: Mapped[str] = mapped_column(String(3))  # ISO 3166-1 alpha-3 zoals in Cellar: NLD, DEU, FRA …
    nim_id: Mapped[str] = mapped_column(String(40))  # "72019L0771NLD_202202827"
    titel: Mapped[str] = mapped_column(Text)
    soort_akte: Mapped[str | None] = mapped_column(String(120))  # "Wet", "Gesetz", "Loi", "Decreto legislativo"
    datum: Mapped[date | None] = mapped_column(Date)  # datum van het publicatieblad
    vindplaats: Mapped[str | None] = mapped_column(String(120))  # "nr. 164, p. 1–18"

    handeling: Mapped[EuHandeling] = relationship(back_populates="nims")


# Soorten koppeling tussen een handeling en nationaal recht.
OMZETTING_SOORTEN: dict[str, str] = {
    "omzetting": "omzetting",  # richtlijn → nationale bepaling
    "uitvoering": "uitvoering",  # verordening: sancties, toezicht, keuzes die de verordening laat
    "verwijzing": "verwijzing",  # nationale bepaling verklaart de verordening van toepassing (IPR)
    "navolging": "autonome navolging",  # geen lidstaat (CH) of na de Brexit (EN), maar naar het voorbeeld van de handeling
    "voortgezet": "voortgezet als assimilated law",  # EN: retained EU law, sinds 2024 assimilated law
}


class Omzetting(Base):
    """Artikel(en) van een nationale wet die (een artikel van) een EU-handeling omzetten of uitvoeren."""

    __tablename__ = "omzetting"

    id: Mapped[int] = mapped_column(primary_key=True)
    celex: Mapped[str] = mapped_column(ForeignKey("eu_handeling.celex", ondelete="CASCADE"))
    eu_artikel: Mapped[str | None] = mapped_column(String(40))  # "5", "10–12"; None = de handeling als geheel
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    wet: Mapped[str | None] = mapped_column(String(60))  # None = hoofdcodificatie
    wet_titel: Mapped[str | None] = mapped_column(String(300))  # voor wetten zonder artikelverwijzing ("Uitvoeringswet AVG")
    nummer: Mapped[str | None] = mapped_column(String(40))  # None = de wet als geheel
    tot: Mapped[str | None] = mapped_column(String(40))
    soort: Mapped[str] = mapped_column(String(16), default="omzetting")  # sleutel uit OMZETTING_SOORTEN
    opmerking: Mapped[str | None] = mapped_column(Text)
    geverifieerd: Mapped[bool] = mapped_column(default=False)  # tegen de officiële tekst gecontroleerd
    volgorde: Mapped[int] = mapped_column(Integer, default=0)

    handeling: Mapped[EuHandeling] = relationship(back_populates="omzettingen")
    stelsel: Mapped[Stelsel] = relationship()

    @property
    def ref(self):
        from .services.artikelen import Ref

        return Ref(self.stelsel_code, self.nummer, self.wet, self.tot)

    @property
    def soort_label(self) -> str:
        return _(OMZETTING_SOORTEN.get(self.soort, self.soort))

    @property
    def wet_label(self) -> str:
        """Naam van de wet als geheel (koppeling zonder artikelnummer)."""
        from .services.artikelen import wetnaam

        return self.wet_titel or wetnaam(self.stelsel_code, self.wet) or self.wet or ""


class EuTitel(Base):
    """Officiële titel van een handeling in een andere taal dan het Nederlands (Cellar)."""

    __tablename__ = "eu_titel"

    celex: Mapped[str] = mapped_column(ForeignKey("eu_handeling.celex", ondelete="CASCADE"), primary_key=True)
    taal: Mapped[str] = mapped_column(String(5), primary_key=True)
    titel: Mapped[str] = mapped_column(Text)


class EuRepertoriumLabel(Base):
    """Rubrieknaam van het repertorium in een andere taal dan het Nederlands (Cellar, EuroVoc-stijl)."""

    __tablename__ = "eu_repertorium_label"

    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    taal: Mapped[str] = mapped_column(String(5), primary_key=True)
    label: Mapped[str] = mapped_column(String(300))


class InhoudVertaling(Base):
    """Vertaalgeheugen voor eigen inhoud: Nederlandse brontekst (als hash) → tekst in een andere taal.

    Zie `i18n.py`. `herkomst` is "claude" (machinevertaling, niet
    geverifieerd) of "eigen" (zelf ingevoerd of nagekeken).
    """

    __tablename__ = "inhoud_vertaling"

    hash: Mapped[str] = mapped_column(String(40), primary_key=True)
    taal: Mapped[str] = mapped_column(String(5), primary_key=True)
    tekst: Mapped[str] = mapped_column(Text)
    herkomst: Mapped[str] = mapped_column(String(12), default="claude")
    gewijzigd: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


# Profielen: vast aantal plekken, elk met een eigen taal en wachtwoord.
AANTAL_PROFIELEN = 5
ROLLEN: dict[str, str] = {
    "beheerder": "beheerder",  # alles, ook profielen beheren
    "redacteur": "redacteur",  # lezen en invoeren
    "lezer": "lezer",  # alleen lezen
}


class Profiel(Base):
    __tablename__ = "profiel"

    id: Mapped[int] = mapped_column(primary_key=True)
    gebruikersnaam: Mapped[str] = mapped_column(String(40), unique=True)
    naam: Mapped[str] = mapped_column(String(80))
    rol: Mapped[str] = mapped_column(String(12), default="lezer")
    taal: Mapped[str] = mapped_column(String(5), default="nl")
    wachtwoord_hash: Mapped[str | None] = mapped_column(String(200))
    actief: Mapped[bool] = mapped_column(default=False)
    # Ophogen bij een nieuw wachtwoord of uitzetten: oude sessiecookies vervallen dan.
    sessie_versie: Mapped[int] = mapped_column(Integer, default=0)
    laatst_ingelogd: Mapped[datetime | None] = mapped_column(DateTime)
    # Koppeling met Wunderkammer (routes/wunderkammer.py), per profiel aan te zetten op /profiel.
    wunderkammer: Mapped[bool] = mapped_column(default=False)
    wk_gezien: Mapped[datetime | None] = mapped_column(DateTime)  # laatst dat Wunderkammer de kaarten ophaalde
    # Zelf aangemeld met de uitnodigingscode (/aanmelden): geen domeincookie (sso.py) in of uit, anders kon wie een
    # gebruikersnaam van een ander Wunderkammer-account kiest, dat account overnemen.
    zelf_aangemeld: Mapped[bool] = mapped_column(default=False)
    # Mijn stelsels (kommagescheiden codes), te kiezen op /profiel: alleen die staan in kiezers, filters en kolommen, de
    # rest onder 'meer stelsels…'. None = nog niet gekozen: dan alle actieve, en na het inloggen de stap /welkom.
    stelsels: Mapped[str | None] = mapped_column(Text)
    # Het vak waarin het laatst is bewaard (services/vakken.py): daar komt de volgende kaart terecht als het vak niet volgt
    # uit wat je bewaart.
    laatste_vak: Mapped[str | None] = mapped_column(String(60))
    # De taal waarin juridische inhoud geleverd wordt: welke taalversie van een verdrag, welke afkorting (VWEU of AEUV)
    # en de taal van de kaartzijden. Leeg = volg de interfacetaal. Wie in Berlijn recht studeert zet dit op 'de' en houdt
    # de interface in het Nederlands.
    rechtstaal: Mapped[str | None] = mapped_column(String(5))

    @property
    def stelsel_codes(self) -> list[str] | None:
        return None if self.stelsels is None else [c for c in self.stelsels.split(",") if c]

    @property
    def rol_label(self) -> str:
        return _(ROLLEN.get(self.rol, self.rol))

    @property
    def mag_bewerken(self) -> bool:
        return self.rol in ("beheerder", "redacteur")

    @property
    def is_beheerder(self) -> bool:
        return self.rol == "beheerder"


# --- leren ------------------------------------------------------------------------------
# Leerlijsten zijn persoonlijk (per profiel). Synoptikon maakt de kaarten, Wunderkammer plant de herhaling: het haalt
# de kaarten op via /api/wk/kaarten en meldt per kaart de stand terug (KaartStand). Oefenen in Synoptikon is stampen
# zonder planning; alleen 'gekend / nog niet' wordt bijgehouden.

# soort → (label, uitleg); de volgorde is die in het formulier.
KAARTSOORTEN: dict[str, tuple[str, str]] = {
    "artikel": ("artikel → inhoud", "Wat staat er in dit artikel?"),
    "kern": ("inhoud → artikel", "Welk artikel regelt dit?"),
    "plaats": ("waar staat het", "Plaats in de systematiek van de wet"),
    "tegenhanger": ("tegenhanger", "Het corresponderende artikel in een ander stelsel"),
    "arrest": ("arrest → rechtsregel", "Wat besliste de rechter?"),
    "feiten": ("feiten → arrest", "Welk arrest hoort bij deze feiten?"),
    "vrij": ("vrije kaart", "Eigen vraag en antwoord"),
}
ARTIKELSOORTEN = ("artikel", "kern", "plaats", "tegenhanger")
ARRESTSOORTEN = ("arrest", "feiten")


class Leerlijst(Base):
    __tablename__ = "leerlijst"

    id: Mapped[int] = mapped_column(primary_key=True)
    profiel_id: Mapped[int] = mapped_column(ForeignKey("profiel.id", ondelete="CASCADE"), index=True)
    naam: Mapped[str] = mapped_column(String(120))
    omschrijving: Mapped[str | None] = mapped_column(Text)
    vak: Mapped[str | None] = mapped_column(String(60))  # vak in Wunderkammer ("ZR Ia", "Sachenrecht"); leeg = Jura
    examen: Mapped[date | None] = mapped_column(Date)
    naar_wk: Mapped[bool] = mapped_column(default=True)  # door Wunderkammer laten herhalen
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)
    # Delen (routes/gedeeld.py): privé, alleen wie de link /gedeeld/<deelcode> heeft, of iedereen op /gedeeld.
    zichtbaar: Mapped[str] = mapped_column(String(10), default="prive")  # prive | link | iedereen
    deelcode: Mapped[str | None] = mapped_column(String(16), unique=True)
    gedeeld_op: Mapped[datetime | None] = mapped_column(DateTime)
    overgenomen_van: Mapped[int | None] = mapped_column(ForeignKey("leerlijst.id", ondelete="SET NULL"))

    profiel: Mapped["Profiel"] = relationship()
    kaarten: Mapped[list["Kaart"]] = relationship(back_populates="lijst", cascade="all, delete-orphan", order_by="Kaart.id")
    likes: Mapped[list["LijstLike"]] = relationship(cascade="all, delete-orphan")
    reacties: Mapped[list["LijstReactie"]] = relationship(cascade="all, delete-orphan", order_by="LijstReactie.aangemaakt")


class Kaart(Base):
    __tablename__ = "kaart"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(32), unique=True)  # stabiel voor Wunderkammer (gen_key "syn:<uid>")
    lijst_id: Mapped[int] = mapped_column(ForeignKey("leerlijst.id", ondelete="CASCADE"), index=True)
    soort: Mapped[str] = mapped_column(String(16))  # sleutel uit KAARTSOORTEN
    # Artikel (artikel, kern, plaats, tegenhanger)
    stelsel_code: Mapped[str | None] = mapped_column(String(8))
    wet: Mapped[str | None] = mapped_column(String(40))
    nummer: Mapped[str | None] = mapped_column(String(40))
    doel_stelsel: Mapped[str | None] = mapped_column(String(8))  # tegenhanger: in welk stelsel
    lid: Mapped[str | None] = mapped_column(String(8))  # artikel: alleen dit lid ("1", "2a"); leeg = het hele artikel
    # Arrest (arrest, feiten): uit een bron, of met eigen zaaknaam en vindplaats
    bron_id: Mapped[int | None] = mapped_column(ForeignKey("bron.id", ondelete="SET NULL"))
    zaak: Mapped[str | None] = mapped_column(String(300))  # "HR 18 juni 1982 (Plas/Valburg)"
    vindplaats: Mapped[str | None] = mapped_column(String(200))  # ECLI, NJ, BGHZ …
    feiten: Mapped[str | None] = mapped_column(Text)
    # Vrij te vullen; bij artikelkaarten overschrijft `vraag` de voorkant (kern: de omschrijving om naar te vragen)
    vraag: Mapped[str | None] = mapped_column(Text)
    antwoord: Mapped[str | None] = mapped_column(Text)  # arrest: de rechtsregel
    notitie: Mapped[str | None] = mapped_column(Text)  # komt onder het antwoord
    actief: Mapped[bool] = mapped_column(default=True)
    # Uit een notitie (services/notities.py): eerst een voorstel, dat je overneemt (status leeg) of afwijst. Een
    # afgewezen kaart blijft bewaard, zodat dezelfde kaart bij de volgende ronde niet opnieuw wordt voorgesteld.
    status: Mapped[str | None] = mapped_column(String(10))  # leeg | voorstel | afgewezen
    herkomst: Mapped[str | None] = mapped_column(String(300))  # pad van de notitie
    gekend: Mapped[bool | None] = mapped_column()  # laatste oefenresultaat in Synoptikon
    geoefend: Mapped[datetime | None] = mapped_column(DateTime)
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)
    gewijzigd: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    lijst: Mapped[Leerlijst] = relationship(back_populates="kaarten")
    bron: Mapped["Bron | None"] = relationship()
    stand: Mapped["KaartStand | None"] = relationship(cascade="all, delete-orphan", uselist=False)

    @property
    def soort_label(self) -> str:
        return _(KAARTSOORTEN.get(self.soort, (self.soort, ""))[0])


ZICHTBAAR: dict[str, str] = {
    "prive": "alleen ik",
    "link": "iedereen met de link",
    "iedereen": "alle studenten (op Gedeeld)",
}


class LijstLike(Base):
    __tablename__ = "lijst_like"

    lijst_id: Mapped[int] = mapped_column(ForeignKey("leerlijst.id", ondelete="CASCADE"), primary_key=True)
    profiel_id: Mapped[int] = mapped_column(ForeignKey("profiel.id", ondelete="CASCADE"), primary_key=True)
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)


class LijstReactie(Base):
    __tablename__ = "lijst_reactie"

    id: Mapped[int] = mapped_column(primary_key=True)
    lijst_id: Mapped[int] = mapped_column(ForeignKey("leerlijst.id", ondelete="CASCADE"), index=True)
    profiel_id: Mapped[int] = mapped_column(ForeignKey("profiel.id", ondelete="CASCADE"))
    tekst: Mapped[str] = mapped_column(Text)
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)

    profiel: Mapped["Profiel"] = relationship()


class KaartStand(Base):
    """Wat Wunderkammer over een kaart terugmeldt (FSRS)."""

    __tablename__ = "kaart_stand"

    kaart_id: Mapped[int] = mapped_column(ForeignKey("kaart.id", ondelete="CASCADE"), primary_key=True)
    due: Mapped[datetime | None] = mapped_column(DateTime)
    stabiliteit: Mapped[float | None] = mapped_column()  # dagen
    herhalingen: Mapped[int] = mapped_column(Integer, default=0)
    missers: Mapped[int] = mapped_column(Integer, default=0)
    laatst: Mapped[datetime | None] = mapped_column(DateTime)
    laatste_score: Mapped[int | None] = mapped_column(Integer)  # 1 opnieuw … 4 makkelijk
    bijgewerkt: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    @property
    def fase(self) -> str:
        """nieuw · leert · vastzit · beheerst (sleutel uit FASEN)."""
        if not self.herhalingen:
            return "nieuw"
        if (self.stabiliteit or 0) >= BEHEERST_DAGEN:
            return "beheerst"
        if self.missers >= 2 or (self.missers and self.laatste_score == 1):
            return "vastzit"
        return "leert"


# Stand van een kaart in Wunderkammer, van zwak naar sterk. Vast zit: twee keer vergeten, of vergeten en de laatste keer
# weer fout. Beheerst: Wunderkammer verwacht dat je haar over drie weken nog weet (stabiliteit in dagen, FSRS).
FASEN: dict[str, str] = {"vastzit": "zit vast", "nieuw": "nieuw", "leert": "leert", "beheerst": "beheerst"}
BEHEERST_DAGEN = 21


class NotitieBestand(Base):
    """Een notitie uit de vault die kaartvoorstellen heeft opgeleverd; de hash bepaalt of ze opnieuw aan de beurt is."""

    __tablename__ = "notitie_bestand"
    __table_args__ = (UniqueConstraint("profiel_id", "pad"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    profiel_id: Mapped[int] = mapped_column(ForeignKey("profiel.id", ondelete="CASCADE"), index=True)
    pad: Mapped[str] = mapped_column(String(300))  # relatief, bijv. "Zivilrecht 1A/1 Einführung/Vorlesung.md"
    vak: Mapped[str | None] = mapped_column(String(60))
    hash: Mapped[str] = mapped_column(String(64))
    voorstellen: Mapped[int] = mapped_column(Integer, default=0)  # bij de laatste ronde
    fout: Mapped[str | None] = mapped_column(Text)
    verwerkt: Mapped[datetime] = mapped_column(DateTime, default=now)


# --- Claude ----------------------------------------------------------------------------
# Opzoeken (een artikel, wet of uitspraak noemen, Claude zegt waar het staat en wat er staat) en onderzoek bij een vraag.
# Alles wat Claude levert is gemarkeerd als niet geverifieerd; de wettekst zelf komt altijd uit de lokale import.


class LlmGebruik(Base):
    """Eén aanroep van de API: voor het maandbudget (config.llm_budget_usd)."""

    __tablename__ = "llm_gebruik"

    id: Mapped[int] = mapped_column(primary_key=True)
    doel: Mapped[str] = mapped_column(String(20))  # opzoeken | onderzoek
    model: Mapped[str] = mapped_column(String(60))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_uit: Mapped[int] = mapped_column(Integer, default=0)
    zoekacties: Mapped[int] = mapped_column(Integer, default=0)
    usd: Mapped[float] = mapped_column(default=0.0)
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class Opzoeking(Base):
    """Wat iemand op /opzoeken intypte en wat er gevonden werd: het logboek van een college."""

    __tablename__ = "opzoeking"

    id: Mapped[int] = mapped_column(primary_key=True)
    profiel_id: Mapped[int] = mapped_column(ForeignKey("profiel.id", ondelete="CASCADE"), index=True)
    invoer: Mapped[str] = mapped_column(String(400))
    # Wat er gevonden is: {"soort": artikel|wet|uitspraak|onbekend, "stelsel", "wet", "nummer", "citeer", "titel",
    # "vindplaats", "url", "plaats", "tekst", "toelichting", "bron": "lokaal"|"claude"}
    resultaat: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(12), default="klaar")  # klaar | bezig | fout
    fout: Mapped[str | None] = mapped_column(Text)
    bron_id: Mapped[int | None] = mapped_column(ForeignKey("bron.id", ondelete="SET NULL"))  # uitspraak, als bron bewaard
    kaart_id: Mapped[int | None] = mapped_column(ForeignKey("kaart.id", ondelete="SET NULL"))  # bewaard voor Wunderkammer
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)

    kaart: Mapped["Kaart | None"] = relationship()


MARKERINGSOORTEN: dict[str, str] = {"kern": "Kern", "voorwaarde": "Voorwaarde", "let_op": "Let op"}


class Markering(Base):
    """Een stuk tekst dat je in een artikel of uitspraak aanwees, voor een vak (services/markeringen.py).

    Bewaard als tekstaanhaling (`quote` met een stukje tekst ervoor en erna), niet als index: een nieuwe versie van de
    wettekst verschuift niets. Een artikel wordt aangewezen met stelsel, wet en nummer (zoals een Kaart), niet met het rijnummer
    van een import. Gemarkeerde stukken zijn het materiaal voor kaarten: de rechtsregel van een arrest, de vetgedrukte
    voorwaarden in een artikel."""

    __tablename__ = "markering"

    id: Mapped[int] = mapped_column(primary_key=True)
    profiel_id: Mapped[int] = mapped_column(ForeignKey("profiel.id", ondelete="CASCADE"), index=True)
    bron_id: Mapped[int | None] = mapped_column(ForeignKey("bron.id", ondelete="CASCADE"), index=True)
    stelsel_code: Mapped[str | None] = mapped_column(String(8))
    wet: Mapped[str | None] = mapped_column(String(40))
    nummer: Mapped[str | None] = mapped_column(String(40))
    quote: Mapped[str] = mapped_column(Text)
    voor: Mapped[str] = mapped_column(String(80), default="")  # tekst vlak vóór de quote (om de juiste plek te vinden)
    na: Mapped[str] = mapped_column(String(80), default="")
    vak: Mapped[str | None] = mapped_column(String(60))  # leeg = voor elk vak
    soort: Mapped[str] = mapped_column(String(12), default="kern")  # sleutel uit MARKERINGSOORTEN
    notitie: Mapped[str | None] = mapped_column(Text)
    aangemaakt: Mapped[datetime] = mapped_column(DateTime, default=now)

    @property
    def soort_label(self) -> str:
        return _(MARKERINGSOORTEN.get(self.soort, self.soort))


class Onderzoek(Base):
    """Rechtsvergelijkend onderzoek door Claude bij een vraag; het resultaat vult de synopse waar die nog leeg is."""

    __tablename__ = "onderzoek"

    id: Mapped[int] = mapped_column(primary_key=True)
    vraag_id: Mapped[int] = mapped_column(ForeignKey("vraag.id", ondelete="CASCADE"), index=True)
    stelsels: Mapped[str] = mapped_column(String(200))  # kommagescheiden codes
    opdracht: Mapped[str | None] = mapped_column(Text)  # extra aanwijzingen
    status: Mapped[str] = mapped_column(String(12), default="wacht")  # wacht | bezig | klaar | fout
    voortgang: Mapped[str | None] = mapped_column(Text)  # laatste stap, voor de statusregel
    fout: Mapped[str | None] = mapped_column(Text)
    resultaat: Mapped[dict | None] = mapped_column(JSON)  # {"synthese", "stelsels": [{code, kern, analyse, bronnen: [..]}]}
    model: Mapped[str | None] = mapped_column(String(60))
    usd: Mapped[float] = mapped_column(default=0.0)
    gestart: Mapped[datetime] = mapped_column(DateTime, default=now)
    klaar: Mapped[datetime | None] = mapped_column(DateTime)

    vraag: Mapped[Vraag] = relationship()
