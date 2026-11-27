## LAB - ČÁST 2

### Od základního nasazení k bezpečné a udržitelné architektuře v Azure

V první části labu jste vytvořili základní strukturu Azure a nasadili jednoduchou aplikaci. V této druhé části se posuneme blíže k realitě produkčního provozu. Nebudeme se soustředit pouze na to, aby aplikace fungovala, ale také na to, aby byla provozovatelná, bezpečná a ekonomicky udržitelná.

Cílem této části není vybudovat kompletní produkční řešení, ale pochopit principy, které se při návrhu cloudové architektury používají v praxi.

### Rozšířený kontext scénáře

Aplikace firmy AcmeSoft se dostává do fáze, kdy ji začínají používat první reální uživatelé. Postupně se objevují nové požadavky:

- aplikace musí ukládat stav a data,
- některé části infrastruktury nesmí být vystavené veřejnému internetu,
- firma chce mít kontrolu nad náklady,
- bezpečnost přestává být „nice to have“ a stává se nutností.

Vaším úkolem je rozšířit stávající řešení tak, aby odpovídalo těmto požadavkům, ale zároveň nepřidávalo zbytečnou komplexitu. V cloudu totiž často platí, že jednoduché řešení je bezpečnější a levnější než překomplikovaná architektura.

## Úkol 6 - Virtual Network jako základ bezpečnosti

#### Proč se o sítě v cloudu vůbec starat

V on-prem prostředí bývá síť přirozenou bezpečnostní hranicí. Většina serverů není přímo dostupná z internetu a fyzická infrastruktura poskytuje určitou míru izolace. V cloudu tento předpoklad neplatí.

Pokud v Azure službě výslovně nezakážete veřejný přístup, je velmi často:

- dostupná z internetu,
- chráněna pouze aplikačními mechanismy,
- nebo zabezpečena jen minimálně.

Virtual Network (VNet) slouží jako základní nástroj pro vytvoření logické privátní sítě uvnitř Azure. Umožňuje oddělit veřejné části aplikace od interních komponent, jako jsou databáze nebo interní služby.

#### Zadání

Navrhněte síťovou strukturu pro vývojové prostředí aplikace AcmeSoft. Cílem není optimalizovat IP adresy, ale pochopit logické členění infrastruktury.

#### Implementační část

V Resource Group `rg-acmesoft-dev` vytvořte Virtual Network s následujícími vlastnostmi:

- název: `vnet-acmesoft-dev`
- adresní rozsah: např. `10.10.0.0/16`

V rámci této VNet vytvořte alespoň dva subnety:

- `snet-app`, určený pro aplikační vrstvu (web, API),
- `snet-data`, určený pro databáze a další interní služby.

Tyto subnety zatím nemusíte nijak dále konfigurovat. Slouží především k oddělení jednotlivých vrstev architektury a k budoucímu zpřísňování bezpečnostních pravidel.

#### Otázky k zamyšlení

Zamyslete se nad tím, proč je rozumné oddělit aplikační a datovou vrstvu už na úrovni sítě. Jaké problémy by mohly nastat, kdyby všechny komponenty běžely ve stejném subnetu? Jak by vám VNet pomohl v případě, že by bylo potřeba propojit Azure s on-prem infrastrukturou nebo VPN?

## Úkol 7 - Databáze jako služba (DBaaS)

#### Proč není databáze na VM dobrý nápad

Jednou z nejčastějších chyb v začátcích práce s cloudem je snaha provozovat databázi stejným způsobem jako na vlastním serveru - tedy jako proces běžící na virtuálním stroji. Tento přístup s sebou nese vysokou provozní zátěž: správu operačního systému, zálohování, patchování i řešení dostupnosti.

Azure nabízí databáze jako službu (DBaaS), kde se poskytovatel stará o:

- infrastrukturu,
- vysokou dostupnost,
- zálohování a obnovu,
- bezpečnost základního prostředí.

Zákazník se soustředí pouze na práci s daty.

