import os
import sys
import json
import time
import importlib.util
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

# --- PELIMOOTTORI ---

class Game:
    def __init__(self):
        self.stats = {
            'raha': 47,
            'vaimon_tyytyvaisyys': 15,
            'bisnesmaine': 25,
            'ego': 90,
            'avioliiton_lampo': 10,
            'nolous': 0,
            'stressi': 30
        }
        self.items = {
            'NAHKASALKKU': "Aitoa keinonahkaa. Sisällä on kolme tyhjää muovitaskua ja menestymisen tuoksu. Tuoksu muistuttaa lähinnä vanhaa tupakkaa.",
            'KÄYNTIKORTTINIPPU': "Markku Mursunen, CEO, Founder, Visionary, International Operations. Kortissa on kuusi titteliä eikä yhtään toimivaa puhelinnumeroa."
        }
        self.flags = {}
        self.completed_actions = set()
        self.current_chapter = 0
        self.chapter_time_elapsed = 0.0
        self.chapter_times = [90, 100, 100, 110, 100, 110, 100, 100, 90]
        self.total_time = 0.0
        self.clock = time

    def say(self, text: str):
        print(text)

    def choose(self, question: str, options: List[Tuple[str, str]]) -> str:
        print(question)
        for i, (key, option) in enumerate(options, 1):
            print(f"{i}. {option}")
        while True:
            try:
                choice = int(input("Valitse numero: ")) - 1
                if 0 <= choice < len(options):
                    return options[choice][0]
                else:
                    print("Virheellinen valinta. Valitse jokin tarjolla olevista numeroista.")
            except ValueError:
                print("Syötä numero.")

    def change(self, **kwargs):
        for stat, value in kwargs.items():
            if stat in self.stats:
                new_value = self.stats[stat] + value
                self.stats[stat] = max(0, min(100, new_value))
            else:
                raise ValueError(f"Tuntematon tilasto: {stat}")

    def set_flag(self, name: str, value=True):
        self.flags[name] = value

    def has_flag(self, name: str) -> bool:
        return self.flags.get(name, False)

    def give(self, item_id: str, description: str):
        self.items[item_id] = description

    def has_item(self, item_id: str) -> bool:
        return item_id in self.items

    def remove_item(self, item_id: str):
        if item_id in self.items:
            del self.items[item_id]

    def spend(self, amount: int) -> bool:
        if self.stats['raha'] >= amount:
            self.stats['raha'] -= amount
            return True
        else:
            print("Tilillä ei ole katetta. Tämä on Mursumiehelle täysin uudenlainen tilanne, joka toistuu päivittäin.")
            return False

    def record_action(self, action_id: str) -> bool:
        if action_id in self.completed_actions:
            return False
        else:
            self.completed_actions.add(action_id)
            return True

    def explore(self, title: str, entries: Dict[str, str]):
        print(f"\n{title}")
        while True:
            print("\nValitse tutkittava kohde (tai 'poistu' palataksesi):")
            for i, (key, desc) in enumerate(entries.items(), 1):
                print(f"{i}. {key}")
            print(f"{len(entries)+1}. Poistu")
            
            try:
                choice = int(input("Valitse numero: ")) - 1
                if 0 <= choice < len(entries):
                    print(f"\n{list(entries.keys())[choice]}: {list(entries.values())[choice]}")
                    input("\nPaina Enter jatkaaksesi...")
                elif choice == len(entries):
                    break
                else:
                    print("Virheellinen valinta.")
            except ValueError:
                print("Syötä numero.")

# --- KELLORAJAPINTA ---

class ClockInterface:
    def time(self) -> float:
        raise NotImplementedError

class RealClock(ClockInterface):
    def time(self) -> float:
        return time.monotonic()

class FakeClock(ClockInterface):
    def __init__(self, initial_time: float = 0.0):
        self._time = initial_time
    def time(self) -> float:
        return self._time
    def advance(self, seconds: float):
        self._time += seconds

# --- PELIMOOTTORI ---

def load_chapters() -> List[str]:
    chapters_dir = "chapters"
    if not os.path.exists(chapters_dir):
        return []
    files = [f for f in os.listdir(chapters_dir) if f.startswith("ch") and f.endswith(".py")]
    files.sort()
    return [os.path.join(chapters_dir, f) for f in files]

