## LAB – ČÁST 1

### Od prázdného tenantu k běžící aplikaci v Microsoft Azure

### Koncept labu

Tento praktický lab vás provede základními principy práce s cloudovou platformou Microsoft Azure. Jeho cílem není pouze mechanicky vytvořit několik zdrojů v portálu, ale především pochopit souvislosti mezi architekturou, bezpečností, náklady a provozem.

Lab je navržen tak, aby účastníky naučil přemýšlet o cloudu jako o systému rozhodnutí, nikoli jako o sadě tlačítek v grafickém rozhraní. Každý krok má své technické i organizační dopady, které jsou v praxi často důležitější než samotná implementace.

### Scénář (business kontext)

Jste součástí firmy AcmeSoft, která vyvíjí webovou aplikaci pro externí zákazníky. Firma:

- sídlí v České republice,
- musí dodržovat GDPR,
- má omezený rozpočet,
- chce se vyhnout zbytečně složité a drahé infrastruktuře.

Firma se rozhodla začít využívat cloudovou platformu Azure, aby:

- nemusela spravovat vlastní hardware,
- mohla rychle nasazovat nové verze aplikace,
- měla možnost postupně řešení rozšiřovat.

Vaším úkolem je navrhnout a částečně implementovat vývojové prostředí v Azure, které:

- je přehledné a srozumitelné,
- respektuje základní bezpečnostní principy,
- dává smysl z pohledu provozu i nákladů,
- je připravené na další rozšiřování.

### Základní požadavky

Při návrhu řešení musíte splnit následující požadavky:

- existuje oddělené prostředí DEV a PROD,
- vývojáři nesmí mít možnost rozbít produkční prostředí,
- aplikace musí být dostupná z internetu,
- infrastruktura má být:
  - co nejjednodušší,
  - bez nutnosti správy serverů,
- všechna data i služby musí běžet v Evropské unii.

Tyto požadavky odpovídají velmi typické situaci ve firmách, které s cloudem začínají.

### Předpoklady

Před zahájením labu předpokládáme, že:

