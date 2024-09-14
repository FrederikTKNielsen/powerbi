Kort intro til hvordan analysis.py kunne være lavet i PowerBI

Trin 1: Import af data og grundlæggende datarensning
Vi starter med at importere vores data til Power BI. Vi skal være opmærksomme på datoformater og oprette et par beregnede kolonner for at håndtere eventuelle null-værdier:
DAXCopyDatoKolonne = HVIS(ERTVÆRT([Dato]), TOM(), [Dato])
FinansielDatoKolonne = HVIS(ERTVÆRT([Bogføringsdato]), TOM(), [Bogføringsdato])
Vi bør også tilføje en kolonne for månedsafslutning:
DAXCopyMåneds_Afslutning = SLUTMÅNED([Bogføringsdato], 0)
Trin 2: Beregning af gennemsnitlige budgetter
For at få et mere præcist billede af vores budget, skal vi beregne gennemsnittet af vores tre budgetkolonner:
DAXCopyGennemsnitlige_budgetter = GENNEMSNITX(
    { [Budget], [Budgetbeløb_Vedrører], [OprindeligtBudgetbeløb] },
    [Værdi]
)
Trin 3: Aggregering af data
Vi skal lave en opsummering af vores budgetdata baseret på dato og budgetnavn:
DAXCopyBudget_Aggregeret = OPSUMMÉR(
    facts_budgetpost,
    [Dato], [Budgetnavn],
    "Samlet Budget", SUM([Budget]),
    "Samlet Budgetbeløb_Vedrører", SUM([Budgetbeløb_Vedrører]),
    "Samlet OprindeligtBudgetbeløb", SUM([OprindeligtBudgetbeløb]),
    "Gennemsnitlige_budgetter", GENNEMSNIT([Gennemsnitlige_budgetter])
)
Trin 4: Beregning af udnyttelsesprocent
Vi skal lave en sikker beregning af udnyttelsesprocenten for at undgå division med nul:
DAXCopyUdnyttelsesprocent = DIVIDER(
    SUM([Forbrug]),
    SUM([Gennemsnitlige_budgetter]),
    0
) * 100
Trin 5: Sammenlægning af data
Vi skal bruge OPSLAGSVÆRDI til at sammenflette vores finansielle data:
DAXCopySammenflettetFinansielData = OPSLAGSVÆRDI(
    financial_monthly[Forbrug],
    financial_monthly[Måneds_Afslutning],
    facts_budgetpost[Dato]
)
Trin 6 og 7: Forberedelse til visualisering og beregning af procentvis forskel
Vi skal oprette nogle nøglemål til vores visualiseringer:
DAXCopySamlet_Gennemsnitligt_Budget = SUM([Gennemsnitlige_budgetter])
Samlet_Forbrug = SUM([Forbrug])
Procentvis_Forskel = DIVIDER([Samlet_Forbrug], [Samlet_Gennemsnitligt_Budget], 0) * 100 - 100
Trin 8 og 9: Visualiseringer og annotationer
Til sidst skal vi lave linje- og søjlediagrammer ved at trække vores mål ind i visualiseringerne. Vi bør også tilføje et kort, der viser den procentvise forskel mellem budget og forbrug.