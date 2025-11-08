SELECT
    LFA1.LIFNR AS "S_Ansprech.Konto",
    2 AS "S_Ansprech.Kontenbereich",  -- statisch für Lieferanten
    ADRC.ADDRNUMBER AS "S_Ansprech.AdressNr",
    ADRC.NAME1 AS "S_Ansprech.Name",
    ADRC.NAME2 AS "S_Ansprech.Nachname",
    ADRC.NAME3 AS "S_Ansprech.Vorname",
    ADRC.NAME4 AS "S_Ansprech.Abteilung",
    ADRC.TITLE AS "S_Ansprech.Titel",
    ADR2.TEL_NUMBER || COALESCE('/' || ADR2.TEL_EXTENS, '') AS "S_Ansprech.Telefon",
    ADR3.FAX_NUMBER || COALESCE('/' || ADR3.FAX_EXTENS, '') AS "S_Ansprech.Telefax",
    ADR6.SMTP_ADDR AS "S_Ansprech.EMail",
    ADRC.SORT1 AS "S_Ansprech.Selektion",
    ADRC.SORT2 AS "S_Ansprech.Selektionscode",
    ADRC.ADDR_GROUP AS "S_Ansprech.AnzeigeFolge",
    ADRC.REMARK AS "S_Ansprech.BriefAnrede",
    ROW_NUMBER() OVER (PARTITION BY LFA1.LIFNR ORDER BY ADRC.NAME1, ADRC.NAME2)
        AS "S_Ansprech.AnsprechNr"
FROM main.LFA1 AS LFA1
JOIN main.ADRC AS ADRC
    ON LFA1.ADRNR = ADRC.ADDRNUMBER
LEFT JOIN main.ADR2 AS ADR2
    ON ADRC.ADDRNUMBER = ADR2.ADDRNUMBER
LEFT JOIN main.ADR3 AS ADR3
    ON ADRC.ADDRNUMBER = ADR3.ADDRNUMBER
LEFT JOIN main.ADR6 AS ADR6
    ON ADRC.ADDRNUMBER = ADR6.ADDRNUMBER
ORDER BY "S_Ansprech.Konto", "S_Ansprech.AnsprechNr"