# Plan prac

[x] skopiować z Boomer kod czytający pliki PnP
[x] szablon aplikacji w tkinter
[x] podgląd pliku PnP
    [x] entry do wpisania pierwszego wiersza
    [x] zaznaczenie że PnP na wiersz nagłówka
[x] okienko wyszukiwania i skanowania plików *.Tou
    [x] wybór katalogu i skanowanie plików
    [x] parsowanie pliku Tou
    [x] podgląd listy unikalnych komponentów
    [x] klasa trzymająca komponenty z Yamahy w pliku CSV
    [x] zapisywanie wyciągniętej listy komponentów do CSV
[x] okno edycji wczytanego PnP
    [x] okienko wyboru kolumn: footprint i wartość
    [x] dodawanie nowej kolumny
    [x] lista z komponentami z Tou
    [x] mechanizm wyszukiwania komponentu, case-insensitive
    [x] mechanizm automatycznego wyboru komponentu na podstawie footprint+wartość
    [x] po ręcznym wyborze komponentu, zastosować do wszystkich pasujących
    [x] kolorować brak wyboru/wybrany automatycznie/ręcznie/filtr
    [x] lista komponentów: natural sorting
    [x] zamiast licznika, podawać identyfikator z pierwszej kolumny
    [ ] w ttk.Combobox obsłużyć TAB/Ctrl+TAB żeby bez myszy dało sie przejść do następnego wiersza, teraz np Down rozwija listę
    [x] generować raport: posortwana lista komponentów Yamaha + ilość do obsadzenia
    [ ] Rotation: gdy dla C0805_10k zmieniono kąt z 90 na 180 (+90) to dla wszystkich C0805_10k wykonać +90
        kolumna ze statusem, jak dla footprintu
    [ ] filtr (wszystkie/nieustawione/usunięte)
[x] zapis nowego PnP jako CSV
[x] katalog z Tou - trzymać ścieżkę w historii i uzupełniać pole
[x] okno podglądu i edycji bazy komponentów
  [x] podgląd
  [x] możliwość oznaczenia jako Hidden
  [x] przeniesienie z Home info o bazie i przycisku do skanera
[ ] osobne PnP dla top/bottom - po edycji trzeba zapisać osobno?
[x] zapisywanie niekompletnego edytowanego pliku, z możliwością kontynuacji
[x] przed zapisaniem sprawdź status każdego komponentu, zabroń zapisać jeśli nie-zielone
[x] progressbar: wybrane/wszystkie
[x] popupy - centrować na głównym bo uciekają
[x] wybór kolumn: pozycje oznaczać od 1, nie od 0
[x] nazwa pliku PnP w tutule okna
[x] 1row ignorowany po wczytaniu nowego pliku PnP
[x] 4 wątki wyszukiwania komponentu na podstawie Comment+Footprint
[x] logi - opcjonalne kolorowanie (konsola CMD jest nieczytelna)
[ ] weryfikacja wczytanego projektu:
    [ ] parametry Rotation są liczbami (wartość niesprecyzowana)
    [ ] parametry Layer są tylko dwa
[x] xls: rotation 180.00 -> 180
[x] gdy element M0805 12k, to próbować szukać znanych footprintów (402, 603, 805, 1206 itd)
    w członie footprintu i wstawiać samą liczbę do filtra
[x] przy wczytywaniu projektu ustawiać pole FirstRow na "1".
[x] obsługa DevLibEd2.Lib
[x] dodawanie nowych komponentów zamiast zastępować bazę tą z importu
[x] alias dla komponentu jako dodatkowa opcja wyszukiwania dopasowania
[x] edytor - least recently used
    [x] pamiętać ostatnie wybory komponentu dla danego filtra, przy robieniu listy sortować wg. ostatniego użycia
    [x] trzymać w osobnym pliku jako klucz(filtr) : lista[nazwa komponentów]
    [x] przy ładowaniu sprawdzać, czy komponenty z MRU nadal istnieją w DB i usuwać nieaktualne
[x] zapamiętywać drugi plik pnp: recent_pnp2_path
[x] yedytor.ini: zastąpić [columns] przez [recent]:
    <path> = "separator"; first-row; "columns";
    przywracać na starcie programu i po wczytaniu pliku
[ ] wczytywanie CSV/inne: przerywać nie jak kolumna A == "", tylko A==B==C==""
[ ] w niektórych plikach, gdy Rotation==0, to wczytuje ""
[ ] w niektórych plikach kolumna Description nie wczytuje sie dla każdego elementu
[ ] PnP Editor:
    [x] paginacja
    [x] filtry
    [ ] zastosowanie wyboru komponentu: brać descr pod uwagę?
        bo może być "402 100p" i "402 100p | 50V"