- máte přístup do Azure účtu (testovacího nebo vlastního),
- máte přidělenou roli Contributor,
- pracujete v Azure Portalu (https://portal.azure.com),
- během labu nevytvářejte drahé zdroje (velké VM, enterprise databáze apod.).

Cílem labu není utratit kredit, ale naučit se správně přemýšlet o architektuře.

## Úkol 1 – Návrh Azure struktury (organizační pohled)

### Proč řešit strukturu hned na začátku

Azure není jeden „účet“, ale hierarchicky strukturovaná platforma. Špatně navržená struktura na začátku vede v praxi k:

- chaosu v nákladech,
- nejasným odpovědnostem,
- bezpečnostním rizikům,
- složitému provozu.

Proto je první krok vždy návrh organizační struktury, ne samotné služby.

### Zadání

Navrhněte základní strukturu Azure pro firmu AcmeSoft.

Zamyslete se zejména nad tím:

- kolik potřebujete subscriptions,
- jak oddělíte vývojové a produkční prostředí,
- kde chcete řídit náklady a přístupy.

### Implementační část

V rámci jedné subscription vytvořte:

- Resource Group `rg-acmesoft-dev`
- Resource Group `rg-acmesoft-prod`

Pro obě Resource Groups nastavte:

- region West Europe (Netherlands).

Toto rozdělení zatím reprezentuje pouze logické oddělení prostředí, nikoli bezpečnostní hranici.

### Otázky k zamyšlení

Zamyslete se nad následujícími otázkami a připravte si odpovědi:

- Proč je Resource Group vhodná jako hranice životního cyklu aplikace?
- Co by se stalo, kdyby DEV a PROD byly v jedné Resource Group?
- Kdy by už v reálné firmě dávalo smysl použít více subscriptions místo jedné?

## Úkol 2 – Identity a řízení přístupu (RBAC)

### Proč je identita v cloudu klíčová

V tradiční infrastruktuře se bezpečnost často staví na síti. V cloudu je však identita hlavním bezpečnostním perimetrem. Každý přístup ke službám je autorizován a auditovatelný.

Špatně nastavená oprávnění jsou jedním z nejčastějších zdrojů bezpečnostních incidentů v cloudu.

### Zadání

Firma AcmeSoft má následující role:

- Vývojáři
  - pracují v prostředí DEV,
  - do PROD mají pouze náhled.
- Ops / Admin
  - spravují infrastrukturu,
  - nesou odpovědnost za provoz.

### Implementační část

V Microsoft Entra ID vytvořte:

- skupinu `acmesoft-devs`,
- skupinu `acmesoft-ops`.

Nastavte Role-Based Access Control (RBAC):

#### Skupina `acmesoft-devs`

- Contributor na `rg-acmesoft-dev`,
- Reader na `rg-acmesoft-prod`.

#### Skupina `acmesoft-ops`

- Contributor nebo Owner (dle společné diskuze).

Oprávnění nepřiřazujte přímo uživatelům, ale pouze skupinám.

### Otázky k zamyšlení

- Proč nepřiřazujeme oprávnění přímo jednotlivým uživatelům?
- Jaké riziko představuje role Owner?
- Co by se mohlo stát, kdyby měli vývojáři Contributor oprávnění na PROD?

## Úkol 3 – Výběr compute modelu

### Proč je výběr compute modelu důležitý

Compute služba určuje:

- kolik práce máte s provozem,
- kolik řeší Azure za vás,
- kolik řešení stojí v dlouhodobém horizontu.

Špatná volba compute modelu se často projeví až po měsících provozu, kdy je změna bolestivá a drahá.

### Zadání

Potřebujete nasadit jednoduchou webovou aplikaci, která:

- nevyžaduje správu serverů,
- dokáže se automaticky škálovat,
- je dostupná přes veřejnou URL.

### Rozhodovací část

Odpovězte si a ideálně prodiskutujte:

- Proč není Virtual Machine ideální volba pro tento scénář?
- Proč je AKS v tomto případě zbytečně složitý?
- Jaké vlastnosti by měl mít ideální compute model pro tuto aplikaci?

## Úkol 4 – Nasazení aplikace (Azure Container Apps)

### Proč Container Apps

Azure Container Apps umožňují běh kontejnerizované aplikace bez nutnosti správy Kubernetes clusteru. Azure zde přebírá:

- orchestrace,
- škálování,
- základní networking.

Vývojář se soustředí pouze na aplikaci.

### Implementační část

V Resource Group `rg-acmesoft-dev`:

- Vytvořte Azure Container App.
- Vytvořte nový Container App Environment.
- Použijte veřejný Docker image, například:
  - `mcr.microsoft.com/k8se/quickstart`.

Nastavte přístupnost aplikace:

- Ingress: External,
- Protokol: HTTP,
- Port: 80.

Nastavte automatické škálování:

- minimum instancí: 0,
- maximum instancí: 3.

### Ověření funkčnosti

- Otevřete veřejnou URL aplikace v prohlížeči.
- Ověřte, že aplikace odpovídá a běží korektně.

Zamyslete se nad tím, že:

- při nulovém provozu aplikace neběží,
- platíte pouze za skutečné využití.

## Úkol 5 – Síťový a bezpečnostní pohled

### Proč přemýšlet o síti už teď

I když aplikace funguje, její bezpečnost závisí na tom, které části jsou veřejně dostupné a které zůstávají skryté. Špatné rozhodnutí zde může mít vážné bezpečnostní důsledky.

### Analytická část

Zamyslete se nad architekturou aplikace:

- Které části musí být veřejně dostupné?
- Které části by měly být privátní?
- Kde by měla běžet databáze?

Nakreslete si jednoduché schéma:

- klient (internet),
- frontend / API,
- databáze.

### Otázky k zamyšlení

- Proč by databáze neměla mít veřejnou IP adresu, i kdyby byla chráněna heslem?
- Jakou roli by v této architektuře sehrála Virtual Network?
- Jak by se architektura změnila při napojení na další systémy?

## Rozšiřující úkoly (pokud stíháte)

Pokud máte dostatek času, zamyslete se nad těmito tématy:

- Jak byste:
  - oddělili PROD a DEV pomocí subscriptions?
  - řešili ukládání tajemství (hesla, connection stringy)?
  - přidali monitoring a alerting?
- Kde byste nastavili budgety a cost alerty?
- Jaký by byl další krok směrem k produkčnímu provozu?

### Výstup labu

Na konci labu byste měli mít:

- navrženou základní Azure strukturu,
- implementované vývojové prostředí (DEV),
- funkční aplikaci dostupnou z internetu,
- základní porozumění:
  - compute službám,
  - RBAC,
  - architektuře Azure,
  - základním bezpečnostním principům.

Správný start v cloudu není o počtu služeb, ale o kvalitě rozhodnutí. To, co se na začátku může zdát jako detail, často rozhoduje o bezpečnosti, ceně i provozuschopnosti celého řešení.
