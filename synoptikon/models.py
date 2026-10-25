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
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


class Base(DeclarativeBase):
    pass


class Stelsel(Base):
    __tablename__ = "stelsel"

    code: Mapped[str] = mapped_column(String(8), primary_key=True)  # NL, DE, FR, EU, IT, EN …
    naam: Mapped[str] = mapped_column(String(80))
    taal: Mapped[str] = mapped_column(String(5))  # hoofdtaal van de wetteksten
    volgorde: Mapped[int] = mapped_column(Integer, default=0)
    actief: Mapped[bool] = mapped_column(default=True)
    toelichting: Mapped[str | None] = mapped_column(Text)

    bronnen: Mapped[list["Bron"]] = relationship(back_populates="stelsel")
    begrippen: Mapped[list["Begrip"]] = relationship(back_populates="stelsel")
    systematiek: Mapped[list["Systematiek"]] = relationship(back_populates="stelsel")


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
        return RELATIE_TYPES.get(self.type, self.type)

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


class Wettekst(Base):
    """Eén geïmporteerde versie van één wet, lokaal opgeslagen."""

    __tablename__ = "wettekst"
    __table_args__ = (UniqueConstraint("stelsel_code", "wet_id", "versie"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    stelsel_code: Mapped[str] = mapped_column(ForeignKey("stelsel.code"))
    wet_id: Mapped[str] = mapped_column(String(80))  # BWBR0005291 | bgb | LEGITEXT000006070721 | 32007R0864
    titel: Mapped[str] = mapped_column(String(300))
    versie: Mapped[str] = mapped_column(String(40))  # geldigheidsdatum of versielabel van de bron
    bron_url: Mapped[str | None] = mapped_column(String(500))
    bestand: Mapped[str | None] = mapped_column(String(300))  # relatief pad onder data/wetteksten
    opgehaald: Mapped[datetime] = mapped_column(DateTime, default=now)

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
