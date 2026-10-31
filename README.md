# MURSUMIES – TAVARA EI OLE TYRKYLLÄ

**Bisnes. Avioliitto. Konkurssi.**

Suomenkielinen, absurdin kaksimielinen komentorivitekstiseikkailu. Päähenkilö Markku Mursunen eli Mursumies on yrittäjä, jonka firma tekee hädin tuskin liikevaihtoa, mutta jonka mielestä vika on aina markkinoissa, vaimossa tai tavaran tyrkyllä olemisessa.

## Pelin käynnistäminen

Tarvitset **Python 3.11:n tai uudemman**. Ulkoisia Python-kirjastoja tai verkkoyhteyttä ei tarvita.

**Windows:** pura ZIP kokonaan yhteen kansioon ja kaksoisnapsauta `pelaa.bat`. Voit myös avata komentokehotteen projektikansiossa ja suorittaa:

```powershell
py -3 mursumies.py
```

**Linux/macOS:**

```bash
python3 mursumies.py
```

Myös `python main.py` toimii.

**Älä siirrä** pelin käynnistystiedostoa erilleen `game.py`-tiedostosta ja `chapters`-kansiosta: niiden pitää olla samassa projektikansiossa.

## Pelaaminen

Valitse valikoista numeroilla. Valinnat vaikuttavat rahaan, vaimon tyytyväisyyteen, bisnesmaineeseen, avioliiton lämpöön, Mursumiehen egoon, nolouteen ja stressiin. Rahaa voi ansaita myös sivutehtävistä. Joissakin tilanteissa aiemmin hankitut esineet tai aiemmat valinnat avaavat uusia vaihtoehtoja.

Pelaamisen aikana käytössä ovat seuraavat komennot:

| Komento | Toiminto |
|---|---|
| `tila` | Tilastot ja kulunut aika |
| `esineet` | Tutki omistamiasi esineitä |
| `tutki` | Tutki luvun ympäristöä |
| `sivut` | Tee luvun valinnaisia sivukeikkoja |
| `aika` | Näytä luvun ja koko pelin aika |
| `tallenna` | Tallenna tilanteesi |
| `lopeta` | Tallenna ja lopeta |
| `ohje` | Näytä komennot |
| `nopeus` | Vaihda kirjoituskonetulostus päälle/pois |

Peli tallentuu myös automaattisesti valintojen jälkeen. Tallennus löytyy tiedostosta `tallennus.json`, joka syntyy pelin käynnistämisen jälkeen. **Kun käynnistät uuden pelin, vanha tallennus korvataan** erillisen vahvistuksen jälkeen.

## Kesto

Pelissä on **yhdeksän lukua, 45 pääkohtausta, 18 sivutapahtumaa ja 54 tutkittavaa kohdetta**. Jokaisessa pääkohtauksessa on useita valintoja.

Koko peliä ei voi saada päätökseen alle **15 minuutin todellista pelaamisaikaa**. Jokaisessa luvussa on oma vähimmäiskestonsa. Vähimmäisajan aikana voit tehdä sivukeikkoja ja tutkia ympäristöä. Kun luvun tehtävät on tehty ja aika täyttyy, pääset jatkamaan seuraavaan lukuun.

Pelissä käytetään monotonista ajastinta, joten tietokoneen järjestelmäkellon muuttaminen ei ohita aikaa. Peliaika **ei kerry**, kun ohjelma on suljettuna. Jos suoritat kaikki kohtaukset poikkeuksellisen nopeasti, luvun lopussa voi olla aikaa jäljellä.

## Loppuratkaisut

Tarjolla on viisi erilaista lopputulosta. Kultaisessa lopussa Mursumies saa tavaran tyrkylle ja on tyytyväinen. Myös aivan toisenlaisia lopputuloksia on mahdollista saada.

Vaimon kanssa onnistuminen perustuu kuuntelemiseen, vastuun ottamiseen ja yhteiseen haluun viettää iltaa. Avioliitto ei ole ostettavissa rahalla tai valmiilla neuvottelutaktiikalla.

## Tekninen rakenne

- `mursumies.py` ja `main.py`: käynnistimet
- `game.py`: pelimoottori, rahankäyttö, valinnat, esineet, tallennus ja ajastin
- `chapters/ch01.json`–`ch09.json`: luvut ja suomenkielinen sisältö
- `loput.json`: loppuratkaisujen tekstit
- `tests/test_game.py`: automaattiset testit

Lukujen tekstit ja valinnat ovat JSON-muodossa. Niitä voi muokata koodaamatta pelimoottoria uusiksi, kunhan kenttien rakenne säilyy. Pelaamiseen ei tarvita Qweniä, internet-yhteyttä eikä muita ohjelmia kuin Python.

## Testien ajaminen

Projektikansiossa:

```bash
python -m unittest discover -s tests -v
```

Testit käyttävät keinotekoista pelikelloa, jotta peliaikarajoitus voidaan testata ilman oikean viidentoista minuutin odotusta. Varsinaisessa pelissä käytetään oikeaa aikaa.
