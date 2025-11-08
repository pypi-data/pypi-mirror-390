WITH lfb1_first AS (
    SELECT LIFNR,
        ALTKN,
        PERNR,
        ZTERM,
        ZWELS,
        ZAHLS,
        AKONT,
        FDGRV,
        BUKRS,
        ROW_NUMBER() OVER (
            PARTITION BY LIFNR
            ORDER BY BUKRS ASC
        ) AS rn
    FROM main.lfb1
)
SELECT lfa1.LIFNR AS "S_Lieferant.Lieferant",
    lfa1.MCOD1 AS "S_Lieferant.Suchbegriff",
    lfa1.MCOD2 AS "S_Lieferant.Selektion",
    lfa1.NAME1 AS "S_Adresse.Name1",
    lfa1.NAME2 AS "S_Adresse.Name2",
    lfa1.NAME3 AS "S_Adresse.Name3",
    lfa1.ORT01 AS "S_Adresse.Ort",
    lfa1.ORT02 AS "S_Adresse.CityPostfix",
    lfa1.PFACH AS "S_Adresse.Postfach",
    lfa1.PSTL2 AS "S_Adresse.PLZ_Postfach",
    lfa1.PSTLZ AS "S_Adresse.PLZ",
    lfa1.ADRNR AS "S_Adresse.AdressNr",
    lfa1.ANRED AS "S_Adresse.Anrede",
    lfa1.BRSCH AS "S_Lieferant.Branche",
    lfa1.KUNNR AS "S_Lieferant.Kundennummer",
    lfa1.LAND1 AS "S_Adresse.Staat",
    lfa1.LFURL AS "S_Adresse.HomePage",
    lfa1.REGIO AS "S_Adresse.Bundesland",
    lfa1.SPERM AS "BBM_WflLockStatus.BBM_WflLockStatus_ID",
    lfa1.SPRAS AS "S_Lieferant.Sprache",
    lfa1.STCD1 AS "S_Lieferant.inlaendische_SteuerNr",
    lfa1.STCD2 AS "S_Lieferant.cRU_ForeignTaxID",
    lfa1.STCD6 AS "S_Lieferant.cIN_GSTID",
    lfa1.STCEG AS "S_UStID.UStID",
    lfa1.STENR AS "S_Lieferant.P_Steuerregister",
    lfa1.STKZU AS "S_UStID.bestaetigt",
    lfa1.STRAS AS "S_Adresse.Strasse",
    lfa1.TELF1 AS "S_Adresse.Telefon",
    lfa1.TELF2 AS "S_Adresse.Telefon2",
    lfa1.TELFX AS "S_Adresse.Telefax",
    lfb1_f.PERNR AS "S_Lieferant.Sachbearbeiter",
    lfb1_f.ZTERM AS "S_Lieferant.ZahlungsZiel",
    lfb1_f.ZWELS AS "S_Lieferant.ZahlungsArt",
    lfb1_f.ZAHLS AS "S_Lieferant.RemittanceAdvice",
    lfb1_f.AKONT AS "S_KONTO.sammelkonto",
    lfb1_f.FDGRV AS "S_Lieferant.Kreditlimit"
FROM main.lfa1 AS lfa1
    LEFT JOIN lfb1_first AS lfb1_f ON lfa1.LIFNR = lfb1_f.LIFNR
    AND lfb1_f.rn = 1