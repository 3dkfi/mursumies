TITLE = "Mahonkikonttorin kriisi"
MIN_SECONDS = 90

def play(game):
    # Chapter flag to show opening only once
    if not game.has_flag("ch01_opening_shown"):
        game.say("Perjantai. Kello 15.47.")
        game.say("Markku Mursunen heräsi toimistonsa nahkasohvalta.")
        game.say("Hän oli nähnyt unta, jossa omisti yksityisen helikopterin, kaksi Audia ja vaimon, joka oli sanonut: 'Markku, sinä olit oikeassa.'")
        game.say("Herättyään hän huomasi omistavansa kahvinkeittimen, joka ei keittänyt kahvia, sekä yrityksen, joka ei tehnyt voittoa.")
        game.say("Mursumies suoristi solmiotaan.")
        game.say("'Jälleen yksi erinomainen päivä olla toimitusjohtaja.'")
        game.say("Puhelin värisi pöydällä.")
        game.say("13 vastaamatonta puhelua vaimolta.")
        game.say("'Puhelinmyyjät ovat nykyään kyllä aggressiivisia', Mursumies totesi.")
        game.set_flag("ch01_opening_shown")
    
    # Optional exploration
    if not game.has_flag("ch01_explored"):
        entries = {
            "Mahonkityöpöytä": "Pöytä on mahongin väristä lastulevyä. Mursumies maksoi siitä 300 euroa, koska myyjä käytti sanaa 'executive'.",
            "Kassakaappi": "Kassakaappi on tyhjä. Sisällä on käsin kirjoitettu lappu: PAREMMAT AJAT TULEVAT. Lappu on päivätty vuodelle 2017.",
            "Kahvinkeitin": "Keitin pitää ääntä, mutta mitään ei tapahdu. Mursumies tunnistaa toimintamallin omasta yrityksestään.",
            "Motivaatiojuliste": "Julisteessa lukee: NEVER GIVE UP. Sen alla on ulosoton kirjekuori.",
            "Hääkuva": "Kuvassa on kaksi onnellista ihmistä. Toinen heistä on tunnistettavasti Mursumies. Toinen näyttää ihmiseltä, joka ei vielä tiedä, mihin on ryhtymässä.",
            "Laskupino": "Yrityksen laskut on järjestetty värin mukaan. Punaisia on eniten.",
            "Toimistotuoli": "Tuoli narisee, vaikka siinä ei istu kukaan. Mursumies pitää ääntä työmotivaation merkkinä.",
            "Ikkuna": "Ikkunasta näkyy pysäköintialue. Mursumies kutsuu näkymää kansainvälisen logistiikkakeskuksen panoraamaksi.",
            "Vanhentunut yritysesite": "Esitteen kannessa lukee: MURSU CONSULTING – TULEVAISUUS ON MEIDÄN. Sisäsivut ovat tyhjiä. Mursumiehen mielestä tämä jättää tilaa kasvulle.",
            "Roska-astia": "Roska-astiassa on seitsemän hylättyä liiketoimintasuunnitelmaa ja yksi avioehtosopimuksen luonnos. Jälkimmäinen on kirjoitettu servietille.",
            "Työpöydän laatikko": "Laatikossa on kolme kynää, joista yksikään ei toimi, sekä käyntikortti, jossa Mursumies kutsuu itseään Pohjoismaiden johtavaksi strategiseksi visionääriksi. Kortin kääntöpuolella lukee käsin: MUISTA MAITO."
        }
        game.explore("MAHONKIKONTTORI – KANSAINVÄLISEN MENESTYKSEN KESKUS", entries)
        game.set_flag("ch01_explored")
    
    # Scene 1.1 - Yrityksen taloustilanne
    if not game.has_flag("ch01_finances"):
        game.say("Pöydällä oli pino laskuja, yrityksen tilinpäätös ja puoliksi syöty lihapiirakka.")
        game.say("Tilinpäätös oli päivätty viime viikolle.")
        game.say("Lihapiirakka ei.")
        game.say("Mursumies istuutui toimitusjohtajan tuoliin.")
        game.say("'On aika analysoida konsernin taloudellinen tilanne.'")
        
        choice = game.choose("Mitä Mursumies tutkii?", [
            ("financials", "Tutki tilinpäätöstä."),
            ("pie", "Tutki lihapiirakkaa."),
            ("bank", "Tarkista yrityksen pankkitili.")
        ])
        
        if choice == "financials":
            game.say("Liikevaihto: 47 euroa.")
            game.say("Liiketoiminnan muut tuotot: 0 euroa.")
            game.say("Asiakkaat: Markku Mursunen.")
            game.say("Mursumies nyökkäsi hyväksyvästi.")
            game.say("'Asiakaskunta on lojaali. Kasvupotentiaalia löytyy.'")
            game.say("Hän otti esiin laskimen.")
            game.say("'Jos kaksinkertaistamme asiakkaiden määrän, meillä on kaksi asiakasta.'")
            game.say("Tulos teki häneen vaikutuksen.")
            game.change(bisnesmaine=2, stressi=5)
            game.set_flag("ch01_finances_checked")
        elif choice == "pie":
            game.say("Mursumies haistoi lihapiirakkaa.")
            game.say("'Hmm. Kypsytetty.'")
            game.say("Hän sulki rasian ja kirjoitti sen päälle:")
            game.say("PREMIUM-LIHA, VUOSIKERTA 2024.")
            game.say("'Kenties elintarvikeala kaipaa tällaista innovaatiota.'")
            game.say("Lihapiirakka ei esittänyt vastalausetta.")
            game.say("Se oli toimiston yhteistyökykyisin työntekijä.")
            game.change(ego=2, nolous=3)
            game.set_flag("ch01_pie_investigated")
        elif choice == "bank":
            game.say("Pankkisovellus ilmoitti:")
            game.say("Käytettävissä: 47,00 €")
            game.say("Mursumies tuijotti lukua.")
            game.say("'Siinä on neljäkymmentäseitsemän mahdollisuutta tehdä eurosta miljoona.'")
            game.say("Puhelin ehdotti säästötavoitteen asettamista.")
            game.say("Mursumies kirjoitti tavoitteeksi:")
            game.say("ENSIMMÄINEN MILJARDI.")
            game.say("Sovellus kysyi tavoitepäivää.")
            game.say("Mursumies valitsi ensi perjantain.")
            game.change(stressi=7, ego=2)
            game.set_flag("ch01_bank_checked")
        
        game.set_flag("ch01_finances")
    
    # Scene 1.2 - Häädäivän mysteeri
    if not game.has_flag("ch01_anniversary"):
        game.say("Seinällä roikkui kalenteri.")
        game.say("Tämän päivän kohdalle oli piirretty punainen sydän, kolme huutomerkkiä ja teksti:")
        game.say("ÄLÄ UNOHDA!")
        game.say("Pöydällä oli myös muistilappu:")
        game.say("'Kukat. Illallinen. Älä puhu veroista.'")
        game.say("Toinen muistilappu sanoi:")
        game.say("'Perjantai. Ole ajoissa. Älä mainitse viime vuoden lahjaa.'")
        game.say("Kolmannessa luki:")
        game.say("'Kaksikymmentä vuotta yhteistä elämää.'")
        game.say("Mursumies raapi viiksiään.")
        game.say("'Tämä vaikuttaa vakavalta asiakastapaamiselta.'")
        game.say("Hän alkoi yhdistellä vihjeitä.")
        
        choice = game.choose("Mistä merkkipäivästä on kyse?", [
            ("wedding", "Hääpäivästä."),
            ("foundation", "Yrityksen perustamispäivästä."),
            ("birthday", "Vaimon syntymäpäivästä."),
            ("event", "Kunnan yritystapahtumasta.")
        ])
        
        if choice == "wedding":
            game.say("Mursumies katsoi kalenteria uudestaan.")
            game.say("'Saatanan perkele. Hääpäivä.'")
            game.say("Hän kirjoitti muistilehtiöön:")
            game.say("KOTIMAAN SUHTEET – KRIITTINEN TILANNE.")
            game.say("Tämän jälkeen hän piirsi muistiinpanon ympärille punaisen varoituskolmion.")
            game.say("Se tuntui ammattimaiselta.")
            game.change(avioliiton_lampo=5, stressi=10)
            game.set_flag("haapaiva_muistettu")
        elif choice == "foundation":
            game.say("'Mursu Consulting International Oy! Taas yksi menestyksen vuosi!'")
            game.say("Mursumies nousi seisomaan ja taputti itselleen.")
            game.say("Sitten hän huomasi hääkuvan.")
            game.say("'Pahus. Väärä organisaatio.'")
            game.say("Hän istuutui takaisin.")
            game.say("'Kummallakaan ei tosin ole ollut merkittävää kasvua viime vuosina.'")
            game.change(nolous=5, stressi=12)
            game.set_flag("haapaiva_muistettu")
        elif choice == "birthday":
            game.say("'Vaimon syntymäpäivä!'")
            game.say("Mursumies katsoi kalenteria tarkemmin.")
            game.say("'Hetkinen. Eihän hän täytä kahtakymmentä.'")
            game.say("Hän vilkaisi hääkuvaa.")
            game.say("'Aivan. Meillä on avioliiton vuosipäivä.'")
            game.say("Mursumies oli vähällä onnitella itseään päättelykyvystään.")
            game.change(stressi=10, nolous=4)
            game.set_flag("haapaiva_muistettu")
        elif choice == "event":
            game.say("'Kunnan yritystapahtuma!'")
            game.say("Mursumies alkoi etsiä parasta solmiotaan.")
            game.say("Sitten hän näki kalenterin reunaan kirjoitetun viestin:")
            game.say("'MARKKU, MEIDÄN HÄÄPÄIVÄ.'")
            game.say("Hän pysähtyi.")
            game.say("'Tämä on kyllä erittäin huonosti laadittu tapahtumakutsu.'")
            game.change(stressi=12, ego=2)
            game.set_flag("haapaiva_muistettu")
        
        game.set_flag("ch01_anniversary")
    
    # Scene 1.3 - Puhelu kotirintamaalle
    if not game.has_flag("ch01_phone"):
        game.say("Puhelin soi jälleen.")
        game.say("Näytössä luki:")
        game.say("VAIMO – ÄLÄ JÄTÄ VASTAAMATTA.")
        game.say("Mursumies ei muistanut tallentaneensa yhteystietoa noin.")
        game.say("Todennäköisesti vaimo oli tehnyt pienen päivityksen.")
        game.say("Puhelin jatkoi soimista.")
        game.say("Mursumies suoristi selkänsä.")
        game.say("'Kriisiviestintä on toimitusjohtajan tärkeimpiä ominaisuuksia.'")
        
        choice = game.choose("Miten Mursumies vastaa?", [
            ("apologize", "Vastaa ja myönnä olleesi huolimaton."),
            ("negotiate", "Vastaa ja väitä olevasi kansainvälisessä neuvottelussa."),
            ("auto", "Lähetä automaattinen poissaoloviesti."),
            ("service", "Vastaa kuin yrityksen asiakaspalvelu.")
        ])
        
        if choice == "apologize":
            game.say("'Hei. Minä olen ollut vähän huolimaton.'")
            game.say("'Vähän?'")
            game.say("'Keskisuuressa mittakaavassa.'")
            game.say("'Markku, onko sinulla mitään suunnitelmaa tälle illalle?'")
            game.say("'On. Ja ensimmäistä kertaa siihen kuuluu sinä.'")
            game.say("Vaimo huokaisi.")
            game.say("'No. Se on sentään alku.'")
            game.say("Mursumies hymyili.")
            game.say("'Neuvotteluyhteys on avattu.'")
            game.say("'Älä kutsu tätä neuvotteluksi, Markku.'")
            game.change(vaimon_tyytyvaisyys=10, avioliiton_lampo=8)
            game.set_flag("vastuu_otettu")
        elif choice == "negotiate":
            game.say("'Markku Mursunen, kansainvälinen johtoryhmä.'")
            game.say("'Kuulen jääkaapin hurinan. Olet taas toimistolla.'")
            game.say("'Se on yrityksen datakeskus.'")
            game.say("'Kotona ei ole ruokaa.'")
            game.say("'Selvä. Logistiikkaongelma.'")
            game.say("'Ja sauna on rikki.'")
            game.say("'Infrastruktuurikriisi.'")
            game.say("'Ja tänään on meidän hääpäivä.'")
            game.say("'Strateginen merkkipaalu.'")
            game.say("'Et sinä ole normaali.'")
            game.say("Mursumies kirjoitti muistiin:")
            game.say("ASIAKASPALAUTE: NEGATIIVINEN.")
            game.change(vaimon_tyytyvaisyys=-7, ego=3, nolous=5)
        elif choice == "auto":
            game.say("Mursumies naputti viestin:")
            game.say("'Kiitos yhteydenotostanne. Mursu Consulting International Oy käsittelee reklamaationne 3–5 arkipäivässä.'")
            game.say("Vastaus saapui välittömästi:")
            game.say("'SINÄ ASUT KOHTA SIELLÄ TOIMISTOLLA.'")
            game.say("Mursumies nyökkäsi.")
            game.say("'Nopea asiakaspalveluprosessi.'")
            game.say("Toinen viesti saapui:")
            game.say("'JA TÄNÄÄN ON MEIDÄN HÄÄPÄIVÄ.'")
            game.say("Mursumies vastasi peukaloemojilla.")
            game.say("Se oli virhe.")
            game.change(vaimon_tyytyvaisyys=-10, nolous=8, ego=2)
        elif choice == "service":
            game.say("'Mursu Consulting International Oy, asiakaspalvelu, Markku puhelimessa.'")
            game.say("'Hyvä. Minä haluaisin palauttaa yhden tuotteen.'")
            game.say("'Selvä. Mikä tuote on kyseessä?'")
            game.say("'Viisikymmentäkaksivuotias mies, joka ei tee kotitöitä.'")
            game.say("Mursumies hiljeni.")
            game.say("'Onko teillä kuittia?'")
            game.say("'On. Vihkitodistus.'")
            game.say("Mursumies katsoi puhelinta.")
            game.say("Tämä reklamaatio saattaisi mennä kuluttajariitalautakuntaan.")
            game.change(nolous=10, vaimon_tyytyvaisyys=-5, ego=-3)
        
        game.set_flag("ch01_phone")
    
    # Scene 1.4 - Sähkölaskun strateginen käsitteleminen
    if not game.has_flag("ch01_bill"):
        game.say("Laskupinosta paljastui 12 euron sähkölasku.")
        game.say("Eräpäivä oli ollut e