# Projekt pri predmetu IEPS

## Okolje 
Vzpostavitev okolja je enaka kot v navodilih za nalogo. Uporabljali smo Anacondo ter PostgreSQL podatkovno bazo.
Shema baze se nahaja v crawldb.sql.

## Operacije nad bazo
Vse operacije (branje, pisanje v bazo) so implementirane v funkcijah v datoteki DBLogic.py. 

## Zagon programa
Program se zažene z zagonom datoteke crawler.py, ki požene pajka.
Za vzpostavitev baze in pravilno delovanje programa je potrebno v datoteki DbLogic.py spremeniti uporabniško ime in geslo za dostop do baze (funckija connect_to_db(().

## Podatkovna baza
Podatkovna baza je bila prevelika za Github (cca 590 MB), zato smo jo naložili na OneDrive in link pripeli v datoteko db.

