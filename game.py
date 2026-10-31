"""Mursumies: data-driven terminal adventure, no external dependencies."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import textwrap
import time
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
CHAPTER_DIR = ROOT / "chapters"
STATS = {
    "raha": 47,
    "vaimon_tyytyvaisyys": 15,
    "bisnesmaine": 25,
    "ego": 90,
    "avioliiton_lampo": 10,
    "nolous": 0,
    "stressi": 30,
}
LABELS = {
    "raha": "Likviditeetti (€)",
    "vaimon_tyytyvaisyys": "Hallituksen tyytyväisyys",
    "bisnesmaine": "Markkinauskottavuus",
    "ego": "Toimitusjohtajan itsearvio",
    "avioliiton_lampo": "Kotimaan suhteet",
    "nolous": "Julkinen katastrofipotentiaali",
    "stressi": "Sisäinen kassakriisi",
}
START_ITEMS = {
    "nahkasalkku": "Aitoa keinonahkaa. Kolme tyhjää muovitaskua ja menestymisen tuoksu, joka muistuttaa vanhaa tupakkaa.",
    "käyntikortit": "CEO, Founder, Visionary, International Operations. Kuusi titteliä, ei yhtään toimivaa puhelinnumeroa.",
}
STANDARD_TEXT = {
    "unknown": "Mursumies ei tunnista kyseistä liiketoimintamallia.",
    "badnumber": "Valitse jokin tarjolla olevista numeroista. Mursumies ei hyväksy luovaa kirjanpitoa tässä asiassa.",
    "poor": "Tilillä ei ole katetta. Tämä on Mursumiehelle täysin uudenlainen tilanne, joka toistuu päivittäin.",
    "locked": "Tämä vaihtoehto ei ole vielä käytettävissä.",
    "timer": "Strateginen aikataulu ei ole vielä täyttynyt. Tutki ympäristöä tai kokeile sivutapahtumia.",
}


def load_story() -> list[dict[str, Any]]:
    result = []
    for n in range(1, 10):
        path = CHAPTER_DIR / f"ch{n:02}.json"
        if not path.exists():
            raise FileNotFoundError(f"Pelin luku puuttuu: {path.name}")
        with path.open("r", encoding="utf-8") as stream:
            result.append(json.load(stream))
    return result


def fresh_state() -> dict[str, Any]:
    return {
        "version": 1,
        "stats": dict(STATS),
        "items": dict(START_ITEMS),
        "flags": {},
        "seen": [],
        "history": [],
        "chapter": 1,
        "scene": 0,
        "seconds": {},
        "finished": False,
        "ending": None,
    }


class GameExit(Exception):
    """Clean exit via the 'lopeta' global command."""


class Game:
    def __init__(
        self,
        state: dict[str, Any] | None = None,
        *,
        save_path: str | Path = ROOT / "tallennus.json",
        clock: Callable[[], float] = time.monotonic,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
        stories: list[dict[str, Any]] | None = None,
        color: bool | None = None,
    ):
        self.state = state if state is not None else fresh_state()
        self.clock = clock
        self.reader = input_func
        self.writer = output_func
        self.save_path = Path(save_path)
        self.stories = stories if stories is not None else load_story()
        self.last_tick = self.clock()
        self.color = (sys.stdout.isatty() and os.getenv("NO_COLOR") is None) if color is None else color
        self.slow = False

    @property
    def current(self) -> dict[str, Any]:
        return self.stories[self.state["chapter"] - 1]

    def _write(self, message: str = "") -> None:
        self.writer(message)

    def say(self, message: str, *, accent: bool = False) -> None:
        if not message:
            return
        text = message.strip("\n")
        for line in text.splitlines():
            if not line.strip():
                self._write("")
                continue
            formatted = textwrap.fill(line.strip(), width=84, break_long_words=False, break_on_hyphens=False)
            if self.color and accent:
                formatted = "\033[1;36m" + formatted + "\033[0m"
            if self.slow and self.writer is print:
                for char in formatted:
                    print(char, end="", flush=True)
                    time.sleep(.009)
                self._write("")
            else:
                self._write(formatted)
        self._write("")

    def sync_time(self) -> None:
        now = self.clock()
        elapsed = max(0.0, now - self.last_tick)
        if not self.state["finished"]:
            key = str(self.state["chapter"])
            self.state["seconds"][key] = self.state["seconds"].get(key, 0.0) + elapsed
        self.last_tick = now

    def chapter_seconds(self) -> float:
        self.sync_time()
        return float(self.state["seconds"].get(str(self.state["chapter"]), 0.0))

    def total_seconds(self) -> float:
        self.sync_time()
        return sum(float(v) for v in self.state["seconds"].values())

    def save(self) -> None:
        self.sync_time()
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.save_path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as stream:
            json.dump(self.state, stream, ensure_ascii=False, indent=2)
        tmp.replace(self.save_path)

    @staticmethod
    def load(save_path: str | Path) -> dict[str, Any]:
        with Path(save_path).open("r", encoding="utf-8") as stream:
            state = json.load(stream)
        if state.get("version") != 1:
            raise ValueError("Tallennus on eri peliversiosta.")
        if not isinstance(state.get("chapter"), int) or not 1 <= state["chapter"] <= 9:
            raise ValueError("Tallennuksen lukunumero on virheellinen.")
        return state

    def change(self, **stats: int) -> None:
        for name, delta in stats.items():
            if name not in STATS:
                raise KeyError(f"Unknown stat: {name}")
            new_value = self.state["stats"][name] + int(delta)
            self.state["stats"][name] = max(0, new_value) if name == "raha" else max(0, min(100, new_value))

    def set_flag(self, name: str, value: bool = True) -> None:
        self.state["flags"][name] = bool(value)

    def has_flag(self, name: str) -> bool:
        return bool(self.state["flags"].get(name, False))

    def give(self, item: str, description: str) -> None:
        self.state["items"][item] = description

    def has_item(self, item: str) -> bool:
        return item in self.state["items"]

    def remove_item(self, item: str) -> None:
        self.state["items"].pop(item, None)

    def spend(self, amount: int) -> bool:
        if self.state["stats"]["raha"] < amount:
            return False
        self.change(raha=-amount)
        return True

    def condition(self, cond: dict[str, Any] | None) -> bool:
        if not cond:
            return True
        if "all" in cond:
            return all(self.condition(x) for x in cond["all"])
        if "any" in cond:
            return any(self.condition(x) for x in cond["any"])
        if "not" in cond:
            return not self.condition(cond["not"])
        if "flag" in cond:
            return self.has_flag(cond["flag"]) == cond.get("equals", True)
        if "item" in cond:
            return self.has_item(cond["item"]) == cond.get("equals", True)
        if "stat" in cond:
            value = self.state["stats"][cond["stat"]]
            return value >= cond["min"] if "min" in cond else value <= cond["max"]
        raise ValueError(f"Unknown requirement: {cond}")

    def apply(self, effects: dict[str, Any] | None) -> None:
        if not effects:
            return
        self.change(**effects.get("stats", {}))
        for name, value in effects.get("flags", {}).items():
            self.set_flag(name, value)
        for item, description in effects.get("give", {}).items():
            self.give(item, description)
        for item in effects.get("remove", []):
            self.remove_item(item)

    def show_conditions(self, entry: dict[str, Any]) -> None:
        for addition in entry.get("extras", []):
            if self.condition(addition.get("when")):
                self.say(addition["text"])

    def display_stats(self) -> None:
        self.say("MURSUMIEHEN HENKILÖKOHTAINEN TILINPÄÄTÖS", accent=True)
        for name, label in LABELS.items():
            self._write(f"  {label:<35} {self.state['stats'][name]:>4}")
        self._write(f"  Luku {self.state['chapter']}/9 | Aika {self.format_seconds(self.total_seconds())}")
        self._write("")

    def display_items(self) -> None:
        self.say("MURSUMIEHEN STRATEGINEN OMAISUUS", accent=True)
        for item, description in self.state["items"].items():
            self.say(f"{item.upper()}: {description}")
        if not self.state["items"]:
            self.say("Yhtiön omaisuus on arvioitu. Arvio oli nopea.")

    @staticmethod
    def format_seconds(seconds: float) -> str:
        total = int(seconds)
        return f"{total // 60:02}:{total % 60:02}"

    def show_time(self) -> None:
        self._write(f"Koko peli: {self.format_seconds(self.total_seconds())}.")
        self._write(f"Tämä luku: {self.format_seconds(self.chapter_seconds())} / {self.format_seconds(self.current['min_seconds'])}.")

    def help(self) -> None:
        self.say("OHJEET: Vastaa valintoihin numerolla. Komennot: tila, esineet, tutki, sivut, aika, ohje, tallenna, lopeta, nopeus. Valintojen vaikutuksia ei voi perua. 'sivut' näyttää pienet sivuseikkailut.")

    def explore(self) -> None:
        places = self.current.get("locations", [])
        if not places:
            self.say("Täällä ei ole tällä hetkellä mitään kiinnostavaa tutkittavaa.")
            return
        while True:
            self._write("\nTUTKI YMPÄRISTÖÄ")
            for i, place in enumerate(places, 1):
                self._write(f" {i}. {place['name']}")
            self._write(" 0. Palaa takaisin")
            cmd = self._read("Tutki > ")
            if cmd == "0":
                return
            if cmd.isdigit() and 1 <= int(cmd) <= len(places):
                place = places[int(cmd) - 1]
                self.say(place["text"])
            else:
                self.say(STANDARD_TEXT["badnumber"])

    def _read(self, prompt: str) -> str:
        try:
            result = self.reader(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            self.save()
            raise GameExit()
        commands = {
            "tila": self.display_stats,
            "esineet": self.display_items,
            "tutki": self.explore,
            "sivut": self.side_menu,
            "aika": self.show_time,
            "ohje": self.help,
            "tallenna": self.save_and_notice,
            "nopeus": self.toggle_speed,
        }
        lowered = result.lower()
        if lowered == "lopeta":
            self.save()
            raise GameExit()
        if lowered in commands:
            commands[lowered]()
            return "__command__"
        return result

    def save_and_notice(self) -> None:
        self.save()
        self.say("Taloushallinto tallensi tilanteen. Tilintarkastaja ei ole vielä nähnyt tätä.")

    def toggle_speed(self) -> None:
        self.slow = not self.slow
        self.say("Tekstin nopeus: " + ("hidas" if self.slow else "nopea"))

    def choose(self, question: str, options: list[dict[str, Any]], *, allow_back: bool = False) -> dict[str, Any] | None:
        while True:
            self._write("\n" + question)
            for i, option in enumerate(options, 1):
                access = self.condition(option.get("requires"))
                cost = int(option.get("cost", 0))
                note = " [ei käytettävissä]" if not access else " [ei varaa]" if cost > self.state["stats"]["raha"] else ""
                self._write(f" {i}. {option['label']}{note}")
            if allow_back:
                self._write(" 0. Takaisin")
            command = self._read("Valitse > ")
            if command == "__command__":
                continue
            if allow_back and command == "0":
                return None
            if not command.isdigit() or int(command) not in range(1, len(options) + 1):
                self.say(STANDARD_TEXT["badnumber"])
                continue
            selected = options[int(command) - 1]
            if not self.condition(selected.get("requires")):
                self.say(STANDARD_TEXT["locked"])
                continue
            cost = int(selected.get("cost", 0))
            if cost and self.state["stats"]["raha"] < cost:
                self.say(STANDARD_TEXT["poor"])
                continue
            return selected

    def resolve(self, selected: dict[str, Any], *, track: str) -> None:
        if track in self.state["seen"]:
            return
        if selected.get("cost"):
            if not self.spend(int(selected["cost"])):
                raise RuntimeError("Not enough funds after choice selection")
        self.say(selected["result"])
        self.show_conditions(selected)
        self.apply(selected.get("effects"))
        changes = selected.get("effects", {}).get("stats", {})
        if changes or selected.get("cost"):
            summaries = []
            if selected.get("cost"):
                summaries.append(f"Raha -{int(selected['cost'])} €")
            for name, amount in changes.items():
                if amount:
                    summaries.append(f"{LABELS[name]} {'+' if amount > 0 else ''}{amount}")
            self._write("  [ " + " | ".join(summaries) + " ]")
            self._write("")
        self.state["seen"].append(track)
        self.state["history"].append({"chapter": self.state["chapter"], "choice": selected["id"]})
        self.save()

    def side_menu(self) -> None:
        options = [x for x in self.current.get("optional", []) if x["id"] not in self.state["seen"]]
        if not options:
            self.say("Kaikki sivubisnekset on jo tutkittu. Yllättävää kyllä, yksikään ei ole tuottanut miljoonaa.")
            return
        self._write("\nSIVUKEIKAT")
        for i, item in enumerate(options, 1):
            self._write(f" {i}. {item['title']}")
        self._write(" 0. Takaisin")
        while True:
            command = self._read("Sivukeikka > ")
            if command == "__command__":
                continue
            if command == "0":
                return
            if command.isdigit() and 1 <= int(command) <= len(options):
                item = options[int(command) - 1]
                self.say(item["intro"])
                chosen = self.choose(item["question"], item["options"])
                self.resolve(chosen, track=item["id"])
                return
            self.say(STANDARD_TEXT["badnumber"])

    def run_scene(self, scene: dict[str, Any]) -> None:
        self.say(scene["intro"])
        self.show_conditions(scene)
        chosen = self.choose(scene["question"], scene["options"])
        self.resolve(chosen, track=scene["id"])
        self.state["scene"] += 1
        self.save()

    def chapter_gate(self, *, final: bool = False) -> None:
        limit = self.current["min_seconds"]
        self.say("LUKU SUORITETTU – TILANNE ON HALLINNASSA, VAIKKA MIKÄÄN EI VIITTAA SIIHEN.", accent=True)
        while True:
            elapsed = self.chapter_seconds()
            left = max(0, limit - elapsed)
            if final:
                left = max(left, 900 - self.total_seconds())
            self._write(f"\nLukuaika {self.format_seconds(elapsed)} / {self.format_seconds(limit)}")
            if final:
                self._write(f"Koko peli {self.format_seconds(self.total_seconds())} / 15:00")
            options = ["Jatka seuraavaan lukuun", "Tutki ympäristöä", "Tee sivukeikka", "Katso tilinpäätös", "Tutki esineitä", "Mietiskele hetki (10 sekuntia)"]
            for i, label in enumerate(options, 1):
                self._write(f" {i}. {label}")
            command = self._read("Toimi > ")
            if command == "__command__":
                continue
            if command == "1":
                if left <= 0:
                    self.sync_time()
                    return
                self.say(f"Pääkonttorin kello vaatii vielä {int(left + .999)} sekuntia toimintaa. Tutki ympäristöä tai tee sivukeikka.")
            elif command == "2":
                self.explore()
            elif command == "3":
                self.side_menu()
            elif command == "4":
                self.display_stats()
            elif command == "5":
                self.display_items()
            elif command == "6":
                self.say("Mursumies harjoittaa strategista hiljaisuutta. Se muistuttaa hänen tavallista työntekoaan.")
                time.sleep(10)
            else:
                self.say(STANDARD_TEXT["badnumber"])

    def play(self) -> None:
        self.say("MURSUMIES – TAVARA EI OLE TYRKYLLÄ", accent=True)
        self.say("Bisnes. Avioliitto. Konkurssi.")
        try:
            while not self.state["finished"]:
                chapter = self.current
                self._write("=" * 66)
                self._write(f"LUKU {self.state['chapter']}/9 – {chapter['title'].upper()}")
                self._write("=" * 66)
                intro_id = f"ch{self.state['chapter']:02}_intro"
                if intro_id not in self.state["seen"]:
                    self.say(chapter["intro"])
                    self.state["seen"].append(intro_id)
                    self.save()
                while self.state["scene"] < len(chapter["scenes"]):
                    self.run_scene(chapter["scenes"][self.state["scene"]])
                outro_id = f"ch{self.state['chapter']:02}_outro"
                if outro_id not in self.state["seen"]:
                    self.say(chapter["outro"])
                    self.state["seen"].append(outro_id)
                    self.save()
                self.chapter_gate(final=self.state["chapter"] == 9)
                if self.state["chapter"] == 9:
                    self.finish()
                    break
                self.state["chapter"] += 1
                self.state["scene"] = 0
                self.save()
        except GameExit:
            self.say("Mursumies sulki salkun. Liiketoiminta jatkuu myöhemmin.")

    def determine_ending(self) -> str:
        s = self.state["stats"]
        flags = self.state["flags"]
        odd = sum(1 for x in ("tanssiva kaktus", "premium-ilmapurkki", "CEO-kravatti", "sähköinen vihta") if self.has_item(x))
        if flags.get("mursuvaltio") and s["ego"] >= 95 and s["bisnesmaine"] <= 20 and odd >= 2:
            return "salainen"
        love = s["vaimon_tyytyvaisyys"] >= 58 and s["avioliiton_lampo"] >= 58 and flags.get("vaimon_luottamus", False)
        business = s["bisnesmaine"] >= 52 and flags.get("yrityssopimus", False)
        if love and business and flags.get("romanttinen_ele", False) and flags.get("haapaiva_muistettu", False):
            return "kultainen"
        if business and not love:
            return "hopeinen"
        if love:
            return "pronssinen"
        return "katastrofi"

    def finish(self) -> None:
        # The nine mandatory chapter clocks must total at least 900 seconds.
        if self.total_seconds() < 900:
            raise RuntimeError("Voittoa ei voida kirjata ennen 900 sekunnin peliaikaa.")
        ending = self.determine_ending()
        self.state["finished"] = True
        self.state["ending"] = ending
        success = ending == "kultainen"
        self.set_flag("tavara_tyrkylla", success)
        self.set_flag("mursumies_tyytyvainen", success)
        self.save()
        with (ROOT / "loput.json").open("r", encoding="utf-8") as stream:
            endings = json.load(stream)
        self.say(endings[ending], accent=True)
        self.display_stats()
        self.say(f"LOPPURATKAISU: {ending.upper()}")
        self.say("Kiitos pelaamisesta. Mursumies aikoo tuotteistaa tämänkin kokemuksen.")


def validate_story(stories: list[dict[str, Any]]) -> None:
    assert len(stories) == 9
    assert sum(x["min_seconds"] for x in stories) == 900
    all_ids = set()
    for chapter in stories:
        assert chapter["scenes"] and chapter["locations"]
        for event in chapter["scenes"] + chapter.get("optional", []):
            assert event["id"] not in all_ids, event["id"]
            all_ids.add(event["id"])
            assert len(event["options"]) >= 2
            for option in event["options"]:
                assert option["id"] and option["label"] and option["result"]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    stories = load_story()
    validate_story(stories)
    save_path = ROOT / "tallennus.json"
    print("=" * 56)
    print("               M U R S U M I E S")
    print("            TAVARA EI OLE TYRKYLLÄ")
    print("=" * 56)
    print("           BISNES. AVIOLIITTO. KONKURSSI.")
    print('    "Vaimo on kauhea. Tai tavara ei ole tyrkyllä."')
    print("=" * 56)
    while True:
        print("\n 1. Aloita uusi liiketoimintaseikkailu")
        print(" 2. Jatka kesken jäänyttä konkurssia")
        print(" 3. Käyttöohjeet")
        print(" 4. Poistu markkinoilta")
        try:
            ans = input("Valitse > ").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if ans == "1":
            if save_path.exists():
                confirm = input("Uusi peli korvaa vanhan tallennuksen. Kirjoita KYLLÄ jatkaaksesi > ")
                if confirm != "KYLLÄ":
                    continue
            Game(save_path=save_path, stories=stories).play()
        elif ans == "2":
            if not save_path.exists():
                print("Kirjanpito on hukassa. Tallennusta ei löydy.")
            else:
                try:
                    state = Game.load(save_path)
                    if state["finished"]:
                        print("Tilikausi on jo päätetty. Loppuratkaisu: " + str(state["ending"]))
                    else:
                        Game(state, save_path=save_path, stories=stories).play()
                except (ValueError, KeyError, json.JSONDecodeError) as error:
                    print("Tallennusta ei voitu avata:", error)
        elif ans == "3":
            print("Vastaa numerolla. Komennot: tila, esineet, tutki, sivut, aika, ohje, tallenna, lopeta, nopeus.")
            print("Yhdeksän lukua, 15 minuuttia oikeaa peliaikaa. Peliaika ei kulu ohjelman ollessa suljettuna.")
        elif ans == "4":
            return
        else:
            print(STANDARD_TEXT["badnumber"])


if __name__ == "__main__":
    main()
