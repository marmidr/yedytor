# Plan prac

[x] skopiować z Boomer kod czytający pliki PnP
[x] szablon aplikacji w tkinter
[x] podgląd pliku PnP
[ ] okienko wyszukiwania i skanowania plików *.Tou
    [x] wybór katalogu i skanowanie plików
    [x] parsowanie pliku Tou
    [x] podgląd listy unikalnych komponentów
    [ ] klasa trzymająca komponenty z Yamahy w pliku CSV
    [ ] przed dodaniem do lokalnej bazy, zatwierdzamy
        (np ignorujemy R0603_1K jak już mamy R0603_1k, oznaczamy jako zignorowany,
        żeby przy kolejnym skanowaniu nie pokazywać jako nowego)
    [x] zapisywanie wyciągniętej listy komponentów do CSV
[ ] okno edycji wczytanego PnP
    [ ] okienko wyboru kolumn: footprint i wartość
    [ ] dodawanie nowej kolumny
    [ ] lista z komponentami z Tou
    [ ] mechanizm wyszukiwania komponentu regex, case-insensitive
    [ ] mechanizm automatycznego wyboru komponentu na podstawie footprint+wartość
[ ] zapis nowego PnP zawsze jako CSV
[ ] katalog z Tou - trzymać ścieżkę w historii i uzupełniać pole
