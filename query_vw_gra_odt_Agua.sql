
CREATE   VIEW [dbo].[vw_gra_odt_Agua] AS
  SELECT [OdtId],
          [MorId],
          [MorNombre],
		  [SmoNombre],
		  [TeoNombre],
		  [EsoFechaHoraOriginada] AS FechaOriginada,
		  [EsoFechaHoraIniciada] AS FechaIniciada,
		  [EsoFechaHoraFinalizada] AS FechaFinalizada,
		  [DepId],
		  [DepNombre] AS Departamento,
		  GEOMETRY::Point(OdtX,OdtY,22192) AS geom
  FROM [Jelu].[dbo].[vwOdtCompleta]
  WHERE ([OdtX]>2000000 AND [OdtY]>6000000 AND MorId=1)



