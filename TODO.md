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
[x] zapis nowego PnP jako CSV
[x] katalog z Tou - trzymać ścieżkę w historii i uzupełniać pole
[x] okno podglądu i edycji bazy komponentów
  [x] podgląd
  [x] możliwość oznaczenia jako Hidden
  [x] przeniesienie z Home info o bazie i przycisku do skanera
[ ] osobne PnP dla top/bottom - po edycji trzeba zapisać osobno?
[ ] zapisywanie niekompletnego edytowanego pliku, z możliwością kontynuacji
[ ] zapisywanie niekompletnego - jak zapisać filtr, żeby odróżniał sie w pliku od prawdziwego komponentu?
[x] przed zapisaniem sprawdź status każdego komponentu, zabroń zapisać jeśli nie-zielone
[x] progressbar: wybrane/wszystkie
[x] popupy - centrować na głównym bo uciekają
[x] wybór kolumn: pozycje oznaczać od 1, nie od 0
[x] nazwa pliku PnP w tutule okna
[x] 1row ignorowany po wczytaniu nowego pliku PnP