#### Zadání

Navrhněte databázovou vrstvu aplikace tak, aby:

- nebyla veřejně dostupná z internetu,
- byla provozně nenáročná,
- měla nízké náklady pro vývojové prostředí.

#### Implementační část

Vytvořte Azure Database for PostgreSQL - Flexible Server s těmito vlastnostmi:

- typ workloadu: Development
- compute tier: Burstable
- region: stejný jako Virtual Network
- autentizace: PostgreSQL (uživatel a heslo)

V síťovém nastavení zvolte private access, tedy přístup pouze z Virtual Network. Databáze by neměla mít veřejnou IP adresu ani veřejný endpoint.

#### Vysvětlení síťového chování

Pokud byste se nyní pokusili připojit k databázi z lokálního počítače mimo Azure, připojení by selhalo. To je žádoucí chování - databáze je dostupná pouze z prostředí, které je součástí VNetu. V produkční architektuře by se k ní připojovala například aplikace běžící v Container Apps napojená na stejnou síť.

## Úkol 8 - Veřejné a privátní části aplikace

#### Rozlišení odpovědnosti

Každá aplikace má části, které musí být dostupné uživatelům z internetu, a části, které by měly zůstat skryté. Typickou chybou je vystavení příliš velkého množství komponent veřejnému provozu, což zvyšuje bezpečnostní rizika.

#### Analytická část

Rozdělte komponenty aplikace do dvou kategorií:

Veřejné komponenty
Sem patří ty části, se kterými komunikují koncoví uživatelé - typicky webové rozhraní nebo veřejné API.

Privátní komponenty
Sem patří databáze, storage, interní služby nebo backendová logika, ke které nemají mít uživatelé přímý přístup.

Nakreslete si jednoduché schéma komunikace mezi těmito částmi.

#### Otázky k zamyšlení

Proč je obecně špatný nápad mít databázi dostupnou z internetu, i když je chráněna heslem? Jaký bezpečnostní problém řeší private endpointy a síťová izolace?

## Úkol 9 - Práce s tajemstvími a přístupy

#### Proč jsou tajemství problém

Connection stringy, hesla a API klíče patří mezi nejčastější zdroj bezpečnostních incidentů v cloudu. Velmi často se objevují:

- přímo v kódu,
- v konfiguračních souborech,
- v CI/CD pipeline bez dostatečné ochrany.

Únik takového tajemství často znamená plný kompromis dané služby.

#### Koncepční zadání

Navrhněte, jak byste řešili:

- ukládání databázových přístupových údajů,
- přístup aplikace k těmto údajům bez použití hesla.

Využijte koncepty:

- Azure Key Vault,
- Managed Identity.

#### Otázky k zamyšlení

Proč je bezpečnější, když aplikace nezná žádné heslo? Jaký problém řeší identita spravovaná platformou? Jak byste postupovali v případě, že je nutné přístupové údaje rotovat?

## Úkol 10 - Řízení nákladů a prevence překvapení

#### Proč řešit náklady už v dev prostředí

Cloud umožňuje velmi rychle vytvářet nové zdroje, ale stejně rychle může generovat nečekané náklady. Správné řízení nákladů není účetní téma, ale architektonické rozhodnutí.

#### Implementační část

Prohlédněte si sekci Cost Management ve vaší subscription. Vytvořte jednoduchý budget, který vás upozorní při překročení definované hranice.

#### Otázky k zamyšlení

Jaký je rozdíl mezi sledováním nákladů na úrovni jednotlivých zdrojů a na úrovni subscription? Proč by budget měl být nastaven dřív, než vznikne problém?

## Shrnutí celé architektury

Na závěr se pokuste slovně nebo diagramem popsat výslednou architekturu:

- identita organizace (tenant),
- rozdělení zdrojů do Resource Groups,
- síťová izolace pomocí VNetu,
- veřejné a privátní komponenty,
- základní principy zabezpečení a řízení nákladů.