def run_chapter(game: Game, chapter_path: str, clock: ClockInterface) -> bool:
    try:
        spec = importlib.util.spec_from_file_location("chapter", chapter_path)
        chapter_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chapter_module)
        
        start_time = clock.time()
        chapter_module.play(game)
        end_time = clock.time()
        
        elapsed = end_time - start_time
        required_time = game.chapter_times[game.current_chapter]
        
        if elapsed < required_time:
            remaining = required_time - elapsed
            print(f"\nLuku ei ole vielä valmis. Odota vielä {remaining:.1f} sekuntia...")
            while clock.time() - start_time < required_time:
                time.sleep(0.1)
        
        game.current_chapter += 1
        return True
    except Exception as e:
        print(f"Virhe luvun suorituksessa: {e}")
        return False

def save_game(game: Game, filename: str = "savegame.json"):
    data = {
        'stats': game.stats,
        'items': game.items,
        'flags': game.flags,
        'completed_actions': list(game.completed_actions),
        'current_chapter': game.current_chapter,
        'chapter_times': game.chapter_times,
        'total_time': game.total_time,
        'chapter_time_elapsed': game.chapter_time_elapsed
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_game(filename: str = "savegame.json") -> Optional[Game]:
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        game = Game()
        game.stats = data['stats']
        game.items = data['items']
        game.flags = data['flags']
        game.completed_actions = set(data['completed_actions'])
        game.current_chapter = data['current_chapter']
        game.chapter_times = data['chapter_times']
        game.total_time = data['total_time']
        game.chapter_time_elapsed = data['chapter_time_elapsed']
        
        return game
    except Exception as e:
        print(f"Virhe ladattaessa peliä: {e}")
        return None

def display_stats(game: Game):
    print("\nMURSUMIEHEN HENKILÖKOHTAINEN TILINPÄÄTÖS")
    print("=" * 40)
    for key, value in game.stats.items():
        print(f"{key}: {value}")
    print()

def display_items(game: Game):
    print("\nMURSUMIEHEN STRATEGINEN OMAISUUS")
    print("=" * 40)
    if not game.items:
        print("Ei esineitä.")
    else:
        for item_id, description in game.items.items():
            print(f"{item_id}: {description}")
    print()

def display_time(game: Game):
    print(f"\nPeliaika: {game.total_time:.1f} sekuntia")
    if game.current_chapter < len(game.chapter_times):
        print(f"Seuraava luku: {game.current_chapter + 1} ({game.chapter_times[game.current_chapter]} sekuntia minimi)")
    else:
        print("Kaikki luvut suoritettu.")

def display_help():
    print("\nKomennot:")
    print("tila - Näyttää pelin tilastot")
    print("esineet - Näyttää pelaajan esineet")
    print("tutki - Avaa tutkimisvalikon")
    print("aika - Näyttää kuluneen ajan")
    print("ohje - Näyttää tämän ohjeen")
    print("lopeta - Lopettaa pelin ja tallentaa")

def main():
    print("\nBISNES. AVIOLIITTO. KONKURSSI.")
    print('"Vaimo on kauhea. Tai sitten tavara ei ole tyrkyllä."')
    print("– Markku Mursunen             Toimitusjohtaja")
    print("=" * 50)
    
    game = load_game()
    clock = RealClock()
    
    if not game:
        # Uusi peli
        game = Game()
        print("\nAloita uusi liiketoimintaseikkailu")
        print("Jatka kesken jäänyttä konkurssia")
        print("Käyttöohjeet")
        print("Poistu markkinoilta")
        
        while True:
            try:
                choice = int(input("\nValitse numero: "))
                if choice == 1:
                    break
                elif choice == 2:
                    game = load_game()
                    if not game:
                        print("Ei tallennusta löytynyt.")
                        continue
                    else:
                        print("Jatketaan kesken jäänyttä peliä...")
                        break
                elif choice == 3:
                    display_help()
                    continue
                elif choice == 4:
                    print("Kiitos pelaamisesta!")
                    return
                else:
                    print("Virheellinen valinta. Valitse jokin tarjolla olevista numeroista.")
            except ValueError:
                print("Syötä numero.")
    
    chapters = load_chapters()
    
    if not chapters:
        print("\nEi lukuja saatavilla. Lataa ensin lukumoduulit.")
        return
    
    # Tarkistetaan, missä luvussa ollaan
    if game.current_chapter >= len(chapters):
        print("Kaikki luvut on jo suoritettu.")
        return
    
    for i in range(game.current_chapter, len(chapters)):
        chapter_path = chapters[i]
        print(f"\nSuoritetaan luku {i+1}...")
        if not run_chapter(game, chapter_path, clock):
            print("Luvun suoritus epäonnistui.")
            break
        game.total_time += game.chapter_times[i]
    
    # Loput
    print("\nSeikkailun seuraava luku on vielä suunnittelupöydällä. Mursumies kutsuu tätä hallituksi viivästykseksi.")
    save_game(game)
    print("Peli tallennettu.")

if __name__ == "__main__":
    main()